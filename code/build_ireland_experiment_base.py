#!/usr/bin/env python3
"""
build_ireland_experiment_base.py

Builds the canonical hourly dataset for the Ireland PM10 + meteorology experiment.
Reads raw merged CSVs from ~/Downloads/Finalised_merged_datasets/, applies quality
rules, and outputs a single long-format CSV with station column.

Quality rules applied:
  - EXCLUDED: Rathmines Dublin (PM10 min=-488, 121 negatives)
  - ALL stations: negative PM10 → NaN
  - Dundalk Co Louth: PM10 > 500 µg/m³ → NaN (max=2010.8 in audit)
  - Ringsend dublin: duplicate timestamps resolved (keep first after sort), NaT dropped
  - Meteorology: kept as-is, no imputation at this stage
  - No imputation of PM10 target

Output: data_processed/ireland_pm10_meteorology_hourly.csv
Report: reports/ireland_experiment_setup.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
INPUT_DIR = Path.home() / "Downloads" / "Finalised_merged_datasets"
OUT_CSV = REPO / "data_processed" / "ireland_pm10_meteorology_hourly.csv"
OUT_MD = REPO / "reports" / "ireland_experiment_setup.md"

EXCLUDED_STATIONS = {"Rathmines Dublin"}
DUNDALK_PM10_CAP = 500.0

DATE_COLUMNS = ("Date and Time", "datetime", "timestamp", "date")
CANONICAL_METEO = ("rain", "temp", "wetb", "dewpt", "vappr", "rhum", "msl", "wdsp", "wddir")
CANONICAL_POLLUTANTS = ("PM10", "PM2.5", "NO2", "O3", "SO2", "CO")
CANONICAL_OUTPUT = ["timestamp", "station"] + list(CANONICAL_POLLUTANTS) + list(CANONICAL_METEO)

STATION_SUFFIXES = [
    "_finalised_merged_dublin_NA",
    "_finalised merged_NA",
    "_finalised merging_NA",
    "_merging finalised_NA",
    "_finalised_merged_NA",
    "_merged_NA",
]


def infer_station_name(path: Path) -> str:
    name = path.stem
    for suffix in STATION_SUFFIXES:
        name = name.replace(suffix, "")
    return " ".join(name.replace("_", " ").split()).strip()


def find_date_column(columns: list[str]) -> str:
    normalized = {str(col).strip().lstrip("﻿"): col for col in columns}
    for candidate in DATE_COLUMNS:
        if candidate in normalized:
            return normalized[candidate]
    raise ValueError(f"No date column found in: {list(columns)}")


def load_station(path: Path, station: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [str(c).strip().lstrip("﻿") for c in df.columns]

    date_col = find_date_column(df.columns)
    df["timestamp"] = pd.to_datetime(df[date_col], errors="coerce", format="mixed")

    # Drop rows where timestamp could not be parsed
    n_before = len(df)
    df = df.dropna(subset=["timestamp"]).copy()
    n_dropped = n_before - len(df)
    if n_dropped:
        print(f"    [{station}] Dropped {n_dropped} rows with unparseable timestamps")

    df["station"] = station

    # Resolve duplicate timestamps: sort then keep first occurrence
    n_dups = df.duplicated(subset=["timestamp"]).sum()
    if n_dups:
        df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"], keep="first")
        print(f"    [{station}] Resolved {n_dups} duplicate timestamps (kept first)")

    df = df.sort_values("timestamp").reset_index(drop=True)

    # Numeric coercion of pollutants and meteo
    for col in list(CANONICAL_POLLUTANTS) + list(CANONICAL_METEO):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def apply_quality_rules(df: pd.DataFrame, station: str) -> tuple[pd.DataFrame, dict]:
    report: dict = {"station": station, "actions": []}

    # Rule 1: negative PM10 → NaN (all stations)
    if "PM10" in df.columns:
        n_neg = int((df["PM10"] < 0).sum())
        if n_neg:
            df.loc[df["PM10"] < 0, "PM10"] = float("nan")
            report["actions"].append(f"PM10 negatives set to NaN: {n_neg}")

    # Rule 2: Dundalk Co Louth PM10 cap
    if station == "Dundalk Co Louth" and "PM10" in df.columns:
        n_cap = int((df["PM10"] > DUNDALK_PM10_CAP).sum())
        if n_cap:
            df.loc[df["PM10"] > DUNDALK_PM10_CAP, "PM10"] = float("nan")
            report["actions"].append(
                f"PM10 values > {DUNDALK_PM10_CAP} µg/m³ set to NaN: {n_cap}"
            )

    return df, report


def select_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in CANONICAL_OUTPUT if c in df.columns]
    # Add any canonical columns missing from this station as NaN
    for col in CANONICAL_OUTPUT:
        if col not in df.columns:
            df[col] = float("nan")
    return df[CANONICAL_OUTPUT].copy()


def build_dataset(input_dir: Path) -> tuple[pd.DataFrame, list[dict]]:
    files = sorted(input_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")

    frames: list[pd.DataFrame] = []
    quality_reports: list[dict] = []

    for path in files:
        station = infer_station_name(path)

        if station in EXCLUDED_STATIONS:
            print(f"  SKIP (excluded): {station}")
            quality_reports.append({
                "station": station,
                "file": path.name,
                "status": "excluded",
                "reason": "Strong negative PM10 values (PM10_min=-488)",
                "rows_included": 0,
                "actions": [],
            })
            continue

        print(f"  Loading: {station} ({path.name})")
        df = load_station(path, station)
        df, qr = apply_quality_rules(df, station)
        df = select_canonical_columns(df)

        qr["file"] = path.name
        qr["status"] = "included"
        qr["reason"] = ""
        qr["rows_included"] = len(df)
        quality_reports.append(qr)

        frames.append(df)
        print(f"    → {len(df)} rows, PM10 missing: {df['PM10'].isna().mean()*100:.2f}%")

    if not frames:
        raise RuntimeError("No stations loaded after exclusions")

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(["station", "timestamp"]).reset_index(drop=True)
    return combined, quality_reports


def write_report(combined: pd.DataFrame, quality_reports: list[dict], out_path: Path) -> None:
    stations = combined["station"].unique()
    lines = [
        "# Ireland Experiment Setup",
        "",
        "Generated by `code/build_ireland_experiment_base.py`.",
        "",
        "## Station decisions",
        "",
        "| Station | Status | Reason / Actions | Rows |",
        "|---------|--------|-----------------|------|",
    ]
    for qr in quality_reports:
        actions = "; ".join(qr["actions"]) if qr["actions"] else "—"
        reason = qr.get("reason") or actions
        lines.append(f"| {qr['station']} | {qr['status']} | {reason} | {qr['rows_included']} |")

    lines += [
        "",
        "## Canonical columns",
        "",
        f"Target: `PM10`  ",
        f"Meteorology: {', '.join(f'`{c}`' for c in CANONICAL_METEO)}  ",
        f"Aux pollutants: `PM2.5`, `NO2`, `O3`, `SO2`, `CO` (nullable per station)",
        "",
        "## Dataset summary",
        "",
        "| Station | Start | End | Rows | PM10 missing % |",
        "|---------|-------|-----|------|----------------|",
    ]
    for stn in sorted(stations):
        s = combined[combined["station"] == stn]
        start = str(s["timestamp"].min())
        end = str(s["timestamp"].max())
        pm10_miss = s["PM10"].isna().mean() * 100
        lines.append(f"| {stn} | {start} | {end} | {len(s)} | {pm10_miss:.2f}% |")

    lines += [
        "",
        "## Quality rules applied",
        "",
        "- `Rathmines Dublin` excluded: PM10_min = -488 µg/m³, 121 negative readings.",
        f"- `Dundalk Co Louth`: PM10 > {DUNDALK_PM10_CAP} µg/m³ set to NaN (audit max = 2010.8).",
        "- All stations: negative PM10 set to NaN.",
        "- `Ringsend dublin`: duplicate timestamps resolved (keep first); NaT timestamps dropped.",
        "- Meteorology: no imputation applied. Missing values remain NaN.",
        "- PM10 target: not imputed.",
        "",
        "## Leakage note",
        "",
        "All preprocessing (negative removal, outlier capping) is applied globally before",
        "any model fitting. Meteorology imputation, if needed, must be applied inside each",
        "rolling-origin training fold by the experiment runner.",
    ]

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    print("=== Ireland Experiment Base Builder ===\n")

    parser = argparse.ArgumentParser(
        description="Build the canonical Ireland PM10 + meteorology hourly dataset."
    )
    parser.add_argument(
        "--input-dir",
        default=str(INPUT_DIR),
        help="Directory containing the 9 Finalised_merged_datasets CSV files "
        "(portability override only; defaults to ~/Downloads/Finalised_merged_datasets).",
    )
    parser.add_argument(
        "--out-csv",
        default=str(OUT_CSV),
        help="Output path for the consolidated hourly CSV.",
    )
    parser.add_argument(
        "--out-md",
        default=str(OUT_MD),
        help="Output path for the setup report markdown.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_csv = Path(args.out_csv).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory not found: {input_dir}\n"
            "Place the Finalised_merged_datasets folder in ~/Downloads/ or pass --input-dir."
        )

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    print("Loading and cleaning stations...")
    combined, quality_reports = build_dataset(input_dir)

    combined.to_csv(out_csv, index=False)
    print(f"\nExported: {out_csv}  ({len(combined)} rows, {combined['station'].nunique()} stations)")

    write_report(combined, quality_reports, out_md)
    print(f"Exported: {out_md}")

    print("\nStation row counts:")
    for stn, grp in combined.groupby("station"):
        pm10_miss = grp["PM10"].isna().mean() * 100
        print(f"  {stn}: {len(grp)} rows, PM10 missing {pm10_miss:.2f}%")

    print("\nDone.")


if __name__ == "__main__":
    main()
