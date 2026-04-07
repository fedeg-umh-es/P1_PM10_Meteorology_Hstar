from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


@dataclass
class ARIMAForecaster:
    """Simple ARIMA wrapper for rolling-origin evaluation.

    This module covers non-seasonal ARIMA only.
    SARIMA should live in a separate module if added later.
    """

    order: tuple[int, int, int]
    fitted_model: object | None = None

    def fit(self, y: pd.Series) -> "ARIMAForecaster":
        """Fit ARIMA on the training window only."""
        if y.empty:
            raise ValueError("Cannot fit ARIMA on an empty series.")

        clean_y = pd.to_numeric(y, errors="coerce").dropna()
        if clean_y.empty:
            raise ValueError("Training series contains no valid numeric observations.")

        model = ARIMA(clean_y, order=self.order)
        self.fitted_model = model.fit()
        return self

    def predict(self, horizon: int) -> list[float]:
        """Generate multi-step forecasts from the fitted ARIMA model."""
        if self.fitted_model is None:
            raise ValueError("ARIMAForecaster must be fitted before calling predict().")
        if horizon <= 0:
            raise ValueError("horizon must be a positive integer.")

        forecast = self.fitted_model.forecast(steps=horizon)
        return [float(v) for v in forecast]

    def predict_one(self, step: int) -> float:
        """Return the prediction for a single forecast step."""
        if step <= 0:
            raise ValueError("step must be a positive integer.")
        return self.predict(horizon=step)[-1]
