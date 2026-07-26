#!/usr/bin/env python3
"""
compare_ireland_regenerated_to_manuscript.py

Compares the regenerated Ireland E2-MET run against the 76 manuscript claims
already catalogued in results/e2_met_ireland_pm10/tables/manuscript_source_values.csv.

Computes H*_strict under both candidate definitions (see manuscript_main.tex
lines 356-361 for the manuscript's own stated definition):
  - H_strict_from_h1:  longest consecutive positive-skill run STARTING at h=1
                        (the manuscript's literal definition).
  - H_strict_max_run:  longest consecutive positive-skill run ANYWHERE in
                        h=1..24 (what code/e2_met_ireland_run.py actually
                        computes as its "H_star_strict" column).
These two definitions can differ whenever a station's skill curve has an
early break followed by a later, longer positive run.

Also computes descriptive PM10 statistics (train period 2020-01-01 to
2022-12-31 23:00:00, matching code/e2_autocorrelation_analysis.py) and
lag-1 autocorrelation (rho1) directly from the regenerated dataset, since
these were previously SOURCE_NOT_FOUND.

Usage:
  python3 code/compare_ireland_regenerated_to_manuscript.py \
      --regenerated-dir results/e2_met_ireland_pm10_regenerated \
      --dataset data_processed/ireland_pm10_meteorology_hourly.csv \
      --claims results/e2_met_ireland_pm10/tables/manuscript_source_values.csv \
      --out results/e2_met_ireland_pm10_regenerated/manuscript_claim_comparison.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

TRAIN_START = "2020-01-01"
TRAIN_END = "2022-12-31 23:00:00"

# Map manuscript short station names -> dataset station names
STATION_MAP = {
    "Birr (Co. Offaly)": "Birr co offlay",
    "Dublin Airport": "Dublin Airport",
    "Dundalk (Co. Louth)": "Dundalk Co Louth",
    "Pearse St. Dublin": "Pearse street dublin",
    "Ringsend Dublin": "Ringsend dublin",
    "Edenderry (Co. Offaly)": "edenderry co offlay",
    "Henry St. Limerick": "henry street Limerick",
    "Portlaoise (Co. Laois)": "porrlaoise co laois",
}

# The original manuscript_source_values.csv (from the prior evidence-recovery
# PR) recorded manuscript_value="see manuscript table" (a placeholder, not a
# number) for IE-045..IE-068, because that recovery session had no dataset to
# compute against and never transcribed the actual figures. The real values
# ARE present in manuscripts/manuscript_main.tex, Table tab:descriptive
# (lines ~230-256), Training (2020-2022) columns. Transcribed read-only here
# (manuscript itself is not modified) so the placeholder can be replaced with
# a real comparison target.
MANUSCRIPT_DESCRIPTIVE_TRAIN = {
    # dataset_station: (mean, sd, p95)
    "Birr co offlay": (12.8, 12.5, 31.4),
    "Dublin Airport": (19.1, 16.1, 46.9),
    "Dundalk Co Louth": (11.4, 8.6, 24.3),
    "Pearse street dublin": (13.0, 9.9, 30.2),
    "Ringsend dublin": (15.6, 16.1, 41.9),
    "edenderry co offlay": (17.8, 19.8, 48.8),
    "henry street Limerick": (13.0, 12.1, 30.8),
    "porrlaoise co laois": (11.3, 9.7, 27.5),
}


def h_strict_from_h1(skill: np.ndarray) -> int:
    """Longest consecutive positive-skill run starting at h=1 (manuscript def.)."""
    count = 0
    for value in skill:
        if pd.notna(value) and value > 0:
            count += 1
        else:
            break
    return int(count)


def h_strict_max_run(skill: np.ndarray) -> int:
    """Longest consecutive positive-skill run anywhere (code's current H_star_strict)."""
    best = current = 0
    for value in skill:
        if pd.notna(value) and value > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return int(best)


def h_relax(skill: np.ndarray) -> int:
    pos = np.where(skill > 0)[0]
    return int(pos.max() + 1) if len(pos) > 0 else 0


def lag1_autocorr(series: pd.Series) -> float:
    s = series.dropna()
    if len(s) < 2:
        return float("nan")
    return float(s.autocorr(lag=1))


def compute_hstar_both_defs(metrics: pd.DataFrame, horizon_max: int) -> pd.DataFrame:
    rows = []
    for (station, condition, model), group in metrics.groupby(["station", "condition", "model"]):
        if model == "persistence":
            continue
        skill = (
            group.set_index("horizon")["skill_rmse_vs_persistence"]
            .reindex(range(1, horizon_max + 1))
            .to_numpy()
        )
        rows.append({
            "station": station,
            "condition": condition,
            "model": model,
            "H_strict_from_h1": h_strict_from_h1(skill),
            "H_strict_max_run": h_strict_max_run(skill),
            "H_relax": h_relax(skill),
        })
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerated-dir", default="results/e2_met_ireland_pm10_regenerated")
    parser.add_argument("--dataset", default="data_processed/ireland_pm10_meteorology_hourly.csv")
    parser.add_argument(
        "--claims",
        default="results/e2_met_ireland_pm10/tables/manuscript_source_values.csv",
    )
    parser.add_argument(
        "--out",
        default="results/e2_met_ireland_pm10_regenerated/manuscript_claim_comparison.csv",
    )
    args = parser.parse_args()

    regen_dir = Path(args.regenerated_dir)
    metrics = pd.read_csv(regen_dir / "metrics" / "metrics_all_models.csv")
    hstar_both = compute_hstar_both_defs(metrics, horizon_max=24)
    hstar_both.to_csv(regen_dir / "metrics" / "hstar_summary_both_definitions.csv", index=False)

    ds = pd.read_csv(args.dataset, parse_dates=["timestamp"])
    train = ds[(ds["timestamp"] >= TRAIN_START) & (ds["timestamp"] <= TRAIN_END)]

    desc_stats: dict[str, dict[str, float]] = {}
    rho1_stats: dict[str, float] = {}
    for stn, grp in train.groupby("station"):
        pm10 = pd.to_numeric(grp["PM10"], errors="coerce").dropna()
        desc_stats[stn] = {
            "mean": float(pm10.mean()) if len(pm10) else float("nan"),
            "sd": float(pm10.std()) if len(pm10) else float("nan"),
            "p95": float(pm10.quantile(0.95)) if len(pm10) else float("nan"),
        }
        rho1_stats[stn] = lag1_autocorr(grp["PM10"])

    row_counts = ds.groupby("station").size().to_dict()

    claims = pd.read_csv(args.claims)
    out_rows = []

    for _, claim in claims.iterrows():
        claim_id = claim["claim_id"]
        metric = claim["metric"]
        manuscript_value = claim["manuscript_value"]
        station_short = claim["station"]
        condition = claim["condition"]
        regenerated_value = None
        status = "SOURCE_NOT_FOUND"
        source_file = str(args.out)
        source_row = ""

        dataset_station = STATION_MAP.get(station_short)

        if metric == "H_star_strict_hours" and dataset_station:
            match = hstar_both[
                (hstar_both["station"] == dataset_station)
                & (hstar_both["condition"] == condition)
                & (hstar_both["model"] == "xgboost_direct")
            ]
            if not match.empty:
                from_h1 = int(match["H_strict_from_h1"].iloc[0])
                max_run = int(match["H_strict_max_run"].iloc[0])
                # IMPORTANT FINDING (see hstar_definition_discrepancy.md):
                # the manuscript's own Methods text (manuscript_main.tex:356-361)
                # defines H*_strict as the run starting at h=1, but empirically
                # its own TABLE values match H_strict_max_run (the "longest run
                # anywhere" definition code/e2_met_ireland_run.py actually
                # computes), not H_strict_from_h1. max_run is used as the
                # primary regenerated_value here because it is what the
                # manuscript's tables demonstrably reproduce; from_h1 is
                # recorded alongside for full transparency, since under the
                # manuscript's own literal prose definition several stations
                # would not match at all (see the discrepancy report).
                regenerated_value = max_run
                source_row = (
                    f"H_strict_max_run={max_run} (used); H_strict_from_h1={from_h1}"
                )
                source_file = str(regen_dir / "metrics" / "hstar_summary_both_definitions.csv")

        elif metric == "H_star_relax_hours" and station_short == "all 8 stations":
            vals = hstar_both[hstar_both["model"] == "xgboost_direct"]["H_relax"]
            regenerated_value = int(vals.min()) if not vals.empty else None
            source_row = f"min={vals.min()}, max={vals.max()}, all_values={sorted(vals.unique().tolist())}"
            source_file = str(regen_dir / "metrics" / "hstar_summary_both_definitions.csv")

        elif metric == "mean_delta_H_star_strict_hours":
            meteo = hstar_both[
                (hstar_both["condition"] == "lags_meteo") & (hstar_both["model"] == "xgboost_direct")
            ].set_index("station")["H_strict_max_run"]
            only = hstar_both[
                (hstar_both["condition"] == "lags_only") & (hstar_both["model"] == "xgboost_direct")
            ].set_index("station")["H_strict_max_run"]
            delta = (meteo - only).dropna()
            regenerated_value = round(float(delta.mean()), 4) if not delta.empty else None
            source_row = "computed using H_strict_max_run (see note on H_star_strict_hours rows)"
            source_file = str(regen_dir / "metrics" / "hstar_summary_both_definitions.csv")

        elif metric == "DM_favours_count_lags_meteo/lags_only/undetermined":
            dm_path = regen_dir / "stats" / "dm_lags_meteo_vs_lags_only.csv"
            if dm_path.exists():
                dm = pd.read_csv(dm_path)
                counts = dm["favours"].value_counts()
                regenerated_value = (
                    f"{counts.get('lags_meteo', 0)}/{counts.get('lags_only', 0)}/{counts.get('undetermined', 0)}"
                )
                source_file = str(dm_path)

        elif metric == "total_hourly_rows_2020_2023" and dataset_station:
            regenerated_value = int(row_counts.get(dataset_station, 0))
            source_file = "reports/ireland_experiment_setup.md (regenerated)"

        elif metric.startswith("PM10_") and metric.endswith("_train_ugm3") and dataset_station:
            stat_key = metric.replace("PM10_", "").replace("_train_ugm3", "")
            stat_idx = {"mean": 0, "sd": 1, "p95": 2}.get(stat_key)
            if dataset_station in desc_stats and stat_idx is not None:
                regenerated_value = round(desc_stats[dataset_station][stat_key], 1)
                source_file = str(args.dataset)
                # The original claims CSV recorded manuscript_value="see
                # manuscript table" (a placeholder). Resolve it to the real
                # transcribed value from manuscripts/manuscript_main.tex's
                # Table tab:descriptive (Training 2020-2022 columns) so the
                # comparison is against an actual number, not a placeholder
                # string. Manuscript itself is not modified.
                if str(manuscript_value).strip().lower() == "see manuscript table":
                    manuscript_value = MANUSCRIPT_DESCRIPTIVE_TRAIN[dataset_station][stat_idx]
                    source_row = "manuscript_value resolved from manuscript_main.tex tab:descriptive (was a placeholder in the original claims CSV)"

        elif metric == "rho1_lag1_autocorrelation_2020_2022" and dataset_station:
            if dataset_station in rho1_stats and pd.notna(rho1_stats[dataset_station]):
                regenerated_value = round(rho1_stats[dataset_station], 4)
                source_file = str(args.dataset)

        # compute diff/status
        abs_diff = ""
        if regenerated_value is not None:
            try:
                mv = float(str(manuscript_value).replace(",", ""))
                rv = float(regenerated_value) if not isinstance(regenerated_value, str) else None
                if rv is not None:
                    abs_diff = round(abs(mv - rv), 6)
                    if abs_diff == 0:
                        status = "MATCH"
                    elif abs_diff <= max(1.0, 0.01 * abs(mv)):
                        status = "ROUNDING_MATCH"
                    else:
                        status = "MISMATCH"
                else:
                    # string-valued metric (e.g. DM favours counts)
                    status = "MATCH" if str(manuscript_value) == str(regenerated_value) else "MISMATCH"
            except (ValueError, TypeError):
                status = "MATCH" if str(manuscript_value) == str(regenerated_value) else "MISMATCH"
        else:
            status = "SOURCE_NOT_FOUND"

        out_rows.append({
            "claim_id": claim_id,
            "manuscript_value": manuscript_value,
            "regenerated_value": regenerated_value if regenerated_value is not None else "NOT_FOUND",
            "absolute_difference": abs_diff,
            "status": status,
            "source_file": source_file,
            "source_row": source_row,
        })

    out_df = pd.DataFrame(out_rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out, index=False)

    print(f"Wrote {args.out}")
    print(out_df["status"].value_counts())


if __name__ == "__main__":
    main()
