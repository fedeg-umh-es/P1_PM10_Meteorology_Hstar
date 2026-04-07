#!/usr/bin/env python3
"""
Ingest official RVVCCA exports from data_raw/rvvcca/official_drop/ and produce
standardized hourly CSVs per station.

Supported input formats (auto-detected):
  A. Wide pivot: columns H01..H24 present, with date info via AÑO+MES+DIA or FECHA.
  B. Long format: columns FECHA + HORA + PARAMETRO/VARIABLE + VALOR.
  Both .xlsx and .csv (auto-detected separator ; or ,) are accepted.

Station identification:
  Files may contain a CODEST / ESTACION column; or the station code may appear
  in the filename.  Both single-station and multi-station files are handled.

Hour convention (RVVCCA end-of-period):
  H01 → same date 01:00
  H24 → next date 00:00

Target stations:
  3065007  ELX - PARC DE BOMBERS    (PM10 target)
  3065006  ELX - AGROALIMENTARI     (meteo donor)

Output schema per station (CSV, comma-separated):
  timestamp,variable,value
  2017-01-01 01:00:00,PM10,15.2

Outputs:
  data_raw/rvvcca/rvvcca_raw_3065007_hourly.csv
  data_raw/rvvcca/rvvcca_raw_3065006_hourly.csv
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
DROP_DIR = ROOT_DIR / "data_raw" / "rvvcca" / "official_drop"
OUT_DIR = ROOT_DIR / "data_raw" / "rvvcca"

TARGET_STATIONS = {"3065007", "3065006"}

# RVVCCA hourly column patterns
H_COLS_RE = re.compile(r"^[Hh](\d{1,2})$")  # H01..H24 or H1..H24

STATION_COL_ALIASES = ["codest", "estacion", "codigo", "cod_est", "station", "cod"]
DATE_COL_ALIASES = ["fecha", "date", "día", "dia"]
YEAR_COL_ALIASES = ["año", "anyo", "year", "anio"]
MONTH_COL_ALIASES = ["mes", "month"]
DAY_COL_ALIASES = ["dia", "día", "day"]
PARAM_COL_ALIASES = ["parametro", "variable", "param", "contaminante", "pollutant"]
HOUR_COL_ALIASES = ["hora", "hour", "hh"]
VALUE_COL_ALIASES = ["valor", "value", "concentracion", "conc"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(name: str) -> str:
    """Lowercase, strip BOM and spaces, strip accents for matching."""
    import unicodedata
    name = str(name).replace("\ufeff", "").strip().lower()
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    return name


def _find_col(df: pd.DataFrame, aliases: list[str]) -> str | None:
    normed = {_norm(c): c for c in df.columns}
    for a in aliases:
        if a in normed:
            return normed[a]
    return None


def _detect_sep(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig", errors="ignore") as fh:
        first = fh.readline()
    return ";" if first.count(";") >= first.count(",") else ","


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    return df


def _extract_station_from_path(path: Path) -> str | None:
    """Try to extract a 7-digit station code from the filename."""
    m = re.search(r"\b(30\d{5})\b", path.stem)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------

def _read_file(path: Path) -> list[pd.DataFrame]:
    """Return a list of DataFrames (one per sheet for xlsx, one for csv)."""
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls", ".xlsm"}:
        xl = pd.ExcelFile(path)
        dfs = []
        for sheet in xl.sheet_names:
            df = xl.parse(sheet, dtype=str)
            df = _normalize_columns(df)
            dfs.append(df)
        return dfs
    else:
        sep = _detect_sep(path)
        df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", dtype=str)
        df = _normalize_columns(df)
        return [df]


# ---------------------------------------------------------------------------
# Format detection & parsing
# ---------------------------------------------------------------------------

def _has_hour_cols(df: pd.DataFrame) -> bool:
    return any(H_COLS_RE.match(c) for c in df.columns)


def _get_hour_cols(df: pd.DataFrame) -> dict[int, str]:
    """Return {hour_int: col_name} for H01-H24 columns."""
    mapping = {}
    for c in df.columns:
        m = H_COLS_RE.match(c)
        if m:
            mapping[int(m.group(1))] = c
    return mapping


def _parse_wide(df: pd.DataFrame, filename_station: str | None) -> pd.DataFrame | None:
    """Parse wide-format DataFrame (H01-H24 columns)."""
    hour_map = _get_hour_cols(df)
    if not hour_map:
        return None

    station_col = _find_col(df, STATION_COL_ALIASES)
    param_col = _find_col(df, PARAM_COL_ALIASES)

    # Build date column
    fecha_col = _find_col(df, DATE_COL_ALIASES)
    year_col = _find_col(df, YEAR_COL_ALIASES)
    month_col = _find_col(df, MONTH_COL_ALIASES)
    day_col = _find_col(df, DAY_COL_ALIASES)

    work = df.copy()

    if fecha_col:
        work["_date"] = pd.to_datetime(work[fecha_col], dayfirst=True, errors="coerce")
    elif year_col and month_col and day_col:
        work["_date"] = pd.to_datetime(
            work[year_col].str.strip() + "-" +
            work[month_col].str.strip().str.zfill(2) + "-" +
            work[day_col].str.strip().str.zfill(2),
            errors="coerce",
        )
    else:
        print("  [WARN] No date columns found in wide-format file; skipping.", flush=True)
        return None

    work = work.dropna(subset=["_date"])

    # Station filter
    if station_col:
        work["_station"] = work[station_col].astype(str).str.strip()
    elif filename_station:
        work["_station"] = filename_station
    else:
        print("  [WARN] No station column or filename code; skipping.", flush=True)
        return None

    work = work[work["_station"].isin(TARGET_STATIONS)]
    if work.empty:
        return None

    # Variable
    if param_col:
        work["_variable"] = work[param_col].astype(str).str.strip().str.upper()
    else:
        work["_variable"] = "UNKNOWN"

    # Melt hours
    id_cols = ["_date", "_station", "_variable"]
    h_cols = list(hour_map.values())
    melted = work[id_cols + h_cols].melt(
        id_vars=id_cols, var_name="_hcol", value_name="_value"
    )

    def _to_ts(row: pd.Series) -> pd.Timestamp:
        m = H_COLS_RE.match(row["_hcol"])
        h = int(m.group(1))
        base: pd.Timestamp = row["_date"]
        if h == 24:
            return base + pd.Timedelta(days=1)
        return base.replace(hour=h)

    melted["timestamp"] = melted.apply(_to_ts, axis=1)
    melted["value"] = pd.to_numeric(melted["_value"], errors="coerce")

    result = (
        melted[["timestamp", "_station", "_variable", "value"]]
        .rename(columns={"_station": "station", "_variable": "variable"})
        .dropna(subset=["timestamp"])
        .sort_values(["station", "variable", "timestamp"])
        .reset_index(drop=True)
    )
    return result


def _parse_long(df: pd.DataFrame, filename_station: str | None) -> pd.DataFrame | None:
    """Parse long-format DataFrame (FECHA + HORA + VARIABLE + VALOR)."""
    fecha_col = _find_col(df, DATE_COL_ALIASES)
    hora_col = _find_col(df, HOUR_COL_ALIASES)
    value_col = _find_col(df, VALUE_COL_ALIASES)
    param_col = _find_col(df, PARAM_COL_ALIASES)
    station_col = _find_col(df, STATION_COL_ALIASES)

    if not fecha_col or not hora_col or not value_col:
        return None

    work = df.copy()
    work["_date"] = pd.to_datetime(work[fecha_col], dayfirst=True, errors="coerce")
    work["_hora"] = pd.to_numeric(work[hora_col], errors="coerce")
    work = work.dropna(subset=["_date", "_hora"])

    # Station
    if station_col:
        work["_station"] = work[station_col].astype(str).str.strip()
    elif filename_station:
        work["_station"] = filename_station
    else:
        return None

    work = work[work["_station"].isin(TARGET_STATIONS)]
    if work.empty:
        return None

    # Variable
    if param_col:
        work["_variable"] = work[param_col].astype(str).str.strip().str.upper()
    else:
        work["_variable"] = "UNKNOWN"

    def _to_ts(row: pd.Series) -> pd.Timestamp:
        h = int(row["_hora"])
        base: pd.Timestamp = row["_date"]
        if h == 24:
            return base + pd.Timedelta(days=1)
        if h == 0:
            return base
        return base.replace(hour=h)

    work["timestamp"] = work.apply(_to_ts, axis=1)
    work["value"] = pd.to_numeric(work[value_col], errors="coerce")

    result = (
        work[["timestamp", "_station", "_variable", "value"]]
        .rename(columns={"_station": "station", "_variable": "variable"})
        .dropna(subset=["timestamp"])
        .sort_values(["station", "variable", "timestamp"])
        .reset_index(drop=True)
    )
    return result


def _parse_dataframe(df: pd.DataFrame, filename_station: str | None) -> pd.DataFrame | None:
    if _has_hour_cols(df):
        return _parse_wide(df, filename_station)
    return _parse_long(df, filename_station)


# ---------------------------------------------------------------------------
# Main ingestion
# ---------------------------------------------------------------------------

def ingest_drop_folder(drop_dir: Path) -> pd.DataFrame:
    """Read all files in drop_dir and return a unified long DataFrame."""
    files = sorted(
        p for p in drop_dir.iterdir()
        if p.is_file() and not p.name.startswith(".")
    )
    if not files:
        print(f"[ERROR] No files found in {drop_dir}", flush=True)
        sys.exit(1)

    print(f"\nFiles found in official_drop/: {len(files)}", flush=True)
    for f in files:
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}  ({size_kb:.1f} KB)", flush=True)

    all_parts: list[pd.DataFrame] = []
    for path in files:
        print(f"\nProcessing: {path.name}", flush=True)
        filename_station = _extract_station_from_path(path)
        try:
            sheets = _read_file(path)
        except Exception as exc:
            print(f"  [WARN] Could not read {path.name}: {exc}", flush=True)
            continue

        for i, df in enumerate(sheets):
            label = f"sheet {i}" if len(sheets) > 1 else "single"
            parsed = _parse_dataframe(df, filename_station)
            if parsed is None or parsed.empty:
                print(f"  [{label}] No target-station data detected; skipped.", flush=True)
                continue
            stations_found = parsed["station"].unique().tolist()
            rows = len(parsed)
            print(f"  [{label}] Parsed {rows} rows. Stations: {stations_found}", flush=True)
            all_parts.append(parsed)

    if not all_parts:
        print("\n[ERROR] No usable data extracted from any file.", flush=True)
        sys.exit(1)

    combined = pd.concat(all_parts, ignore_index=True)
    # Deduplicate: keep last value for same (station, variable, timestamp)
    combined = (
        combined
        .sort_values(["station", "variable", "timestamp"])
        .drop_duplicates(subset=["station", "variable", "timestamp"], keep="last")
        .reset_index(drop=True)
    )
    return combined


def write_station_raw(combined: pd.DataFrame, station: str, out_dir: Path) -> Path:
    sub = combined[combined["station"] == station].copy()
    if sub.empty:
        print(f"\n[WARN] No data for station {station}; output not written.", flush=True)
        return None

    sub = sub.sort_values(["variable", "timestamp"]).reset_index(drop=True)
    out_path = out_dir / f"rvvcca_raw_{station}_hourly.csv"
    sub[["timestamp", "variable", "value"]].to_csv(out_path, index=False)

    variables = sub["variable"].unique().tolist()
    n_rows = len(sub)
    ts_min = sub["timestamp"].min()
    ts_max = sub["timestamp"].max()
    n_missing = int(sub["value"].isna().sum())
    pct_missing = 100.0 * n_missing / n_rows if n_rows > 0 else float("nan")

    print(f"\nStation {station} -> {out_path.name}", flush=True)
    print(f"  Rows: {n_rows}", flush=True)
    print(f"  Variables: {variables}", flush=True)
    print(f"  Range: {ts_min} to {ts_max}", flush=True)
    print(f"  Missing values: {n_missing} ({pct_missing:.1f}%)", flush=True)
    return out_path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not DROP_DIR.exists():
        print(f"[ERROR] Drop folder not found: {DROP_DIR}", flush=True)
        sys.exit(1)

    combined = ingest_drop_folder(DROP_DIR)

    for station in sorted(TARGET_STATIONS):
        write_station_raw(combined, station, OUT_DIR)

    print("\n[DONE] Raw reconstruction complete.", flush=True)


if __name__ == "__main__":
    main()
