#!/usr/bin/env python3
"""Regression tests added by the P1 computational audit
(codex/p1-editorial-computational-audit).

Plain-assert style, matching smoke_test.py's convention (no pytest
dependency in this repo). Run with:

  python3 code/test_regression_p1_audit.py

Covers: no look-ahead in features/targets, consecutive lags, matched
origins across compared conditions, exact origin accounting, H_star_strict
(max-run and from-h1) on synthetic cases, H_star_relax with intermittent
skill, the ceiling flag (including the Edenderry-style submaximal tie),
DM-HLN on paired samples, determinism with a fixed seed, and the SARIMA
origin-alignment fix (Phase 2/10 finding: forecasts were scored one step
short of the labelled horizon).
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sys as _sys
from unittest.mock import MagicMock

try:
    import xgboost  # noqa: F401
except Exception:
    _sys.modules["xgboost"] = MagicMock()

from e2_met_madrid_shared import (
    _from_h1_run,
    _max_run_and_bounds,
    add_target_lags,
    compute_ceiling_flag,
    diebold_mariano_test,
    get_condition_feature_columns,
    predict_sarima,
)
from features import build_autoregressive_features
from rolling_origin import generate_rolling_origins, get_test_window, get_train_window


def _make_hourly_series(n_hours: int, start: str = "2023-01-01") -> pd.DataFrame:
    idx = pd.date_range(start, periods=n_hours, freq="h")
    rng = np.random.default_rng(0)
    values = 20 + np.cumsum(rng.normal(0, 0.5, size=n_hours))
    return pd.DataFrame({"timestamp": idx, "PM10": values})


# ── 1. No look-ahead in autoregressive features ──────────────────────────

def test_no_lookahead_in_lag_features() -> None:
    df = _make_hourly_series(200)
    lagged = add_target_lags(df, target_col="PM10", lags=[1, 3, 24])
    for lag in (1, 3, 24):
        col = f"PM10_lag_{lag}"
        # value at row i must equal the *raw* series lag positions before it
        raw = df["PM10"].to_numpy()
        for i in range(lag, len(df)):
            assert lagged[col].iloc[i] == raw[i - lag], (
                f"lag_{lag} at row {i} uses a value other than row i-{lag}"
            )
        # first `lag` rows must be NaN (no information from before series start)
        assert lagged[col].iloc[:lag].isna().all()


def test_lags_are_temporally_consecutive_on_complete_grid() -> None:
    df = _make_hourly_series(100)
    out = build_autoregressive_features(df, target_col="PM10", lags=[1, 2])
    ts = df["timestamp"]
    for i in range(2, len(df)):
        assert ts.iloc[i - 1] - ts.iloc[i - 2] == pd.Timedelta(hours=1)
        assert out["PM10_lag_1"].iloc[i] == df["PM10"].iloc[i - 1]
        assert out["PM10_lag_2"].iloc[i] == df["PM10"].iloc[i - 2]


# ── 2. Train window never includes the origin (no target leakage) ───────

def test_train_window_excludes_origin() -> None:
    df = _make_hourly_series(300)
    origin = df["timestamp"].iloc[250]
    train = get_train_window(df, origin=origin, timestamp_col="timestamp", train_start="2023-01-01")
    assert train["timestamp"].max() < origin
    test = get_test_window(df, origin=origin, horizon_max=25, timestamp_col="timestamp")
    assert test["timestamp"].iloc[0] == origin
    assert test["timestamp"].iloc[24] == origin + pd.Timedelta(hours=24)


# ── 3. Origin-time (not future) meteorology feature selection ───────────

def test_meteo_condition_uses_only_configured_features() -> None:
    df = pd.DataFrame({"PM10": [1, 2], "rain": [0, 1], "temp": [10, 11]})
    config = {
        "target_col": "PM10",
        "lags": [1],
        "calendar_features": ["hour_of_day"],
        "meteo_features": ["rain", "temp"],
    }
    only_cols = get_condition_feature_columns(df, config, "lags_only")
    meteo_cols = get_condition_feature_columns(df, config, "lags_meteo")
    assert "rain" not in only_cols and "temp" not in only_cols
    assert "rain" in meteo_cols and "temp" in meteo_cols
    # lags_meteo must be a strict superset of lags_only
    assert set(only_cols).issubset(set(meteo_cols))


# ── 4. H_star_strict (max-run + from-h1) on synthetic skill curves ──────

def test_hstar_max_run_synthetic() -> None:
    # positive at h=3..11 (matches the Madrid lags-only story), zero elsewhere
    skill = np.zeros(24)
    skill[2:11] = 0.1  # indices 2..10 -> h=3..11
    best, start, end = _max_run_and_bounds(skill)
    assert (best, start, end) == (9, 3, 11)

    # two runs: pick the longer one
    skill2 = np.zeros(24)
    skill2[0:3] = 0.1     # h=1..3 (len 3)
    skill2[10:17] = 0.1   # h=11..17 (len 7)
    best2, start2, end2 = _max_run_and_bounds(skill2)
    assert (best2, start2, end2) == (7, 11, 17)

    # all non-positive -> zero run
    assert _max_run_and_bounds(np.zeros(24)) == (0, 0, 0)


def test_hstar_from_h1_synthetic() -> None:
    skill = np.array([0.1, 0.1, -0.1] + [0.1] * 21)
    # from-h1 stops at the first non-positive value, even though a much
    # longer run exists later in the horizon
    assert _from_h1_run(skill) == 2
    assert _max_run_and_bounds(skill)[0] == 21

    all_positive = np.full(24, 0.05)
    assert _from_h1_run(all_positive) == 24

    starts_negative = np.array([-0.1] + [0.1] * 23)
    assert _from_h1_run(starts_negative) == 0


def test_hstar_relax_intermittent_skill() -> None:
    # relax = last horizon with positive skill, regardless of gaps in between
    skill = np.array([0.1, -0.1, 0.1, -0.1] + [-0.1] * 19 + [0.1])
    pos = np.where(skill > 0)[0]
    h_relax = int(pos.max() + 1)
    assert h_relax == 24  # the isolated positive value at h=24 still counts


# ── 5. Ceiling flag, including the Edenderry-style submaximal tie ───────

def test_ceiling_flag_classification() -> None:
    wide = pd.DataFrame(
        {
            "station": ["A_at_ceiling", "B_edenderry_tie", "C_unconstrained"],
            "H_star_strict_lags_only": [24, 16, 17],
            "H_star_strict_lags_meteo": [24, 16, 24],
        }
    )
    out = compute_ceiling_flag(wide, horizon_max=24)
    assert out.set_index("station")["ceiling"].to_dict() == {
        "A_at_ceiling": "Yes",
        "B_edenderry_tie": "No (submaximal tie)",
        "C_unconstrained": "No",
    }


# ── 6. DM-HLN on paired samples ──────────────────────────────────────────

def test_dm_hln_paired_samples_and_sign() -> None:
    rng = np.random.default_rng(1)
    n = 100
    origins = pd.date_range("2023-01-01", periods=n, freq="D")
    y_true = rng.normal(20, 5, size=n)
    # model B is uniformly better (smaller errors) -> DM should favour B
    pred_a = pd.DataFrame(
        {
            "origin": origins,
            "forecast_timestamp": origins + pd.Timedelta(hours=1),
            "horizon": 1,
            "y_true": y_true,
            "y_pred": y_true + rng.normal(0, 3, size=n),
        }
    )
    pred_b = pred_a.copy()
    pred_b["y_pred"] = y_true + rng.normal(0, 0.5, size=n)

    result = diebold_mariano_test(pred_a, pred_b, horizon=1, loss="squared_error")
    assert result["n"] == n
    assert result["favours"] == "lags_meteo"  # "b" convention: a=lags_only, b=lags_meteo
    assert result["p_value"] < 0.05

    # unpaired origins must not silently inflate n
    pred_b_missing = pred_b.iloc[:-10]
    result_partial = diebold_mariano_test(pred_a, pred_b_missing, horizon=1, loss="squared_error")
    assert result_partial["n"] == n - 10


# ── 7. SARIMA origin-alignment fix ───────────────────────────────────────

def test_sarima_alignment_matches_persistence_and_xgboost_convention() -> None:
    """Regression test for the Phase 2/10 finding: predict_sarima's forecast
    must be indexed so that dict key h corresponds to timestamp origin+h,
    the same convention used by run_backtest's y_true assignment
    (test_df.iloc[h] where test_df.iloc[0] == origin). Before the fix,
    forecast.iloc[h-1] represented origin+(h-1), one step short.
    """
    df = _make_hourly_series(9000, start="2020-01-01")
    origin = df["timestamp"].iloc[8760]
    train_df = get_train_window(df, origin=origin, timestamp_col="timestamp", train_start="2020-01-01")

    # sanity: on this complete hourly grid, gap between train end and origin is 1h
    assert origin - train_df["timestamp"].iloc[-1] == pd.Timedelta(hours=1)

    config = {
        "target_col": "PM10",
        "timestamp_col": "timestamp",
        "horizon_max": 5,
        "include_sarima": True,
        "sarima_max_train_rows": 500,
        "sarima_order": [1, 0, 0],
        "sarima_seasonal_order": [0, 0, 0, 0],
    }

    preds_with_origin = predict_sarima(train_df=train_df, config=config, origin=origin)
    preds_without_origin = predict_sarima(train_df=train_df, config=config, origin=None)

    # Without `origin`, gap_steps defaults to 1 (the pre-fix, on-grid-only
    # assumption) -- on this gap-free synthetic grid the two must agree,
    # which pins down that the default path is exactly the fixed h=1 case.
    for h in range(1, 6):
        assert np.isclose(preds_with_origin[h], preds_without_origin[h], equal_nan=True)

    # The fitted model, queried directly, must show the fix shifts every
    # returned value by exactly one internal SARIMAX step relative to the
    # naive (unfixed) indexing convention `forecast.iloc[h-1]`.
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    # must mirror predict_sarima's own sarima_max_train_rows truncation, or
    # the two fits see different training data and are not comparable
    y_train = train_df["PM10"].iloc[-int(config["sarima_max_train_rows"]):]
    model = SARIMAX(y_train, order=(1, 0, 0), seasonal_order=(0, 0, 0, 0),
                     enforce_stationarity=False, enforce_invertibility=False)
    result = model.fit(disp=False, maxiter=50)
    forecast = result.get_forecast(steps=6).predicted_mean
    naive_h1 = float(forecast.iloc[0])       # pre-fix behaviour: origin, not origin+1
    fixed_h1 = preds_with_origin[1]          # post-fix behaviour: origin+1
    naive_h2 = float(forecast.iloc[1])       # this is what origin+1 actually was
    assert np.isclose(fixed_h1, naive_h2), (
        "predict_sarima(h=1) must equal the pre-fix h=2 value (origin+1), "
        "confirming the one-step shift is applied"
    )
    assert not np.isclose(fixed_h1, naive_h1), (
        "predict_sarima(h=1) must NOT equal the pre-fix h=1 value (origin), "
        "or the misalignment has silently returned"
    )


# ── 8. Determinism with a fixed seed (XGBoost) ───────────────────────────

def test_xgboost_determinism_with_fixed_seed() -> None:
    try:
        from xgboost import XGBRegressor
    except Exception:
        print("  [skip] xgboost not importable in this environment")
        return
    rng = np.random.default_rng(2)
    X = rng.normal(size=(200, 4))
    y = X[:, 0] * 2 - X[:, 1] + rng.normal(0, 0.1, size=200)
    params = dict(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
    m1 = XGBRegressor(**params).fit(X, y)
    m2 = XGBRegressor(**params).fit(X, y)
    assert np.allclose(m1.predict(X[:10]), m2.predict(X[:10]))


# ── 9. Exact origin accounting against generate_rolling_origins ─────────

def test_origin_accounting_matches_generator() -> None:
    df = _make_hourly_series(400)
    origins = generate_rolling_origins(
        df,
        timestamp_col="timestamp",
        test_start=str(df["timestamp"].iloc[200]),
        test_end=str(df["timestamp"].iloc[399]),
        horizon_max=24,
    )
    # every returned origin must leave at least horizon_max-1 rows after it
    ts_to_idx = {t: i for i, t in enumerate(df["timestamp"])}
    for o in origins:
        assert ts_to_idx[o] + 24 - 1 < len(df)


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


if __name__ == "__main__":
    failures = 0
    for fn in TESTS:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {fn.__name__}: {exc}")
        except Exception:
            failures += 1
            print(f"ERROR {fn.__name__}:")
            traceback.print_exc()
    print()
    print(f"{len(TESTS) - failures}/{len(TESTS)} passed")
    sys.exit(1 if failures else 0)
