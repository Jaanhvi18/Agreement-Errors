# Import required libraries
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader

# Force CPU usage (ensuring compatibility for all systems)
device = torch.device("cpu")

# -------------------------------
# DATASET PREPARATION
# -------------------------------

# Simulated dataset for Subject-Verb Agreement (SVA) classification
# Sentences with correct agreement are labeled as 1, and incorrect ones as 0.
sentences = [
    ("The dog runs fast.", 1),   # Correct
    ("The dogs run fast.", 1),   # Correct
    ("The cat eat fish.", 0),    # Incorrect (should be 'eats')
    ("The cat eats fish.", 1),   # Correct
    ("The jury decide the case.", 0),  # Incorrect (should be 'decides')
    ("The jury decides the case.", 1), # Correct
    ("The team play together.", 0),    # Incorrect (should be 'plays')
    ("The team plays together.", 1)    # Correct
]

# Tokenization setup: Assign a unique ID to each word
vocab = {"<PAD>": 0, "<UNK>": 1}  # Special tokens for padding and unknown words
for sentence, _ in sentences:
    for word in sentence.lower().split():
        if word not in vocab:
            vocab[word] = len(vocab)  # Assign a new unique ID

# Function to convert words into token IDs
def tokenize(sentence):
    return [vocab.get(word.lower(), vocab["<UNK>"]) for word in sentence.split()]

# Custom PyTorch dataset class
class SVADataset(Dataset):
    def __init__(self, sentences):
        self.data = [(tokenize(sentence), label) for sentence, label in sentences]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sentence, label = self.data[idx]
        return torch.tensor(sentence, dtype=torch.long), torch.tensor(label, dtype=torch.float)

# Load dataset and prepare DataLoader for training
dataset = SVADataset(sentences)
dataloader = DataLoader(
    dataset,
    batch_size=2,
    shuffle=True,
    collate_fn=lambda batch: (
        nn.utils.rnn.pad_sequence([x[0] for x in batch], batch_first=True, padding_value=0),
        torch.stack([x[1] for x in batch])
    ),
)

# -------------------------------
# MODEL DEFINITION
# -------------------------------

# LSTM model for Subject-Verb Agreement classification
class LSTMSVA(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super(LSTMSVA, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)  # Word embedding layer
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, num_layers=3)  # LSTM with 3 layers
        self.fc = nn.Linear(hidden_dim, 1)  # Fully connected layer for classification
        self.sigmoid = nn.Sigmoid()  # Sigmoid activation for binary classification

    def forward(self, x):
        x = self.embedding(x)  # Convert word indices to embeddings
        output, (h_n, _) = self.lstm(x)  # Extract activations from LSTM layers
        out = self.fc(h_n[-1])  # Use last LSTM layer hidden state for prediction
        return self.sigmoid(out), h_n  # Return predicted probability + hidden states

# Instantiate model, define loss function and optimizer
model = LSTMSVA(vocab_size=len(vocab), embed_dim=50, hidden_dim=64).to(device)
criterion = nn.BCELoss()  # Binary Cross-Entropy Loss for classification
optimizer = optim.Adam(model.parameters(), lr=0.01)  # Adam optimizer

# -------------------------------
# TRAINING LOOP
# -------------------------------

epochs = 20  # Number of training epochs
training_losses = []  # Store loss per epoch

print("Training started...")
for epoch in range(epochs):
    total_loss = 0
    for inputs, labels in dataloader:
        inputs, labels = inputs.to(device), labels.to(device)  # Move to CPU (or GPU if applicable)

        optimizer.zero_grad()  # Reset gradients before each batch
        outputs, _ = model(inputs)  # Forward pass
        loss = criterion(outputs.squeeze(), labels)  # Compute loss
        loss.backward()  # Backpropagation
        optimizer.step()  # Update weights

        total_loss += loss.item()  # Accumulate batch loss

    training_losses.append(total_loss)  # Store loss per epoch

    # Print progress every 5 epochs
    if (epoch + 1) % 5 == 0:
        print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss:.4f}")

print("Training complete!")

# Save training loss data to a CSV file
training_df = pd.DataFrame({"Epoch": list(range(1, epochs+1)), "Loss": training_losses})
training_df.to_csv("training_losses.csv", index=False)
print("\nLoss data saved to 'training_losses.csv'.")

# -------------------------------
# LOGIT LENS ANALYSIS
# -------------------------------

# Sample sentences for interpretability analysis
sample_sentences = [
    "The dog runs fast.",
    "The dogs run fast.",
    "The cat eat fish.",  # Incorrect agreement
    "The cat eats fish."
]

# Tokenize the sample sentences
tokenized_sentences = [tokenize(sentence) for sentence in sample_sentences]

# Function to extract hidden activations at different LSTM layers
def get_lstm_activations(model, sentence_tokens):
    with torch.no_grad():
        sentence_tensor = torch.tensor([sentence_tokens], dtype=torch.long).to(device)
        _, hidden_states = model(sentence_tensor)  # Get LSTM hidden states
        return hidden_states.cpu().numpy()  # Convert to NumPy array

# Extract LSTM activations for sample sentences
activations = [get_lstm_activations(model, tokens) for tokens in tokenized_sentences]

# Convert activations into a NumPy array and inspect shape
activations_array = np.array(activations).squeeze()
print(f"Shape of extracted activations: {activations_array.shape}")  # Should be (4, 3, 64)

# Reshape activations for visualization
num_samples = len(sample_sentences)
num_layers = activations_array.shape[1]  # Number of LSTM layers
hidden_size = activations_array.shape[2]  # Hidden size per layer (64 neurons)

# Flatten activations for easier analysis
flattened_activations = activations_array.reshape(num_samples, num_layers * hidden_size)

# Generate column names dynamically
column_names = [f"Layer_{i+1}_Neuron_{j+1}" for i in range(num_layers) for j in range(hidden_size)]

# Convert activations into a DataFrame for visualization
logit_lens_df = pd.DataFrame(flattened_activations, columns=column_names)
logit_lens_df.insert(0, "Sentence", sample_sentences)

# Display activation analysis results
print("\nLogit Lens Analysis:")
print(logit_lens_df)

# -------------------------------
# VISUALIZATION
# -------------------------------

# Plot neuron activations across layers (subset for clarity)
plt.figure(figsize=(12, 6))
sns.lineplot(data=logit_lens_df.iloc[:, 1:10])  # Plot only first 9 neurons
plt.xlabel("Sentence Index")
plt.ylabel("Activation Magnitude")
plt.title("Logit Lens Analysis Across LSTM Layers (Subset of Neurons)")
plt.legend(labels=column_names[:9], loc="upper right")

# Save the plot as an image
plt.savefig("logit_lens_analysis.png", dpi=300, bbox_inches="tight")
plt.show()
