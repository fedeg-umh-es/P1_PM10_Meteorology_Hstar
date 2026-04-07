from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def build_lstm_sequences(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    sequence_length: int,
    horizon_max: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Build MIMO sequences after the train/test split has already been applied.

    This function assumes the caller passes only the data available for the
    current rolling-origin training window. It does not perform any split.
    """
    if sequence_length <= 0:
        raise ValueError("sequence_length must be a positive integer.")
    if horizon_max <= 0:
        raise ValueError("horizon_max must be a positive integer.")
    if target_col not in df.columns:
        raise ValueError(f"Missing target column: {target_col}")

    missing_features = [col for col in feature_cols if col not in df.columns]
    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")

    values_x = df[feature_cols].to_numpy(dtype=np.float32)
    values_y = pd.to_numeric(df[target_col], errors="coerce").to_numpy(dtype=np.float32)

    X_seq: list[np.ndarray] = []
    y_seq: list[np.ndarray] = []

    start_max = len(df) - sequence_length - horizon_max + 1
    for start_idx in range(max(0, start_max)):
        end_idx = start_idx + sequence_length
        target_end = end_idx + horizon_max

        x_window = values_x[start_idx:end_idx]
        y_window = values_y[end_idx:target_end]

        if np.isnan(x_window).any() or np.isnan(y_window).any():
            continue

        X_seq.append(x_window)
        y_seq.append(y_window)

    if not X_seq:
        raise ValueError("No valid sequences could be built from the provided frame.")

    return np.stack(X_seq), np.stack(y_seq)


class LSTMMIMONetwork(nn.Module):
    """Minimal LSTM network for multi-output forecasting."""

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int,
        horizon_max: int,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        effective_dropout = dropout if num_layers > 1 else 0.0
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=effective_dropout,
        )
        self.output = nn.Linear(hidden_size, horizon_max)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        return self.output(last_hidden)


@dataclass
class LSTMMIMOForecaster:
    """Conservative LSTM-MIMO wrapper for rolling-origin use.

    Architecture and training parameters are intentionally simple and editable.
    Sequence construction must happen strictly after the temporal split.
    """

    input_size: int
    horizon_max: int
    hidden_size: int = 32
    num_layers: int = 1
    dropout: float = 0.0
    learning_rate: float = 1e-3
    batch_size: int = 32
    epochs: int = 20
    device: str | None = None
    random_seed: int = 42
    model: LSTMMIMONetwork | None = None

    def __post_init__(self) -> None:
        if self.input_size <= 0:
            raise ValueError("input_size must be a positive integer.")
        if self.horizon_max <= 0:
            raise ValueError("horizon_max must be a positive integer.")

        torch.manual_seed(self.random_seed)
        np.random.seed(self.random_seed)

        if self.device is None:
            if torch.backends.mps.is_available():
                self.device = "mps"
            elif torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"

        self.model = LSTMMIMONetwork(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            horizon_max=self.horizon_max,
            dropout=self.dropout,
        ).to(self.device)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LSTMMIMOForecaster":
        """Fit the LSTM-MIMO model on pre-built train-window sequences only."""
        if self.model is None:
            raise ValueError("Model has not been initialized.")
        if X.ndim != 3:
            raise ValueError("X must have shape (n_samples, sequence_length, n_features).")
        if y.ndim != 2:
            raise ValueError("y must have shape (n_samples, horizon_max).")
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must contain the same number of samples.")
        if X.shape[2] != self.input_size:
            raise ValueError("Last dimension of X must match input_size.")
        if y.shape[1] != self.horizon_max:
            raise ValueError("Second dimension of y must match horizon_max.")

        x_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32)
        dataset = TensorDataset(x_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.MSELoss()

        self.model.train()
        for _ in range(self.epochs):
            for batch_x, batch_y in loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)

                optimizer.zero_grad()
                predictions = self.model(batch_x)
                loss = criterion(predictions, batch_y)
                loss.backward()
                optimizer.step()

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict horizon_max outputs from pre-built input sequences."""
        if self.model is None:
            raise ValueError("Model has not been initialized.")
        if X.ndim != 3:
            raise ValueError("X must have shape (n_samples, sequence_length, n_features).")
        if X.shape[2] != self.input_size:
            raise ValueError("Last dimension of X must match input_size.")

        self.model.eval()
        with torch.no_grad():
            x_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
            predictions = self.model(x_tensor).cpu().numpy()
        return predictions

    def predict_one(self, X: np.ndarray, horizon: int) -> float:
        """Predict a single horizon from one input sequence."""
        if horizon <= 0 or horizon > self.horizon_max:
            raise ValueError("horizon must be between 1 and horizon_max.")
        predictions = self.predict(X)
        if predictions.shape[0] != 1:
            raise ValueError("predict_one expects exactly one input sequence.")
        return float(predictions[0, horizon - 1])


def build_single_inference_sequence(
    df: pd.DataFrame,
    feature_cols: list[str],
    sequence_length: int,
) -> np.ndarray:
    """Build one inference sequence from the most recent rows only.

    The caller is responsible for passing only data available at the current
    rolling-origin step. This function does not access any future rows.
    """
    if sequence_length <= 0:
        raise ValueError("sequence_length must be a positive integer.")

    missing_features = [col for col in feature_cols if col not in df.columns]
    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")
    if len(df) < sequence_length:
        raise ValueError("Not enough rows to build the requested inference sequence.")

    recent = df[feature_cols].tail(sequence_length).to_numpy(dtype=np.float32)
    if np.isnan(recent).any():
        raise ValueError("Inference sequence contains missing values.")

    return recent.reshape(1, sequence_length, len(feature_cols))
