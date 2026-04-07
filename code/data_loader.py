from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from config import (
    DATA_RAW_DIR,
    FREQ,
    TEST_END,
    TEST_START,
    TRAIN_END,
    TRAIN_START,
)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip BOMs and surrounding whitespace from column names."""
    out = df.copy()
    out.columns = [str(c).replace("\ufeff", "").strip() for c in out.columns]
    return out


def _detect_separator(csv_path: Path) -> str:
    """Infer a CSV separator from the first line."""
    with csv_path.open("r", encoding="utf-8-sig", errors="ignore") as handle:
        first_line = handle.readline()
    return ";" if first_line.count(";") >= first_line.count(",") else ","


def validate_time_index(
    df: pd.DataFrame,
    timestamp_col: str,
    expected_freq: str | None = FREQ,
) -> dict[str, Any]:
    """Validate timestamp ordering, duplicates, and inferred frequency."""
    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    ts = pd.to_datetime(df[timestamp_col], errors="coerce")
    if ts.isna().any():
        n_invalid = int(ts.isna().sum())
        raise ValueError(f"Timestamp column contains {n_invalid} invalid values.")

    is_sorted = bool(ts.is_monotonic_increasing)
    n_duplicates = int(ts.duplicated().sum())

    inferred_freq = None
    freq_matches_expected = None
    if len(ts) >= 3:
        try:
            inferred_freq = pd.infer_freq(ts)
        except ValueError:
            inferred_freq = None

    if expected_freq is not None:
        freq_matches_expected = inferred_freq == expected_freq if inferred_freq is not None else None

    return {
        "is_sorted": is_sorted,
        "n_duplicates": n_duplicates,
        "inferred_freq": inferred_freq,
        "expected_freq": expected_freq,
        "freq_matches_expected": freq_matches_expected,
    }


def load_target_series(
    path: str | Path,
    timestamp_col: str = "datetime",
    target_col: str = "value",
    sep: str = "auto",
) -> pd.DataFrame:
    """Load the target PM10 series without scaling or feature construction."""
    csv_path = Path(path).expanduser().resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"Target series file not found: {csv_path}")

    delimiter = _detect_separator(csv_path) if sep == "auto" else sep
    df = pd.read_csv(csv_path, sep=delimiter, encoding="utf-8-sig")
    df = _normalize_columns(df)

    missing = [col for col in [timestamp_col, target_col] if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in target series: {missing}")

    out = df[[timestamp_col, target_col]].copy()
    out[timestamp_col] = pd.to_datetime(out[timestamp_col], errors="coerce")
    out[target_col] = pd.to_numeric(out[target_col], errors="coerce")
    out = out.dropna(subset=[timestamp_col])
    out = out.sort_values(timestamp_col).drop_duplicates(subset=[timestamp_col], keep="last")

    report = validate_time_index(out, timestamp_col=timestamp_col, expected_freq=FREQ)
    if not report["is_sorted"]:
        raise ValueError("Target series is not strictly ordered by timestamp.")
    if report["n_duplicates"] > 0:
        raise ValueError("Target series contains duplicated timestamps after normalization.")

    return out.reset_index(drop=True)


def load_meteorological_data(
    path: str | Path | None = None,
    timestamp_col: str = "datetime",
    sep: str = "auto",
) -> pd.DataFrame:
    """Load meteorological covariates if a source is available.

    The meteorological source is not yet fixed in the repository.
    This function therefore provides a minimal, reusable loader that
    returns an empty DataFrame when no path is supplied.
    """
    if path is None:
        return pd.DataFrame(columns=[timestamp_col])

    csv_path = Path(path).expanduser().resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"Meteorological data file not found: {csv_path}")

    delimiter = _detect_separator(csv_path) if sep == "auto" else sep
    df = pd.read_csv(csv_path, sep=delimiter, encoding="utf-8-sig")
    df = _normalize_columns(df)

    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column in meteorological data: {timestamp_col}")

    out = df.copy()
    out[timestamp_col] = pd.to_datetime(out[timestamp_col], errors="coerce")
    out = out.dropna(subset=[timestamp_col])
    out = out.sort_values(timestamp_col).drop_duplicates(subset=[timestamp_col], keep="last")

    report = validate_time_index(out, timestamp_col=timestamp_col, expected_freq=FREQ)
    if report["n_duplicates"] > 0:
        raise ValueError("Meteorological data contains duplicated timestamps after normalization.")

    return out.reset_index(drop=True)


def merge_target_and_meteorology(
    target_df: pd.DataFrame,
    meteo_df: pd.DataFrame | None,
    timestamp_col: str = "datetime",
    how: str = "left",
) -> pd.DataFrame:
    """Merge target and meteorology on timestamp without imputation."""
    if timestamp_col not in target_df.columns:
        raise ValueError(f"Missing timestamp column in target_df: {timestamp_col}")

    if meteo_df is None or meteo_df.empty:
        return target_df.copy()

    if timestamp_col not in meteo_df.columns:
        raise ValueError(f"Missing timestamp column in meteo_df: {timestamp_col}")

    target_sorted = target_df.sort_values(timestamp_col).copy()
    meteo_sorted = meteo_df.sort_values(timestamp_col).copy()

    merged = pd.merge(
        target_sorted,
        meteo_sorted,
        on=timestamp_col,
        how=how,
        validate="one_to_one",
        sort=True,
    )
    return merged.reset_index(drop=True)


def split_train_test_by_time(
    df: pd.DataFrame,
    timestamp_col: str = "datetime",
    train_start: str = TRAIN_START,
    train_end: str = TRAIN_END,
    test_start: str = TEST_START,
    test_end: str = TEST_END,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a DataFrame into chronological train and test partitions."""
    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    out = df.copy()
    out[timestamp_col] = pd.to_datetime(out[timestamp_col], errors="coerce")
    out = out.dropna(subset=[timestamp_col]).sort_values(timestamp_col)

    train_start_ts = pd.Timestamp(train_start)
    train_end_ts = pd.Timestamp(train_end)
    test_start_ts = pd.Timestamp(test_start)
    test_end_ts = pd.Timestamp(test_end)

    if train_end_ts >= test_start_ts:
        raise ValueError("Train period must end before test period starts.")

    train_df = out[(out[timestamp_col] >= train_start_ts) & (out[timestamp_col] <= train_end_ts)].copy()
    test_df = out[(out[timestamp_col] >= test_start_ts) & (out[timestamp_col] <= test_end_ts)].copy()

    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def basic_missingness_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return a compact missingness summary without modifying the data."""
    report = pd.DataFrame(
        {
            "column": df.columns,
            "n_missing": [int(df[col].isna().sum()) for col in df.columns],
            "pct_missing": [float(df[col].isna().mean() * 100.0) for col in df.columns],
        }
    )
    return report.sort_values(["pct_missing", "column"], ascending=[False, True]).reset_index(drop=True)


def load_default_target_series(
    filename: str,
    timestamp_col: str = "datetime",
    target_col: str = "value",
    base_dir: Path = DATA_RAW_DIR,
) -> pd.DataFrame:
    """Convenience wrapper to load a target series from the raw-data directory."""
    return load_target_series(
        path=base_dir / filename,
        timestamp_col=timestamp_col,
        target_col=target_col,
    )
