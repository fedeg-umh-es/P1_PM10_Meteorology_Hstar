from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

import pandas as pd

from config import (
    HORIZON_MAX,
    TEST_END,
    TEST_START,
    TRAIN_END,
    TRAIN_START,
)
from features import (
    add_calendar_features,
    build_autoregressive_features,
    drop_rows_with_insufficient_history,
    select_features_by_condition,
)


ModelFactory = Callable[[], Any]
PredictFunction = Callable[[Any, pd.DataFrame, list[str], str, int], float]
ScalerFactory = Callable[[], Any]


@dataclass
class RollingOriginResult:
    """Container for rolling-origin outputs."""

    predictions: pd.DataFrame
    metadata: dict[str, Any]


def generate_rolling_origins(
    df: pd.DataFrame,
    timestamp_col: str = "datetime",
    test_start: str = TEST_START,
    test_end: str = TEST_END,
    horizon_max: int | None = HORIZON_MAX,
) -> list[pd.Timestamp]:
    """Generate valid rolling-origin timestamps inside the test period."""
    if horizon_max is None:
        raise ValueError("HORIZON_MAX is not fixed. Pass horizon_max explicitly.")
    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    out = df.copy()
    out[timestamp_col] = pd.to_datetime(out[timestamp_col], errors="coerce")
    out = out.dropna(subset=[timestamp_col]).sort_values(timestamp_col).reset_index(drop=True)

    test_start_ts = pd.Timestamp(test_start)
    test_end_ts = pd.Timestamp(test_end)

    test_mask = (out[timestamp_col] >= test_start_ts) & (out[timestamp_col] <= test_end_ts)
    test_indices = out.index[test_mask].tolist()

    valid_origins: list[pd.Timestamp] = []
    for idx in test_indices:
        max_required_idx = idx + horizon_max - 1
        if max_required_idx >= len(out):
            continue
        valid_origins.append(pd.Timestamp(out.loc[idx, timestamp_col]))
    return valid_origins


def get_train_window(
    df: pd.DataFrame,
    origin: pd.Timestamp,
    timestamp_col: str = "datetime",
    train_start: str = TRAIN_START,
) -> pd.DataFrame:
    """Return the expanding training window up to origin minus one step."""
    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    out = df.copy()
    out[timestamp_col] = pd.to_datetime(out[timestamp_col], errors="coerce")
    out = out.dropna(subset=[timestamp_col]).sort_values(timestamp_col)

    train_start_ts = pd.Timestamp(train_start)
    mask = (out[timestamp_col] >= train_start_ts) & (out[timestamp_col] < pd.Timestamp(origin))
    return out.loc[mask].copy().reset_index(drop=True)


def get_test_window(
    df: pd.DataFrame,
    origin: pd.Timestamp,
    horizon_max: int,
    timestamp_col: str = "datetime",
) -> pd.DataFrame:
    """Return the future window starting at the origin for the required horizon."""
    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    out = df.copy()
    out[timestamp_col] = pd.to_datetime(out[timestamp_col], errors="coerce")
    out = out.dropna(subset=[timestamp_col]).sort_values(timestamp_col).reset_index(drop=True)

    origin_matches = out.index[out[timestamp_col] == pd.Timestamp(origin)].tolist()
    if not origin_matches:
        raise ValueError(f"Origin not found in DataFrame: {origin}")

    origin_idx = origin_matches[0]
    end_idx = origin_idx + horizon_max
    return out.iloc[origin_idx:end_idx].copy().reset_index(drop=True)


def fit_scaler_on_train_only(
    train_df: pd.DataFrame,
    feature_cols: Iterable[str],
    scaler_factory: ScalerFactory | None = None,
) -> Any:
    """Fit a scaler using train-only data, or return None if no scaler is requested."""
    feature_cols = list(feature_cols)
    if not feature_cols:
        return None

    if scaler_factory is None:
        return None

    scaler = scaler_factory()
    scaler.fit(train_df[feature_cols])
    return scaler


def _apply_optional_scaler(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    scaler: Any,
) -> pd.DataFrame:
    """Apply a fitted scaler to a feature matrix if a scaler exists."""
    feature_cols = list(feature_cols)
    out = df.copy()
    if scaler is None or not feature_cols:
        return out

    transformed = scaler.transform(out[feature_cols])
    out.loc[:, feature_cols] = transformed
    return out


def _prepare_supervised_frame(
    df: pd.DataFrame,
    condition: str,
    target_col: str,
    timestamp_col: str,
    lags: Iterable[int],
) -> tuple[pd.DataFrame, list[str]]:
    """Build the per-origin supervised frame without using future information."""
    out = add_calendar_features(df, timestamp_col=timestamp_col)
    out = build_autoregressive_features(out, target_col=target_col, lags=lags)

    lag_cols = [f"{target_col}_lag_{lag}" for lag in lags]
    out = drop_rows_with_insufficient_history(out, required_columns=lag_cols)

    feature_cols = select_features_by_condition(
        condition=condition,
        target_col=target_col,
        lags=lags,
        available_columns=out.columns,
    )
    return out, feature_cols


def run_single_origin_evaluation(
    df: pd.DataFrame,
    origin: pd.Timestamp,
    condition: str,
    horizon_max: int,
    model_factory: ModelFactory | None,
    predict_function: PredictFunction | None,
    lags: Iterable[int],
    timestamp_col: str = "datetime",
    target_col: str = "value",
    scaler_factory: ScalerFactory | None = None,
) -> pd.DataFrame:
    """Run the evaluation structure for a single rolling origin.

    This function enforces the protocol skeleton:
    - build train window strictly before the origin
    - fit scaler on train only
    - build features without future leakage
    - fit the model on train data
    - predict each horizon in the test window

    Model behaviour is intentionally delegated to hooks so that no
    unsupported modelling assumptions are introduced here.
    """
    if horizon_max is None:
        raise ValueError("horizon_max must be provided.")

    train_df = get_train_window(df, origin=origin, timestamp_col=timestamp_col)
    test_df = get_test_window(
        df,
        origin=origin,
        horizon_max=horizon_max,
        timestamp_col=timestamp_col,
    )

    if train_df.empty:
        raise ValueError(f"Training window is empty for origin {origin}.")
    if len(test_df) < horizon_max:
        raise ValueError(f"Insufficient test rows for origin {origin} and horizon {horizon_max}.")

    prepared_train, feature_cols = _prepare_supervised_frame(
        train_df,
        condition=condition,
        target_col=target_col,
        timestamp_col=timestamp_col,
        lags=lags,
    )
    prepared_test, _ = _prepare_supervised_frame(
        pd.concat([train_df, test_df], ignore_index=True),
        condition=condition,
        target_col=target_col,
        timestamp_col=timestamp_col,
        lags=lags,
    )

    prepared_test = prepared_test[prepared_test[timestamp_col] >= pd.Timestamp(origin)].copy()
    prepared_test = prepared_test.head(horizon_max).reset_index(drop=True)

    scaler = fit_scaler_on_train_only(
        train_df=prepared_train,
        feature_cols=feature_cols,
        scaler_factory=scaler_factory,
    )
    prepared_train = _apply_optional_scaler(prepared_train, feature_cols, scaler)
    prepared_test = _apply_optional_scaler(prepared_test, feature_cols, scaler)

    model = None
    if condition != "C0":
        if model_factory is None:
            raise NotImplementedError("model_factory must be provided for non-baseline conditions.")
        if predict_function is None:
            raise NotImplementedError("predict_function must be provided for non-baseline conditions.")
        model = model_factory()
        if not hasattr(model, "fit"):
            raise TypeError("Model returned by model_factory must implement .fit().")
        model.fit(prepared_train[feature_cols], prepared_train[target_col])

    rows: list[dict[str, Any]] = []
    for step in range(1, horizon_max + 1):
        row = prepared_test.iloc[step - 1]
        y_true = row[target_col]

        if condition == "C0":
            prediction = prepared_train[target_col].iloc[-1]
        else:
            prediction = predict_function(model, prepared_test, feature_cols, target_col, step)

        rows.append(
            {
                "origin": pd.Timestamp(origin),
                "horizon": step,
                "timestamp": row[timestamp_col],
                "y_true": y_true,
                "y_pred": prediction,
                "condition": condition,
            }
        )

    return pd.DataFrame(rows)


def run_rolling_backtest(
    df: pd.DataFrame,
    condition: str,
    horizon_max: int,
    model_factory: ModelFactory | None = None,
    predict_function: PredictFunction | None = None,
    lags: Iterable[int] | None = None,
    timestamp_col: str = "datetime",
    target_col: str = "value",
    scaler_factory: ScalerFactory | None = None,
    test_start: str = TEST_START,
    test_end: str = TEST_END,
) -> RollingOriginResult:
    """Run the strict rolling-origin backtest over all valid test origins."""
    if lags is None:
        lags = []

    origins = generate_rolling_origins(
        df=df,
        timestamp_col=timestamp_col,
        test_start=test_start,
        test_end=test_end,
        horizon_max=horizon_max,
    )

    all_predictions: list[pd.DataFrame] = []
    for origin in origins:
        origin_result = run_single_origin_evaluation(
            df=df,
            origin=origin,
            condition=condition,
            horizon_max=horizon_max,
            model_factory=model_factory,
            predict_function=predict_function,
            lags=lags,
            timestamp_col=timestamp_col,
            target_col=target_col,
            scaler_factory=scaler_factory,
        )
        all_predictions.append(origin_result)

    predictions_df = (
        pd.concat(all_predictions, ignore_index=True)
        if all_predictions
        else pd.DataFrame(columns=["origin", "horizon", "timestamp", "y_true", "y_pred", "condition"])
    )

    metadata = {
        "condition": condition,
        "horizon_max": horizon_max,
        "n_origins": len(origins),
        "timestamp_col": timestamp_col,
        "target_col": target_col,
        "lags": list(lags),
        "train_end_anchor": TRAIN_END,
        "test_start": test_start,
        "test_end": test_end,
    }

    return RollingOriginResult(predictions=predictions_df, metadata=metadata)
