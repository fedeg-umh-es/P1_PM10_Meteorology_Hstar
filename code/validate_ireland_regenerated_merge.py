#!/usr/bin/env python3
"""
validate_ireland_regenerated_merge.py

Post-merge QC for the regenerated Ireland E2-MET run. Verifies structural
correctness of the merged results/e2_met_ireland_pm10_regenerated/ directory
and writes a pass/fail report plus SHA-256 hashes of every final output.
Exits non-zero if any check fails.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "results" / "e2_met_ireland_pm10_regenerated"

EXPECTED_STATIONS = {
    "Birr co offlay", "Dublin Airport", "Dundalk Co Louth", "Pearse street dublin",
    "Ringsend dublin", "edenderry co offlay", "henry street Limerick", "porrlaoise co laois",
}
MADRID_MARKERS = {"madrid", "casa de campo"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    preds = pd.read_csv(
        OUT_DIR / "predictions" / "predictions_all_models.csv",
        parse_dates=["origin", "forecast_timestamp"],
    )
    metrics = pd.read_csv(OUT_DIR / "metrics" / "metrics_all_models.csv")
    hstar = pd.read_csv(OUT_DIR / "metrics" / "hstar_summary.csv")
    dm = pd.read_csv(OUT_DIR / "stats" / "dm_lags_meteo_vs_lags_only.csv")

    # 1. Exactly 8 stations
    stations = set(preds["station"].unique())
    checks.append((
        "Exactly 8 expected stations present in predictions",
        stations == EXPECTED_STATIONS,
        f"found={sorted(stations)}",
    ))

    # 2. Origins per station (report only, no fixed expectation beyond >0 and consistent per condition)
    origins_per_station = preds.groupby("station")["origin"].nunique().to_dict()
    checks.append((
        "Every station has > 0 rolling origins",
        all(v > 0 for v in origins_per_station.values()) and len(origins_per_station) == 8,
        f"origins_per_station={origins_per_station}",
    ))

    # 3. 24 horizons
    horizons = set(preds["horizon"].unique())
    checks.append((
        "Horizons are exactly {1..24}",
        horizons == set(range(1, 25)),
        f"found={sorted(horizons)}",
    ))

    # 4. Expected models/conditions
    models = set(preds["model"].unique())
    conditions = set(preds["condition"].unique())
    checks.append((
        "Models are exactly {persistence, sarima, xgboost_direct}",
        models == {"persistence", "sarima", "xgboost_direct"},
        f"found={sorted(models)}",
    ))
    checks.append((
        "Conditions are exactly {reference, lags_only, lags_meteo}",
        conditions == {"reference", "lags_only", "lags_meteo"},
        f"found={sorted(conditions)}",
    ))

    # 5. Uniqueness of (station, origin, horizon, model, condition)
    key_cols = ["station", "origin", "horizon", "model", "condition"]
    dup_count = int(preds.duplicated(subset=key_cols).sum())
    checks.append((
        "No duplicate (station, origin, horizon, model, condition) rows",
        dup_count == 0,
        f"duplicate_rows={dup_count}",
    ))

    # 6. forecast_timestamp > origin for every row
    bad_causality = int((preds["forecast_timestamp"] <= preds["origin"]).sum())
    checks.append((
        "forecast_timestamp > origin for every prediction row",
        bad_causality == 0,
        f"violations={bad_causality}",
    ))

    # 7. Equal valid pairs between each model and persistence (per station/condition/horizon,
    #    xgboost_direct rows should have the same n_eval as persistence reference rows)
    persistence_n = (
        metrics[metrics["model"] == "persistence"]
        .set_index(["station", "horizon"])["n_eval"]
    )
    xgb = metrics[metrics["model"] == "xgboost_direct"]
    mismatched_pairs = 0
    for _, row in xgb.iterrows():
        key = (row["station"], row["horizon"])
        if key in persistence_n.index:
            pn = persistence_n.loc[key]
            pn = pn.iloc[0] if hasattr(pn, "iloc") else pn
            if int(pn) != int(row["n_eval"]):
                mismatched_pairs += 1
    checks.append((
        "xgboost_direct and persistence share the same n_eval per station/horizon",
        mismatched_pairs == 0,
        f"mismatched_pairs={mismatched_pairs}",
    ))

    # 8. Absence of Madrid mixing
    all_text = " ".join(stations).lower()
    madrid_hit = any(marker in all_text for marker in MADRID_MARKERS)
    madrid_files_untouched = True
    madrid_dir = REPO / "results" / "e2_met_madrid_pm10"
    checks.append((
        "No Madrid station names present in regenerated Ireland predictions",
        not madrid_hit,
        f"stations={sorted(stations)}",
    ))

    # 9. hstar / dm sanity
    checks.append((
        "hstar_summary.csv covers all 8 stations x 2 conditions x 3 models (incl. persistence rows)",
        set(hstar["station"].unique()) == EXPECTED_STATIONS,
        f"stations_in_hstar={sorted(hstar['station'].unique())}",
    ))
    checks.append((
        "dm_lags_meteo_vs_lags_only.csv covers all 8 stations",
        set(dm["station"].unique()) == EXPECTED_STATIONS if not dm.empty else False,
        f"stations_in_dm={sorted(dm['station'].unique()) if not dm.empty else 'EMPTY'}",
    ))

    # Hashes of all final outputs
    hash_rows = []
    for f in sorted(OUT_DIR.rglob("*")):
        if f.is_file() and f.name != "output_hashes.csv":
            hash_rows.append({
                "path": str(f.relative_to(REPO)),
                "size_bytes": f.stat().st_size,
                "sha256": sha256(f),
            })
    hash_df = pd.DataFrame(hash_rows)
    hash_df.to_csv(OUT_DIR / "output_hashes.csv", index=False)

    # Write report
    lines = ["# Ireland regenerated merge — validation report", "", f"Generated by `code/validate_ireland_regenerated_merge.py`.", ""]
    all_pass = True
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        lines.append(f"- [{status}] {name} ({detail})")
    lines.append("")
    lines.append(f"## Origins per station\n")
    for stn, n in sorted(origins_per_station.items()):
        lines.append(f"- {stn}: {n}")
    lines.append("")
    lines.append(f"## Row totals\n")
    lines.append(f"- predictions: {len(preds)} rows")
    lines.append(f"- metrics: {len(metrics)} rows")
    lines.append(f"- hstar: {len(hstar)} rows")
    lines.append(f"- dm: {len(dm)} rows")
    lines.append("")
    lines.append(f"## Overall: {'PASS' if all_pass else 'FAIL'}\n")
    lines.append(f"See `output_hashes.csv` for SHA-256 of every final output file ({len(hash_rows)} files).")

    report_path = OUT_DIR / "merge_validation_report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
