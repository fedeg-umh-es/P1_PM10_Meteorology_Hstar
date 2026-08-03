#!/usr/bin/env python3
"""Fase 2 -- evidencia primaria de Madrid.

Recomputa, EXCLUSIVAMENTE a partir de las predicciones row-level ya
trackeadas en `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`
(el dataset base `data_processed/madrid_pm10_meteorology_experiment_base.csv`
no existe en este entorno -- ver docs/audit/00_inventory.md Sec.5):

  - S(h) para persistence, sarima, xgboost_direct(lags_only),
    xgboost_direct(lags_meteo), h=1..24
  - H*_strict,max-run   (racha positiva mas larga en cualquier punto de 1..24)
  - H*_strict,from-h1   (racha positiva que arranca exactamente en h=1)
  - H*_relax            (ultimo horizonte con S(h) > 0)
  - Delta H*_strict,max-run = H*(lags_meteo) - H*(lags_only)
  - Bootstrap de bloques moviles (block=7 dias/origenes, 2000 remuestras,
    semilla fija) sobre Delta H*_strict,max-run
  - DM-HLN en h in {1,6,12,24} (reutilizando la funcion de produccion
    e2_met_madrid_shared.diebold_mariano_test para no reimplementar la
    inferencia estadistica de forma distinta a la que genero las cifras
    publicadas)

No reentrena ningun modelo: todo se deriva de predicciones ya calculadas
por el motor de produccion verificado VERDE en la Fase 1
(docs/audit/01_leak_verdict.md). Por eso todo lo que produce este script se
etiqueta REPRODUCED, no VERIFIED_PRIMARY (esa etiqueta exigiria reentrenar
desde el dataset base, ausente).

Uso:
    source .venv_audit/bin/activate
    python3 code/audit_phase2_madrid_recompute.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from e2_met_madrid_shared import diebold_mariano_test  # noqa: E402

PREDICTIONS_PATH = ROOT / "results" / "e2_met_madrid_pm10" / "predictions" / "predictions_all_models.csv"
OUT_DIR = ROOT / "results" / "audit" / "madrid_recompute"
HORIZON_MAX = 24
DM_HORIZONS = [1, 6, 12, 24]
BOOTSTRAP_BLOCK_DAYS = 7
BOOTSTRAP_N_RESAMPLES = 2000
BOOTSTRAP_SEED = 20260803  # fixed seed, registered for reproducibility

MANUSCRIPT_CLAIMS = {
    "hstar_strict_max_run.lags_only": 9,
    "hstar_strict_max_run.lags_meteo": 17,
    "hstar_strict_from_h1.lags_only": 0,
    "hstar_strict_from_h1.lags_meteo": 17,
    "delta_hstar_strict_max_run": 8,
    "dm.h1.p_value": 0.243,
    "dm.h1.n": 354,
    "dm.h6.p_value": 0.961,
    "dm.h6.n": 356,
    "dm.h12.p_value": 0.012,
    "dm.h12.n": 346,
    "dm.h24.p_value": 0.398,
    "dm.h24.n": 354,
}


def rmse(y_true: pd.Series, y_pred: pd.Series) -> float:
    valid = pd.concat([y_true, y_pred], axis=1).dropna()
    if valid.empty:
        return float("nan")
    return float(np.sqrt(mean_squared_error(valid.iloc[:, 0], valid.iloc[:, 1])))


def compute_skill_curve(preds: pd.DataFrame, condition: str, model: str, persistence: pd.DataFrame) -> pd.Series:
    """S(h) = 1 - RMSE(model)/RMSE(persistence), per horizon, over the given origin subset."""
    sub = preds[(preds["condition"] == condition) & (preds["model"] == model)]
    out = {}
    for h in range(1, HORIZON_MAX + 1):
        rmse_m = rmse(sub.loc[sub["horizon"] == h, "y_true"], sub.loc[sub["horizon"] == h, "y_pred"])
        p = persistence[persistence["horizon"] == h]
        rmse_p = rmse(p["y_true"], p["y_pred"])
        out[h] = 1.0 - (rmse_m / rmse_p) if rmse_p and not np.isnan(rmse_p) and rmse_p != 0 else np.nan
    return pd.Series(out).reindex(range(1, HORIZON_MAX + 1))


def hstar_max_run(skill: pd.Series) -> int:
    best = current = 0
    for h in range(1, HORIZON_MAX + 1):
        v = skill.get(h, np.nan)
        if pd.notna(v) and v > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def hstar_from_h1(skill: pd.Series) -> int:
    count = 0
    for h in range(1, HORIZON_MAX + 1):
        v = skill.get(h, np.nan)
        if pd.notna(v) and v > 0:
            count += 1
        else:
            break
    return count


def hstar_relax(skill: pd.Series) -> int:
    positive = [h for h in range(1, HORIZON_MAX + 1) if pd.notna(skill.get(h, np.nan)) and skill.get(h) > 0]
    return max(positive) if positive else 0


def _origin_by_horizon_matrices(preds: pd.DataFrame, condition: str, model: str, origins: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pivot row-level predictions to (n_origins, HORIZON_MAX) matrices, origin-ordered."""
    sub = preds[(preds["condition"] == condition) & (preds["model"] == model)]
    true_p = sub.pivot(index="origin", columns="horizon", values="y_true").reindex(index=origins, columns=range(1, HORIZON_MAX + 1))
    pred_p = sub.pivot(index="origin", columns="horizon", values="y_pred").reindex(index=origins, columns=range(1, HORIZON_MAX + 1))
    return true_p.to_numpy(dtype=float), pred_p.to_numpy(dtype=float)


def _hstar_max_run_from_skill_array(skill: np.ndarray) -> int:
    best = current = 0
    for v in skill:
        if np.isfinite(v) and v > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def _rmse_per_horizon(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """y_true/y_pred: (n_rows, HORIZON_MAX). Returns RMSE per horizon column, NaN-safe."""
    err2 = (y_true - y_pred) ** 2
    valid = np.isfinite(err2)
    with np.errstate(invalid="ignore"):
        counts = valid.sum(axis=0)
        sums = np.where(valid, err2, 0.0).sum(axis=0)
        mean = np.divide(sums, counts, out=np.full(counts.shape, np.nan), where=counts > 0)
    return np.sqrt(mean)


def moving_block_bootstrap_delta_hstar(preds: pd.DataFrame, block_days: int, n_resamples: int, seed: int) -> np.ndarray:
    origins = np.sort(preds["origin"].unique())
    n = len(origins)
    if n <= block_days:
        raise ValueError("Not enough origins for the requested block length.")

    true_pe, pred_pe = _origin_by_horizon_matrices(preds, "reference", "persistence", origins)
    true_lo, pred_lo = _origin_by_horizon_matrices(preds, "lags_only", "xgboost_direct", origins)
    true_lm, pred_lm = _origin_by_horizon_matrices(preds, "lags_meteo", "xgboost_direct", origins)

    rng = np.random.default_rng(seed)
    n_blocks_needed = int(np.ceil(n / block_days))
    max_start = n - block_days  # inclusive, 0-indexed

    deltas = np.empty(n_resamples, dtype=float)
    for b in range(n_resamples):
        starts = rng.integers(0, max_start + 1, size=n_blocks_needed)
        chosen_idx = np.concatenate([np.arange(s, s + block_days) for s in starts])[:n]

        rmse_pe = _rmse_per_horizon(true_pe[chosen_idx], pred_pe[chosen_idx])
        rmse_lo = _rmse_per_horizon(true_lo[chosen_idx], pred_lo[chosen_idx])
        rmse_lm = _rmse_per_horizon(true_lm[chosen_idx], pred_lm[chosen_idx])

        with np.errstate(invalid="ignore", divide="ignore"):
            skill_lo = 1.0 - (rmse_lo / rmse_pe)
            skill_lm = 1.0 - (rmse_lm / rmse_pe)

        deltas[b] = _hstar_max_run_from_skill_array(skill_lm) - _hstar_max_run_from_skill_array(skill_lo)

    return deltas


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    preds = pd.read_csv(PREDICTIONS_PATH, parse_dates=["origin", "forecast_timestamp"])

    persistence = preds[(preds["condition"] == "reference") & (preds["model"] == "persistence")]
    sarima = preds[(preds["condition"] == "reference") & (preds["model"] == "sarima")]

    skill_curves = {
        "persistence": compute_skill_curve(persistence, "reference", "persistence", persistence),
        "sarima": compute_skill_curve(sarima, "reference", "sarima", persistence),
        "lags_only": compute_skill_curve(preds, "lags_only", "xgboost_direct", persistence),
        "lags_meteo": compute_skill_curve(preds, "lags_meteo", "xgboost_direct", persistence),
    }
    skill_df = pd.DataFrame(skill_curves)
    skill_df.index.name = "horizon"
    skill_df.to_csv(OUT_DIR / "skill_curves_S_h.csv")

    hstar_rows = []
    for label in ["sarima", "lags_only", "lags_meteo"]:
        s = skill_curves[label]
        hstar_rows.append(
            {
                "model_condition": label,
                "hstar_strict_max_run": hstar_max_run(s),
                "hstar_strict_from_h1": hstar_from_h1(s),
                "hstar_relax": hstar_relax(s),
            }
        )
    hstar_df = pd.DataFrame(hstar_rows)
    hstar_df.to_csv(OUT_DIR / "hstar_variants.csv", index=False)

    delta_hstar_max_run = int(
        hstar_df.loc[hstar_df.model_condition == "lags_meteo", "hstar_strict_max_run"].iloc[0]
        - hstar_df.loc[hstar_df.model_condition == "lags_only", "hstar_strict_max_run"].iloc[0]
    )
    delta_hstar_from_h1 = int(
        hstar_df.loc[hstar_df.model_condition == "lags_meteo", "hstar_strict_from_h1"].iloc[0]
        - hstar_df.loc[hstar_df.model_condition == "lags_only", "hstar_strict_from_h1"].iloc[0]
    )

    deltas = moving_block_bootstrap_delta_hstar(
        preds=preds,
        block_days=BOOTSTRAP_BLOCK_DAYS,
        n_resamples=BOOTSTRAP_N_RESAMPLES,
        seed=BOOTSTRAP_SEED,
    )
    ci_low, ci_high = np.percentile(deltas, [2.5, 97.5])
    bootstrap_summary = {
        "block_days": BOOTSTRAP_BLOCK_DAYS,
        "n_resamples": BOOTSTRAP_N_RESAMPLES,
        "seed": BOOTSTRAP_SEED,
        "point_estimate_delta_hstar_max_run": delta_hstar_max_run,
        "bootstrap_mean": float(np.mean(deltas)),
        "bootstrap_sd": float(np.std(deltas, ddof=1)),
        "ci95_low": float(ci_low),
        "ci95_high": float(ci_high),
    }
    pd.Series(deltas, name="delta_hstar_max_run").to_csv(OUT_DIR / "bootstrap_delta_hstar_replicates.csv", index=False)
    with (OUT_DIR / "bootstrap_summary.json").open("w") as fh:
        json.dump(bootstrap_summary, fh, indent=2)

    dm_rows = []
    preds_lo = preds[(preds["condition"] == "lags_only") & (preds["model"] == "xgboost_direct")]
    preds_lm = preds[(preds["condition"] == "lags_meteo") & (preds["model"] == "xgboost_direct")]
    for h in DM_HORIZONS:
        dm_rows.append(diebold_mariano_test(preds_a=preds_lo, preds_b=preds_lm, horizon=h, loss="squared_error"))
    dm_df = pd.DataFrame(dm_rows)
    dm_df.to_csv(OUT_DIR / "dm_recomputed.csv", index=False)

    recomputed = {
        "hstar_strict_max_run.lags_only": int(hstar_df.loc[hstar_df.model_condition == "lags_only", "hstar_strict_max_run"].iloc[0]),
        "hstar_strict_max_run.lags_meteo": int(hstar_df.loc[hstar_df.model_condition == "lags_meteo", "hstar_strict_max_run"].iloc[0]),
        "hstar_strict_from_h1.lags_only": int(hstar_df.loc[hstar_df.model_condition == "lags_only", "hstar_strict_from_h1"].iloc[0]),
        "hstar_strict_from_h1.lags_meteo": int(hstar_df.loc[hstar_df.model_condition == "lags_meteo", "hstar_strict_from_h1"].iloc[0]),
        "delta_hstar_strict_max_run": delta_hstar_max_run,
        "dm.h1.p_value": round(float(dm_df.loc[dm_df.horizon == 1, "p_value"].iloc[0]), 3),
        "dm.h1.n": int(dm_df.loc[dm_df.horizon == 1, "n"].iloc[0]),
        "dm.h6.p_value": round(float(dm_df.loc[dm_df.horizon == 6, "p_value"].iloc[0]), 3),
        "dm.h6.n": int(dm_df.loc[dm_df.horizon == 6, "n"].iloc[0]),
        "dm.h12.p_value": round(float(dm_df.loc[dm_df.horizon == 12, "p_value"].iloc[0]), 3),
        "dm.h12.n": int(dm_df.loc[dm_df.horizon == 12, "n"].iloc[0]),
        "dm.h24.p_value": round(float(dm_df.loc[dm_df.horizon == 24, "p_value"].iloc[0]), 3),
        "dm.h24.n": int(dm_df.loc[dm_df.horizon == 24, "n"].iloc[0]),
    }

    comparison = []
    for key, manuscript_value in MANUSCRIPT_CLAIMS.items():
        got = recomputed[key]
        comparison.append(
            {
                "claim": key,
                "manuscript_value": manuscript_value,
                "recomputed_value": got,
                "status": "COINCIDE" if got == manuscript_value else "DIFIERE",
            }
        )
    comparison_df = pd.DataFrame(comparison)
    comparison_df.to_csv(OUT_DIR / "manuscript_comparison.csv", index=False)

    with (OUT_DIR / "delta_hstar_from_h1.json").open("w") as fh:
        json.dump({"delta_hstar_strict_from_h1": delta_hstar_from_h1}, fh, indent=2)

    print(hstar_df.to_string(index=False))
    print()
    print(f"Delta H*_strict,max-run = {delta_hstar_max_run}")
    print(f"Delta H*_strict,from-h1 = {delta_hstar_from_h1}")
    print()
    print(f"Bootstrap 95% CI on Delta H*_strict,max-run: [{ci_low:.1f}, {ci_high:.1f}] (mean={np.mean(deltas):.2f}, sd={np.std(deltas, ddof=1):.2f})")
    print()
    print(dm_df.to_string(index=False))
    print()
    print(comparison_df.to_string(index=False))


if __name__ == "__main__":
    main()
