import spacy
import random
from typing import Dict, Set, Tuple

nlp = spacy.load("en_core_web_sm")


# Find all the singular verbs (e.g., eats) and create a dictionary mapping
# singular verbs -> lemmas (which is the plural form; eg the lemma for has is have)
# And lemmas -> singular verbs
# Then we swap verbs to inject errors
# If the verb is in the lemmas -> singular verbs dictionary then it’s plural, and we are making it singular (e.g., eat -> eats)
# If the verb is in the singular -> lemmas then it’s singular and we make it plural (e.g., has -> have)
# If the verb is not in the dictionaries we don’t swap it for now
# Train models with different amounts of errors
# 0
# 10
# 20
# 50


def build_verb_dictionaries(texts: list[str]) -> tuple[Dict[str, str], Dict[str, str]]:
    singular_to_lemma = {}  # has-->have, eat-->eats
    lemma_to_singular = {}  # have--> has, eat--> eats
    # prob only want  verbs --> need to verify
    all_verb_forms = []

    for text in texts:
        doc = nlp(text)
        for token in doc:
            if token.pos_ == "VERB":
                # print(f"Verb --> {token.text}")
                all_verb_forms.append((token.text, token.lemma_, token.tag_))
                # bc sing verb --> VBZ tag
                if token.tag_ == "VBZ":
                    singular_form = token.text
                    lemma = token.lemma_
                    singular_to_lemma[singular_form] = lemma
                    lemma_to_singular[lemma] = singular_form

    # print("\nAll verb forms:")
    # print(f"{'Verb':<15} {'Lemma':<15} {'Tag':<10}")
    # for verb, lemma, tag in sorted(all_verb_forms):
    #     print(f"{verb:<15} {lemma:<15} {tag:<10}")

    # # Print the mapping dictionaries
    # print("\nSingular to Lemma mappings:")
    # for singular, lemma in singular_to_lemma.items():
    #     print(f"{singular:<15} -> {lemma}")

    return singular_to_lemma, lemma_to_singular


def swap_verb_form(
    token: spacy.tokens.Token,
    singular_to_lemma: Dict[str, str],
    lemma_to_singular: Dict[str, str],
) -> Tuple[str, bool, str]:
    original = token.text

    # If the verb is in singular_to_lemma, it's singular, make it plural
    if token.text in singular_to_lemma:
        return singular_to_lemma[token.text], True, original

    # If the verb is in lemma_to_singular's values, it's plural, make it singular
    if token.lemma_ in lemma_to_singular:
        return lemma_to_singular[token.lemma_], True, original

    #  If the verb is not in the dictionaries we don’t swap it for now return original
    return token.text, False, original


def inject_errors(
    sentence: str,
    singular_to_lemma: Dict[str, str],
    lemma_to_singular: Dict[str, str],
    error_rate: float = 0.15,
    swap_limit: int = 10,
) -> Tuple[str, list]:
    doc = nlp(sentence)
    modified_tokens = []
    swaps_made = []
    # no of swaps fr ecah verb
    swap_count = {}

    for token in doc:
        if token.pos_ == "VERB":
            # injceting errors with thegiven error rate
            if random.random() < error_rate:
                verb_lemma = token.lemma_
                current_count = swap_count.get(verb_lemma, 0)

                # check for swap limit swap_limit times
                if current_count < swap_limit:
                    new_verb, was_swapped, original = swap_verb_form(
                        token, singular_to_lemma, lemma_to_singular
                    )
                    modified_tokens.append(new_verb)
                    if was_swapped:
                        swap_count[verb_lemma] = current_count + 1
                        swaps_made.append((original, new_verb))
                        # print(
                        #     f"Swapped '{original}' to '{new_verb}' (Count: {swap_count[verb_lemma]})"
                        # )
                else:
                    # swap limit reached --> no more swaps for this verb
                    modified_tokens.append(token.text)
                    # print(
                    #     f"Swap limit reached for '{token.text}' (Count: {current_count})"
                    # )
            else:
                # No swap based on the error rate probability
                modified_tokens.append(token.text)
        else:
            modified_tokens.append(token.text)

    # # final swap counts after processing the sentence
    # print("\nFinal swap counts for this sentence:")
    # for verb, count in swap_count.items():
    #     print(f"{verb:<15}: {count} swaps made")

    return " ".join(modified_tokens), swaps_made


def main(input_file: str, output_file: str, error_rates: list[float]):
    with open(input_file, "r") as f:
        texts = [line.strip() for line in f if line.strip()]
    singular_to_lemma, lemma_to_singular = build_verb_dictionaries(texts)
    for rate in error_rates:
        rate_str = str(int(rate * 100))
        output_path = output_file.replace(".txt", f"_{rate_str}_errors.txt")

        print(f"\nERROR RATE: {rate_str}%")

        all_swaps = []
        with open(output_path, "w") as f_out:
            for text in texts:
                modified_sentence, swaps = inject_errors(
                    text, singular_to_lemma, lemma_to_singular, error_rate=rate
                )
                f_out.write(modified_sentence + "\n")
                all_swaps.extend(swaps)

        # if all_swaps:
        #     print(f"\nVerbs that were swapped ({len(all_swaps)} total):")
        #     print(f"{'Original':<15} -> {'Modified':<15}")
        #     for original, modified in sorted(set(all_swaps)):
        #         print(f"{original:<15} -> {modified:<15}")
        # else:
        #     print("No verb swaps were made.")


# 0% errors, 5% errors, 10% errors, 15% errors, 25% errors, 50% errors)
if __name__ == "__main__":
    input_file = "data/train.txt"
    output_file = "data/error_data/train_with_errors.txt"
    error_rates = [0.1]
    main(input_file, output_file, error_rates)
