#!/usr/bin/env python3
"""Build the frozen Madrid station-24 PM10 + meteorology hourly input."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

STATION = 24
PM10_MAGNITUDE = 10
METEO_NAMES = {
    81: "wind_speed_ms", 82: "wind_dir_deg", 83: "temp_c",
    86: "humidity_pct", 87: "pressure_hpa", 88: "solar_rad_wm2",
    89: "precip_mm",
}


def _hourly_rows(frame: pd.DataFrame, value_name: str) -> pd.DataFrame:
    rows = []
    for hour in range(1, 25):
        value = pd.to_numeric(frame[f"H{hour:02d}"], errors="coerce")
        valid = frame[f"V{hour:02d}"].astype(str).str.upper().eq("V")
        timestamp = pd.to_datetime(
            dict(year=frame["ANO"], month=frame["MES"], day=frame["DIA"]),
            errors="raise",
        ) + pd.to_timedelta(hour - 1, unit="h")
        rows.append(pd.DataFrame({"timestamp": timestamp, value_name: value.where(valid)}))
    return pd.concat(rows, ignore_index=True)


def build_pm10(manifest_path: Path) -> pd.DataFrame:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    paths = []
    for year in sorted(manifest["years"]):
        paths.extend(Path(rec["path"]) for rec in manifest["years"][year]["valid_files"])
    frames = []
    for path in paths:
        raw = pd.read_csv(path, sep=";", encoding="utf-8-sig")
        raw = raw[(raw["ESTACION"] == STATION) & (raw["MAGNITUD"] == PM10_MAGNITUDE)]
        frames.append(_hourly_rows(raw, "PM10"))
    out = pd.concat(frames, ignore_index=True).sort_values("timestamp")
    if out["timestamp"].duplicated().any():
        raise ValueError("Unresolved duplicate PM10 timestamps")
    return out.reset_index(drop=True)


def build_meteo(manifest_path: Path) -> pd.DataFrame:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    frames = []
    for rec in sorted(manifest["files"], key=lambda r: (r["year"], r["month"])):
        raw = pd.read_csv(rec["path"], sep=rec["delimiter"], encoding=rec["encoding"])
        raw = raw[(raw["ESTACION"] == STATION) & raw["MAGNITUD"].isin(METEO_NAMES)]
        month_parts = []
        for magnitude, name in METEO_NAMES.items():
            part = _hourly_rows(raw[raw["MAGNITUD"] == magnitude], name)
            month_parts.append(part.set_index("timestamp"))
        frames.append(pd.concat(month_parts, axis=1).reset_index())
    out = pd.concat(frames, ignore_index=True).sort_values("timestamp")
    if out["timestamp"].duplicated().any():
        raise ValueError("Unresolved duplicate meteorology timestamps")
    return out.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pm10-manifest", required=True)
    parser.add_argument("--meteo-manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    pm10 = build_pm10(Path(args.pm10_manifest))
    meteo = build_meteo(Path(args.meteo_manifest))
    joined = pm10.merge(meteo, on="timestamp", how="outer", validate="one_to_one")
    joined = joined.sort_values("timestamp").reset_index(drop=True)
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    joined.to_csv(output, index=False)
    expected = pd.date_range(joined.timestamp.min(), joined.timestamp.max(), freq="h")
    missing_clock = expected.difference(joined.timestamp)
    report = {
        "station": STATION,
        "station_name": "Casa de Campo",
        "timestamp_semantics": "official timezone-naive hourly labels; H01 maps to 00:00",
        "rows": len(joined),
        "start": str(joined.timestamp.min()),
        "end": str(joined.timestamp.max()),
        "missing_clock_timestamps": len(missing_clock),
        "duplicate_timestamps": int(joined.timestamp.duplicated().sum()),
        "missing_percent": {c: float(joined[c].isna().mean() * 100) for c in joined.columns if c != "timestamp"},
        "pm10_manifest": str(Path(args.pm10_manifest).resolve()),
        "meteo_manifest": str(Path(args.meteo_manifest).resolve()),
    }
    report_path = Path(args.report); report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
