import os
import pandas as pd
import numpy as np


def analyze_roi_accuracies(filename, output_folder, accuracy_table):
    df = pd.read_csv(filename, sep="\s+", on_bad_lines="skip")
    roi_pairs = detect_rois(df)

    output_data = []
    correct_predictions = 0

    for sent1, sent2, roi in roi_pairs:
        word1 = df[(df["sentid"] == sent1) & (df["sentpos"] == roi)]["word"].values[0]
        word2 = df[(df["sentid"] == sent2) & (df["sentpos"] == roi)]["word"].values[0]
        surp1 = df[(df["sentid"] == sent1) & (df["sentpos"] == roi)]["surp"].values[0]
        surp2 = df[(df["sentid"] == sent2) & (df["sentpos"] == roi)]["surp"].values[0]

        # Calculate probabilities from surprisals
        prob1 = np.exp(-surp1)
        prob2 = np.exp(-surp2)

        # Assume first sentence is the expected correct one
        expected_winner = word1
        actual_winner = word1 if surp1 < surp2 else word2
        is_correct = actual_winner == expected_winner
        correct_predictions += is_correct

        output_data.append(
            {
                "ROI": roi_pairs.index((sent1, sent2, roi)) + 1,
                "Position": roi,
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

    accuracy = (correct_predictions / len(roi_pairs)) * 100 if roi_pairs else 0

    # Save detailed output for this file
    output_df = pd.DataFrame(output_data)
    detailed_output_path = os.path.join(
        output_folder, f"{os.path.basename(filename).replace('.tsv', '_detailed.tsv')}"
    )
    output_df.to_csv(detailed_output_path, sep="\t", index=False)

    # Add accuracy to the table
    structure_type = os.path.basename(filename).replace(".tsv", "")
    accuracy_table.append(
        {
            "ID": len(accuracy_table),
            "Structure Type": structure_type,
            "0%": f"{accuracy:.2f}%",
        }
    )

    # Save accuracy score for this file
    accuracy_score_path = os.path.join(
        output_folder, f"{os.path.basename(filename).replace('.tsv', '_score.txt')}"
    )
    with open(accuracy_score_path, "w") as f:
        f.write(f"Model accuracy: {accuracy:.2f}%\n")


def detect_rois(df):
    roi_pairs = []
    unique_sentids = df["sentid"].unique()

    for i in range(0, len(unique_sentids) - 1, 2):
        sent1, sent2 = unique_sentids[i], unique_sentids[i + 1]

        sent1_words = df[df["sentid"] == sent1]
        sent2_words = df[df["sentid"] == sent2]

        for pos in sent1_words["sentpos"].values:
            word1_values = sent1_words[sent1_words["sentpos"] == pos]["word"].values
            word2_values = sent2_words[sent2_words["sentpos"] == pos]["word"].values

            if len(word1_values) == 0 or len(word2_values) == 0:
                continue

            word1 = word1_values[0]
            word2 = word2_values[0]

            if word1 != word2 and pos > 1:
                roi_pairs.append((sent1, sent2, pos))
    return roi_pairs


def main():
    input_folder = "2323"
    output_folder = "2323/accuracy/"
    accuracy_table = []

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".tsv"):
            input_file = os.path.join(input_folder, filename)
            output_subfolder = os.path.join(output_folder, filename.replace(".tsv", ""))
            os.makedirs(output_subfolder, exist_ok=True)

            analyze_roi_accuracies(input_file, output_subfolder, accuracy_table)

    # Save the combined accuracy scores table
    accuracy_df = pd.DataFrame(accuracy_table)
    accuracy_table_path = os.path.join(output_folder, "accuracy_scores_table.csv")
    accuracy_df.to_csv(accuracy_table_path, index=False)

    # Print the table to the console for verification
    print("\nCombined ROI Accuracy Scores Table:")
    print(accuracy_df)
    print(f"\nCombined accuracy scores table saved to {accuracy_table_path}")
    return accuracy_df


if __name__ == "__main__":
    accuracy_df = main()
