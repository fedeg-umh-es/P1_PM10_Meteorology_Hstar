from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from xgboost import XGBRegressor


@dataclass
class XGBoostDirectForecaster:
    """Direct multi-step forecaster with one XGBoost model per horizon.

    Expected workflow:
    - training data already prepared with leakage-free features
    - feature columns passed explicitly
    - one target column per horizon supplied to `fit`

    This wrapper does not perform hyperparameter search.
    """

    horizon_max: int
    xgb_params: dict[str, Any] | None = None
    models_by_horizon: dict[int, XGBRegressor] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.horizon_max <= 0:
            raise ValueError("horizon_max must be a positive integer.")

        if self.xgb_params is None:
            self.xgb_params = {
                "n_estimators": 200,
                "max_depth": 4,
                "learning_rate": 0.05,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
                "objective": "reg:squarederror",
                "random_state": 42,
            }

    def fit(
        self,
        X: pd.DataFrame,
        y_by_horizon: dict[int, pd.Series],
    ) -> "XGBoostDirectForecaster":
        """Fit one XGBoost regressor per forecast horizon."""
        if X.empty:
            raise ValueError("Cannot fit XGBoostDirectForecaster on an empty feature matrix.")

        self.models_by_horizon = {}
        for horizon in range(1, self.horizon_max + 1):
            if horizon not in y_by_horizon:
                raise ValueError(f"Missing training target for horizon {horizon}.")

            y = pd.to_numeric(y_by_horizon[horizon], errors="coerce")
            valid_mask = y.notna()
            if valid_mask.sum() == 0:
                raise ValueError(f"No valid training targets for horizon {horizon}.")

            model = XGBRegressor(**self.xgb_params)
            model.fit(X.loc[valid_mask], y.loc[valid_mask])
            self.models_by_horizon[horizon] = model

        return self

    def predict(self, X_future: pd.DataFrame) -> dict[int, list[float]]:
        """Predict each horizon with its horizon-specific model.

        Parameters
        ----------
        X_future:
            Feature matrix aligned with the prediction rows to score.
            For simple rolling-origin use, this may contain one row per horizon.
        """
        if not self.models_by_horizon:
            raise ValueError("XGBoostDirectForecaster must be fitted before calling predict().")
        if X_future.empty:
            raise ValueError("X_future must contain at least one row.")

        predictions: dict[int, list[float]] = {}
        for horizon, model in self.models_by_horizon.items():
            predictions[horizon] = [float(v) for v in model.predict(X_future)]
        return predictions

    def predict_one(self, X_row: pd.DataFrame, horizon: int) -> float:
        """Predict a single horizon from a single feature row."""
        if horizon not in self.models_by_horizon:
            raise ValueError(f"No fitted model available for horizon {horizon}.")
        if X_row.empty:
            raise ValueError("X_row must contain exactly one feature row.")

        model = self.models_by_horizon[horizon]
        prediction = model.predict(X_row)
        return float(prediction[0])


def make_direct_targets(
    df: pd.DataFrame,
    target_col: str,
    horizon_max: int,
) -> tuple[pd.DataFrame, dict[int, pd.Series]]:
    """Create direct multi-step targets by shifting the target column backward.

    Returns the aligned feature frame and a dictionary of horizon-specific targets.
    Rows with incomplete future targets are removed.
    """
    if target_col not in df.columns:
        raise ValueError(f"Missing target column: {target_col}")
    if horizon_max <= 0:
        raise ValueError("horizon_max must be a positive integer.")

    out = df.copy()
    target_dict: dict[int, pd.Series] = {}
    required_cols: list[str] = []

    for horizon in range(1, horizon_max + 1):
        col_name = f"{target_col}_t_plus_{horizon}"
        out[col_name] = out[target_col].shift(-horizon)
        required_cols.append(col_name)

    out = out.dropna(subset=required_cols).reset_index(drop=True)

    for horizon in range(1, horizon_max + 1):
        col_name = f"{target_col}_t_plus_{horizon}"
        target_dict[horizon] = pd.to_numeric(out[col_name], errors="coerce")

    return out, target_dict
