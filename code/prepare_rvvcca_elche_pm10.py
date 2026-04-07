#!/usr/bin/env python3
"""
ETL base for Elche PM10 — station 3065007 (ELX - PARC DE BOMBERS).

Reads: data_raw/rvvcca/rvvcca_raw_3065007_hourly.csv
       (produced by download_rvvcca_raw.py)

Applies:
  - Filter variable == PM10
  - Build regular hourly grid (no value imputation)
  - Hard-exclude September 2023 (no compatible official hourly data)
  - Train split: 2017-01-01 00:00 .. 2022-12-31 23:00 (inclusive)
  - Test  split: 2023-01-01 00:00 .. 2023-12-31 23:00 (excluding Sep 2023)

Output schema (both files):
  datetime   — ISO8601 hourly timestamp
  pm10       — observed concentration (µg/m³), NaN where missing
  is_missing — 1 if pm10 is NaN, else 0

Outputs:
  data_processed/elche_pm10_train_base.csv
  data_processed/elche_pm10_test_base.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data_raw" / "rvvcca"
OUT_DIR = ROOT_DIR / "data_processed"

RAW_PATH = RAW_DIR / "rvvcca_raw_3065007_hourly.csv"

# ---------------------------------------------------------------------------
# Temporal constants
# ---------------------------------------------------------------------------

TRAIN_START = pd.Timestamp("2017-01-01 00:00")
TRAIN_END   = pd.Timestamp("2022-12-31 23:00")
TEST_START  = pd.Timestamp("2023-01-01 00:00")
TEST_END    = pd.Timestamp("2023-12-31 23:00")

# Explicit exclusion: September 2023 has no compatible official hourly data.
EXCLUDE_START = pd.Timestamp("2023-09-01 00:00")
EXCLUDE_END   = pd.Timestamp("2023-09-30 23:00")

STATION_ID = "3065007"
VARIABLE   = "PM10"


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def load_pm10(raw_path: Path) -> pd.Series:
    """Load and filter PM10 from the raw station file."""
    if not raw_path.exists():
        print(f"[ERROR] Raw file not found: {raw_path}", flush=True)
        sys.exit(1)

    df = pd.read_csv(raw_path, parse_dates=["timestamp"])
    df.columns = [c.strip() for c in df.columns]

    pm10_df = df[df["variable"].str.upper().str.strip() == VARIABLE].copy()
    if pm10_df.empty:
        print(
            f"[ERROR] No rows with variable='{VARIABLE}' found in {raw_path.name}.\n"
            f"  Available variables: {df['variable'].unique().tolist()}",
            flush=True,
        )
        sys.exit(1)

    pm10 = (
        pm10_df
        .sort_values("timestamp")
        .drop_duplicates(subset=["timestamp"], keep="last")
        .set_index("timestamp")["value"]
        .rename("pm10")
    )
    pm10.index = pd.to_datetime(pm10.index)
    pm10 = pd.to_numeric(pm10, errors="coerce")
    return pm10


def build_regular_grid(pm10: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Reindex pm10 onto a complete hourly grid [start, end], no imputation."""
    grid = pd.date_range(start=start, end=end, freq="h")
    series = pm10.reindex(grid)
    df = series.reset_index()
    df.columns = ["datetime", "pm10"]
    df["is_missing"] = df["pm10"].isna().astype(int)
    return df


def apply_exclusions(df: pd.DataFrame) -> pd.DataFrame:
    """Drop September 2023 rows (hard exclusion — no imputation)."""
    mask_sep = (df["datetime"] >= EXCLUDE_START) & (df["datetime"] <= EXCLUDE_END)
    n_dropped = int(mask_sep.sum())
    df = df[~mask_sep].reset_index(drop=True)
    print(f"  September 2023 excluded: {n_dropped} rows dropped.", flush=True)
    return df


def validate_and_report(df: pd.DataFrame, label: str) -> None:
    n = len(df)
    n_missing = int(df["pm10"].isna().sum())
    pct_missing = 100.0 * n_missing / n if n > 0 else float("nan")
    n_dup = int(df["datetime"].duplicated().sum())
    ts_min = df["datetime"].min()
    ts_max = df["datetime"].max()

    # September 2023 check
    sep_present = bool(
        ((df["datetime"] >= EXCLUDE_START) & (df["datetime"] <= EXCLUDE_END)).any()
    )

    print(f"\n{label}:", flush=True)
    print(f"  Rows       : {n}", flush=True)
    print(f"  Start      : {ts_min}", flush=True)
    print(f"  End        : {ts_max}", flush=True)
    print(f"  Duplicates : {n_dup}", flush=True)
    print(f"  PM10 miss% : {pct_missing:.2f}%  ({n_missing}/{n})", flush=True)
    if label.upper().startswith("TEST"):
        print(f"  Sep 2023   : {'PRESENT (ERROR)' if sep_present else 'absent (OK)'}", flush=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading PM10 from: {RAW_PATH}", flush=True)
    pm10 = load_pm10(RAW_PATH)
    print(f"  Raw PM10 obs: {len(pm10)}  range {pm10.index.min()} to {pm10.index.max()}", flush=True)

    # Build full grid spanning both train and test
    full_start = TRAIN_START
    full_end   = TEST_END
    full_df = build_regular_grid(pm10, full_start, full_end)

    # Apply exclusions before splitting
    full_df = apply_exclusions(full_df)

    # Split
    train_df = full_df[
        (full_df["datetime"] >= TRAIN_START) & (full_df["datetime"] <= TRAIN_END)
    ].reset_index(drop=True)

    test_df = full_df[
        (full_df["datetime"] >= TEST_START) & (full_df["datetime"] <= TEST_END)
    ].reset_index(drop=True)

    # Validate
    validate_and_report(train_df, "TRAIN")
    validate_and_report(test_df, "TEST")

    # Write
    train_path = OUT_DIR / "elche_pm10_train_base.csv"
    test_path  = OUT_DIR / "elche_pm10_test_base.csv"

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"\nOK -> {train_path}", flush=True)
    print(f"OK -> {test_path}", flush=True)
    print("\n[DONE] ETL base complete.", flush=True)


if __name__ == "__main__":
    main()
