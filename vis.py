
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


structure_types = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"
]
model_accuracies = np.array([
    [93.74, 87.48, 87.08, 84.38, 80.80, 66.42],
    [63.92, 58.72, 59.02, 55.44, 57.18, 58.04],
    [83.00, 69.28, 67.82, 72.82, 62.78, 66.36],
    [80.84, 74.16, 63.28, 50.60, 52.42, 25.40],
    [47.98, 48.06, 49.42, 47.48, 50.12, 52.94],
    [93.42, 87.62, 88.46, 85.34, 82.70, 67.14],
    [57.56, 54.70, 57.34, 55.58, 54.98, 59.22],
    [79.50, 73.36, 62.72, 48.88, 52.36, 24.14],
    [58.44, 53.08, 49.12, 43.58, 34.84, 34.80],
    [64.92, 66.64, 67.66, 65.20, 62.36, 55.26],
    [46.92, 48.00, 49.44, 47.66, 49.62, 52.56],
    [88.56, 78.76, 75.70, 68.04, 61.18, 43.48],
    [64.72, 68.58, 70.10, 68.86, 62.62, 57.10],
    [56.50, 53.92, 56.18, 55.26, 54.26, 61.00],
    [74.86, 64.12, 45.78, 44.74, 40.76, 21.80],
    [47.02, 48.92, 51.60, 51.82, 51.02, 56.74]
])

error_rates = [0, 5, 10, 15, 25, 50]

plt.figure(figsize=(12, 8))
plt.imshow(model_accuracies, aspect='auto', cmap='coolwarm', interpolation='none')
plt.colorbar(label="Model Accuracy (%)")
plt.xticks(range(len(error_rates)), [f"{e}%" for e in error_rates], rotation=45)
plt.yticks(range(len(structure_types)), structure_types)
plt.title("Model Accuracy by Structure Type and Error Rate")
plt.xlabel("Error Rate (%)")
plt.ylabel("Structure Type")
plt.savefig("model_accuracy_heatmap.png")
plt.show()


complex_structure_idx = [14, 3, 7] 
simple_structure_idx = [0, 5]  

plt.figure(figsize=(10, 6))
for idx in complex_structure_idx:
    plt.plot(error_rates, model_accuracies[idx], label=f"Structure {structure_types[idx]} (Complex)", linestyle="--", marker="o")

for idx in simple_structure_idx:
    plt.plot(error_rates, model_accuracies[idx], label=f"Structure {structure_types[idx]} (Simple)", linestyle="-", marker="o")

plt.title("Model Accuracy Decline: Complex vs Simple Structures")
plt.xlabel("Error Rate (%)")
plt.ylabel("Model Accuracy (%)")
plt.legend()
plt.grid(True)
plt.savefig("accuracy_comparison_complex_vs_simple.png")
plt.show()

