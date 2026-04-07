#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normaliza una serie diaria y crea malla regular."
    )
    parser.add_argument("--input", required=True, help="CSV de entrada.")
    parser.add_argument("--date-col", default="Fecha", help="Columna fecha.")
    parser.add_argument("--value-col", default="PM10", help="Columna valor.")
    parser.add_argument("--city", required=True, help="Ciudad.")
    parser.add_argument("--station-id", required=True, help="ID/nombre de estación.")
    parser.add_argument("--output-dir", default="data_processed", help="Directorio salida.")
    parser.add_argument(
        "--output-name",
        default="",
        help="Nombre de salida opcional.",
    )
    args = parser.parse_args()

    in_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)
    df.columns = [c.replace("\ufeff", "").strip() for c in df.columns]

    if args.date_col not in df.columns or args.value_col not in df.columns:
        raise ValueError(
            f"Faltan columnas requeridas: {args.date_col}, {args.value_col}"
        )

    df[args.date_col] = pd.to_datetime(df[args.date_col], errors="coerce")
    df[args.value_col] = pd.to_numeric(df[args.value_col], errors="coerce")

    df = (
        df[[args.date_col, args.value_col]]
        .dropna(subset=[args.date_col])
        .sort_values(args.date_col)
        .drop_duplicates(subset=[args.date_col], keep="last")
        .rename(columns={args.date_col: "date", args.value_col: "value"})
    )
    df["city"] = args.city
    df["station_id"] = args.station_id

    full_idx = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    y = df.set_index("date")["value"].reindex(full_idx)

    df_out = y.rename("value").reset_index().rename(columns={"index": "date"})
    df_out["city"] = args.city
    df_out["station_id"] = args.station_id
    df_out["is_missing"] = df_out["value"].isna().astype(int)

    output_name = (
        args.output_name
        if args.output_name
        else f"{args.value_col}_{args.city}_{args.station_id}_daily_regular.csv"
    )
    out_path = out_dir / output_name
    df_out.to_csv(out_path, index=False)

    print(f"OK -> {out_path}")
    print(f"Filas: {len(df_out)}")
    print(f"Missing: {int(df_out['is_missing'].sum())}")
    print(f"Rango: {df_out['date'].min()} a {df_out['date'].max()}")


if __name__ == "__main__":
    main()
