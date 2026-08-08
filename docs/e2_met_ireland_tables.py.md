---
title: "e2_met_ireland_tables.py"
categoria: "PERSONAL"
sub_area: "Personal"
tags:
  - personal
  - recurso
---

# 📌 e2_met_ireland_tables.py

## 🧠 Síntesis y Puntos Clave (TDAH-friendly)
- """
- e2_met_ireland_tables.py
- **Builds manuscript-ready** tables from the Ireland E2-MET experiment results.
- Outputs (in results_dir/manuscript_tables/):
- **table_metrics_long.csv —** full metrics table (long format)
- **table_station_hstar_summary.csv —** H* per station (long format)
- **table_station_hstar_wide.csv —** H* pivoted: station × condition, with ΔH*

## 📄 Contenido Detallado / Referencia
#!/usr/bin/env python3
"""
e2_met_ireland_tables.py

Builds manuscript-ready tables from the Ireland E2-MET experiment results.

Outputs (in results_dir/manuscript_tables/):
  table_metrics_long.csv             — full metrics table (long format)
  table_station_hstar_summary.csv    — H* per station (long format)
  table_station_hstar_wide.csv       — H* pivoted: station × condition, with ΔH*
  table_xgboost_horizon_wide.csv     — RMSE/MAE/Skill pivoted per station × condition × horizon
  table_delta_skill_meteo_vs_lags.csv — ΔSkill(h) = skill_meteo - skill_lags per station
  table_dm_lags_meteo_vs_lags_only.csv — DM-HLN results per station × horizon

Usage:
  python3 code/e2_met_ireland_tables.py --config code/e2_met_ireland_config.json
"""

from __future__ import annotations

import argparse

import pandas as pd

from e2_met_madrid_shared import ensure_results_dirs, load_json_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Build manuscript-ready E2-MET Ireland tables.")
    parser.add_argument("--config", default="code/e2_met_ireland_config.json")
    args = parser.parse_args()

    config = load_json_config(args.config)
    paths = ensure_results_dirs(config["results_dir"])

    metrics = pd.read_csv(paths["metrics"] / "metrics_all_models.csv")
    hstar = pd.read_csv(paths["metrics"] / "hstar_summary.csv")
    dm = pd.read_csv(paths["stats"] / "dm_lags_meteo_vs_lags_only.csv")

    # ── raw copies ─────────────────────────────────────────────────────────────
    metrics.to_csv(paths["manuscript_tables"] / "table_metrics_long.csv", index=False)
    hstar.to_csv(paths["manuscript_tables"] / "table_station_hstar_summary.csv", index=False)
    dm.to_csv(paths["manuscript_tables"] / "table_dm_lags_meteo_vs_lags_only.csv", index=False)

    # ── XGBoost wide table: station × condition × horizon ──────────────────────
    xgb = metrics[metrics["model"] == "xgboost_direct"].copy()
    if not xgb.empty:
        wide = xgb.pivot_table(
            index=["station", "model", "condition"],
            columns="horizon",
            values=["rmse", "mae", "skill_rmse_vs_persistence", "skill_mae_vs_persistence"],
        )
        wide.columns = [f"{metric}_h{horizon}" for metric, horizon in wide.columns]
        wide = wide.reset_index()
        wide.to_csv(paths["manuscript_tables"] / "table_xgboost_horizon_wide.csv", index=False)
    else:
        pd.DataFrame().to_csv(
            paths["manuscript_tables"] / "table_xgboost_horizon_wide.csv", index=False
        )

    # ── ΔSkill table: lags_meteo − lags_only per station × horizon ─────────────
    metric_cols = ["rmse", "mae", "skill_rmse_vs_persistence", "skill_mae_vs_persistence"]
    lag_rename = {c: f"{c}_lags_only" for c in metric_cols}
    meteo_rename = {c: f"{c}_lags_meteo" for c in metric_cols}

    lag = (
        xgb[xgb["condition"] == "lags_only"][["station", "horizon"] + metric_cols]
        .rename(columns=lag_rename)
    )
    meteo = (
        xgb[xgb["condition"] == "lags_meteo"][["station", "horizon"] + metric_cols]
        .rename(columns=meteo_rename)
    )
    if not lag.empty and not meteo.empty:
        delta = lag.merge(meteo, on=["station", "horizon"], how="inner")
        delta["delta_rmse_meteo_minus_lags"] = (
            delta["rmse_lags_meteo"] - delta["rmse_lags_only"]
        )
        delta["delta_mae_meteo_minus_lags"] = (
            delta["mae_lags_meteo"] - delta["mae_lags_only"]
        )
        delta["delta_skill_rmse_meteo_minus_lags"] = (
            delta["skill_rmse_vs_persistence_lags_meteo"]
            - delta["skill_rmse_vs_persistence_lags_only"]
        )
        delta["delta_skill_mae_meteo_minus_lags"] = (
            delta["skill_mae_vs_persistence_lags_meteo"]
            - delta["skill_mae_vs_persistence_lags_only"]
        )
        delta = delta.sort_values(["station", "horizon"]).reset_index(drop=True)
        delta.to_csv(
            paths["manuscript_tables"] / "table_delta_skill_meteo_vs_lags.csv", index=False
        )
    else:
        pd.DataFrame().to_csv(
            paths["manuscript_tables"] / "table_delta_skill_meteo_vs_lags.csv", index=False
        )

    # ── H* wide table: station × condition (lags_only / lags_meteo) + ΔH* ──────
    hstar_xgb = hstar[hstar["model"] == "xgboost_direct"].copy()
    if not hstar_xgb.empty:
        hstar_wide = hstar_xgb.pivot_table(
            index="station",
            columns="condition",
            values=["H_star_relax", "H_star_strict"],
        )
        hstar_wide.columns = [f"{metric}_{cond}" for metric, cond in hstar_wide.columns]
        hstar_wide = hstar_wide.reset_index()

        if (
            "H_star_relax_lags_meteo" in hstar_wide.columns
            and "H_star_relax_lags_only" in hstar_wide.columns
        ):
            hstar_wide["delta_H_star_relax"] = (
                hstar_wide["H_star_relax_lags_meteo"] - hstar_wide["H_star_relax_lags_only"]
            )
        if (
            "H_star_strict_lags_meteo" in hstar_wide.columns
            and "H_star_strict_lags_only" in hstar_wide.columns
        ):
            hstar_wide["delta_H_star_strict"] = (
                hstar_wide["H_star_strict_lags_meteo"] - hstar_wide["H_star_strict_lags_only"]
            )

        hstar_wide.to_csv(
            paths["manuscript_tables"] / "table_station_hstar_wide.csv", index=False
        )
    else:
        pd.DataFrame().to_csv(
            paths["manuscript_tables"] / "table_station_hstar_wide.csv", index=False
        )

    print("Manuscript tables written to:", paths["manuscript_tables"])
    for f in sorted(paths["manuscript_tables"].glob("*.csv")):
        rows = pd.read_csv(f).shape[0]
        print(f"  {f.name}  ({rows} rows)")


if __name__ == "__main__":
    main()


---
*Procesado automáticamente por Antigravity (Smart Router)*
