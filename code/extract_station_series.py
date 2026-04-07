#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def detect_separator(csv_path: Path) -> str:
    with csv_path.open("r", encoding="utf-8-sig", errors="ignore") as f:
        first_line = f.readline()
    return ";" if first_line.count(";") >= first_line.count(",") else ","


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.replace("\ufeff", "").strip() for c in df.columns]
    return df


def extract_series(
    df: pd.DataFrame,
    station: str,
    pollutant: str,
    date_col: str = "Fecha",
    station_col: str = "Estacion",
) -> pd.Series:
    required = [date_col, station_col, pollutant]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    series = (
        df[df[station_col].astype(str).str.strip() == station]
        .sort_values(date_col)
        [[date_col, pollutant]]
        .dropna(subset=[pollutant])
        .drop_duplicates(subset=[date_col], keep="last")
        .set_index(date_col)[pollutant]
        .astype(float)
    )

    series.name = pollutant
    return series


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrae serie limpia por estacion/contaminante."
    )
    parser.add_argument("--input", required=True, help="Ruta al CSV de entrada.")
    parser.add_argument("--station", default="Politecnico", help="Nombre de estacion.")
    parser.add_argument("--pollutant", default="PM10", help="Contaminante (ej. PM10).")
    parser.add_argument("--city", default="Valencia", help="Nombre de ciudad para output.")
    parser.add_argument(
        "--output-dir", default="data_processed", help="Directorio de salida."
    )
    parser.add_argument(
        "--sep",
        default="auto",
        help="Separador CSV (auto, ; o ,).",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    sep = detect_separator(input_path) if args.sep == "auto" else args.sep
    df = pd.read_csv(input_path, sep=sep, encoding="utf-8-sig")
    df = normalize_columns(df)

    series = extract_series(df=df, station=args.station, pollutant=args.pollutant)

    station_clean = args.station.replace(" ", "_")
    out_path = output_dir / f"{args.pollutant}_{args.city}_{station_clean}.csv"
    series.to_csv(out_path, index=True)

    print(f"OK -> {out_path}")
    print(f"Filas: {len(series)}")
    if not series.empty:
        print(f"Rango: {series.index.min().date()} a {series.index.max().date()}")


if __name__ == "__main__":
    main()
