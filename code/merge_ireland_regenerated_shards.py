#!/usr/bin/env python3
"""
merge_ireland_regenerated_shards.py

The full 8-station Ireland regeneration run was executed as 8 parallel,
single-station subprocess invocations of the unmodified
code/e2_met_ireland_run.py (identical config/script per station, only
--station and a per-shard results_dir differ), to fit within available
session time using 4 CPU cores. This script merges the 8 shard result
directories into one combined results/e2_met_ireland_pm10_regenerated/
directory, exactly as a single non-parallel invocation across all 8
stations would have produced. No experiment methodology, parameters, or
per-row values are altered by this merge -- it is pure concatenation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SHARD_ROOT = REPO / "results" / "_ireland_regen_shards"
OUT_DIR = REPO / "results" / "e2_met_ireland_pm10_regenerated"

STATIONS = [
    "Birr co offlay", "Dublin Airport", "Dundalk Co Louth", "Pearse street dublin",
    "Ringsend dublin", "edenderry co offlay", "henry street Limerick", "porrlaoise co laois",
]


def main() -> None:
    for sub in ("predictions", "metrics", "stats"):
        (OUT_DIR / sub).mkdir(parents=True, exist_ok=True)

    all_preds = []
    all_metrics = []
    all_dm = []
    metadata_shards = []

    for station in STATIONS:
        safe = station.replace(" ", "_").replace("/", "-")
        shard_dir = SHARD_ROOT / safe
        if not shard_dir.exists():
            raise FileNotFoundError(f"Missing shard output for station: {station} ({shard_dir})")

        preds_path = shard_dir / "predictions" / "predictions_all_models.csv"
        preds = pd.read_csv(preds_path)
        all_preds.append(preds)
        # copy per-station-condition prediction files through unchanged
        for f in (shard_dir / "predictions").glob("predictions_*.csv"):
            if f.name != "predictions_all_models.csv":
                (OUT_DIR / "predictions" / f.name).write_bytes(f.read_bytes())

        metrics_path = shard_dir / "metrics" / "metrics_all_models.csv"
        all_metrics.append(pd.read_csv(metrics_path))

        dm_path = shard_dir / "stats" / "dm_lags_meteo_vs_lags_only.csv"
        if dm_path.exists():
            dm_df = pd.read_csv(dm_path)
            if not dm_df.empty:
                all_dm.append(dm_df)

        with open(shard_dir / "run_metadata.json") as f:
            metadata_shards.append(json.load(f))

    combined_preds = pd.concat(all_preds, ignore_index=True).sort_values(
        ["station", "model", "condition", "origin", "horizon"]
    ).reset_index(drop=True)
    combined_preds.to_csv(OUT_DIR / "predictions" / "predictions_all_models.csv", index=False)

    combined_metrics = pd.concat(all_metrics, ignore_index=True).sort_values(
        ["station", "model", "condition", "horizon"]
    ).reset_index(drop=True)
    combined_metrics.to_csv(OUT_DIR / "metrics" / "metrics_all_models.csv", index=False)

    # Recompute hstar summary (identical logic to e2_met_ireland_run.py's
    # derive_hstar_ireland) directly on the combined metrics for consistency.
    import numpy as np

    def derive_hstar(metrics: pd.DataFrame, horizon_max: int) -> pd.DataFrame:
        rows = []
        for (station, condition, model), group in metrics.groupby(["station", "condition", "model"]):
            if model == "persistence":
                rows.append({"station": station, "condition": condition, "model": model,
                              "H": horizon_max, "H_star_relax": 0, "H_star_strict": 0})
                continue
            skill = (
                group.set_index("horizon")["skill_rmse_vs_persistence"]
                .reindex(range(1, horizon_max + 1)).to_numpy()
            )
            pos = np.where(skill > 0)[0]
            h_relax = int(pos.max() + 1) if len(pos) > 0 else 0
            best = current = 0
            for value in skill:
                if pd.notna(value) and value > 0:
                    current += 1
                    best = max(best, current)
                else:
                    current = 0
            rows.append({"station": station, "condition": condition, "model": model,
                          "H": horizon_max, "H_star_relax": h_relax, "H_star_strict": int(best)})
        return pd.DataFrame(rows).sort_values(["station", "model", "condition"]).reset_index(drop=True)

    hstar = derive_hstar(combined_metrics, horizon_max=24)
    hstar.to_csv(OUT_DIR / "metrics" / "hstar_summary.csv", index=False)

    if all_dm:
        combined_dm = pd.concat(all_dm, ignore_index=True)
    else:
        combined_dm = pd.DataFrame(
            columns=["station", "horizon", "n", "dm_stat", "p_value", "mean_loss_diff", "favours"]
        )
    combined_dm.to_csv(OUT_DIR / "stats" / "dm_lags_meteo_vs_lags_only.csv", index=False)

    combined_metadata = {
        "experiment_label": "REGENERATED -- NOT ORIGINAL RUN",
        "execution_strategy": (
            "8 parallel single-station subprocess invocations of the unmodified "
            "code/e2_met_ireland_run.py (4 concurrent, identical config/script per "
            "station; only --station and a per-shard results_dir differ), merged "
            "post-hoc by code/merge_ireland_regenerated_shards.py."
        ),
        "started_at_utc": min(m["started_at_utc"] for m in metadata_shards),
        "finished_at_utc": max(m["finished_at_utc"] for m in metadata_shards),
        "config_path": "code/e2_met_ireland_config.json (portable copy: dataset_path/results_dir only)",
        "dataset_path": str(REPO / "data_processed" / "ireland_pm10_meteorology_hourly.csv"),
        "conditions_run": ["lags_only", "lags_meteo"],
        "stations": STATIONS,
        "horizon_max": 24,
        "max_origins_cap": None,
        "prediction_rows": int(len(combined_preds)),
        "metrics_rows": int(len(combined_metrics)),
        "dm_rows": int(len(combined_dm)),
        "per_station_metadata": metadata_shards,
    }
    with open(OUT_DIR / "run_metadata.json", "w") as f:
        json.dump(combined_metadata, f, indent=2)

    with open(REPO / "code" / "e2_met_ireland_config.json") as f:
        base_cfg = json.load(f)
    snapshot = dict(base_cfg)
    snapshot["dataset_path"] = str(REPO / "data_processed" / "ireland_pm10_meteorology_hourly.csv")
    snapshot["results_dir"] = str(OUT_DIR)
    with open(OUT_DIR / "config_snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"Merged {len(STATIONS)} station shards into {OUT_DIR}")
    print(f"  predictions: {len(combined_preds)} rows")
    print(f"  metrics: {len(combined_metrics)} rows")
    print(f"  hstar: {len(hstar)} rows")
    print(f"  dm: {len(combined_dm)} rows")


if __name__ == "__main__":
    main()
