import spacy
from collections import defaultdict
import pandas as pd

nlp = spacy.load("en_core_web_sm")

file_path = "data/a.txt"
with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

doc = nlp(text)

pattern_count = defaultdict(int)
structures_found = []


def get_noun_verb_number(token):
    """
    Determine if the noun or verb is singular or plural based on its POS tag.
    """
    if token.tag_ in ["NN", "NNP"]:
        return "Singular"
    elif token.tag_ in ["NNS", "NNPS"]:
        return "Plural"
    elif token.tag_ == "VBZ":  # Present tense singular verb
        return "Singular"
    elif token.tag_ in ["VBP"]:  # Present tense plural verb or past tense
        return "Plural"
    elif token.tag_ in ["VBD", "VBN", "VBG"]:  # Past tense verb
        return "Verbs_no_unk"
    elif token.tag_ in ["CD"]:
        print("Number:", token.text)
        return "Number"
    elif token.tag_ in ["DT"]:
        # print("Number:", token.text)
        return "Det"
    elif token.tag_ in ["PRP"]:  # for I, it
        # print("Number:", token.text)
        return "PRP"
    return "Unknown"


def find_np_pp_vp(doc):
    """
    Find NP PP VP and other related constructions, capturing the number (singular/plural) of nouns and verbs.
    """
    print("ID\tFORM\tLEMMA\tUPOS\tXPOS\tFEATS\tHEAD\tDEPREL\tDEPS\tMISC")

    for sent in doc.sents:
        print(f"\nSentence Check: {sent.text.strip()}")

        main_subject = None
        main_verb = None
        prep = None
        pobj = None

        for idx, token in enumerate(sent, start=1):
            token_id = idx
            form = token.text
            lemma = token.lemma_
            upos = token.pos_
            xpos = token.tag_
            feats = "_"
            head = token.head.i + 1 if token.head != token else 0
            deprel = token.dep_
            deps = "_"
            misc = "_"

            print(
                f"{token_id}\t{form}\t{lemma}\t{upos}\t{xpos}\t{feats}\t{head}\t{deprel}\t{deps}\t{misc}"
            )

            # Find the subject (nsubj or nsubjpass) and the main verb (ROOT)
            if token.dep_ in ["nsubj", "nsubjpass"] and token.head.dep_ == "ROOT":
                main_subject = token
            if token.dep_ == "ROOT":
                main_verb = token

            # Check for prepositional phrase (prep and pobj)
            if token.dep_ == "prep":
                prep = token
            if token.dep_ == "pobj" and prep and token.head == prep:
                pobj = token

        # Check for NP VP match and add number (singular/plural) info
        if main_subject and main_verb:
            subject_number = get_noun_verb_number(main_subject)
            verb_number = get_noun_verb_number(main_verb)

            if prep and pobj:
                pobj_number = get_noun_verb_number(pobj)
                print(f"Prepositional Phrase match: '{prep.text} {pobj.text}'")
                print(f"Found NP PP VP pattern: {sent.text.strip()}")

                # Record the structure occurrence with number info
                pattern_count["NP PP VP"] += 1
                structures_found.append(
                    {
                        "Sentence": sent.text.strip(),
                        "Subject": main_subject.text,
                        "Subject Number": subject_number,
                        "Preposition": prep.text,
                        "Prep Object": pobj.text,
                        "Prep Object Number": pobj_number,
                        "Verb": main_verb.text,
                        "Verb Number": verb_number,
                    }
                )
            else:
                print("No prepositional phrase match found.")
        else:
            print("No main clause match found.")

    df = pd.DataFrame(structures_found)

    print("\n--- Frequency Table ---")
    print(pattern_count)

    df.to_csv("output/np_pp_vp_patterns_with_number.csv", index=False)
    print("\nOutput saved to 'np_pp_vp_patterns_with_number.csv'.")


find_np_pp_vp(doc)
