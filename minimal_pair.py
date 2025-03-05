import random
import os


class AgreementErrorGenerator:
    def __init__(self):
        self.determiners_sing = ["The", "the", "a", "an", "this", "that"]
        self.determiners_plur = ["The", "the", "these", "those"]
        self.nouns_sing = [
            "report",
            "key",
            "soldier",
            "officer",
            "blanket",
            "cabinet",
            "chair",
            "table",
            "book",
            "door",
            "window",
            "team",
            "committee",
            "staff",
        ]
        self.nouns_plur = [
            "reports",
            "keys",
            "soldiers",
            "officers",
            "blankets",
            "cabinets",
            "chairs",
            "tables",
            "books",
            "doors",
            "windows",
            "teams",
        ]
        self.aux_verb_pairs = [("is", "are"), ("was", "were"), ("has", "have")]
        self.non_aux_verb_pairs = [
            ("runs", "run"),
            ("jumps", "jump"),
            ("reads", "read"),
            ("writes", "write"),
            ("speaks", "speak"),
        ]
        self.adjectives = [
            "ornate",
            "Victorian",
            "new",
            "old",
            "important",
            "ready",
            "damaged",
            "missing",
            "innocent",
            "guilty",
            "late",
            "early",
            "senior",
        ]
        self.prepositions = ["of", "to", "in", "on", "with", "by", "from"]
        self.relative_pronouns = ["that", "which", "who"]

    def get_correct_verb_pair(self, noun, singular_only=False):
        """Returns the correct and incorrect verb forms based on noun plurality."""
        if singular_only:

            verb_pairs = [
                (pair[0], pair[1])
                for pair in self.aux_verb_pairs + self.non_aux_verb_pairs
            ]
        else:
            verb_pairs = self.aux_verb_pairs + self.non_aux_verb_pairs

        if noun in self.nouns_plur:
            return random.choice([(pair[1], pair[0]) for pair in verb_pairs])
        else:
            return random.choice(verb_pairs)

    def generate_pair(self, structure_type):
        if structure_type == 0:
            head = random.choice(self.nouns_sing + self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(head)
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {head} {correct_verb} {adj}."
            incorrect_sentence = f"The {head} {incorrect_verb} {adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 1:
            head = random.choice(self.nouns_sing)
            prep = random.choice(self.prepositions)
            obj = random.choice(self.nouns_sing + self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(obj)
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {head} {prep} {obj} {correct_verb} {adj}."
            incorrect_sentence = f"The {head} {prep} {obj} {incorrect_verb} {adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 2:
            head = random.choice(self.nouns_plur)
            rel = random.choice(self.relative_pronouns)
            obj = random.choice(self.nouns_sing + self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(obj)
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {head} {rel} the {obj} {correct_verb} {adj}."
            incorrect_sentence = f"The {head} {rel} the {obj} {incorrect_verb} {adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 3:
            noun1 = random.choice(self.nouns_sing)
            noun2 = random.choice(self.nouns_sing)
            # alwyas pick a plural verb as correct and sing as wrong
            correct_verb, incorrect_verb = random.choice(
                [
                    (pair[1], pair[0])
                    for pair in self.aux_verb_pairs + self.non_aux_verb_pairs
                ]
            )
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {noun1} and the {noun2} {correct_verb} {adj}."
            incorrect_sentence = f"The {noun1} and the {noun2} {incorrect_verb} {adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 4:
            head = random.choice(self.nouns_plur)
            prep = random.choice(self.prepositions)
            obj = random.choice(self.nouns_sing + self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(obj)
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {head} {prep} the {obj} {correct_verb} {adj}."
            incorrect_sentence = f"The {head} {prep} the {obj} {incorrect_verb} {adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 5:
            noun = random.choice(self.nouns_sing + self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(noun)
            sing_verb = "running"
            correct_sentence = f"The {noun} {correct_verb} {sing_verb}."
            incorrect_sentence = f"The {noun} {incorrect_verb} {sing_verb}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 6:
            head = random.choice(self.nouns_sing + self.nouns_plur)
            prep = random.choice(self.prepositions)
            adj1 = random.choice(self.adjectives)
            adj2 = random.choice(self.adjectives)
            obj = random.choice(self.nouns_sing + self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(obj)
            final_adj = random.choice(self.adjectives)
            correct_sentence = (
                f"The {head} {prep} the {adj1} {adj2} {obj} {correct_verb} {final_adj}."
            )
            incorrect_sentence = f"The {head} {prep} the {adj1} {adj2} {obj} {incorrect_verb} {final_adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 7:
            noun1 = random.choice(self.nouns_sing)
            noun2 = random.choice(self.nouns_sing)
            # need to make sure we always get plural verbs for compound subjects
            correct_verb, incorrect_verb = random.choice(
                [
                    (pair[1], pair[0])
                    for pair in self.aux_verb_pairs + self.non_aux_verb_pairs
                ]
            )
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {noun1} and the {noun2} {correct_verb} {adj}."
            incorrect_sentence = f"The {noun1} and the {noun2} {incorrect_verb} {adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 8:
            head = random.choice(self.nouns_sing + self.nouns_plur)
            prep = random.choice(self.prepositions)
            obj = random.choice(self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(obj)
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {head} {prep} these {obj} {correct_verb} {adj}."
            incorrect_sentence = (
                f"The {head} {prep} these {obj} {incorrect_verb} {adj}."
            )
            return correct_sentence, incorrect_sentence

        elif structure_type == 9:
            head = random.choice(self.nouns_sing + self.nouns_plur)
            rel = random.choice(self.relative_pronouns)
            obj = random.choice(self.nouns_sing + self.nouns_plur)
            # chcekc for verb form correctness based on the plurality of the head noun
            if head in self.nouns_plur:
                correct_verb, incorrect_verb = random.choice(
                    [
                        (pair[1], pair[0])
                        for pair in self.aux_verb_pairs + self.non_aux_verb_pairs
                    ]
                )  # pl head needs plural verb as correct
            else:
                correct_verb, incorrect_verb = random.choice(
                    [
                        (pair[0], pair[1])
                        for pair in self.aux_verb_pairs + self.non_aux_verb_pairs
                    ]
                )
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {head} {rel} our {adj} {obj} {correct_verb} {adj}."
            incorrect_sentence = (
                f"The {head} {rel} our {adj} {obj} {incorrect_verb} {adj}."
            )
            return correct_sentence, incorrect_sentence

        elif structure_type == 10:
            head = random.choice(self.nouns_plur)
            prep = random.choice(self.prepositions)
            obj = random.choice(self.nouns_sing + self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(obj)
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {head} {prep} the {obj} {correct_verb} {adj}."
            incorrect_sentence = f"The {head} {prep} the {obj} {incorrect_verb} {adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 11:
            noun1 = random.choice(self.nouns_sing + self.nouns_plur)
            noun2 = random.choice(self.nouns_sing + self.nouns_plur)
            # using a plural verb as correct and a singular verb as incorrect
            correct_verb, incorrect_verb = random.choice(
                [
                    (pair[1], pair[0])
                    for pair in self.aux_verb_pairs + self.non_aux_verb_pairs
                ]
            )
            adj = random.choice(self.adjectives)
            correct_sentence = f"The {noun1} and {noun2} {correct_verb} {adj}."
            incorrect_sentence = f"The {noun1} and {noun2} {incorrect_verb} {adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 12:
            head = random.choice(self.nouns_sing + self.nouns_plur)
            rel = random.choice(self.relative_pronouns)
            #  object noun for the RC
            obj = random.choice(self.nouns_sing + self.nouns_plur)
            #  based on head noun plurality
            if head in self.nouns_plur:
                correct_verb, incorrect_verb = random.choice(
                    [
                        (pair[1], pair[0])
                        for pair in self.aux_verb_pairs + self.non_aux_verb_pairs
                    ]
                )
            else:
                correct_verb, incorrect_verb = random.choice(
                    [
                        (pair[0], pair[1])
                        for pair in self.aux_verb_pairs + self.non_aux_verb_pairs
                    ]
                )
            verb1 = "accused"
            adj = random.choice(self.adjectives)
            correct_sentence = (
                f"The {head} {rel} the {obj} {verb1} {correct_verb} {adj}."
            )
            incorrect_sentence = (
                f"The {head} {rel} the {obj} {verb1} {incorrect_verb} {adj}."
            )
            return correct_sentence, incorrect_sentence

        elif structure_type == 13:
            head = random.choice(self.nouns_sing + self.nouns_plur)
            prep = random.choice(self.prepositions)
            adj1 = random.choice(self.adjectives)
            adj2 = random.choice(self.adjectives)
            obj = random.choice(self.nouns_sing + self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(obj)
            final_adj = random.choice(self.adjectives)
            correct_sentence = (
                f"The {head} {prep} the {adj1} {adj2} {obj} {correct_verb} {final_adj}."
            )
            incorrect_sentence = f"The {head} {prep} the {adj1} {adj2} {obj} {incorrect_verb} {final_adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 14:
            head = random.choice(self.nouns_sing + self.nouns_plur)
            rel = random.choice(self.relative_pronouns)
            adj1 = random.choice(self.adjectives)
            adj2 = random.choice(self.adjectives)
            obj = random.choice(self.nouns_plur)
            verb1 = "accused"
            correct_verb, incorrect_verb = self.get_correct_verb_pair(obj)
            final_adj = random.choice(self.adjectives)
            correct_sentence = f"The {head} {rel} the {adj1} {adj2} {obj} {verb1} {correct_verb} {final_adj}."
            incorrect_sentence = f"The {head} {rel} the {adj1} {adj2} {obj} {verb1} {incorrect_verb} {final_adj}."
            return correct_sentence, incorrect_sentence

        elif structure_type == 15:
            head = random.choice(self.nouns_plur)
            prep = random.choice(self.prepositions)
            adj1 = random.choice(self.adjectives)
            adj2 = random.choice(self.adjectives)
            obj = random.choice(self.nouns_sing + self.nouns_plur)
            correct_verb, incorrect_verb = self.get_correct_verb_pair(obj)
            final_adj = random.choice(self.adjectives)
            correct_sentence = (
                f"The {head} {prep} the {adj1} {adj2} {obj} {correct_verb} {final_adj}."
            )
            incorrect_sentence = f"The {head} {prep} the {adj1} {adj2} {obj} {incorrect_verb} {final_adj}."
            return correct_sentence, incorrect_sentence

    def generate_all_pairs_separate_files(self, n=1000):
        structure_types = range(0, 16)
        os.makedirs("data/generated", exist_ok=True)

        for structure_type in structure_types:
            pairs = []
            for _ in range(n):
                correct, incorrect = self.generate_pair(structure_type)
                pairs.append((correct, incorrect))

            output_file = f"data/generated/structure_type_{structure_type}_pairs.txt"
            with open(output_file, "w") as file:
                for correct, incorrect in pairs:
                    file.write(f"{correct}\n")
                    file.write(f"{incorrect}\n")


if __name__ == "__main__":
    generator = AgreementErrorGenerator()
    generator.generate_all_pairs_separate_files()
