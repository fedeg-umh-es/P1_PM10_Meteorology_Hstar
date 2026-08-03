#!/usr/bin/env python3
"""Fase 4 -- simetria temporal de la ventana de evaluacion de Madrid.

El manuscrito declara la ventana de evaluacion como "1 January 2023 -- 31
July 2023" (manuscripts/manuscript_main.tex:280, y el pie de
tab:descriptive, linea 234: "evaluation: Jan-Jul 2023"), simetrica con
Irlanda. Pero results/e2_met_madrid_pm10/predictions/predictions_all_models.csv
(la fuente verificada en Fase 0/2 de las cifras Madrid publicadas) contiene
362 origenes desde 2023-01-01 hasta 2023-12-30 -- un año casi completo, no
7 meses.

Este script no reentrena nada (el dataset base no existe en este entorno,
Fase 0 Sec.5): filtra las predicciones row-level ya existentes por fecha de
origen para construir dos ventanas y recomputa S(h)/H*/bootstrap/DM para
cada una con el mismo codigo de la Fase 2:

  - PRIMARIA:     origenes en [2023-01-01, 2023-07-31]  (simetrica con Irlanda)
  - SENSIBILIDAD: origenes en [2023-01-01, 2023-12-30]  (todo lo disponible)

Cada origen ya tiene sus predicciones calculadas de forma independiente
(ventana de entrenamiento expansiva especifica de ese origen); subconjuntar
que origenes cuentan para el resumen no reintroduce fuga ni requiere
reentrenar.

Uso:
    source .venv_audit/bin/activate
    python3 code/audit_phase4_madrid_window.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from audit_phase2_madrid_recompute import (  # noqa: E402
    HORIZON_MAX,
    compute_skill_curve,
    hstar_from_h1,
    hstar_max_run,
    hstar_relax,
    moving_block_bootstrap_delta_hstar,
)
from e2_met_madrid_shared import diebold_mariano_test  # noqa: E402

PREDICTIONS_PATH = ROOT / "results" / "e2_met_madrid_pm10" / "predictions" / "predictions_all_models.csv"
OUT_DIR = ROOT / "results" / "audit" / "madrid_window_sensitivity"
DM_HORIZONS = [1, 6, 12, 24]
BOOTSTRAP_BLOCK_DAYS = 7
BOOTSTRAP_N_RESAMPLES = 2000
BOOTSTRAP_SEED = 20260803

WINDOWS = {
    "PRIMARIA_jan_jul_2023": ("2023-01-01", "2023-07-31"),
    "SENSIBILIDAD_jan_dec_2023": ("2023-01-01", "2023-12-30"),
}


def analyse_window(preds: pd.DataFrame, start: str, end: str) -> dict:
    sub = preds[(preds["origin"] >= pd.Timestamp(start)) & (preds["origin"] <= pd.Timestamp(end))].copy()
    n_origins = sub["origin"].nunique()

    persistence = sub[(sub["condition"] == "reference") & (sub["model"] == "persistence")]
    skill_lo = compute_skill_curve(sub, "lags_only", "xgboost_direct", persistence)
    skill_lm = compute_skill_curve(sub, "lags_meteo", "xgboost_direct", persistence)

    hstar = {
        "lags_only": {
            "max_run": hstar_max_run(skill_lo),
            "from_h1": hstar_from_h1(skill_lo),
            "relax": hstar_relax(skill_lo),
        },
        "lags_meteo": {
            "max_run": hstar_max_run(skill_lm),
            "from_h1": hstar_from_h1(skill_lm),
            "relax": hstar_relax(skill_lm),
        },
    }
    delta_max_run = hstar["lags_meteo"]["max_run"] - hstar["lags_only"]["max_run"]
    delta_from_h1 = hstar["lags_meteo"]["from_h1"] - hstar["lags_only"]["from_h1"]

    deltas = moving_block_bootstrap_delta_hstar(
        preds=sub, block_days=BOOTSTRAP_BLOCK_DAYS, n_resamples=BOOTSTRAP_N_RESAMPLES, seed=BOOTSTRAP_SEED
    )
    ci_low, ci_high = np.percentile(deltas, [2.5, 97.5])

    preds_lo = sub[(sub["condition"] == "lags_only") & (sub["model"] == "xgboost_direct")]
    preds_lm = sub[(sub["condition"] == "lags_meteo") & (sub["model"] == "xgboost_direct")]
    dm_rows = [diebold_mariano_test(preds_a=preds_lo, preds_b=preds_lm, horizon=h, loss="squared_error") for h in DM_HORIZONS]

    return {
        "start": start,
        "end": end,
        "n_origins": int(n_origins),
        "hstar": hstar,
        "delta_hstar_max_run": int(delta_max_run),
        "delta_hstar_from_h1": int(delta_from_h1),
        "bootstrap_ci95": [float(ci_low), float(ci_high)],
        "bootstrap_mean": float(np.mean(deltas)),
        "bootstrap_sd": float(np.std(deltas, ddof=1)),
        "dm": dm_rows,
        "skill_lags_only": skill_lo.to_dict(),
        "skill_lags_meteo": skill_lm.to_dict(),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    preds = pd.read_csv(PREDICTIONS_PATH, parse_dates=["origin", "forecast_timestamp"])

    results = {}
    for label, (start, end) in WINDOWS.items():
        results[label] = analyse_window(preds, start, end)
        print(f"\n=== {label} ({start} .. {end}) ===")
        r = results[label]
        print(f"n_origins = {r['n_origins']}")
        print(f"H*_strict,max-run  lags_only={r['hstar']['lags_only']['max_run']}  lags_meteo={r['hstar']['lags_meteo']['max_run']}  delta={r['delta_hstar_max_run']}")
        print(f"H*_strict,from-h1  lags_only={r['hstar']['lags_only']['from_h1']}  lags_meteo={r['hstar']['lags_meteo']['from_h1']}  delta={r['delta_hstar_from_h1']}")
        print(f"H*_relax           lags_only={r['hstar']['lags_only']['relax']}  lags_meteo={r['hstar']['lags_meteo']['relax']}")
        print(f"Bootstrap 95% CI on delta H*_max-run: [{r['bootstrap_ci95'][0]:.1f}, {r['bootstrap_ci95'][1]:.1f}] (mean={r['bootstrap_mean']:.2f})")
        for dm in r["dm"]:
            print(f"  DM h={dm['horizon']:>2} n={dm['n']:>3} p={dm['p_value']:.3f} favours={dm['favours']}")

    with (OUT_DIR / "window_comparison.json").open("w") as fh:
        json.dump(results, fh, indent=2, default=str)

    summary_rows = []
    for label, r in results.items():
        summary_rows.append(
            {
                "window": label,
                "start": r["start"],
                "end": r["end"],
                "n_origins": r["n_origins"],
                "hstar_max_run_lags_only": r["hstar"]["lags_only"]["max_run"],
                "hstar_max_run_lags_meteo": r["hstar"]["lags_meteo"]["max_run"],
                "delta_hstar_max_run": r["delta_hstar_max_run"],
                "hstar_from_h1_lags_only": r["hstar"]["lags_only"]["from_h1"],
                "hstar_from_h1_lags_meteo": r["hstar"]["lags_meteo"]["from_h1"],
                "delta_hstar_from_h1": r["delta_hstar_from_h1"],
                "bootstrap_ci95_low": r["bootstrap_ci95"][0],
                "bootstrap_ci95_high": r["bootstrap_ci95"][1],
            }
        )
    pd.DataFrame(summary_rows).to_csv(OUT_DIR / "window_summary.csv", index=False)

    dm_rows_flat = []
    for label, r in results.items():
        for dm in r["dm"]:
            dm_rows_flat.append({"window": label, **dm})
    pd.DataFrame(dm_rows_flat).to_csv(OUT_DIR / "window_dm.csv", index=False)


if __name__ == "__main__":
    main()
