import spacy
from spacy_conll import init_parser
import json

from spacy_conll.parser import ConllParser

nlp = init_parser("en_core_web_sm", "spacy", include_headers=True)


parser = ConllParser(nlp)


def conllu_to_spacy(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    doc = nlp(text)
    return doc


def find_combined_patterns(doc):
    results = []

    singular_np_plural_verb_count = 0
    plural_np_singular_verb_count = 0
    singular_np_singular_verb_count = 0
    plural_np_plural_verb_count = 0
    singular_np_plural_rc_singular_verb_count = 0
    verbs = []
    aux_verbs = []
    past_tense_verbs = []

    for sent in doc.sents:
        print(f"Processing sentence: {sent.text}")
        sent_start = sent.start_char
        np_singular = None
        np_plural = None
        rc_plural = None
        verb_singular = None
        verb_plural = None
        pattern_match = {}

        for token in sent:
            print(
                f"Token: {token.text}, POS: {token.pos_}, Dep: {token.dep_}, Morph: {token.morph}"
            )
            if token.pos_ == "VERB":
                print(f"Found VERB: {token.text}")
                verbs.append(token.text)
            elif token.pos_ == "AUX":
                print(f"Found AUX: {token.text}")
                aux_verbs.append(token.text)

            # Detect past tense verbs
            if "Tense=Past" in token.morph:
                print(f"Found past tense verb: {token.text}")
                past_tense_verbs.append(
                    {
                        "verb": token.text,
                        "position_in_sentence": (
                            token.idx - sent_start,
                            (token.idx + len(token.text)) - sent_start,
                        ),
                        "sentence": sent.text.strip(),
                    }
                )

            for child in token.children:
                print(
                    f"Child of {token.text}: {child.text}, Dep: {child.dep_}, Morph: {child.morph}"
                )
                if child.dep_ == "nsubj":
                    print(f"Found subject: {child.text}")
                    compound_subject = False
                    for sub_child in child.children:
                        print(
                            f"Checking sub-child: {sub_child.text}, Dep: {sub_child.dep_}"
                        )
                        if sub_child.dep_ == "conj" or sub_child.dep_ == "cc":
                            compound_subject = True
                            print(
                                f"Found compound subject: {child.text} and {sub_child.text}"
                            )
                            break

                    if (
                        not compound_subject
                        and "Number=Sing" in child.morph
                        and "Number=Plur" in token.morph
                    ):
                        pattern_match = {
                            "pattern": "Singular NP with Plural AUX",
                            "np_singular": child.text,
                            "np_position": (
                                child.idx - sent_start,
                                (child.idx + len(child.text)) - sent_start,
                            ),
                            "aux_plural": token.text,
                            "sentence": sent.text.strip(),
                            "tense_info": {
                                "verb": token.text,
                                "tense": token.morph.get("Tense"),
                                "number": token.morph.get("Number"),
                            },
                        }
                        results.append(pattern_match)
                        print(
                            f"Error detected: Singular NP with Plural AUX - {child.text} {token.text}"
                        )
                        singular_np_plural_verb_count += 1

                    # If compound subject is found, treat it as plural
                    if compound_subject:
                        verb_plural = token.text
                    else:
                        verb_plural = "Number=Plur" in token.morph
                        verb_singular = "Number=Sing" in token.morph

                    if (
                        not compound_subject
                        and "Number=Sing" in child.morph  # Singular NP
                        and token.pos_
                        in ["VERB", "AUX"]  # Include both verbs and auxiliary verbs
                        and "Number=Plur" in token.morph  # Plural verb
                    ):
                        # Detected singular NP with plural verb (incorrect)
                        pattern_match = {
                            "pattern": "Singular NP with Plural Verb",
                            "np_singular": child.text,
                            "np_position": (
                                child.idx - sent_start,
                                (child.idx + len(child.text)) - sent_start,
                            ),
                            "verb_plural": token.text,
                            "sentence": sent.text.strip(),
                            "tense_info": {
                                "verb": token.text,
                                "tense": token.morph.get("Tense"),
                                "aspect": token.morph.get("Aspect"),
                                "number": token.morph.get("Number"),
                                "verb_position": (
                                    token.idx - sent_start,
                                    (token.idx + len(token.text)) - sent_start,
                                ),
                            },
                        }
                        results.append(pattern_match)

                        print(
                            f"Error detected: Singular NP with Plural Verb - {child.text} {token.text}"
                        )
                        singular_np_plural_verb_count += 1

                    elif compound_subject or "Number=Plur" in child.morph:
                        pattern_match = {
                            "pattern": "Plural NP with Plural Verb",
                            "np_plural": child.text,
                            "np_position": (
                                child.idx - sent_start,
                                (child.idx + len(child.text)) - sent_start,
                            ),
                            "verb_plural": token.text,
                            "sentence": sent.text.strip(),
                            "tense_info": {
                                "verb": token.text,
                                "tense": token.morph.get("Tense"),
                                "aspect": token.morph.get("Aspect"),
                                "number": token.morph.get("Number"),
                                "verb_position": (
                                    token.idx - sent_start,
                                    (token.idx + len(token.text)) - sent_start,
                                ),
                            },
                        }
                        results.append(pattern_match)
                        plural_np_plural_verb_count += 1

                    elif "Number=Plur" in child.morph and "Number=Sing" in token.morph:
                        pattern_match = {
                            "pattern": "Plural NP with Singular Verb",
                            "np_plural": child.text,
                            "np_position": (
                                child.idx - sent_start,
                                (child.idx + len(child.text)) - sent_start,
                            ),
                            "verb_singular": token.text,
                            "sentence": sent.text.strip(),
                            "tense_info": {
                                "verb": token.text,
                                "tense": token.morph.get("Tense"),
                                "aspect": token.morph.get("Aspect"),
                                "number": token.morph.get("Number"),
                                "verb_position": (
                                    token.idx - sent_start,
                                    (token.idx + len(token.text)) - sent_start,
                                ),
                            },
                        }
                        print(results)
                        results.append(pattern_match)
                        print(results)
                        plural_np_singular_verb_count += 1

                    elif (
                        not compound_subject
                        and "Number=Sing" in child.morph
                        and "Number=Sing" in token.morph
                    ):
                        pattern_match = {
                            "pattern": "Singular NP with Singular Verb",
                            "np_singular": child.text,
                            "np_position": (
                                child.idx - sent_start,
                                (child.idx + len(child.text)) - sent_start,
                            ),
                            "verb_singular": token.text,
                            "sentence": sent.text.strip(),
                            "tense_info": {
                                "verb": token.text,
                                "tense": token.morph.get("Tense"),
                                "aspect": token.morph.get("Aspect"),
                                "number": token.morph.get("Number"),
                                "verb_position": (
                                    token.idx - sent_start,
                                    (token.idx + len(token.text)) - sent_start,
                                ),
                            },
                        }
                        results.append(pattern_match)
                        singular_np_singular_verb_count += 1

        if np_singular and rc_plural and verb_singular:
            pattern_match = {
                "pattern": "Singular NP with Plural RC and Singular Verb",
                "np_singular": np_singular,
                "np_position": (
                    np_singular.idx - sent_start,
                    (np_singular.idx + len(np_singular.text)) - sent_start,
                ),
                "rc_plural": rc_plural,
                "verb_singular": verb_singular,
                "sentence": sent.text.strip(),
            }
            results.append(pattern_match)
            singular_np_plural_rc_singular_verb_count += 1

    print(f"Singular NP with Plural Verb: {singular_np_plural_verb_count}")
    print(f"Plural NP with Singular Verb: {plural_np_singular_verb_count}")
    print(f"Singular NP with Singular Verb: {singular_np_singular_verb_count}")
    print(f"Plural NP with Plural Verb: {plural_np_plural_verb_count}")
    print(
        f"Singular NP with Plural RC and Singular Verb: {singular_np_plural_rc_singular_verb_count}"
    )

    with open("output/pattern_results.json", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    with open("output/past_tense_verbs.txt", "w", encoding="utf-8") as txt_file:
        for entry in past_tense_verbs:
            txt_file.write(
                f"Verb: {entry['verb']}, Position: {entry['position_in_sentence']}, Sentence: {entry['sentence']}\n"
            )

    with open("output/aux.txt", "w", encoding="utf-8") as aux_file:
        aux_file.write("\n".join(aux_verbs))

    with open("output/verb.txt", "w", encoding="utf-8") as verb_file:
        verb_file.write("\n".join(verbs))


file_path = "output/final.conllu"
doc = conllu_to_spacy(file_path)
find_combined_patterns(doc)
