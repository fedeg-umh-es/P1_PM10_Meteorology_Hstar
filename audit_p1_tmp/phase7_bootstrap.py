"""P1 audit — Phase 7: moving-block bootstrap over forecast origins.

Uses the existing row-level predictions (already committed under
results/e2_met_madrid_pm10/predictions/ and
results/e2_met_ireland_pm10_regenerated/predictions/) — no raw data needed.

Block bootstrap over ORIGINS (not individual rows), because within one origin
the 24 forecast errors share the same fitted model and are not independent.
Block length = 7 origins (one calendar week), chosen to capture weekly
PM10 seasonality (traffic/weekday-weekend patterns) documented in the
descriptive statistics; not tuned to the data. Same resample indices are
reused for lags_only and lags_meteo to produce a paired delta-H* distribution.

Read-only w.r.t. canonical results; writes only to audit_p1_tmp/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent

RNG_SEED = 20260802
N_BOOT = 2000
BLOCK_LEN = 7


def h_star_from_skill(skill: np.ndarray) -> tuple[int, int]:
    """Return (H_strict_max_run_length, H_relax_last_positive_horizon)."""
    pos = np.where(skill > 0)[0]
    h_relax = int(pos.max() + 1) if len(pos) > 0 else 0
    best = 0
    cur = 0
    for v in skill:
        if np.isfinite(v) and v > 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best, h_relax


def build_origin_matrix(pred: pd.DataFrame, condition: str, model: str) -> tuple[np.ndarray, np.ndarray]:
    """Return (origins sorted, error matrix [n_origins, 24]) of squared errors."""
    sub = pred[(pred["condition"] == condition) & (pred["model"] == model)].copy()
    sub["sq_err"] = (sub["y_true"] - sub["y_pred"]) ** 2
    wide = sub.pivot_table(index="origin", columns="horizon", values="sq_err")
    wide = wide.reindex(columns=range(1, 25)).sort_index()
    return wide.index.to_numpy(), wide.to_numpy()


def rmse_by_horizon(sq_err_mat: np.ndarray) -> np.ndarray:
    return np.sqrt(np.nanmean(sq_err_mat, axis=0))


def moving_block_bootstrap_indices(n: int, block_len: int, n_boot: int, rng: np.random.Generator) -> np.ndarray:
    n_blocks = int(np.ceil(n / block_len))
    starts_pool = np.arange(0, n - block_len + 1)
    out = np.empty((n_boot, n_blocks * block_len), dtype=int)
    for b in range(n_boot):
        starts = rng.choice(starts_pool, size=n_blocks, replace=True)
        idx = np.concatenate([np.arange(s, s + block_len) for s in starts])
        out[b, :] = idx[: n_blocks * block_len]
    return out[:, :n]


def bootstrap_skill_and_hstar(
    pers_mat: np.ndarray,
    lags_mat: np.ndarray,
    meteo_mat: np.ndarray,
    n_boot: int = N_BOOT,
    block_len: int = BLOCK_LEN,
    seed: int = RNG_SEED,
) -> dict:
    n = pers_mat.shape[0]
    rng = np.random.default_rng(seed)
    boot_idx = moving_block_bootstrap_indices(n, block_len, n_boot, rng)

    skill_lags_samples = np.empty((n_boot, 24))
    skill_meteo_samples = np.empty((n_boot, 24))
    hstrict_lags = np.empty(n_boot, dtype=int)
    hstrict_meteo = np.empty(n_boot, dtype=int)
    hrelax_lags = np.empty(n_boot, dtype=int)
    hrelax_meteo = np.empty(n_boot, dtype=int)

    for b in range(n_boot):
        rows = boot_idx[b]
        rmse_pers = rmse_by_horizon(pers_mat[rows])
        rmse_lags = rmse_by_horizon(lags_mat[rows])
        rmse_meteo = rmse_by_horizon(meteo_mat[rows])
        skill_lags = 1.0 - rmse_lags / rmse_pers
        skill_meteo = 1.0 - rmse_meteo / rmse_pers
        skill_lags_samples[b] = skill_lags
        skill_meteo_samples[b] = skill_meteo
        hstrict_lags[b], hrelax_lags[b] = h_star_from_skill(skill_lags)
        hstrict_meteo[b], hrelax_meteo[b] = h_star_from_skill(skill_meteo)

    delta_hstrict = hstrict_meteo - hstrict_lags

    def ci(a, lo=2.5, hi=97.5):
        return np.nanpercentile(a, lo), np.nanpercentile(a, hi)

    skill_ci = pd.DataFrame(
        {
            "horizon": np.arange(1, 25),
            "skill_lags_only_median": np.nanmedian(skill_lags_samples, axis=0),
            "skill_lags_only_lo95": np.nanpercentile(skill_lags_samples, 2.5, axis=0),
            "skill_lags_only_hi95": np.nanpercentile(skill_lags_samples, 97.5, axis=0),
            "skill_lags_meteo_median": np.nanmedian(skill_meteo_samples, axis=0),
            "skill_lags_meteo_lo95": np.nanpercentile(skill_meteo_samples, 2.5, axis=0),
            "skill_lags_meteo_hi95": np.nanpercentile(skill_meteo_samples, 97.5, axis=0),
        }
    )

    hstar_summary = {
        "n_origins": n,
        "n_boot": n_boot,
        "block_len": block_len,
        "H_strict_lags_only_median": float(np.median(hstrict_lags)),
        "H_strict_lags_only_ci95": ci(hstrict_lags),
        "H_strict_lags_meteo_median": float(np.median(hstrict_meteo)),
        "H_strict_lags_meteo_ci95": ci(hstrict_meteo),
        "delta_H_strict_median": float(np.median(delta_hstrict)),
        "delta_H_strict_ci95": ci(delta_hstrict),
        "delta_H_strict_prob_positive": float(np.mean(delta_hstrict > 0)),
        "H_relax_lags_only_median": float(np.median(hrelax_lags)),
        "H_relax_lags_meteo_median": float(np.median(hrelax_meteo)),
    }
    return {"skill_ci": skill_ci, "hstar_summary": hstar_summary}


def run_madrid() -> None:
    pred = pd.read_csv(
        REPO / "results/e2_met_madrid_pm10/predictions/predictions_all_models.csv",
        parse_dates=["origin", "forecast_timestamp"],
    )
    _, pers_mat = build_origin_matrix(pred, "reference", "persistence")
    _, lags_mat = build_origin_matrix(pred, "lags_only", "xgboost_direct")
    _, meteo_mat = build_origin_matrix(pred, "lags_meteo", "xgboost_direct")

    result = bootstrap_skill_and_hstar(pers_mat, lags_mat, meteo_mat)
    result["skill_ci"].to_csv(OUT / "skill_bootstrap_intervals_madrid.csv", index=False)
    pd.DataFrame([result["hstar_summary"]]).to_csv(OUT / "hstar_bootstrap_summary_madrid.csv", index=False)

    print("=== Madrid bootstrap H* summary (block=7 origins, n_boot=2000) ===")
    for k, v in result["hstar_summary"].items():
        print(f"  {k}: {v}")


def run_ireland_station(station: str) -> dict:
    pred = pd.read_csv(
        REPO / "results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv",
        parse_dates=["origin", "forecast_timestamp"],
    )
    pred = pred[pred["station"] == station]
    _, pers_mat = build_origin_matrix(pred, "reference", "persistence")
    _, lags_mat = build_origin_matrix(pred, "lags_only", "xgboost_direct")
    _, meteo_mat = build_origin_matrix(pred, "lags_meteo", "xgboost_direct")
    result = bootstrap_skill_and_hstar(pers_mat, lags_mat, meteo_mat, n_boot=1000)
    return result["hstar_summary"]


if __name__ == "__main__":
    run_madrid()
    print()
    print("=== Ireland bootstrap H* summary (Henry St. Limerick, the +7h outlier) ===")
    summary_henry = run_ireland_station("henry street Limerick")
    for k, v in summary_henry.items():
        print(f"  {k}: {v}")
    pd.DataFrame([summary_henry]).to_csv(OUT / "hstar_bootstrap_summary_henry_st.csv", index=False)
