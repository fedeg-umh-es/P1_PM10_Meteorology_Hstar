"""P1 audit — Phase 3: origin accounting, reconstructed from existing
row-level predictions (results/e2_met_madrid_pm10/predictions/predictions_all_models.csv
and results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv).

Read-only. Does not touch canonical results.
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent

MADRID_PRED = REPO / "results/e2_met_madrid_pm10/predictions/predictions_all_models.csv"
IRELAND_PRED = REPO / "results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv"


def origin_accounting_madrid() -> pd.DataFrame:
    df = pd.read_csv(MADRID_PRED, parse_dates=["origin", "forecast_timestamp"])
    rows = []
    for (condition, model), g in df.groupby(["condition", "model"]):
        origins = g["origin"].unique()
        rows.append(
            {
                "station": "Madrid",
                "condition": condition,
                "model": model,
                "n_origins": len(origins),
                "first_origin": g["origin"].min(),
                "last_origin": g["origin"].max(),
                "n_rows": len(g),
                "horizons_present": sorted(g["horizon"].unique().tolist()),
                "n_horizons": g["horizon"].nunique(),
            }
        )
    return pd.DataFrame(rows)


def origin_accounting_ireland() -> pd.DataFrame:
    df = pd.read_csv(IRELAND_PRED, parse_dates=["origin", "forecast_timestamp"])
    station_col = "station" if "station" in df.columns else None
    rows = []
    group_cols = (["station"] if station_col else []) + ["condition", "model"]
    for keys, g in df.groupby(group_cols):
        if not isinstance(keys, tuple):
            keys = (keys,)
        rec = dict(zip(group_cols, keys))
        origins = g["origin"].unique()
        rec.update(
            {
                "n_origins": len(origins),
                "first_origin": g["origin"].min(),
                "last_origin": g["origin"].max(),
                "n_rows": len(g),
                "n_horizons": g["horizon"].nunique(),
            }
        )
        rows.append(rec)
    return pd.DataFrame(rows)


def dm_pair_counts_madrid() -> pd.DataFrame:
    df = pd.read_csv(MADRID_PRED, parse_dates=["origin", "forecast_timestamp"])
    lags_only = df[(df["condition"] == "lags_only") & (df["model"] == "xgboost_direct")]
    lags_meteo = df[(df["condition"] == "lags_meteo") & (df["model"] == "xgboost_direct")]
    rows = []
    for h in [1, 6, 12, 24]:
        a = lags_only[lags_only["horizon"] == h][["origin", "forecast_timestamp", "y_true", "y_pred"]]
        b = lags_meteo[lags_meteo["horizon"] == h][["origin", "forecast_timestamp", "y_pred"]]
        merged = a.merge(b, on=["origin", "forecast_timestamp"], suffixes=("_only", "_meteo"))
        merged = merged.dropna(subset=["y_true", "y_pred_only", "y_pred_meteo"])
        rows.append({"horizon": h, "n_paired": len(merged),
                      "n_lags_only_rows": len(a), "n_lags_meteo_rows": len(b)})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    madrid_acc = origin_accounting_madrid()
    ireland_acc = origin_accounting_ireland()
    dm_counts = dm_pair_counts_madrid()

    madrid_acc.to_csv(OUT / "origin_accounting_madrid.csv", index=False)
    ireland_acc.to_csv(OUT / "origin_accounting_ireland.csv", index=False)
    dm_counts.to_csv(OUT / "dm_pair_counts_madrid.csv", index=False)

    print("=== Madrid origin accounting ===")
    print(madrid_acc.to_string(index=False))
    print()
    print("=== Ireland origin accounting (by station/condition/model) ===")
    print(ireland_acc.to_string(index=False))
    print()
    print("=== Madrid DM pair counts (manuscript claims n=354,356,346,354 at h=1,6,12,24) ===")
    print(dm_counts.to_string(index=False))
