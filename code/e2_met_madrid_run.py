#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import pandas as pd

from e2_met_madrid_shared import (
    attach_skill_against_persistence,
    derive_hstar_from_metrics,
    diebold_mariano_test,
    ensure_results_dirs,
    generate_shared_origins_file,
    load_experiment_dataset,
    load_json_config,
    run_backtest,
    compute_metrics,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run E2-MET Madrid PM10 rolling-origin experiment.")
    parser.add_argument("--config", default="code/e2_met_madrid_config.json")
    parser.add_argument(
        "--condition",
        choices=["lags_only", "lags_meteo", "all"],
        default="all",
        help="Which condition to run.",
    )
    parser.add_argument("--max-origins", type=int, default=0, help="Optional cap for smoke tests.")
    args = parser.parse_args()

    config = load_json_config(args.config)
    paths = ensure_results_dirs(config["results_dir"])
    df = load_experiment_dataset(config)
    origins_df = generate_shared_origins_file(df=df, config=config, output_path=paths["base"] / "rolling_origins.csv")

    conditions = ["lags_only", "lags_meteo"] if args.condition == "all" else [args.condition]
    all_predictions: list[pd.DataFrame] = []
    run_metadata: dict[str, object] = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": config["config_path"],
        "dataset_path": config["dataset_path"],
        "conditions_run": conditions,
        "n_origins": int(len(origins_df)),
        "horizon_max": int(config["horizon_max"]),
    }

    for condition in conditions:
        include_references = condition == conditions[0]
        preds = run_backtest(
            config=config,
            condition=condition,
            include_references=include_references,
            max_origins=args.max_origins if args.max_origins > 0 else None,
        )
        preds_path = paths["predictions"] / f"predictions_{condition}.csv"
        preds.to_csv(preds_path, index=False)
        all_predictions.append(preds)

    if all_predictions:
        predictions = pd.concat(all_predictions, ignore_index=True)
    else:
        predictions = pd.DataFrame(columns=["origin", "forecast_timestamp", "horizon", "condition", "model", "y_true", "y_pred"])

    combined_path = paths["predictions"] / "predictions_all_models.csv"
    predictions.to_csv(combined_path, index=False)

    metrics = compute_metrics(predictions)
    metrics = attach_skill_against_persistence(metrics)
    metrics_path = paths["metrics"] / "metrics_all_models.csv"
    metrics.to_csv(metrics_path, index=False)

    hstar = derive_hstar_from_metrics(metrics=metrics, horizon_max=int(config["horizon_max"]))
    hstar_path = paths["metrics"] / "hstar_summary.csv"
    hstar.to_csv(hstar_path, index=False)

    dm_rows = []
    if args.condition == "all":
        preds_lags = predictions[
            (predictions["condition"] == "lags_only") & (predictions["model"] == "xgboost_direct")
        ].copy()
        preds_meteo = predictions[
            (predictions["condition"] == "lags_meteo") & (predictions["model"] == "xgboost_direct")
        ].copy()
        for horizon in config["dm_horizons"]:
            dm_rows.append(
                diebold_mariano_test(
                    preds_a=preds_lags,
                    preds_b=preds_meteo,
                    horizon=int(horizon),
                    loss=str(config["dm_loss"]),
                )
            )
    dm_df = pd.DataFrame(dm_rows)
    dm_path = paths["stats"] / "dm_lags_meteo_vs_lags_only.csv"
    dm_df.to_csv(dm_path, index=False)

    snapshot_path = paths["base"] / "config_snapshot.json"
    with snapshot_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)

    run_metadata["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    run_metadata["prediction_rows"] = int(len(predictions))
    run_metadata["metrics_rows"] = int(len(metrics))
    run_metadata["dm_rows"] = int(len(dm_df))
    with (paths["base"] / "run_metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(run_metadata, handle, indent=2)


if __name__ == "__main__":
    main()
