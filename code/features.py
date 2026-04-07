from __future__ import annotations

from typing import Iterable

import pandas as pd

from config import CALENDAR_FEATURES, METEO_CORE_FEATURES, METEO_EXTENDED_FEATURES


def add_calendar_features(
    df: pd.DataFrame,
    timestamp_col: str = "datetime",
) -> pd.DataFrame:
    """Add simple calendar features derived from the timestamp column."""
    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    out = df.copy()
    ts = pd.to_datetime(out[timestamp_col], errors="coerce")
    if ts.isna().any():
        n_invalid = int(ts.isna().sum())
        raise ValueError(f"Timestamp column contains {n_invalid} invalid values.")

    out["hour_of_day"] = ts.dt.hour.astype(int)
    out["day_of_week"] = ts.dt.dayofweek.astype(int)
    out["month"] = ts.dt.month.astype(int)
    out["julian_day"] = ts.dt.dayofyear.astype(int)
    return out


def build_autoregressive_features(
    df: pd.DataFrame,
    target_col: str = "value",
    lags: Iterable[int] | None = None,
) -> pd.DataFrame:
    """Create backward-looking lag features for the target series."""
    if target_col not in df.columns:
        raise ValueError(f"Missing target column: {target_col}")

    if lags is None:
        lags = []

    out = df.copy()
    for lag in lags:
        if lag <= 0:
            raise ValueError(f"Lag values must be positive integers. Received: {lag}")
        out[f"{target_col}_lag_{lag}"] = out[target_col].shift(lag)
    return out


def drop_rows_with_insufficient_history(
    df: pd.DataFrame,
    required_columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Drop rows that cannot be used because required history is missing."""
    if required_columns is None:
        required_columns = []

    required_columns = list(required_columns)
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for history filtering: {missing}")

    if not required_columns:
        return df.copy().reset_index(drop=True)

    return df.dropna(subset=required_columns).reset_index(drop=True)


def get_feature_groups(
    target_col: str = "value",
    lags: Iterable[int] | None = None,
) -> dict[str, list[str]]:
    """Expose feature groups in a compact, reusable structure."""
    if lags is None:
        lags = []

    autoregressive_features = [f"{target_col}_lag_{lag}" for lag in lags]

    return {
        "autoregressive": autoregressive_features,
        "calendar": list(CALENDAR_FEATURES),
        "meteo_core": list(METEO_CORE_FEATURES),
        "meteo_extended": list(METEO_EXTENDED_FEATURES),
    }


def select_features_by_condition(
    condition: str,
    target_col: str = "value",
    lags: Iterable[int] | None = None,
    available_columns: Iterable[str] | None = None,
) -> list[str]:
    """Select feature columns according to the experimental condition."""
    feature_groups = get_feature_groups(target_col=target_col, lags=lags)

    if condition == "C0":
        selected: list[str] = []
    elif condition == "C1":
        selected = feature_groups["autoregressive"] + feature_groups["calendar"]
    elif condition == "C2":
        selected = (
            feature_groups["autoregressive"]
            + feature_groups["calendar"]
            + feature_groups["meteo_core"]
        )
    elif condition == "C3":
        selected = (
            feature_groups["autoregressive"]
            + feature_groups["calendar"]
            + feature_groups["meteo_extended"]
        )
    else:
        raise ValueError(f"Unknown experimental condition: {condition}")

    if available_columns is None:
        return selected

    available = set(available_columns)
    return [col for col in selected if col in available]
