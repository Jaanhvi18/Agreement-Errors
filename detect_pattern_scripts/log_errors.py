import spacy
from collections import defaultdict
import os

nlp = spacy.load("en_core_web_sm")

file_path = "data/a.txt"
with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

doc = nlp(text)

subject_verb_pairs = []

def log_error(
    sentence,
    subject,
    verb,
    error_type="Main Clause",
    error_file_path="output/error_log.txt",
):
    os.makedirs(os.path.dirname(error_file_path), exist_ok=True)

    with open(error_file_path, "a", encoding="utf-8") as error_file:
        error_file.write("\n--- Structure Counts ---\n")
        error_file.write(f"Sentence Check: {sentence}\n")
        error_file.write(f"{error_type} error detected:\n")
        error_file.write(f"Subject: '{subject}' (nsubj)\n")
        error_file.write(f"Verb: '{verb}' (ROOT/aux/relcl)\n")
        error_file.write(
            f"{error_type} error: NP '{subject}' does not agree with VP '{verb}'\n"
        )
        print(f"{error_type} error: NP '{subject}' does not agree with VP '{verb}'")


def is_compound_subject(token):
    compound_conjunctions = ["and", "or", "as well as", "along with", "together with"]
    return any(
        child.dep_ == "cc"
        and any(phrase in child.text for phrase in compound_conjunctions)
        for child in token.children
    )


def find_antecedent(subject):
    antecedent = subject.head
    while (
        antecedent.dep_ not in ["nsubj", "nsubjpass", "attr", "ROOT"]
        and antecedent != antecedent.head
    ):
        antecedent = antecedent.head
    return antecedent


def check_agreement(subject, verb):
    if subject.text.lower() in ["who", "which", "whose", "whom", "that"]:
        antecedent = find_antecedent(subject)
        subject_is_plural = antecedent.tag_ in ["NNS", "NNPS"] or is_compound_subject(
            antecedent
        )
    else:
        subject_is_plural = subject.tag_ in ["NNS", "NNPS"] or is_compound_subject(
            subject
        )

    if subject.text.lower() == "each" and subject.head.dep_ != "nsubj":
        return True

    if "each" in [child.text.lower() for child in subject.children]:
        return verb.tag_ == "VBP"

    verb_is_singular = verb.tag_ == "VBZ"
    verb_is_plural = verb.tag_ == "VBP"

    if verb.tag_ == "VBD":
        return True

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

    if subject_is_plural and verb_is_plural:
        return True
    elif not subject_is_plural and verb_is_singular:
        return True

    print(
        f"Main verb agreement error: '{subject.text}' does not agree with '{verb.text}'"
    )
    return False


def find_subject_verb_pairs(token, subject_verb_pairs=None, level=0):
    if subject_verb_pairs is None:
        subject_verb_pairs = []

    if token.pos_ in ["VERB", "AUX"]:
        for child in token.children:
            if child.dep_ in ["nsubj", "nsubjpass"]:
                subject_verb_pairs.append((child, token, level))

    for child in token.children:
        find_subject_verb_pairs(child, subject_verb_pairs, level + 1)
    return subject_verb_pairs


def check_nested_subject_verb_agreement(doc):
    for sent in doc.sents:
        print(f"\nSentence: {sent.text.strip()}")
        subject_verb_pairs = find_subject_verb_pairs(sent.root)

        for subject, verb, level in subject_verb_pairs:
            if check_agreement(subject, verb):
                print(
                    f"Level {level} - NP '{subject.text}' agrees with VP '{verb.text}'"
                )
            else:
                log_error(
                    sent.text.strip(), subject.text, verb.text, error_type="Main Clause"
                )


def find_np_rc_rc_rc_vp(doc):
    structure_count = defaultdict(int)
    structures_found = []

    for sent in doc.sents:
        print(f"\nSentence Check: {sent.text.strip()}")

        main_subject = None
        main_verb = None
        relative_clause_subject = None
        relative_clause_verb = None

        np_count = 0
        rc_count = 0
        vp_count = 0

        for token in sent:
            if token.dep_ == "nsubj" and token.head.dep_ in ["aux", "ROOT"]:
                main_subject = token
                np_count += 1
                print(f"Debug: Main subject identified as {main_subject.text}.")

            if token.dep_ in ["aux", "ROOT"]:
                main_verb = token
                vp_count += 1
                print(f"Debug: Main verb identified as {main_verb.text}.")

            if token.dep_ == "nsubj" and token.head.dep_ == "relcl":
                relative_clause_subject = token
                np_count += 1
                rc_count += 1
                print(
                    f"Debug: Relative clause subject found: {relative_clause_subject.text}."
                )

            if token.dep_ == "relcl" and token.head.dep_ != "relcl":
                relative_clause_verb = token
                vp_count += 1
                print(
                    f"Debug: Relative clause verb found: {relative_clause_verb.text}."
                )

            if relative_clause_subject and relative_clause_verb:
                if check_agreement(relative_clause_subject, relative_clause_verb):
                    print(
                        f"Relative clause match: NP '{relative_clause_subject.text}', VP '{relative_clause_verb.text}'"
                    )
                else:
                    log_error(
                        sent.text.strip(),
                        relative_clause_subject.text,
                        relative_clause_verb.text,
                        error_type="Relative Clause",
                    )

        print(
            f"Debug: Total NPs: {np_count}, Total RCs: {rc_count}, Total VPs: {vp_count}"
        )

        if rc_count >= 2:
            structure_count["NP -> RC -> RC -> VP"] += 1
            structures_found.append(f"Sentence: {sent.text.strip()}")
            structures_found.append(
                f"NP: {main_subject.text}, RC_Subj: {relative_clause_subject.text}, RC_Verb: {relative_clause_verb.text}, VP: {main_verb.text}"
            )
            print(f"Debug: Found NP -> RC -> RC -> VP pattern.")


find_np_rc_rc_rc_vp(doc)
check_nested_subject_verb_agreement(doc)
