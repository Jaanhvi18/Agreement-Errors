import os
import pandas as pd
import numpy as np


def analyze_roi_accuracies(filename, output_folder):
    df = pd.read_csv(filename, sep="\s+", on_bad_lines="skip")

    unique_sentids = sorted(df["sentid"].unique())

    output_data = []
    correct_predictions = 0
    total_comparisons = 0

    for i in range(0, len(unique_sentids) - 1, 2):
        sent1_data = df[df["sentid"] == unique_sentids[i]]
        sent2_data = df[df["sentid"] == unique_sentids[i + 1]]

        sent1_words = sent1_data["word"].tolist()
        sent2_words = sent2_data["word"].tolist()

        # find rois
        for pos in range(min(len(sent1_words), len(sent2_words))):
            if sent1_words[pos] != sent2_words[pos]:
                word1 = sent1_words[pos]
                word2 = sent2_words[pos]
                surp1 = sent1_data.iloc[pos]["surp"]
                surp2 = sent2_data.iloc[pos]["surp"]

                prob1 = np.exp(-surp1)
                prob2 = np.exp(-surp2)

                expected_winner = word1
                actual_winner = word1 if prob1 > prob2 else word2
                is_correct = actual_winner == expected_winner

                if is_correct:
                    correct_predictions += 1
                total_comparisons += 1

                output_data.append(
                    {
                        "ROI": total_comparisons,
                        "Position": pos,
                        "Sentence1_ID": unique_sentids[i],
                        "Sentence2_ID": unique_sentids[i + 1],
                        "Word1": word1,
                        "Word2": word2,
                        "Surp1": surp1,
                        "Surp2": surp2,
                        "Prob1": prob1,
                        "Prob2": prob2,
                        "Expected_Winner": expected_winner,
                        "Actual_Winner": actual_winner,
                        "Is_Correct": is_correct,
                    }
                )

    #  overall accuracy
    accuracy = (
        (correct_predictions / total_comparisons * 100) if total_comparisons > 0 else 0
    )

    output_df = pd.DataFrame(output_data)
    detailed_output_path = os.path.join(output_folder, "detailed_comparison.tsv")
    output_df.to_csv(detailed_output_path, sep="\t", index=False)

    accuracy_score_path = os.path.join(output_folder, "score.txt")
    with open(accuracy_score_path, "w") as f:
        f.write(f"Model accuracy: {accuracy:.2f}%\n")
        f.write(f"Total comparisons: {total_comparisons}\n")
        f.write(f"Correct predictions: {correct_predictions}\n")


def main():
    input_folder = "colorless_30"
    output_folder = "colorless_30/output"
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".tsv"):
            input_file = os.path.join(input_folder, filename)
            output_subfolder = os.path.join(output_folder, filename.replace(".tsv", ""))
            os.makedirs(output_subfolder, exist_ok=True)
            analyze_roi_accuracies(input_file, output_subfolder)


if __name__ == "__main__":
    main()
