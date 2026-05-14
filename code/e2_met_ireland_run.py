#!/usr/bin/env python3
"""
e2_met_ireland_run.py

Rolling-origin PM10 forecasting experiment for Ireland — multi-station variant.

Conditions:
  - lags_only:  PM10 lags + calendar features
  - lags_meteo: PM10 lags + calendar features + meteorology

Baselines:
  - persistence
  - SARIMA (disabled by default; set include_sarima=true in config to enable)

Usage:
  python3 code/e2_met_ireland_run.py --config code/e2_met_ireland_config.json --condition all
  python3 code/e2_met_ireland_run.py --config code/e2_met_ireland_config.json --condition all --max-origins 5
  python3 code/e2_met_ireland_run.py --config code/e2_met_ireland_config.json --station "Dublin Airport"
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from e2_met_madrid_shared import (
    diebold_mariano_test,
    ensure_results_dirs,
    fit_xgboost_direct,
    load_json_config,
    predict_persistence,
    predict_sarima,
    predict_xgboost_direct,
)
from rolling_origin import generate_rolling_origins, get_test_window, get_train_window


# ── data loading ───────────────────────────────────────────────────────────────

def load_ireland_dataset(config: dict[str, Any]) -> pd.DataFrame:
    dataset_path = Path(config["dataset_path"]).expanduser().resolve()
    timestamp_col = config["timestamp_col"]
    station_col = config["station_col"]
    df = pd.read_csv(dataset_path, parse_dates=[timestamp_col])
    df = df.sort_values([station_col, timestamp_col]).reset_index(drop=True)
    return df


# ── per-station backtest ───────────────────────────────────────────────────────

def run_backtest_for_station(
    station_df: pd.DataFrame,
    station: str,
    config: dict[str, Any],
    condition: str,
    include_references: bool = True,
    max_origins: int | None = None,
) -> pd.DataFrame:
    """Rolling-origin backtest for a single station.

    Mirrors the logic of e2_met_madrid_shared.run_backtest but accepts a
    pre-filtered station DataFrame and tags each row with the station name.
    """
    timestamp_col = config["timestamp_col"]
    target_col = config["target_col"]
    horizon_max = int(config["horizon_max"])
    train_start = config["train_start"]

    # Dedup within station (safety; build script should have resolved these)
    df = (
        station_df
        .sort_values(timestamp_col)
        .drop_duplicates(subset=[timestamp_col], keep="last")
        .reset_index(drop=True)
    )

    origins = generate_rolling_origins(
        df=df,
        timestamp_col=timestamp_col,
        test_start=config["test_start"],
        test_end=config["test_end"],
        horizon_max=horizon_max + 1,
    )
    origins = origins[:: int(config["origin_stride_hours"])]
    if max_origins is not None:
        origins = origins[:max_origins]

    if not origins:
        print(f"    [{station}] No valid origins for condition={condition}")
        return pd.DataFrame(
            columns=["station", "origin", "forecast_timestamp", "horizon",
                     "condition", "model", "y_true", "y_pred"]
        )

    rows: list[dict[str, Any]] = []

    for origin in origins:
        train_df = get_train_window(
            df=df,
            origin=origin,
            timestamp_col=timestamp_col,
            train_start=train_start,
        )
        test_df = get_test_window(
            df=df,
            origin=origin,
            horizon_max=horizon_max + 1,
            timestamp_col=timestamp_col,
        )

        if len(train_df) < int(config["min_train_rows"]):
            continue
        if len(test_df) < horizon_max + 1:
            continue

        persistence_preds = predict_persistence(train_df=train_df, config=config)
        sarima_preds = predict_sarima(train_df=train_df, config=config)

        model, medians, usable_features = fit_xgboost_direct(
            train_df=train_df,
            config=config,
            condition=condition,
        )
        model_preds = predict_xgboost_direct(
            model=model,
            train_df=train_df,
            origin_row_df=test_df.iloc[:1].copy(),
            origin=origin,
            config=config,
            condition=condition,
            medians=medians,
            usable_features=usable_features,
        )

        for horizon in range(1, horizon_max + 1):
            y_true = pd.to_numeric(
                pd.Series([test_df[target_col].iloc[horizon]]), errors="coerce"
            ).iloc[0]
            forecast_ts = pd.Timestamp(test_df[timestamp_col].iloc[horizon])

            if include_references:
                rows.append({
                    "station": station,
                    "origin": pd.Timestamp(origin),
                    "forecast_timestamp": forecast_ts,
                    "horizon": horizon,
                    "condition": "reference",
                    "model": "persistence",
                    "y_true": y_true,
                    "y_pred": persistence_preds[horizon],
                })
                rows.append({
                    "station": station,
                    "origin": pd.Timestamp(origin),
                    "forecast_timestamp": forecast_ts,
                    "horizon": horizon,
                    "condition": "reference",
                    "model": "sarima",
                    "y_true": y_true,
                    "y_pred": sarima_preds[horizon],
                })

            rows.append({
                "station": station,
                "origin": pd.Timestamp(origin),
                "forecast_timestamp": forecast_ts,
                "horizon": horizon,
                "condition": condition,
                "model": "xgboost_direct",
                "y_true": y_true,
                "y_pred": model_preds[horizon],
            })

    preds = pd.DataFrame(rows)
    if preds.empty:
        return preds
    return (
        preds
        .sort_values(["station", "model", "condition", "origin", "horizon"])
        .reset_index(drop=True)
    )


# ── metrics ────────────────────────────────────────────────────────────────────

def compute_metrics_ireland(predictions: pd.DataFrame) -> pd.DataFrame:
    """RMSE and MAE per station × condition × model × horizon."""
    if predictions.empty:
        return pd.DataFrame(
            columns=["station", "condition", "model", "horizon", "n_eval", "mae", "rmse"]
        )
    records: list[dict[str, Any]] = []
    group_keys = ["station", "condition", "model", "horizon"]
    for keys, group in predictions.groupby(group_keys):
        station, condition, model, horizon = keys
        valid = group.dropna(subset=["y_true", "y_pred"])
        if valid.empty:
            records.append({
                "station": station, "condition": condition, "model": model,
                "horizon": int(horizon), "n_eval": 0,
                "mae": float("nan"), "rmse": float("nan"),
            })
            continue
        mae = float(mean_absolute_error(valid["y_true"], valid["y_pred"]))
        rmse = float(np.sqrt(mean_squared_error(valid["y_true"], valid["y_pred"])))
        records.append({
            "station": station, "condition": condition, "model": model,
            "horizon": int(horizon), "n_eval": int(len(valid)),
            "mae": mae, "rmse": rmse,
        })
    return (
        pd.DataFrame(records)
        .sort_values(["station", "model", "condition", "horizon"])
        .reset_index(drop=True)
    )


def attach_skill_ireland(metrics: pd.DataFrame) -> pd.DataFrame:
    """Skill vs persistence, computed per station to avoid cross-station contamination."""
    if metrics.empty:
        return metrics.copy()
    baseline = (
        metrics[metrics["model"] == "persistence"][["station", "horizon", "mae", "rmse"]]
        .drop_duplicates(subset=["station", "horizon"])
        .rename(columns={"mae": "mae_persistence", "rmse": "rmse_persistence"})
    )
    out = metrics.merge(baseline, on=["station", "horizon"], how="left")
    out["skill_mae_vs_persistence"] = 1.0 - (out["mae"] / out["mae_persistence"])
    out["skill_rmse_vs_persistence"] = 1.0 - (out["rmse"] / out["rmse_persistence"])
    out.loc[
        out["model"] == "persistence",
        ["skill_mae_vs_persistence", "skill_rmse_vs_persistence"],
    ] = float("nan")
    return out


def derive_hstar_ireland(metrics: pd.DataFrame, horizon_max: int) -> pd.DataFrame:
    """H* (skill horizon) per station × condition × model."""
    rows: list[dict[str, Any]] = []
    for (station, condition, model), group in metrics.groupby(["station", "condition", "model"]):
        if model == "persistence":
            rows.append({
                "station": station, "condition": condition, "model": model,
                "H": horizon_max, "H_star_relax": 0, "H_star_strict": 0,
            })
            continue
        skill = (
            group.set_index("horizon")["skill_rmse_vs_persistence"]
            .reindex(range(1, horizon_max + 1))
            .to_numpy()
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
        rows.append({
            "station": station, "condition": condition, "model": model,
            "H": horizon_max, "H_star_relax": h_relax, "H_star_strict": int(best),
        })
    return (
        pd.DataFrame(rows)
        .sort_values(["station", "model", "condition"])
        .reset_index(drop=True)
    )


def run_dm_ireland(predictions: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """DM-HLN test (lags_meteo vs lags_only) per station × horizon."""
    dm_rows: list[dict[str, Any]] = []
    for station in sorted(predictions["station"].unique()):
        preds_lags = predictions[
            (predictions["station"] == station)
            & (predictions["condition"] == "lags_only")
            & (predictions["model"] == "xgboost_direct")
        ].copy()
        preds_meteo = predictions[
            (predictions["station"] == station)
            & (predictions["condition"] == "lags_meteo")
            & (predictions["model"] == "xgboost_direct")
        ].copy()
        if preds_lags.empty or preds_meteo.empty:
            continue
        for horizon in config["dm_horizons"]:
            result = diebold_mariano_test(
                preds_a=preds_lags,
                preds_b=preds_meteo,
                horizon=int(horizon),
                loss=str(config["dm_loss"]),
            )
            result["station"] = station
            dm_rows.append(result)
    if not dm_rows:
        return pd.DataFrame(
            columns=["station", "horizon", "n", "dm_stat", "p_value", "mean_loss_diff", "favours"]
        )
    return pd.DataFrame(dm_rows)[
        ["station", "horizon", "n", "dm_stat", "p_value", "mean_loss_diff", "favours"]
    ]


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run E2-MET Ireland PM10 rolling-origin experiment (multi-station)."
    )
    parser.add_argument("--config", default="code/e2_met_ireland_config.json")
    parser.add_argument(
        "--condition",
        choices=["lags_only", "lags_meteo", "all"],
        default="all",
    )
    parser.add_argument(
        "--max-origins",
        type=int,
        default=0,
        help="Cap on rolling origins per station (0 = no cap; use 5 for smoke test).",
    )
    parser.add_argument(
        "--station",
        default=None,
        help="Run only this station name (exact match). Useful for SARIMA runs.",
    )
    args = parser.parse_args()

    config = load_json_config(args.config)
    paths = ensure_results_dirs(config["results_dir"])
    df = load_ireland_dataset(config)

    station_col = config["station_col"]
    stations = sorted(df[station_col].unique())
    if args.station:
        if args.station not in stations:
            raise ValueError(
                f"Station '{args.station}' not found. Available: {stations}"
            )
        stations = [args.station]

    conditions = ["lags_only", "lags_meteo"] if args.condition == "all" else [args.condition]
    max_origins = args.max_origins if args.max_origins > 0 else None

    run_metadata: dict[str, Any] = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": config["config_path"],
        "dataset_path": config["dataset_path"],
        "conditions_run": conditions,
        "stations": list(stations),
        "horizon_max": int(config["horizon_max"]),
        "max_origins_cap": max_origins,
    }

    all_predictions: list[pd.DataFrame] = []

    for station in stations:
        station_df = df[df[station_col] == station].copy()
        print(f"\n[{station}]  {len(station_df)} rows")

        for i, condition in enumerate(conditions):
            # Include persistence / SARIMA reference rows only on the first condition
            # to avoid storing duplicate reference rows in the combined file.
            include_references = i == 0
            preds = run_backtest_for_station(
                station_df=station_df,
                station=station,
                config=config,
                condition=condition,
                include_references=include_references,
                max_origins=max_origins,
            )
            safe_name = station.replace(" ", "_").replace("/", "-")
            preds_path = paths["predictions"] / f"predictions_{safe_name}_{condition}.csv"
            preds.to_csv(preds_path, index=False)
            all_predictions.append(preds)
            print(f"  {condition}: {len(preds)} prediction rows → {preds_path.name}")

    if all_predictions:
        predictions = pd.concat(all_predictions, ignore_index=True)
    else:
        predictions = pd.DataFrame(
            columns=["station", "origin", "forecast_timestamp", "horizon",
                     "condition", "model", "y_true", "y_pred"]
        )

    combined_path = paths["predictions"] / "predictions_all_models.csv"
    predictions.to_csv(combined_path, index=False)
    print(f"\nCombined predictions: {len(predictions)} rows → {combined_path}")

    print("Computing metrics...")
    metrics = compute_metrics_ireland(predictions)
    metrics = attach_skill_ireland(metrics)
    metrics_path = paths["metrics"] / "metrics_all_models.csv"
    metrics.to_csv(metrics_path, index=False)

    print("Deriving H*...")
    hstar = derive_hstar_ireland(metrics=metrics, horizon_max=int(config["horizon_max"]))
    hstar_path = paths["metrics"] / "hstar_summary.csv"
    hstar.to_csv(hstar_path, index=False)

    dm_df = pd.DataFrame()
    if args.condition == "all":
        print("Running DM-HLN tests...")
        dm_df = run_dm_ireland(predictions=predictions, config=config)
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

    print(f"\nDone. {len(predictions)} prediction rows, {len(metrics)} metric rows.")


if __name__ == "__main__":
    main()
