"""Timestamp-only temporal primitives for the P3 forecasting experiment."""
from __future__ import annotations

from typing import Iterable

import pandas as pd


ONE_HOUR = pd.Timedelta(hours=1)


def normalise_timestamps(df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
    """Parse and sort timestamps, rejecting ambiguity instead of silently deduplicating."""
    out = df.copy()
    out[timestamp_col] = pd.to_datetime(out[timestamp_col], errors="raise")
    if out[timestamp_col].isna().any():
        raise ValueError("Null timestamps are not allowed")
    duplicated = out[timestamp_col].duplicated(keep=False)
    if duplicated.any():
        values = out.loc[duplicated, timestamp_col].astype(str).unique()[:5]
        raise ValueError(f"Unresolved duplicate timestamps: {values.tolist()}")
    return out.sort_values(timestamp_col).reset_index(drop=True)


def generate_clock_origins(
    df: pd.DataFrame,
    timestamp_col: str,
    test_start: str,
    test_end: str,
    stride_hours: int = 24,
) -> list[pd.Timestamp]:
    """Return candidate origins from a clock calendar, never from row positions."""
    out = normalise_timestamps(df, timestamp_col)
    available = pd.Index(out[timestamp_col])
    start = pd.Timestamp(test_start)
    end = pd.Timestamp(test_end)
    candidates = pd.date_range(start=start, end=end, freq=pd.Timedelta(hours=stride_hours))
    return [pd.Timestamp(ts) for ts in candidates if ts in available]


def filter_complete_origins(
    df: pd.DataFrame,
    origins: Iterable[pd.Timestamp],
    timestamp_col: str,
    target_col: str,
    lags: Iterable[int],
    horizon_max: int,
) -> list[pd.Timestamp]:
    """Keep origins having PM10(T), every exact lag and every exact target."""
    out = normalise_timestamps(df[[timestamp_col, target_col]], timestamp_col)
    values = pd.to_numeric(out[target_col], errors="coerce")
    lookup = pd.Series(values.to_numpy(), index=out[timestamp_col])
    valid = []
    for origin in origins:
        required = [pd.Timestamp(origin)]
        required += [pd.Timestamp(origin) - pd.Timedelta(hours=int(lag)) for lag in lags]
        required += [pd.Timestamp(origin) + pd.Timedelta(hours=h) for h in range(1, horizon_max + 1)]
        if all(ts in lookup.index and pd.notna(lookup.loc[ts]) for ts in required):
            valid.append(pd.Timestamp(origin))
    return valid


def exact_time_values(
    df: pd.DataFrame,
    timestamp_col: str,
    value_col: str,
    requested_times: pd.Series,
) -> pd.Series:
    """Resolve values using an exact timestamp lookup; absent timestamps remain missing."""
    source = normalise_timestamps(df[[timestamp_col, value_col]], timestamp_col)
    lookup = source.set_index(timestamp_col)[value_col]
    return pd.to_datetime(requested_times).map(lookup)


def add_exact_lags(
    df: pd.DataFrame,
    timestamp_col: str,
    target_col: str,
    lags: Iterable[int],
) -> pd.DataFrame:
    out = normalise_timestamps(df, timestamp_col)
    for lag in lags:
        source_time = out[timestamp_col] - pd.Timedelta(hours=int(lag))
        out[f"{target_col}_lag_{int(lag)}_timestamp"] = source_time
        out[f"{target_col}_lag_{int(lag)}"] = exact_time_values(
            out, timestamp_col, target_col, source_time
        )
    return out


def add_exact_targets(
    df: pd.DataFrame,
    timestamp_col: str,
    target_col: str,
    horizon_max: int,
) -> pd.DataFrame:
    out = normalise_timestamps(df, timestamp_col)
    for horizon in range(1, horizon_max + 1):
        target_time = out[timestamp_col] + pd.Timedelta(hours=horizon)
        out[f"{target_col}_t_plus_{horizon}_timestamp"] = target_time
        out[f"{target_col}_t_plus_{horizon}"] = exact_time_values(
            out, timestamp_col, target_col, target_time
        )
    return out


def exact_horizon_window(
    df: pd.DataFrame,
    origin: pd.Timestamp,
    horizon_max: int,
    timestamp_col: str,
) -> pd.DataFrame:
    """Return origin and exact T+h rows, preserving missing required timestamps as gaps."""
    out = normalise_timestamps(df, timestamp_col).set_index(timestamp_col)
    required = pd.date_range(pd.Timestamp(origin), periods=horizon_max + 1, freq=ONE_HOUR)
    window = out.reindex(required)
    window.index.name = timestamp_col
    return window.reset_index()
