import argparse
import time

import torch
from torch import nn


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


def main():
    args = parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested, but no CUDA GPU is available.")

    device = torch.device(args.device)
    print(f"Device: {device}")

    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    model = HiggsMLP()
    parameter_count = sum(p.numel() for p in model.parameters())

    print("Required MLP: 28 -> 300 -> 300 -> 100 -> 1")
    print(f"Trainable parameters: {parameter_count}")


if __name__ == "__main__":
    main()