from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class PersistenceModel:
    """Simple persistence baseline for multi-step forecasting."""

    last_observed_value: float | None = None

    def fit(self, y: pd.Series) -> "PersistenceModel":
        """Store the last observed target value from the training window."""
        if y.empty:
            raise ValueError("Cannot fit persistence model on an empty series.")

        clean_y = pd.to_numeric(y, errors="coerce").dropna()
        if clean_y.empty:
            raise ValueError("Training series contains no valid numeric observations.")

        self.last_observed_value = float(clean_y.iloc[-1])
        return self

    def predict(self, horizon: int) -> list[float]:
        """Repeat the last observed value for the requested horizon."""
        if self.last_observed_value is None:
            raise ValueError("PersistenceModel must be fitted before calling predict().")
        if horizon <= 0:
            raise ValueError("horizon must be a positive integer.")

        return [self.last_observed_value] * horizon

    def predict_one(self, step: int) -> float:
        """Return a single persistence prediction for one forecast step."""
        if step <= 0:
            raise ValueError("step must be a positive integer.")
        return self.predict(horizon=step)[-1]


def predict_persistence(last_value: float, horizon: int) -> list[float]:
    """Functional interface for persistence multi-step prediction."""
    model = PersistenceModel(last_observed_value=float(last_value))
    return model.predict(horizon=horizon)
