import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class HiggsMLP(nn.Module):
    """Required architecture: 28 → 300 → 300 → 100 → 1."""

    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(28, 300),
            nn.ReLU(),
            nn.Linear(300, 300),
            nn.ReLU(),
            nn.Linear(300, 100),
            nn.ReLU(),
            nn.Linear(100, 1),
        )

    def forward(self, x):
        return self.network(x)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train and benchmark the CPSC 488 HIGGS MLP."
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        required=True,
        help="Execution device for the matched benchmark.",
    )
    parser.add_argument(
        "--data-path",
        default="/data/HIGGS.csv.gz",
        help="Path to the already-downloaded HIGGS CSV file.",
    )
    parser.add_argument("--batch-size", type=int, default=8192)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    return parser.parse_args()

def load_higgs_data(data_path: str, batch_size: int):
    """
    Load all 11 million HIGGS examples as float32, then use the exact
    assignment-required split: first 10M for training, final 1M for testing.
    """
    path = Path(data_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"HIGGS data file was not found at {path}. "
            "Download it before starting the benchmark."
        )

    print(f"Loading data from: {path}")
    started = time.perf_counter()

    frame = pd.read_csv(path, header=None, dtype=np.float32)
    if frame.shape != (11_000_000, 29):
        raise ValueError(
            f"Expected 11,000,000 rows and 29 columns; found {frame.shape}."
        )

    values = frame.to_numpy(copy=False)
    del frame

    # Column 0 is the binary label; columns 1–28 are the input features.
    features = values[:, 1:]
    labels = values[:, 0:1]

    train_features = torch.from_numpy(features[:10_000_000])
    train_labels = torch.from_numpy(labels[:10_000_000])
    test_features = torch.from_numpy(features[10_000_000:])
    test_labels = torch.from_numpy(labels[10_000_000:])

    train_loader = DataLoader(
        TensorDataset(train_features, train_labels),
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )
    test_loader = DataLoader(
        TensorDataset(test_features, test_labels),
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    loading_seconds = time.perf_counter() - started
    print(f"Data loading time: {loading_seconds:.2f} seconds")
    print("Training examples: 10,000,000")
    print("Testing examples: 1,000,000")

    return train_loader, test_loader, loading_seconds

def train_model(model, train_loader, device, optimizer, loss_function, epochs):
    model.train()
    started = time.perf_counter()

    for epoch in range(1, epochs + 1):
        epoch_loss = 0.0

        for features, labels in train_loader:
            features = features.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            logits = model(features)
            loss = loss_function(logits, labels)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item() * features.size(0)

        if device.type == "cuda":
            torch.cuda.synchronize()

        average_loss = epoch_loss / len(train_loader.dataset)
        print(f"Epoch {epoch}/{epochs} - training loss: {average_loss:.6f}")

    return time.perf_counter() - started


def evaluate_model(model, test_loader, device):
    model.eval()
    correct_predictions = 0
    total_examples = 0
    started = time.perf_counter()

    with torch.no_grad():
        for features, labels in test_loader:
            features = features.to(device)
            labels = labels.to(device)

            logits = model(features)
            predictions = (torch.sigmoid(logits) >= 0.5).float()

            correct_predictions += (predictions == labels).sum().item()
            total_examples += labels.size(0)

    if device.type == "cuda":
        torch.cuda.synchronize()

    evaluation_seconds = time.perf_counter() - started
    accuracy = 100.0 * correct_predictions / total_examples
    return accuracy, evaluation_seconds


def main():
    args = parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested, but no CUDA GPU is available.")

    torch.manual_seed(42)
    device = torch.device(args.device)

    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    pipeline_started = time.perf_counter()

    train_loader, test_loader, loading_seconds = load_higgs_data(
        args.data_path,
        args.batch_size,
    )

    initialization_started = time.perf_counter()
    model = HiggsMLP().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    loss_function = nn.BCEWithLogitsLoss()

    if device.type == "cuda":
        torch.cuda.synchronize()

    initialization_seconds = time.perf_counter() - initialization_started

    print("Required MLP: 28 -> 300 -> 300 -> 100 -> 1")
    print(f"Trainable parameters: {sum(p.numel() for p in model.parameters())}")

    training_seconds = train_model(
        model,
        train_loader,
        device,
        optimizer,
        loss_function,
        args.epochs,
    )

    accuracy, evaluation_seconds = evaluate_model(model, test_loader, device)

    if device.type == "cuda":
        torch.cuda.synchronize()

    total_seconds = time.perf_counter() - pipeline_started

    print("\n=== Benchmark Results ===")
    print(f"Data loading seconds: {loading_seconds:.2f}")
    print(f"Model initialization seconds: {initialization_seconds:.2f}")
    print(f"Training seconds: {training_seconds:.2f}")
    print(f"Evaluation seconds: {evaluation_seconds:.2f}")
    print(f"Total pipeline seconds: {total_seconds:.2f}")
    print(f"Test accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    main()