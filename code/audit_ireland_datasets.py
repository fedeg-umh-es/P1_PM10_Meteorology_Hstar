#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


REPO_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = Path.home() / "Downloads" / "Finalised_merged_datasets"
DEFAULT_REPORTS_DIR = REPO_DIR / "reports"

DATE_COLUMNS = ("Date and Time", "datetime", "timestamp", "date")
TARGET_COLUMNS = ("PM10", "PM2.5")
METEO_COLUMNS = ("rain", "temp", "wetb", "dewpt", "vappr", "rhum", "msl", "wdsp", "wddir")
AUX_POLLUTANTS = ("NO2", "O3", "SO2", "CO")


def infer_station_name(path: Path) -> str:
    name = path.stem
    suffixes = [
        "_finalised_merged_dublin_NA",
        "_finalised merged_NA",
        "_finalised merging_NA",
        "_merging finalised_NA",
        "_finalised_merged_NA",
        "_merged_NA",
    ]
    for suffix in suffixes:
        name = name.replace(suffix, "")
    return " ".join(name.replace("_", " ").split()).strip()


def find_date_column(columns: Iterable[str]) -> str:
    normalized = {str(col).strip().lstrip("\ufeff"): col for col in columns}
    for candidate in DATE_COLUMNS:
        if candidate in normalized:
            return normalized[candidate]
    raise ValueError(f"No date column found. Expected one of: {', '.join(DATE_COLUMNS)}")


def parse_datetime(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", format="mixed")
    if parsed.isna().mean() > 0.01:
        fallback = pd.to_datetime(series, errors="coerce", dayfirst=False)
        parsed = parsed.fillna(fallback)
    return parsed


def expected_hourly_rows(start: pd.Timestamp | pd.NaT, end: pd.Timestamp | pd.NaT) -> int:
    if pd.isna(start) or pd.isna(end) or end < start:
        return 0
    return int(((end - start).total_seconds() // 3600) + 1)


def numeric_profile(df: pd.DataFrame, column: str) -> dict[str, object]:
    if column not in df.columns:
        return {
            f"{column}_available": False,
            f"{column}_missing_pct": None,
            f"{column}_negative_count": None,
            f"{column}_zero_count": None,
            f"{column}_min": None,
            f"{column}_p50": None,
            f"{column}_p95": None,
            f"{column}_p99": None,
            f"{column}_max": None,
            f"{column}_iqr_outlier_count": None,
        }

    values = pd.to_numeric(df[column], errors="coerce")
    non_na = values.dropna()
    if non_na.empty:
        return {
            f"{column}_available": True,
            f"{column}_missing_pct": 100.0,
            f"{column}_negative_count": 0,
            f"{column}_zero_count": 0,
            f"{column}_min": None,
            f"{column}_p50": None,
            f"{column}_p95": None,
            f"{column}_p99": None,
            f"{column}_max": None,
            f"{column}_iqr_outlier_count": 0,
        }

    q1 = non_na.quantile(0.25)
    q3 = non_na.quantile(0.75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    lower = q1 - 1.5 * iqr
    outliers = values[(values < lower) | (values > upper)]

    return {
        f"{column}_available": True,
        f"{column}_missing_pct": round(float(values.isna().mean() * 100), 3),
        f"{column}_negative_count": int((values < 0).sum()),
        f"{column}_zero_count": int((values == 0).sum()),
        f"{column}_min": round(float(non_na.min()), 6),
        f"{column}_p50": round(float(non_na.quantile(0.50)), 6),
        f"{column}_p95": round(float(non_na.quantile(0.95)), 6),
        f"{column}_p99": round(float(non_na.quantile(0.99)), 6),
        f"{column}_max": round(float(non_na.max()), 6),
        f"{column}_iqr_outlier_count": int(outliers.notna().sum()),
    }


def audit_file(path: Path) -> dict[str, object]:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [str(col).strip().lstrip("\ufeff") for col in df.columns]
    date_col = find_date_column(df.columns)
    timestamps = parse_datetime(df[date_col])

    valid_ts = timestamps.dropna().sort_values()
    start = valid_ts.min() if not valid_ts.empty else pd.NaT
    end = valid_ts.max() if not valid_ts.empty else pd.NaT
    expected_rows = expected_hourly_rows(start, end)
    duplicate_timestamps = int(timestamps.duplicated().sum())

    row = {
        "file": path.name,
        "station": infer_station_name(path),
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "date_column": date_col,
        "datetime_parse_failures": int(timestamps.isna().sum()),
        "start": None if pd.isna(start) else start.isoformat(sep=" "),
        "end": None if pd.isna(end) else end.isoformat(sep=" "),
        "expected_hourly_rows": expected_rows,
        "hourly_coverage_pct": round(float(len(df) / expected_rows * 100), 3) if expected_rows else None,
        "duplicate_timestamps": duplicate_timestamps,
        "pm10_available": "PM10" in df.columns,
        "pm25_available": "PM2.5" in df.columns,
        "meteo_columns_available": ",".join([col for col in METEO_COLUMNS if col in df.columns]),
        "aux_pollutants_available": ",".join([col for col in AUX_POLLUTANTS if col in df.columns]),
    }

    for column in list(TARGET_COLUMNS) + list(AUX_POLLUTANTS) + list(METEO_COLUMNS):
        row.update(numeric_profile(df, column))

    flags = []
    if row["datetime_parse_failures"]:
        flags.append("datetime_parse_failures")
    if duplicate_timestamps:
        flags.append("duplicate_timestamps")
    for target in TARGET_COLUMNS:
        if row.get(f"{target}_available") and (row.get(f"{target}_negative_count") or 0) > 0:
            flags.append(f"{target}_negative_values")
        if row.get(f"{target}_available") and (row.get(f"{target}_missing_pct") or 0) > 5:
            flags.append(f"{target}_missing_gt_5pct")
        if row.get(f"{target}_available") and row.get(f"{target}_max") is not None and float(row[f"{target}_max"]) > 500:
            flags.append(f"{target}_max_gt_500")
    row["audit_flags"] = ";".join(flags) if flags else "OK"
    return row


def write_markdown(summary: pd.DataFrame, output_path: Path) -> None:
    compact_cols = [
        "station",
        "rows",
        "start",
        "end",
        "hourly_coverage_pct",
        "pm10_available",
        "PM10_missing_pct",
        "PM10_negative_count",
        "PM10_max",
        "PM10_iqr_outlier_count",
        "pm25_available",
        "PM2.5_missing_pct",
        "PM2.5_negative_count",
        "PM2.5_max",
        "PM2.5_iqr_outlier_count",
        "meteo_columns_available",
        "audit_flags",
    ]
    available_cols = [col for col in compact_cols if col in summary.columns]
    compact = summary[available_cols].copy()
    markdown_table = dataframe_to_markdown(compact)

    lines = [
        "# Ireland PM10/PM2.5 dataset inventory",
        "",
        "Generated by `code/audit_ireland_datasets.py`.",
        "",
        "This is a structural audit only. It does not impute, filter, train models, or alter raw CSV files.",
        "",
        "## Summary table",
        "",
        markdown_table,
        "",
        "## Interpretation guardrails",
        "",
        "- Negative target values must be resolved before forecasting claims.",
        "- Outlier counts are Tukey IQR flags, not automatic exclusions.",
        "- Meteorological covariates must be treated as available only at forecast origin unless explicitly nowcast/forecast.",
        "- Any future preprocessing script must fit imputation/scaling rules inside each rolling-origin training fold.",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a compact GitHub-flavored Markdown table without optional deps."""
    if df.empty:
        return "_No rows._"

    def fmt(value: object) -> str:
        if pd.isna(value):
            return ""
        text = str(value)
        return text.replace("|", "\\|").replace("\n", " ")

    headers = [fmt(col) for col in df.columns]
    rows = [[fmt(value) for value in row] for row in df.itertuples(index=False, name=None)]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Ireland merged PM10/PM2.5 + meteorology CSV files.")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR), help="Directory containing Ireland CSV files.")
    parser.add_argument("--pattern", default="*.csv", help="Glob pattern inside input-dir.")
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR), help="Directory for audit outputs.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    reports_dir = Path(args.reports_dir).expanduser().resolve()
    reports_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(input_dir.glob(args.pattern))
    if not files:
        raise FileNotFoundError(f"No files matched {input_dir / args.pattern}")

    rows = [audit_file(path) for path in files]
    summary = pd.DataFrame(rows).sort_values("station").reset_index(drop=True)

    csv_path = reports_dir / "ireland_dataset_inventory.csv"
    md_path = reports_dir / "ireland_dataset_inventory.md"
    summary.to_csv(csv_path, index=False)
    write_markdown(summary, md_path)

    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(f"Audited files: {len(summary)}")


if __name__ == "__main__":
    main()
