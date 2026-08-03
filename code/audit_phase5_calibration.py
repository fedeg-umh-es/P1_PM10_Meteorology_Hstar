#!/usr/bin/env python3
"""Fase 5 (opcional) -- calibracion.

a) Calibracion nula de H*_strict,max-run: es un maximo sobre 24 ventanas
   candidatas (max-run), luego tiene sesgo positivo por seleccion incluso
   si S(h)=0 en todos los horizontes. Se estima la distribucion nula por
   permutacion: para cada origen de Madrid se decide, con una moneda justa,
   si se intercambian las etiquetas modelo/persistencia para TODOS sus
   horizontes a la vez (preserva la correlacion real entre horizontes
   dentro de un mismo origen, que un simple lanzamiento de moneda iid por
   horizonte no captura), se recomputa S(h) y su max-run, y se repite
   muchas veces con semilla fija.

b) rho1 vs Delta H*_strict: n=9 (Madrid + 8 estaciones irlandesas), con la
   variable dependiente censurada en 0 en los sitios donde el modelo
   lags-only ya alcanza el techo de 24h (no puede haber ganancia porque no
   hay margen por encima de 24h). Se reporta el scatter descriptivo, un OLS
   (replicando la cifra ya publicada en el manuscrito, r=0.58/p=0.10/n=9,
   como control de que los datos usados aqui son los mismos) y una
   regresion Tobit (censura por la derecha en 0 para los sitios con techo)
   como alternativa que sí modela la censura, señalando en ambos casos que
   n=9 no sostiene una afirmacion inferencial.

Uso:
    source .venv_audit/bin/activate
    python3 code/audit_phase5_calibration.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from audit_phase2_madrid_recompute import HORIZON_MAX, _hstar_max_run_from_skill_array, _origin_by_horizon_matrices, _rmse_per_horizon  # noqa: E402

PREDICTIONS_PATH = ROOT / "results" / "e2_met_madrid_pm10" / "predictions" / "predictions_all_models.csv"
OUT_DIR = ROOT / "results" / "audit" / "calibration"
NULL_PERMUTATIONS = 5000
NULL_SEED = 20260803

# rho1 / Delta H*_strict table, transcribed verbatim from
# manuscripts/manuscript_main.tex:801-809 (tab:rho1). Ceiling=True means
# the lags-only model already reaches H*_strict=24h, so Delta H* is
# right-censored at 0 (the latent benefit of meteorology cannot be
# observed because there is no headroom above the 24h horizon cap).
# Edenderry has Delta H*=0 too but the manuscript's own footnote (a)
# attributes it to low predictability, not a ceiling -- kept uncensored.
RHO1_DELTA_HSTAR = pd.DataFrame(
    [
        {"site": "Madrid Casa de Campo", "rho1": 0.957, "delta_hstar": 8, "ceiling": False},
        {"site": "Dundalk (Co. Louth)", "rho1": 0.945, "delta_hstar": 0, "ceiling": True},
        {"site": "Henry St. Limerick", "rho1": 0.876, "delta_hstar": 6, "ceiling": False},
        {"site": "Portlaoise (Co. Laois)", "rho1": 0.864, "delta_hstar": 0, "ceiling": True},
        {"site": "Ringsend Dublin", "rho1": 0.843, "delta_hstar": 0, "ceiling": True},
        {"site": "Pearse St. Dublin", "rho1": 0.842, "delta_hstar": 0, "ceiling": True},
        {"site": "Dublin Airport", "rho1": 0.815, "delta_hstar": 1, "ceiling": False},
        {"site": "Birr (Co. Offaly)", "rho1": 0.815, "delta_hstar": 0, "ceiling": True},
        {"site": "Edenderry (Co. Offaly)", "rho1": 0.804, "delta_hstar": 0, "ceiling": False},
    ]
)


def null_calibration_max_run(preds: pd.DataFrame, n_permutations: int, seed: int) -> np.ndarray:
    origins = np.sort(preds["origin"].unique())
    true_pe, pred_pe = _origin_by_horizon_matrices(preds, "reference", "persistence", origins)
    true_lo, pred_lo = _origin_by_horizon_matrices(preds, "lags_only", "xgboost_direct", origins)

    rng = np.random.default_rng(seed)
    n = len(origins)
    null_max_runs = np.empty(n_permutations, dtype=float)

    for b in range(n_permutations):
        swap = rng.integers(0, 2, size=n).astype(bool)
        perm_true_model = np.where(swap[:, None], true_pe, true_lo)
        perm_pred_model = np.where(swap[:, None], pred_pe, pred_lo)
        perm_true_pers = np.where(swap[:, None], true_lo, true_pe)
        perm_pred_pers = np.where(swap[:, None], pred_lo, pred_pe)

        rmse_model = _rmse_per_horizon(perm_true_model, perm_pred_model)
        rmse_pers = _rmse_per_horizon(perm_true_pers, perm_pred_pers)
        with np.errstate(invalid="ignore", divide="ignore"):
            skill_perm = 1.0 - (rmse_model / rmse_pers)
        null_max_runs[b] = _hstar_max_run_from_skill_array(skill_perm)

    return null_max_runs


def tobit_negloglik(params: np.ndarray, x: np.ndarray, y: np.ndarray, censored: np.ndarray) -> float:
    """Right-censored-at-0 Tobit: observed y for censored=True rows is a
    ceiling at 0 for a latent y* that could be > 0; uncensored rows are
    y* = y exactly. beta0, beta1, log_sigma = params.
    """
    beta0, beta1, log_sigma = params
    sigma = np.exp(log_sigma)
    mu = beta0 + beta1 * x

    ll = 0.0
    # Uncensored observations: standard Gaussian likelihood.
    unc = ~censored
    if unc.any():
        resid = (y[unc] - mu[unc]) / sigma
        ll += np.sum(stats.norm.logpdf(resid) - np.log(sigma))
    # Censored observations (ceiling at 0, latent y* >= 0 is consistent
    # with a right-censoring at 0 from above, i.e. observed = min(y*, 0)
    # only makes sense if y* <= 0 is the uncensored region; here the
    # mechanism is "true benefit could be > 0 but is capped at 0", i.e.
    # observed = 0 whenever y* >= 0. So the censored likelihood
    # contribution is P(y* >= 0) = 1 - Phi((0 - mu) / sigma).
    if censored.any():
        z = (0.0 - mu[censored]) / sigma
        surv = 1.0 - stats.norm.cdf(z)
        surv = np.clip(surv, 1e-12, 1.0)
        ll += np.sum(np.log(surv))
    return -ll


def fit_tobit(x: np.ndarray, y: np.ndarray, censored: np.ndarray) -> dict:
    x0 = np.array([0.0, 0.0, np.log(max(np.std(y), 1.0))])
    res = minimize(tobit_negloglik, x0, args=(x, y, censored), method="Nelder-Mead")
    beta0, beta1, log_sigma = res.x
    return {
        "converged": bool(res.success),
        "beta0": float(beta0),
        "beta1_slope": float(beta1),
        "sigma": float(np.exp(log_sigma)),
        "neg_loglik": float(res.fun),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── a) null calibration ────────────────────────────────────────────
    preds = pd.read_csv(PREDICTIONS_PATH, parse_dates=["origin", "forecast_timestamp"])
    null_draws = null_calibration_max_run(preds, NULL_PERMUTATIONS, NULL_SEED)
    null_summary = {
        "n_permutations": NULL_PERMUTATIONS,
        "seed": NULL_SEED,
        "observed_hstar_max_run_lags_only": 9,
        "null_mean": float(np.mean(null_draws)),
        "null_p50": float(np.percentile(null_draws, 50)),
        "null_p95": float(np.percentile(null_draws, 95)),
        "null_p99": float(np.percentile(null_draws, 99)),
        "fraction_null_ge_observed": float(np.mean(null_draws >= 9)),
    }
    pd.Series(null_draws, name="null_max_run").to_csv(OUT_DIR / "null_max_run_draws.csv", index=False)
    with (OUT_DIR / "null_calibration_summary.json").open("w") as fh:
        json.dump(null_summary, fh, indent=2)

    print("=== a) Calibracion nula de H*_strict,max-run (permutacion, lags_only vs persistence) ===")
    print(json.dumps(null_summary, indent=2))

    # ── b) rho1 vs Delta H*: OLS vs Tobit ──────────────────────────────
    df = RHO1_DELTA_HSTAR.copy()
    x = df["rho1"].to_numpy(dtype=float)
    y = df["delta_hstar"].to_numpy(dtype=float)
    censored = df["ceiling"].to_numpy(dtype=bool)

    ols = stats.linregress(x, y)
    tobit = fit_tobit(x, y, censored)

    comparison = {
        "n": int(len(df)),
        "ols": {
            "slope": float(ols.slope),
            "intercept": float(ols.intercept),
            "r": float(ols.rvalue),
            "p_value": float(ols.pvalue),
        },
        "tobit_right_censored_at_0": tobit,
        "manuscript_reported_ols": {"r": 0.58, "p_value": 0.10, "n": 9},
        "ols_matches_manuscript": bool(round(ols.rvalue, 2) == 0.58 and round(ols.pvalue, 2) == 0.10),
        "caveat": "n=9 (Madrid + 8 estaciones irlandesas); ni el OLS ni el Tobit sostienen una afirmacion inferencial con esta n. Ambos se reportan como diagnostico descriptivo, no como evidencia confirmatoria.",
    }
    df.to_csv(OUT_DIR / "rho1_delta_hstar_table.csv", index=False)
    with (OUT_DIR / "rho1_delta_hstar_regression.json").open("w") as fh:
        json.dump(comparison, fh, indent=2)

    print("\n=== b) rho1 vs Delta H*_strict: OLS vs Tobit (n=9) ===")
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
