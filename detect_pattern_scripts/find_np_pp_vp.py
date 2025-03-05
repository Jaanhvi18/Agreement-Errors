import spacy

nlp = spacy.load("en_core_web_sm")

file_path = "data/a.txt"
with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

doc = nlp(text)


def find_np_pp_vp(doc):

    print("ID\tFORM\tLEMMA\tUPOS\tXPOS\tFEATS\tHEAD\tDEPREL\tDEPS\tMISC")


    for sent in doc.sents:
        print(f"\nSentence Check: {sent.text}")

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

# included checks for passive subjecst bacause if for example the sentence has "A letter" as the 
# subject and "was sent" as the passive VP, then the "letter" is tagged as nsubjpass i.e passive
   
            if token.dep_ in ["nsubj", "nsubjpass"] and token.head.dep_ == "ROOT":
                main_subject = token
            if token.dep_ == "ROOT":
                main_verb = token

            # Check for prep a.k.a ADP and its prep object (pobj)
            if token.dep_ == "prep":
                prep = token
            if token.dep_ == "pobj" and prep and token.head == prep:
                pobj = token

        if main_subject and main_verb:
            print(f"Main clause match: NP '{main_subject.text}', VP '{main_verb.text}'")
            if prep and pobj:
                print(f"Prepositional Phrase match: '{prep.text} {pobj.text}'")
                print(f"Found NP PP VP pattern: {sent.text.strip()}")
            else:
                print("No prepositional phrase match found.")
        else:
            print("No main clause match found.")


find_np_pp_vp(doc)
