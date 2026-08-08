---
title: "p3_evidence_audit.py"
categoria: "INVESTIGACION"
sub_area: "Investigacion"
tags:
  - investigacion
  - script
---

# 📌 p3_evidence_audit.py

## 🧠 Síntesis y Puntos Clave (TDAH-friendly)
- **from __future__** import annotations
- import json
- import hashlib
- import sys
- **from pathlib** import Path
- **import numpy** as np
- **import pandas** as pd
- ROOT = Path(sys.argv[1])

## 📄 Contenido Detallado / Referencia
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(sys.argv[1])


def hstar(values: pd.DataFrame) -> dict[str, object]:
    values = values.sort_values("horizon")
    pos = {
        int(row.horizon): bool(pd.notna(row.skill_rmse_vs_persistence) and row.skill_rmse_vs_persistence > 0)
        for row in values.itertuples()
    }
    relax = max((h for h, ok in pos.items() if ok), default=0)
    from_h1 = 0
    h = 1
    while pos.get(h, False):
        from_h1 += 1
        h += 1
    best_len = 0
    best_start = None
    best_end = None
    run_start = None
    for h in range(1, max(pos, default=0) + 2):
        if pos.get(h, False):
            if run_start is None:
                run_start = h
        elif run_start is not None:
            run_len = h - run_start
            if run_len > best_len:
                best_len = run_len
                best_start = run_start
                best_end = h - 1
            run_start = None
    return {
        "H_relax": relax,
        "H_strict_from_h1": from_h1,
        "H_strict_max_run": best_len,
        "max_run_interval": [best_start, best_end],
    }


out: dict[str, object] = {}

hash_manifest = pd.read_csv(ROOT / "results/e2_met_ireland_pm10_regenerated/output_hashes.csv")
hash_checks = []
for row in hash_manifest.itertuples(index=False):
    path = ROOT / row.path
    exists = path.is_file()
    actual_size = path.stat().st_size if exists else None
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest() if exists else None
    hash_checks.append(
        {
            "path": row.path,
            "exists": exists,
            "size_matches": exists and actual_size == int(row.size_bytes),
            "hash_matches": exists and actual_hash == row.sha256,
        }
    )
out["ireland_output_hash_manifest"] = {
    "entries": len(hash_checks),
    "present": sum(x["exists"] for x in hash_checks),
    "missing": [x["path"] for x in hash_checks if not x["exists"]],
    "present_hash_mismatches": [x["path"] for x in hash_checks if x["exists"] and not x["hash_matches"]],
    "present_size_mismatches": [x["path"] for x in hash_checks if x["exists"] and not x["size_matches"]],
}

for label, path in {
    "original_claim_map": ROOT / "results/e2_met_ireland_pm10/tables/manuscript_source_values.csv",
    "regenerated_claim_map": ROOT / "results/e2_met_ireland_pm10_regenerated/manuscript_claim_comparison.csv",
}.items():
    claims = pd.read_csv(path)
    status_col = "status" if "status" in claims.columns else next(c for c in claims.columns if "status" in c.lower())
    out[label + "_status_counts"] = {
        str(k): int(v) for k, v in claims[status_col].value_counts(dropna=False).items()
    }

ire_pred = pd.read_csv(ROOT / "results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv")
ire_metrics = pd.read_csv(ROOT / "results/e2_met_ireland_pm10_regenerated/metrics/metrics_all_models.csv")
ire_hstar = pd.read_csv(ROOT / "results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv")
ire_dm = pd.read_csv(ROOT / "results/e2_met_ireland_pm10_regenerated/stats/dm_lags_meteo_vs_lags_only.csv")

out["ireland_shape"] = {
    "prediction_rows": len(ire_pred),
    "stations": int(ire_pred.station.nunique()),
    "station_names": sorted(ire_pred.station.unique().tolist()),
    "horizons": [int(ire_pred.horizon.min()), int(ire_pred.horizon.max())],
    "station_origins": int(ire_pred[["station", "origin"]].drop_duplicates().shape[0]),
    "conditions_models": sorted(
        [f"{a}/{b}" for a, b in ire_pred[["condition", "model"]].drop_duplicates().itertuples(index=False, name=None)]
    ),
}

computed_ireland = []
for (station, condition), grp in ire_metrics[
    (ire_metrics.model == "xgboost_direct") & (ire_metrics.condition.isin(["lags_only", "lags_meteo"]))
].groupby(["station", "condition"]):
    row = {"station": station, "condition": condition, **hstar(grp)}
    stored = ire_hstar[
        (ire_hstar.station == station)
        & (ire_hstar.condition == condition)
        & (ire_hstar.model == "xgboost_direct")
    ].iloc[0]
    row["matches_stored"] = bool(
        row["H_relax"] == stored.H_relax
        and row["H_strict_from_h1"] == stored.H_strict_from_h1
        and row["H_strict_max_run"] == stored.H_strict_max_run
    )
    computed_ireland.append(row)
out["ireland_hstar_recomputed"] = computed_ireland

piv = ire_hstar[
    (ire_hstar.model == "xgboost_direct") & (ire_hstar.condition.isin(["lags_only", "lags_meteo"]))
].pivot(index="station", columns="condition", values="H_strict_max_run")
out["ireland_hstar_means"] = {
    "lags_only": float(piv.lags_only.mean()),
    "lags_meteo": float(piv.lags_meteo.mean()),
    "mean_delta": float((piv.lags_meteo - piv.lags_only).mean()),
}
out["ireland_dm_directional"] = {
    str(k): int(v) for k, v in ire_dm.favours.value_counts(dropna=False).items()
}

mad_metrics = pd.read_csv(ROOT / "results/e2_met_madrid_pm10/metrics/metrics_all_models.csv")
mad_hstar = pd.read_csv(ROOT / "results/e2_met_madrid_pm10/metrics/hstar_summary.csv")
mad_pred = pd.read_csv(ROOT / "results/e2_met_madrid_pm10/predictions/predictions_all_models.csv")
out["madrid_shape"] = {
    "prediction_rows": len(mad_pred),
    "origins": int(mad_pred.origin.nunique()),
    "horizons": [int(mad_pred.horizon.min()), int(mad_pred.horizon.max())],
}
computed_madrid = {}
for condition in ["lags_only", "lags_meteo"]:
    grp = mad_metrics[(mad_metrics.model == "xgboost_direct") & (mad_metrics.condition == condition)]
    computed_madrid[condition] = hstar(grp)
out["madrid_hstar_recomputed"] = computed_madrid
out["madrid_hstar_stored"] = mad_hstar.to_dict(orient="records")

# Arithmetic check only: these rho values are manuscript/canon inputs, not re-derived source evidence.
rhos = np.array([0.957, 0.945, 0.876, 0.864, 0.843, 0.842, 0.815, 0.815, 0.804])
deltas = np.array([8, 0, 7, 0, 0, 0, 1, 0, 0])
r = np.corrcoef(rhos, deltas)[0, 1]
out["rho1_association_arithmetic_only"] = {
    "n": 9,
    "r": float(r),
    "p_declared_not_recomputed": 0.121110,
}

print(json.dumps(out, indent=2, sort_keys=True))


---
*Procesado automáticamente por Antigravity (Smart Router)*
