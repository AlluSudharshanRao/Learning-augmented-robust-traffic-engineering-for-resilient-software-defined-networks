from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def flatten_matrix(matrix: np.ndarray) -> np.ndarray:
    return matrix.reshape(-1)


def reshape_vector(vector: np.ndarray, num_nodes: int) -> np.ndarray:
    return vector.reshape(num_nodes, num_nodes)


class BasePredictor:
    name = "base"

    def fit(self, matrices: np.ndarray) -> None:
        return None

    def predict_next(self, history: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class MovingAveragePredictor(BasePredictor):
    name = "moving_average"

    def predict_next(self, history: np.ndarray) -> np.ndarray:
        return history.mean(axis=0)


@dataclass
class LinearAutoRegressivePredictor(BasePredictor):
    name: str = "linear_autoregressive"

    coefficients: np.ndarray | None = None
    intercept: np.ndarray | None = None

    def fit(self, matrices: np.ndarray) -> None:
        if len(matrices) < 2:
            raise ValueError("Need at least 2 matrices to fit the linear model.")

        x = np.array([flatten_matrix(m) for m in matrices[:-1]])
        y = np.array([flatten_matrix(m) for m in matrices[1:]])
        ones = np.ones((x.shape[0], 1))
        x_aug = np.hstack([ones, x])
        beta, _, _, _ = np.linalg.lstsq(x_aug, y, rcond=None)
        self.intercept = beta[0]
        self.coefficients = beta[1:]

    def predict_next(self, history: np.ndarray) -> np.ndarray:
        if self.coefficients is None or self.intercept is None:
            raise RuntimeError("Predictor must be fit before prediction.")
        latest = flatten_matrix(history[-1])
        prediction = self.intercept + latest @ self.coefficients
        num_nodes = history.shape[1]
        matrix = reshape_vector(prediction, num_nodes)
        matrix = np.clip(matrix, 0.0, None)
        np.fill_diagonal(matrix, 0.0)
        return matrix


class _TrafficLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int) -> None:
        super().__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, batch_first=True)
        self.head = nn.Linear(hidden_size, input_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        output, _ = self.lstm(x)
        return self.head(output[:, -1, :])


@dataclass
class LSTMPredictor(BasePredictor):
    history_window: int = 4
    hidden_size: int = 64
    epochs: int = 80
    learning_rate: float = 1e-2
    batch_size: int = 8
    seed: int = 7
    name: str = "lstm"

    model: _TrafficLSTM | None = None
    num_nodes: int | None = None

    def fit(self, matrices: np.ndarray) -> None:
        if len(matrices) <= self.history_window:
            raise ValueError("Not enough samples to train the LSTM predictor.")

        torch.manual_seed(self.seed)
        self.num_nodes = matrices.shape[1]
        input_size = self.num_nodes * self.num_nodes

        x_samples = []
        y_samples = []
        for idx in range(self.history_window, len(matrices)):
            history = matrices[idx - self.history_window : idx]
            target = matrices[idx]
            x_samples.append(history.reshape(self.history_window, input_size))
            y_samples.append(target.reshape(input_size))

        x_tensor = torch.tensor(np.array(x_samples), dtype=torch.float32)
        y_tensor = torch.tensor(np.array(y_samples), dtype=torch.float32)
        dataset = TensorDataset(x_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.model = _TrafficLSTM(input_size=input_size, hidden_size=self.hidden_size)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        loss_fn = nn.MSELoss()
        self.model.train()

        for _ in range(self.epochs):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                predictions = self.model(batch_x)
                loss = loss_fn(predictions, batch_y)
                loss.backward()
                optimizer.step()

    def predict_next(self, history: np.ndarray) -> np.ndarray:
        if self.model is None or self.num_nodes is None:
            raise RuntimeError("Predictor must be fit before prediction.")

        usable_history = history[-self.history_window :]
        x_tensor = torch.tensor(
            usable_history.reshape(1, self.history_window, self.num_nodes * self.num_nodes),
            dtype=torch.float32,
        )
        self.model.eval()
        with torch.no_grad():
            prediction = self.model(x_tensor).cpu().numpy().reshape(self.num_nodes, self.num_nodes)
        prediction = np.clip(prediction, 0.0, None)
        np.fill_diagonal(prediction, 0.0)
        return prediction
