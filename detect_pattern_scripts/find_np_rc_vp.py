import spacy
from collections import defaultdict


nlp = spacy.load("en_core_web_sm")

file_path = "data/generated/structure_type_9_pairs.txt"
with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

doc = nlp(text)

subject_verb_pairs = []


def is_compound_subject(token):
    # funvtion to check if the subject is compound by finding the coordinatog conjunctions like
    # 'and', 'or', etc, wihin the subject's children (namely dependent tokens) .
    compound_conjunctions = ["and", "or", "as well as", "along with", "together with"]
    return any(
        # if the subject is compound this should/will/can affect
        # whether a plural/singular verb should be used
        child.dep_ == "cc"
        and any(phrase in child.text for phrase in compound_conjunctions)
        for child in token.children
    )


def find_antecedent(subject):
    """
    Find the antecedent of relative pronouns like 'who', 'which', or 'that'
    by traversing the dependency tree upwards to find the noun the relative pronoun refers to.
    """
    antecedent = subject.head
    while (
        antecedent.dep_ not in ["nsubj", "nsubjpass", "attr", "ROOT"]
        and antecedent != antecedent.head
    ):
        antecedent = antecedent.head
    return antecedent


def check_agreement(subject, verb):
    """
    Check if the subject and verb agree, handling relative pronouns and special cases like 'each'.
    """
    # If the subject is a relative pronoun (e.g., "who", "which")
    if subject.text.lower() in ["who", "which", "whose", "whom", "that"]:
        # Find the antecedent (e.g., 'students' for 'who')
        antecedent = find_antecedent(subject)
        print(
            f"Relative pronoun '{subject.text}' refers to antecedent '{antecedent.text}'"
        )
        subject_is_plural = antecedent.tag_ in ["NNS", "NNPS"] or is_compound_subject(
            antecedent
        )
    else:
        # Check if the subject is plural for non-relative clauses
        subject_is_plural = subject.tag_ in ["NNS", "NNPS"] or is_compound_subject(
            subject
        )

    # Handle 'each' specifically
    if subject.text.lower() == "each" and subject.head.dep_ != "nsubj":
        return True

    if "each" in [child.text.lower() for child in subject.children]:
        return verb.tag_ == "VBP"

    verb_is_singular = verb.tag_ == "VBZ"
    verb_is_plural = verb.tag_ == "VBP"

    if verb.tag_ == "VBD":
        return True

    # Handle auxiliary verbs
    aux = [child for child in verb.children if child.dep_ in ["aux", "auxpass"]]
    if aux:
        aux_tag = aux[-1].tag_
        if aux_tag == "VBZ" and not subject_is_plural:
            return True
        elif aux_tag == "VBP" and subject_is_plural:
            return True
        elif aux_tag in ["VBD", "VBN"]:
            return True
        print(
            f"Auxiliary agreement error: '{subject.text}' does not agree with '{aux[-1].text}'"
        )
        return False

    # Main verb check (no auxiliary words)
    if subject_is_plural and verb_is_plural:
        return True
    elif not subject_is_plural and verb_is_singular:
        return True

    print(
        f"Main verb agreement error: '{subject.text}' does not agree with '{verb.text}'"
    )
    return False


def find_subject_verb_pairs(token, subject_verb_pairs=None, level=0):

    # this function recursively traverses the dependency tree and to find  all subject-verb pairs in it
    if subject_verb_pairs is None:
        subject_verb_pairs = []

    # chceks if the token is a verb
    if token.pos_ in ["VERB", "AUX"]:
        # then looking at its correspondng subject
        for child in token.children:
            if child.dep_ in ["nsubj", "nsubjpass"]:
                # add to the subject_verb_pairs list
                subject_verb_pairs.append((child, token, level))

    #  level variable tracks how deep in the sent structure the pair is found(mostly for debugging )
    for child in token.children:
        find_subject_verb_pairs(child, subject_verb_pairs, level + 1)
    return subject_verb_pairs


def check_nested_subject_verb_agreement(doc):
    for sent in doc.sents:
        print(f"\nSentence: {sent.text.strip()}")

        # fina all subject-verb pairs for ecah snetenece
        subject_verb_pairs = find_subject_verb_pairs(sent.root)

        # checks whether they agree using check_agreement.
        for subject, verb, level in subject_verb_pairs:
            if check_agreement(subject, verb):
                # printng the agrremenst resuls for echa pair as well as the level of embedding.
                print(
                    f"Level {level} - NP '{subject.text}' agrees with VP '{verb.text}'"
                )
            else:
                print(
                    f"Level {level} - NP '{subject.text}' does not agree with VP '{verb.text}'"
                )
                # Additional checks for deeply nested clauses
        for subj, verb, lvl in subject_verb_pairs:
            if lvl > 1:
                print(
                    f"more nested clause at level {lvl}: NP '{subj.text}' -> VP '{verb.text}'"
                )


def find_np_rc_vp(doc):

    # This function looks specifically for NP RC VP patterns + counts
    # freq of specific structures --> singular NP -> plural RC -> singular VP --> just for this for now

    structure_count = defaultdict(int)
    structures_found = []

    print("ID\tFORM\tLEMMA\tUPOS\tXPOS\tFEATS\tHEAD\tDEPREL\tDEPS\tMISC")

    for sent in doc.sents:
        print(f"\nSentence Check: {sent.text.strip()}")

        main_subject = None
        main_verb = None
        relative_clause_subject = None
        relative_clause_verb = None

        for idx, token in enumerate(sent, start=1):
            print(
                f"{idx}\t{token.text}\t{token.lemma_}\t{token.pos_}\t{token.tag_}\t_\t{token.head.i + 1 if token.head != token else 0}\t{token.dep_}\t_\t_"
            )

            # Main clause: subject (nsubj) and main verb (ROOT)
            if token.dep_ == "nsubj" and token.head.dep_ == "ROOT":
                main_subject = token
            if token.dep_ == "ROOT":
                main_verb = token

        # Check for main sva
        if main_subject and main_verb:
            if check_agreement(main_subject, main_verb):
                print(
                    f"Main clause match: NP '{main_subject.text}', VP '{main_verb.text}' (agreement correct)"
                )
            else:
                print(
                    f"Main clause error: NP '{main_subject.text}' does not agree with VP '{main_verb.text}'"
                )

            # Check for relative clauses: nsubj and verb (relcl)
            for token in sent:
                if token.dep_ == "nsubj" and token.head.dep_ == "relcl":
                    relative_clause_subject = token
                if token.dep_ == "relcl":
                    relative_clause_verb = token

            # If both RC subject and verb are found
            if relative_clause_subject and relative_clause_verb:
                if check_agreement(relative_clause_subject, relative_clause_verb):
                    print(
                        f"Relative clause match: NP '{relative_clause_subject.text}', VP '{relative_clause_verb.text}' (agreement correct)"
                    )
                else:
                    print(
                        f"Relative clause error: NP '{relative_clause_subject.text}' does not agree with VP '{relative_clause_verb.text}'"
                    )
                print(f"Found NP RC VP pattern: {sent.text.strip()}")

                # checking the specific structure NP RC VP
                main_subject_is_singular = main_subject.tag_ in ["NN", "NNP"]
                relative_clause_subject_is_plural = relative_clause_subject.tag_ in [
                    "NNS",
                    "NNPS",
                ]
                main_verb_is_singular = main_verb.tag_ == "VBZ"

                # checking for the Singular NP, Plural RC, Singular VP
                if (
                    main_subject_is_singular
                    and relative_clause_subject_is_plural
                    and main_verb_is_singular
                ):
                    structure_count["Singular NP -> Plural RC -> Singular VP"] += 1
                    structures_found.append(f"Sentence: {sent.text.strip()}")
                    structures_found.append(
                        f"NP: {main_subject.text}, RC: {relative_clause_subject.text}, VP: {main_verb.text}"
                    )
                    structures_found.append("")

            else:
                print("No relative clause match found.")
        else:
            print("No main clause match found.")

    print("\n--- Structure Frequencies ---")
    for structure, count in structure_count.items():
        print(f"{structure}: {count}")

    with open(
        "output/structure_frequencies_and_examples.txt", "w", encoding="utf-8"
    ) as freq_file:

        freq_file.write("--- Structure Frequencies ---\n")
        for structure, count in structure_count.items():
            freq_file.write(f"{structure}: {count}\n")

        freq_file.write("\n--- Found Structures (NP RC VP Pattern) ---\n")
        for structure in structures_found:
            freq_file.write(structure + "\n")


def find_np_rc_rc_rc_vp(doc):

    # dict to store diff sent struct counts
    structure_count = defaultdict(int)
    # list to store sents that match the specified patterns.
    structures_found = []

    with open("output/np_rc_vp_structure.txt", "w", encoding="utf-8") as output_file:
        output_file.write("Sentence Structure Analysis:\n\n")

        for sent in doc.sents:
            output_file.write(f"Sentence Check: {sent.text.strip()}\n")
            print(f"\nSentence Check: {sent.text.strip()}")

            main_subject = None
            main_verb = None
            relative_clause_subject = None
            relative_clause_verb = None
            nested_rc_subject = None
            nested_rc_verb = None

            # counters
            np_count = 0
            rc_count = 0
            vp_count = 0

            # iterating over each word in the sent
            for idx, token in enumerate(sent, start=1):
                print(
                    f"{idx}\t{token.text}\t{token.lemma_}\t{token.pos_}\t{token.tag_}\t_\t{token.head.i + 1 if token.head != token else 0}\t{token.dep_}\t_\t_"
                )

                # criterias for main_subject = token's dependency is nsubj (nominal subject) and parent word = ["aux", "root verb"]
                if token.dep_ == "nsubj" and token.head.dep_ in ["aux", "ROOT"]:
                    main_subject = token
                    # because main subject was found
                    np_count += 1
                    output_file.write(
                        f"Main subject identified: {main_subject.text} (nsubj)\n"
                    )
                    print(f"Debug: Main subject identified as {main_subject.text}.")

                # for root verb
                if token.dep_ in ["aux", "ROOT"]:
                    main_verb = token
                    # because main verb was found
                    vp_count += 1
                    output_file.write(
                        f"Main verb identified: {main_verb.text} (ROOT/aux)\n"
                    )
                    print(f"Debug: Main verb identified as {main_verb.text}.")

                # Identify relative clause subject and verb
                if token.dep_ == "nsubj" and token.head.dep_ == "relcl":
                    relative_clause_subject = token
                    np_count += 1  # Increment NP counter for RC
                    rc_count += 1  # Increment RC counter
                    output_file.write(
                        f"Relative clause subject: {relative_clause_subject.text} (nsubj)\n"
                    )
                    print(
                        f"Debug: Relative clause subject found: {relative_clause_subject.text}."
                    )

                # checks for relative clause subjects (nsubj where the head is a relative clause relcl)
                if token.dep_ == "relcl" and token.head.dep_ != "relcl":
                    relative_clause_verb = token
                    vp_count += 1
                    output_file.write(
                        f"Relative clause verb: {relative_clause_verb.text} (relcl)\n"
                    )
                    print(
                        f"Debug: Relative clause verb found: {relative_clause_verb.text}."
                    )

                # Check agreement between RC subject and RC verb
                if relative_clause_subject and relative_clause_verb:
                    if check_agreement(relative_clause_subject, relative_clause_verb):
                        print(
                            f"Relative clause match: NP '{relative_clause_subject.text}', VP '{relative_clause_verb.text}' (agreement correct)"
                        )
                        output_file.write(
                            f"Relative clause agreement: NP '{relative_clause_subject.text}' agrees with VP '{relative_clause_verb.text}'\n"
                        )
                    else:
                        print(
                            f"Relative clause error: NP '{relative_clause_subject.text}' does not agree with VP '{relative_clause_verb.text}'"
                        )
                        output_file.write(
                            f"Relative clause error: NP '{relative_clause_subject.text}' does not agree with VP '{relative_clause_verb.text}'\n"
                        )

                # find the 1st level nested relative clause (RC -> RC)
                if (
                    token.dep_ == "nsubj"
                    and token.head.dep_ == "relcl"
                    and token.head.head.dep_ == "relcl"
                ):
                    nested_rc_subject = token
                    # for nested rc and nps
                    np_count += 1
                    rc_count += 1
                    output_file.write(
                        f"Nested relative clause subject: {nested_rc_subject.text} (nsubj)\n"
                    )
                    print(
                        f"Debug: Nested relative clause subject found: {nested_rc_subject.text}."
                    )

                if token.dep_ == "relcl" and token.head.dep_ == "relcl":
                    nested_rc_verb = token
                    vp_count += 1  #
                    output_file.write(
                        f"Nested relative clause verb: {nested_rc_verb.text} (relcl)\n"
                    )
                    print(
                        f"Debug: Nested relative clause verb found: {nested_rc_verb.text}."
                    )

                # handling conjoined RCs with "and"
                if token.dep_ == "cc" and token.head.dep_ == "relcl":
                    # handling conjoined RCs like "whom the girls like and whose parents know"
                    output_file.write(
                        f"Conjoined relative clause: {token.head.text} and {token.text}\n"
                    )
                    rc_count += 1
                    vp_count += 1
                    print(
                        f"Debug: Conjoined relative clause found: {token.head.text} and {token.text}."
                    )

            output_file.write(f"\n--- Structure Counts ---\n")
            output_file.write(f"Total NPs: {np_count}\n")
            output_file.write(f"Total RCs: {rc_count}\n")
            output_file.write(f"Total VPs: {vp_count}\n\n")
            print(
                f"Debug: Total NPs: {np_count}, Total RCs: {rc_count}, Total VPs: {vp_count}"
            )

            # check for if NP -> RC -> RC -> VP pattern , at least 2 RCs found
            if (
                rc_count >= 2
                and main_subject
                and main_verb
                and relative_clause_subject
                and relative_clause_verb
            ):
                structure_count["NP -> RC -> RC -> VP"] += 1
                structures_found.append(f"Sentence: {sent.text.strip()}")
                structures_found.append(
                    f"NP: {main_subject.text}, RC_Subj: {relative_clause_subject.text}, RC_Verb: {relative_clause_verb.text}, VP: {main_verb.text}"
                )
                print(f"Debug: Found NP -> RC -> RC -> VP pattern.")
            elif (
                rc_count == 1
                and main_subject
                and main_verb
                and relative_clause_subject
                and relative_clause_verb
            ):
                structure_count["NP -> RC -> VP"] += 1
                print(f"Debug: Found NP -> RC -> VP pattern.")

    with open(
        "output/structure_frequencies_and_examples.txt", "w", encoding="utf-8"
    ) as freq_file:
        freq_file.write("--- Structure Frequencies ---\n")
        for structure, count in structure_count.items():
            freq_file.write(f"{structure}: {count}\n")

        freq_file.write("\n--- Found Structures (NP RC RC VP Pattern) ---\n")
        for structure in structures_found:
            freq_file.write(structure + "\n")


find_np_rc_rc_rc_vp(doc)


# find_np_rc_vp(doc)


check_nested_subject_verb_agreement(doc)
