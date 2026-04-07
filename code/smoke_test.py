from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_target_series, split_train_test_by_time
from models.persistence import PersistenceModel
from rolling_origin import generate_rolling_origins, get_test_window, get_train_window


def compute_rmse(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Compute RMSE for a small smoke test."""
    diff = pd.to_numeric(y_true, errors="coerce") - pd.to_numeric(y_pred, errors="coerce")
    return float(np.sqrt(np.mean(np.square(diff))))


def compute_mae(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Compute MAE for a small smoke test."""
    diff = pd.to_numeric(y_true, errors="coerce") - pd.to_numeric(y_pred, errors="coerce")
    return float(np.mean(np.abs(diff)))


def compute_skill(rmse_model: float, rmse_baseline: float) -> float:
    """Compute skill score relative to persistence."""
    if rmse_baseline <= 0:
        raise ValueError("rmse_baseline must be strictly positive.")
    return float(1.0 - (rmse_model / rmse_baseline))


def run_persistence_smoke_test(
    input_path: str | Path,
    timestamp_col: str = "datetime",
    target_col: str = "value",
    horizon_max: int = 3,
) -> dict[str, object]:
    """Run a minimal structural smoke test with one rolling origin and persistence."""
    if horizon_max <= 0:
        raise ValueError("horizon_max must be a positive integer.")

    df = load_target_series(
        path=input_path,
        timestamp_col=timestamp_col,
        target_col=target_col,
    )
    train_df, test_df = split_train_test_by_time(
        df,
        timestamp_col=timestamp_col,
    )

    if train_df.empty:
        raise ValueError("Train split is empty.")
    if len(test_df) < horizon_max:
        raise ValueError("Test split is too short for the requested horizon_max.")

    origins = generate_rolling_origins(
        df=df,
        timestamp_col=timestamp_col,
        test_start=str(test_df[timestamp_col].min()),
        test_end=str(test_df[timestamp_col].min()),
        horizon_max=horizon_max,
    )
    if not origins:
        raise ValueError("No valid rolling origins found for the smoke test.")

    origin = origins[0]
    train_window = get_train_window(df, origin=origin, timestamp_col=timestamp_col)
    test_window = get_test_window(df, origin=origin, horizon_max=horizon_max, timestamp_col=timestamp_col)

    model = PersistenceModel().fit(train_window[target_col])
    predictions = model.predict(horizon=horizon_max)

    result_df = pd.DataFrame(
        {
            "origin": [origin] * horizon_max,
            "horizon": list(range(1, horizon_max + 1)),
            "timestamp": test_window[timestamp_col].tolist(),
            "y_true": test_window[target_col].tolist(),
            "y_pred": predictions,
        }
    )

    rmse = compute_rmse(result_df["y_true"], result_df["y_pred"])
    mae = compute_mae(result_df["y_true"], result_df["y_pred"])
    skill = compute_skill(rmse_model=rmse, rmse_baseline=rmse)

    return {
        "result_df": result_df,
        "metrics": {
            "rmse": rmse,
            "mae": mae,
            "skill": skill,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Minimal smoke test for the P1 rolling-origin pipeline with persistence."
    )
    parser.add_argument("--input", required=True, help="Path to the target CSV file.")
    parser.add_argument("--timestamp-col", default="datetime")
    parser.add_argument("--target-col", default="value")
    parser.add_argument("--horizon-max", type=int, default=3)
    args = parser.parse_args()

    output = run_persistence_smoke_test(
        input_path=args.input,
        timestamp_col=args.timestamp_col,
        target_col=args.target_col,
        horizon_max=args.horizon_max,
    )

    print(output["result_df"])
    print(output["metrics"])


if __name__ == "__main__":
    main()
