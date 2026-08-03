#!/usr/bin/env python3
"""
export_results_summary_v1_2_1.py

Post-processing audit pass implementing the H* Methodological Contract
v1.2.1 on top of the already-executed, already-persisted E2-MET runs
(Madrid canonical, Ireland regenerated). Does NOT re-run, re-fit, or
re-seed persistence, SARIMA, or XGBoost -- it only reads existing
`predictions_all_models.csv` / `metrics_all_models.csv` /
`dm_lags_meteo_vs_lags_only.csv` artifacts and derives new, explicitly
separated diagnostics from them.

For each dataset (Madrid, Ireland-regenerated) this writes, without
touching or deleting any pre-existing file:

  <results_dir>/metrics/loss_matrix_full.parquet
      Fine-grained L_model(d, f, h) / L_baseline(d, f, h): one row per
      station (d) x origin (f) x horizon (h) x condition x model, with
      per-row squared/absolute loss.

  <results_dir>/metrics/hstar_summary_v1_2_1.csv
      Hstar_strict_from_h1, Hstar_strict_max_run, Hstar_relax and their
      per-variant ceiling_constrained flags, per station x condition x
      model.

  <results_dir>/stats/bootstrap_delta_hstar_v1_2_1.csv
      Moving-Block Bootstrap 95% CI for delta H* (lags_meteo - lags_only),
      per station, for all three variants.

And, combining both datasets:

  results/results_summary_v1.2.1.csv / .json
      One row per station (Madrid + the 8 Irish stations): rho1 (training
      period, sourced from the manuscript's own audited tab:rho1 -- see
      results/rho1_reference_from_manuscript.csv and the note in
      docs/protocol/hstar_v1_2_1_contract.md), all three H* variants for
      both conditions, delta H* + 95% MBB CI, DM-HLN p-values at
      h in {1, 6, 12, 24} (read from the existing dm stats files, not
      recomputed), and ceiling flags.

Usage:
  python3 code/export_results_summary_v1_2_1.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hstar_metrics import (  # noqa: E402
    HSTAR_VARIANTS,
    compute_loss_matrix,
    derive_hstar_v1_2_1_table,
    moving_block_bootstrap_delta_hstar,
)

DM_HORIZONS = (1, 6, 12, 24)

MADRID_DIR = ROOT / "results" / "e2_met_madrid_pm10"
IRELAND_DIR = ROOT / "results" / "e2_met_ireland_pm10_regenerated"
RHO1_REFERENCE = ROOT / "results" / "rho1_reference_from_manuscript.csv"
SUMMARY_CSV = ROOT / "results" / "results_summary_v1.2.1.csv"
SUMMARY_JSON = ROOT / "results" / "results_summary_v1.2.1.json"

MODEL = "xgboost_direct"
CONDITION_A = "lags_only"
CONDITION_B = "lags_meteo"
HORIZON_MAX = 24


def _process_dataset(
    dataset_label: str,
    results_dir: Path,
    has_station_col: bool,
    n_boot: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns (loss_matrix, hstar_table, bootstrap_table, dm_table)."""
    predictions_path = results_dir / "predictions" / "predictions_all_models.csv"
    metrics_path = results_dir / "metrics" / "metrics_all_models.csv"
    dm_path = results_dir / "stats" / "dm_lags_meteo_vs_lags_only.csv"

    predictions = pd.read_csv(predictions_path)
    metrics = pd.read_csv(metrics_path)
    dm = pd.read_csv(dm_path)

    default_station = None if has_station_col else "Madrid Casa de Campo"
    loss_matrix = compute_loss_matrix(predictions, default_station=default_station)
    if not has_station_col:
        metrics = metrics.copy()
        metrics.insert(0, "station", "Madrid Casa de Campo")
        dm = dm.copy()
        dm.insert(0, "station", "Madrid Casa de Campo")

    group_cols = ["station", "condition", "model"]
    hstar_table = derive_hstar_v1_2_1_table(
        metrics=metrics, group_cols=group_cols, horizon_max=HORIZON_MAX
    )
    hstar_table.insert(0, "dataset", dataset_label)

    boot_rows: list[dict[str, Any]] = []
    for station in sorted(loss_matrix["station"].unique()):
        boot_rows.append(
            moving_block_bootstrap_delta_hstar(
                loss_matrix=loss_matrix,
                station=station,
                horizon_max=HORIZON_MAX,
                model=MODEL,
                condition_a=CONDITION_A,
                condition_b=CONDITION_B,
                n_boot=n_boot,
                random_state=42,
            )
        )
    bootstrap_table = pd.DataFrame(boot_rows)
    bootstrap_table.insert(0, "dataset", dataset_label)

    out_dm = dm[dm["horizon"].isin(DM_HORIZONS)].copy()
    out_dm.insert(0, "dataset", dataset_label)

    return loss_matrix, hstar_table, bootstrap_table, out_dm


def _write_dataset_artifacts(
    results_dir: Path,
    loss_matrix: pd.DataFrame,
    hstar_table: pd.DataFrame,
    bootstrap_table: pd.DataFrame,
) -> None:
    metrics_dir = results_dir / "metrics"
    stats_dir = results_dir / "stats"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    stats_dir.mkdir(parents=True, exist_ok=True)

    loss_matrix.to_parquet(metrics_dir / "loss_matrix_full.parquet", index=False)
    hstar_table.drop(columns=["dataset"]).to_csv(metrics_dir / "hstar_summary_v1_2_1.csv", index=False)
    bootstrap_table.drop(columns=["dataset"]).to_csv(
        stats_dir / "bootstrap_delta_hstar_v1_2_1.csv", index=False
    )


def _pivot_hstar_wide(hstar_table: pd.DataFrame) -> pd.DataFrame:
    """station x variant wide, split by condition, for the xgboost_direct model."""
    xgb = hstar_table[hstar_table["model"] == MODEL]
    cols = ["Hstar_strict_from_h1", "Hstar_strict_max_run", "Hstar_relax"]
    ceiling_cols = [
        "ceiling_constrained_strict_from_h1",
        "ceiling_constrained_strict_max_run",
        "ceiling_constrained_relax",
    ]
    wide = xgb.pivot_table(
        index=["dataset", "station"],
        columns="condition",
        values=cols + ceiling_cols,
        aggfunc="first",
    )
    wide.columns = [f"{metric}_{condition}" for metric, condition in wide.columns]
    return wide.reset_index()


def build_combined_summary(
    hstar_tables: list[pd.DataFrame],
    bootstrap_tables: list[pd.DataFrame],
    dm_tables: list[pd.DataFrame],
) -> pd.DataFrame:
    hstar_all = pd.concat(hstar_tables, ignore_index=True)
    bootstrap_all = pd.concat(bootstrap_tables, ignore_index=True)
    dm_all = pd.concat(dm_tables, ignore_index=True)

    wide = _pivot_hstar_wide(hstar_all)

    rho1 = pd.read_csv(RHO1_REFERENCE)
    wide = wide.merge(
        rho1[["station_pipeline_name", "rho1", "source"]].rename(
            columns={"station_pipeline_name": "station", "source": "rho1_source"}
        ),
        on="station",
        how="left",
    )

    boot_cols = ["dataset", "station", "n_origins", "n_boot", "block_length"]
    for variant in HSTAR_VARIANTS:
        boot_cols += [f"delta_{variant}", f"delta_{variant}_ci_lower", f"delta_{variant}_ci_upper"]
    wide = wide.merge(bootstrap_all[boot_cols], on=["dataset", "station"], how="left")

    dm_wide = dm_all.pivot_table(
        index=["dataset", "station"], columns="horizon", values="p_value", aggfunc="first"
    )
    dm_wide.columns = [f"dm_pvalue_h{int(h)}" for h in dm_wide.columns]
    dm_wide = dm_wide.reset_index()
    wide = wide.merge(dm_wide, on=["dataset", "station"], how="left")

    dm_favours_wide = dm_all.pivot_table(
        index=["dataset", "station"], columns="horizon", values="favours", aggfunc="first"
    )
    dm_favours_wide.columns = [f"dm_favours_h{int(h)}" for h in dm_favours_wide.columns]
    dm_favours_wide = dm_favours_wide.reset_index()
    wide = wide.merge(dm_favours_wide, on=["dataset", "station"], how="left")

    # Manuscript-style consolidated ceiling flag: True iff the lags_only
    # model already saturates Hstar_strict_max_run at H_max, so there is no
    # ceiling room left for meteorology to add skill (matches tab:rho1's
    # "Ceiling" column semantics).
    wide["ceiling_flag"] = wide["ceiling_constrained_strict_max_run_lags_only"]

    front_cols = ["dataset", "station", "rho1", "rho1_source"]
    ordered = front_cols + [c for c in wide.columns if c not in front_cols]
    return wide[ordered].sort_values(["dataset", "station"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-boot", type=int, default=1000, help="Moving-Block Bootstrap replicates per station.")
    args = parser.parse_args()

    hstar_tables: list[pd.DataFrame] = []
    bootstrap_tables: list[pd.DataFrame] = []
    dm_tables: list[pd.DataFrame] = []

    for dataset_label, results_dir, has_station_col in (
        ("Madrid", MADRID_DIR, False),
        ("Ireland", IRELAND_DIR, True),
    ):
        loss_matrix, hstar_table, bootstrap_table, dm_table = _process_dataset(
            dataset_label=dataset_label,
            results_dir=results_dir,
            has_station_col=has_station_col,
            n_boot=args.n_boot,
        )
        _write_dataset_artifacts(results_dir, loss_matrix, hstar_table, bootstrap_table)
        hstar_tables.append(hstar_table)
        bootstrap_tables.append(bootstrap_table)
        dm_tables.append(dm_table)
        print(f"[{dataset_label}] loss_matrix rows={len(loss_matrix)}  hstar rows={len(hstar_table)}  bootstrap rows={len(bootstrap_table)}")

    summary = build_combined_summary(hstar_tables, bootstrap_tables, dm_tables)
    summary.to_csv(SUMMARY_CSV, index=False)
    summary.to_json(SUMMARY_JSON, orient="records", indent=2)
    print(f"Wrote {SUMMARY_CSV} ({len(summary)} rows)")
    print(f"Wrote {SUMMARY_JSON}")


if __name__ == "__main__":
    main()
