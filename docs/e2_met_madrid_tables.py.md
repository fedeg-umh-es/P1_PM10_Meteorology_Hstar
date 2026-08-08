---
title: "e2_met_madrid_tables.py"
categoria: "PERSONAL"
sub_area: "Personal"
tags:
  - personal
  - recurso
---

# 📌 e2_met_madrid_tables.py

## 🧠 Síntesis y Puntos Clave (TDAH-friendly)
- **from __future__** import annotations
- import argparse
- **import pandas** as pd
- **from e2_met_madrid_shared** import ensure_results_dirs, load_json_config
- **def main()** -> None:
- **parser =** argparse.ArgumentParser(description="Build manuscript-ready E2-MET tables.")
- parser.add_argument("--config", default="code/e2_met_madrid_config.json")

## 📄 Contenido Detallado / Referencia
#!/usr/bin/env python3
from __future__ import annotations

import argparse

import pandas as pd

from e2_met_madrid_shared import ensure_results_dirs, load_json_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Build manuscript-ready E2-MET tables.")
    parser.add_argument("--config", default="code/e2_met_madrid_config.json")
    args = parser.parse_args()

    config = load_json_config(args.config)
    paths = ensure_results_dirs(config["results_dir"])

    metrics = pd.read_csv(paths["metrics"] / "metrics_all_models.csv")
    hstar = pd.read_csv(paths["metrics"] / "hstar_summary.csv")
    dm = pd.read_csv(paths["stats"] / "dm_lags_meteo_vs_lags_only.csv")

    metrics.to_csv(paths["manuscript_tables"] / "table_metrics_long.csv", index=False)
    hstar.to_csv(paths["manuscript_tables"] / "table_hstar_summary.csv", index=False)
    dm.to_csv(paths["manuscript_tables"] / "table_dm_lags_meteo_vs_lags_only.csv", index=False)

    xgb = metrics[metrics["model"] == "xgboost_direct"].copy()
    wide = xgb.pivot_table(
        index=["model", "condition"],
        columns="horizon",
        values=["rmse", "mae", "skill_rmse_vs_persistence", "skill_mae_vs_persistence"],
    )
    wide.columns = [f"{metric}_h{horizon}" for metric, horizon in wide.columns]
    wide = wide.reset_index()
    wide.to_csv(paths["manuscript_tables"] / "table_xgboost_horizon_wide.csv", index=False)

    lag = xgb[xgb["condition"] == "lags_only"][
        ["horizon", "rmse", "mae", "skill_rmse_vs_persistence", "skill_mae_vs_persistence"]
    ].rename(
        columns={
            "rmse": "rmse_lags_only",
            "mae": "mae_lags_only",
            "skill_rmse_vs_persistence": "skill_rmse_lags_only",
            "skill_mae_vs_persistence": "skill_mae_lags_only",
        }
    )
    meteo = xgb[xgb["condition"] == "lags_meteo"][
        ["horizon", "rmse", "mae", "skill_rmse_vs_persistence", "skill_mae_vs_persistence"]
    ].rename(
        columns={
            "rmse": "rmse_lags_meteo",
            "mae": "mae_lags_meteo",
            "skill_rmse_vs_persistence": "skill_rmse_lags_meteo",
            "skill_mae_vs_persistence": "skill_mae_lags_meteo",
        }
    )
    delta = lag.merge(meteo, on="horizon", how="inner")
    delta["delta_rmse_meteo_minus_lags"] = delta["rmse_lags_meteo"] - delta["rmse_lags_only"]
    delta["delta_mae_meteo_minus_lags"] = delta["mae_lags_meteo"] - delta["mae_lags_only"]
    delta["delta_skill_rmse_meteo_minus_lags"] = delta["skill_rmse_lags_meteo"] - delta["skill_rmse_lags_only"]
    delta["delta_skill_mae_meteo_minus_lags"] = delta["skill_mae_lags_meteo"] - delta["skill_mae_lags_only"]
    delta.to_csv(paths["manuscript_tables"] / "table_delta_lags_meteo_vs_lags_only.csv", index=False)


if __name__ == "__main__":
    main()


---
*Procesado automáticamente por Antigravity (Smart Router)*
