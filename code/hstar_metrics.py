#!/usr/bin/env python3
"""
hstar_metrics.py

Shared, read-only post-processing layer implementing the H* Methodological
Contract v1.2.1 on top of already-persisted E2-MET row-level predictions.

This module never re-runs, re-fits, or re-seeds any forecasting model. It
only consumes existing `predictions_all_models.csv` / `metrics_all_models.csv`
artifacts (Madrid, Ireland) and derives, in a clean and explicitly separated
way:

  1. Fine-grained loss matrices L_model(d, f, h) / L_baseline(d, f, h), where
     d = station/site, f = rolling-origin forecast start, h = horizon.
  2. Three H* variants per the v1.2.1 contract:
       - Hstar_strict_from_h1  : contiguous positive-skill run starting at
                                  h=1; the first failure cancels the streak.
       - Hstar_strict_max_run  : longest contiguous positive-skill run
                                  located anywhere in h=1..H_max.
       - Hstar_relax           : last horizon with positive skill
                                  (last-passage time; intermittent failures
                                  and recoveries are allowed).
     plus an explicit `ceiling_constrained` flag per variant, True iff the
     computed H* equals H_max (administrative censoring at H_max, not an
     estimate of a true, uncensored useful horizon).
  3. A Moving-Block Bootstrap (MBB) 95% CI for delta H* (lags_meteo minus
     lags_only), which resamples rolling-origin blocks (not individual rows)
     to respect the serial dependence between forecasts issued at nearby
     origins.

See docs/protocol/hstar_v1_2_1_contract.md for the full methodological
write-up and results/e2_met_ireland_pm10_regenerated/hstar_definition_discrepancy.md
for the audit finding that motivated formally separating
Hstar_strict_from_h1 from Hstar_strict_max_run instead of conflating both
under a single "H*_strict" label.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd

HSTAR_VARIANTS: tuple[str, ...] = (
    "Hstar_strict_from_h1",
    "Hstar_strict_max_run",
    "Hstar_relax",
)


# ── 1. Loss matrices ─────────────────────────────────────────────────────────

def compute_loss_matrix(
    predictions: pd.DataFrame,
    default_station: str | None = None,
) -> pd.DataFrame:
    """Add per-row squared/absolute loss to a row-level predictions table.

    The result is the fine-grained L_model(d, f, h) / L_baseline(d, f, h)
    artifact: one row per (station, origin, horizon, condition, model), with
    d = station, f = origin, h = horizon. Rows with model == "persistence"
    are L_baseline; all other rows are L_model. Nothing is aggregated or
    dropped, so the artifact is complete for every origin f and every
    horizon h in the input.
    """
    out = predictions.copy()
    if "station" not in out.columns:
        if default_station is None:
            raise ValueError("predictions has no 'station' column and no default_station was given")
        out.insert(0, "station", default_station)

    y_true = pd.to_numeric(out["y_true"], errors="coerce")
    y_pred = pd.to_numeric(out["y_pred"], errors="coerce")
    error = y_true - y_pred
    out["loss_squared_error"] = error.pow(2)
    out["loss_absolute_error"] = error.abs()

    ordered_cols = [
        "station", "origin", "forecast_timestamp", "horizon", "condition", "model",
        "y_true", "y_pred", "loss_squared_error", "loss_absolute_error",
    ]
    ordered_cols = [c for c in ordered_cols if c in out.columns]
    remaining = [c for c in out.columns if c not in ordered_cols]
    return out[ordered_cols + remaining]


# ── 2. H* v1.2.1 metrics ─────────────────────────────────────────────────────

def hstar_v1_2_1_from_skill(skill: np.ndarray, horizon_max: int) -> dict[str, Any]:
    """Compute the three H* v1.2.1 variants (+ ceiling flags) from a skill
    curve S(h), h = 1..horizon_max (skill[0] is h=1).

    NaN/missing horizons are treated as skill failures (not positive), same
    convention as the pre-existing derive_hstar_from_metrics /
    derive_hstar_ireland implementations in e2_met_madrid_shared.py and
    e2_met_ireland_run.py (kept unmodified; this module reproduces their
    "max run anywhere" and "last horizon with positive skill" logic exactly,
    and adds the from-h1 variant that was previously computed only ad hoc
    for the Ireland regeneration).
    """
    skill = np.asarray(skill, dtype=float)
    if len(skill) != horizon_max:
        raise ValueError(f"skill has length {len(skill)}, expected horizon_max={horizon_max}")
    positive = np.where(np.isnan(skill), False, skill > 0)

    strict_from_h1 = 0
    for is_positive in positive:
        if is_positive:
            strict_from_h1 += 1
        else:
            break

    best = current = 0
    for is_positive in positive:
        if is_positive:
            current += 1
            best = max(best, current)
        else:
            current = 0
    strict_max_run = best

    positive_idx = np.where(positive)[0]
    relax = int(positive_idx.max() + 1) if len(positive_idx) > 0 else 0

    return {
        "Hstar_strict_from_h1": int(strict_from_h1),
        "Hstar_strict_max_run": int(strict_max_run),
        "Hstar_relax": int(relax),
        "ceiling_constrained_strict_from_h1": bool(strict_from_h1 == horizon_max),
        "ceiling_constrained_strict_max_run": bool(strict_max_run == horizon_max),
        "ceiling_constrained_relax": bool(relax == horizon_max),
    }


def derive_hstar_v1_2_1_table(
    metrics: pd.DataFrame,
    group_cols: Sequence[str],
    horizon_max: int,
    skill_col: str = "skill_rmse_vs_persistence",
    model_col: str = "model",
    baseline_model: str = "persistence",
) -> pd.DataFrame:
    """Group `metrics` (one row per group_cols x horizon) by group_cols and
    compute the v1.2.1 H* table. `metrics` must carry `horizon` and
    `skill_col`. Baseline rows (model == baseline_model) get all-zero H*
    (skill vs itself is undefined/zero by convention, matching the
    pre-existing pipelines).
    """
    rows: list[dict[str, Any]] = []
    for key, group in metrics.groupby(list(group_cols), dropna=False):
        key_tuple = key if isinstance(key, tuple) else (key,)
        row: dict[str, Any] = dict(zip(group_cols, key_tuple))
        row["H"] = int(horizon_max)

        is_baseline = model_col in group.columns and (group[model_col] == baseline_model).all()
        if is_baseline:
            row.update({
                "Hstar_strict_from_h1": 0,
                "Hstar_strict_max_run": 0,
                "Hstar_relax": 0,
                "ceiling_constrained_strict_from_h1": False,
                "ceiling_constrained_strict_max_run": False,
                "ceiling_constrained_relax": False,
            })
            rows.append(row)
            continue

        skill = (
            group.set_index("horizon")[skill_col]
            .reindex(range(1, horizon_max + 1))
            .to_numpy(dtype=float)
        )
        row.update(hstar_v1_2_1_from_skill(skill, horizon_max))
        rows.append(row)

    return pd.DataFrame(rows).sort_values(list(group_cols)).reset_index(drop=True)


# ── 3. Moving-Block Bootstrap CI for delta H* ────────────────────────────────

def _mbb_resample_positions(n: int, block_length: int, rng: np.random.Generator) -> np.ndarray:
    """One moving-block-bootstrap resample of positions 0..n-1."""
    block_length = max(1, min(block_length, n))
    n_blocks = int(np.ceil(n / block_length))
    max_start = max(1, n - block_length + 1)
    starts = rng.integers(0, max_start, size=n_blocks)
    idx = np.concatenate([np.arange(s, s + block_length) for s in starts])[:n]
    return idx


def default_block_length(n_origins: int) -> int:
    """n^(1/3) heuristic (Politis & White-style), floor 2."""
    return max(2, int(round(n_origins ** (1 / 3))))


def _rmse_curve(pivot: pd.DataFrame, positions: np.ndarray) -> np.ndarray:
    """RMSE(h) over the resampled rows of a (origin x horizon) squared-error
    pivot table, ignoring NaNs the way the original compute_metrics() does
    (dropna per horizon)."""
    resampled = pivot.to_numpy(dtype=float)[positions, :]
    with np.errstate(invalid="ignore"):
        return np.sqrt(np.nanmean(resampled, axis=0))


def moving_block_bootstrap_delta_hstar(
    loss_matrix: pd.DataFrame,
    station: str,
    horizon_max: int,
    model: str = "xgboost_direct",
    baseline_model: str = "persistence",
    condition_a: str = "lags_only",
    condition_b: str = "lags_meteo",
    n_boot: int = 1000,
    block_length: int | None = None,
    alpha: float = 0.05,
    random_state: int = 42,
) -> dict[str, Any]:
    """Moving-Block Bootstrap 95% CI for delta H* = H*(condition_b) -
    H*(condition_a), for all three v1.2.1 variants at once.

    Resamples blocks of rolling origins (with replacement) jointly across
    condition_a, condition_b and the persistence baseline, so that skill(h)
    is recomputed consistently within each bootstrap replicate from
    L_model(d, f, h) / L_baseline(d, f, h) rather than resampling
    already-aggregated skill curves.
    """
    station_matrix = loss_matrix[loss_matrix["station"] == station]

    def pivot(condition: str, mdl: str) -> pd.DataFrame:
        sub = station_matrix[
            (station_matrix["condition"] == condition) & (station_matrix["model"] == mdl)
        ]
        wide = sub.pivot_table(index="origin", columns="horizon", values="loss_squared_error", aggfunc="mean")
        return wide.reindex(columns=range(1, horizon_max + 1))

    pivot_a = pivot(condition_a, model)
    pivot_b = pivot(condition_b, model)
    baseline_condition = "reference" if "reference" in station_matrix["condition"].unique() else condition_a
    pivot_base = pivot(baseline_condition, baseline_model)

    common_origins = pivot_a.index.intersection(pivot_b.index).intersection(pivot_base.index)
    pivot_a = pivot_a.loc[common_origins]
    pivot_b = pivot_b.loc[common_origins]
    pivot_base = pivot_base.loc[common_origins]
    n_origins = len(common_origins)

    if n_origins == 0:
        empty = {f"delta_{v}": np.nan for v in HSTAR_VARIANTS}
        empty.update({f"delta_{v}_ci_lower": np.nan for v in HSTAR_VARIANTS})
        empty.update({f"delta_{v}_ci_upper": np.nan for v in HSTAR_VARIANTS})
        empty.update({"station": station, "n_origins": 0, "n_boot": n_boot, "block_length": 0})
        return empty

    if block_length is None:
        block_length = default_block_length(n_origins)

    def skill_and_hstar(positions: np.ndarray) -> dict[str, dict[str, Any]]:
        rmse_a = _rmse_curve(pivot_a, positions)
        rmse_b = _rmse_curve(pivot_b, positions)
        rmse_base = _rmse_curve(pivot_base, positions)
        with np.errstate(invalid="ignore", divide="ignore"):
            skill_a = 1.0 - (rmse_a / rmse_base)
            skill_b = 1.0 - (rmse_b / rmse_base)
        return {
            "a": hstar_v1_2_1_from_skill(skill_a, horizon_max),
            "b": hstar_v1_2_1_from_skill(skill_b, horizon_max),
        }

    identity_positions = np.arange(n_origins)
    point = skill_and_hstar(identity_positions)
    point_delta = {v: point["b"][v] - point["a"][v] for v in HSTAR_VARIANTS}

    rng = np.random.default_rng(random_state)
    boot_deltas: dict[str, list[int]] = {v: [] for v in HSTAR_VARIANTS}
    for _ in range(n_boot):
        positions = _mbb_resample_positions(n_origins, block_length, rng)
        result = skill_and_hstar(positions)
        for v in HSTAR_VARIANTS:
            boot_deltas[v].append(result["b"][v] - result["a"][v])

    out: dict[str, Any] = {"station": station, "n_origins": int(n_origins), "n_boot": int(n_boot), "block_length": int(block_length)}
    for v in HSTAR_VARIANTS:
        dist = np.asarray(boot_deltas[v], dtype=float)
        lower, upper = np.percentile(dist, [100 * alpha / 2, 100 * (1 - alpha / 2)])
        out[f"delta_{v}"] = int(point_delta[v])
        out[f"delta_{v}_ci_lower"] = float(lower)
        out[f"delta_{v}_ci_upper"] = float(upper)
    return out
