"""Fase 1 -- GATE de fuga (bloqueante).

Verifica, con un dataset sintetico trazable "por valor" (no solo por
inspeccion de codigo), que ninguna covariable meteorologica ni ningun lag de
PM10 que entra en el vector de features de un origen de pronostico `t` usa
informacion fechada en `t+1 .. t+h`. Se prueban los DOS flujos identificados
en la Fase 0 (docs/audit/00_inventory.md):

  (a) el motor generico  code/rolling_origin.py
      (run_single_origin_evaluation / run_rolling_backtest) -- codigo
      muerto para Madrid/Irlanda, pero exigido explicitamente por el
      encargo.
  (b) el motor de produccion code/e2_met_madrid_shared.py (run_backtest,
      build_origin_feature_row, predict_xgboost_direct, predict_persistence)
      -- el que genero las cifras publicadas en el manuscrito (Madrid e
      Irlanda comparten este motor).

Truco del dataset trazable: cada columna meteorologica y el propio PM10 se
fijan a una funcion determinista y estrictamente creciente del indice
horario ("reloj"). Si una fila de features contiene el valor del reloj de
un timestamp posterior a `t`, la fuga es detectable comparando valores, sin
tener que leer el codigo.

Ejecucion (sin pytest, con el venv de auditoria):
    source .venv_audit/bin/activate
    python3 tests/test_no_leakage.py

Tambien es descubrible por pytest si esta instalado
(`pytest tests/test_no_leakage.py -v`), pero pytest no es una dependencia
del stack declarado (pandas/numpy/sklearn/statsmodels/xgboost/pyarrow), asi
que no se asume disponible.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

# Flow (a): generic engine
from rolling_origin import (  # noqa: E402
    get_test_window,
    get_train_window,
    run_single_origin_evaluation,
)

# Flow (b): production engine (Madrid + Ireland share this module)
from e2_met_madrid_shared import (  # noqa: E402
    add_target_lags,
    build_origin_feature_row,
    get_condition_feature_columns,
    predict_persistence,
    run_backtest,
)


TARGET_BASE = 1000.0  # offset so PM10 and meteo "clock" values are never confused
N_HOURS = 450
ORIGIN_IDX = 400  # leaves enough post-lag_168 training rows (>=200) for fit_xgboost_direct's floor, and >=24h of horizon after


def _clock_df(timestamp_col: str, target_col: str, meteo_cols: list[str], perturb_from_idx: int | None = None) -> pd.DataFrame:
    """Build a synthetic hourly dataset where every column is a traceable clock.

    - target_col[i] = TARGET_BASE + i
    - each meteo column[i] = i
    - if perturb_from_idx is set, meteo columns for i >= perturb_from_idx are
      replaced with a wildly different value (99_000 + i), so any feature
      row that (incorrectly) reads a future meteo observation is trivially
      distinguishable in value from the correctly-anchored one.
    """
    idx = pd.RangeIndex(N_HOURS)
    timestamps = pd.date_range("2020-01-01", periods=N_HOURS, freq="h")
    data = {timestamp_col: timestamps, target_col: TARGET_BASE + idx.to_numpy(dtype=float)}
    for col in meteo_cols:
        values = idx.to_numpy(dtype=float).copy()
        if perturb_from_idx is not None:
            mask = idx.to_numpy() >= perturb_from_idx
            values = values.copy()
            values[mask] = 99_000.0 + idx.to_numpy(dtype=float)[mask]
        data[col] = values
    return pd.DataFrame(data)


# ─────────────────────────────────────────────────────────────────────────
# Flow (b): production engine (code/e2_met_madrid_shared.py)
# ─────────────────────────────────────────────────────────────────────────

MADRID_METEO_COLS = [
    "temp_c", "humidity_pct", "pressure_hpa",
    "wind_speed_ms", "wind_dir_deg", "solar_rad_wm2", "precip_mm",
]
MADRID_LAGS = [1, 2, 3, 6, 12, 24, 48, 168]

_PROD_CONFIG = {
    "timestamp_col": "timestamp",
    "target_col": "PM10",
    "lags": MADRID_LAGS,
    "calendar_features": ["hour_of_day", "day_of_week", "month", "julian_day"],
    "meteo_features": MADRID_METEO_COLS,
}


def test_flow_b_origin_feature_row_meteo_timestamp_equals_origin_for_every_horizon() -> None:
    """production flow: the feature row meteo value must equal the clock at
    the origin timestamp t, and must be IDENTICAL regardless of which
    horizon h is later predicted from it (the same row feeds every
    horizon-specific XGBoost model -- see XGBoostDirectForecaster.predict).
    """
    df = _clock_df("timestamp", "PM10", MADRID_METEO_COLS)
    origin = df.loc[ORIGIN_IDX, "timestamp"]

    train_df = get_train_window(df, origin=origin, timestamp_col="timestamp", train_start="2020-01-01")
    test_df = get_test_window(df, origin=origin, horizon_max=25, timestamp_col="timestamp")
    origin_row_df = test_df.iloc[:1].copy()  # exactly what run_backtest passes

    feature_cols = get_condition_feature_columns(df=df, config=_PROD_CONFIG, condition="lags_meteo")
    context_df = pd.concat([train_df, origin_row_df], ignore_index=True)
    row = build_origin_feature_row(context_df=context_df, origin=origin, config=_PROD_CONFIG, feature_cols=feature_cols)

    assert len(row) == 1, "build_origin_feature_row must return exactly one row (horizon-invariant)"
    for col in MADRID_METEO_COLS:
        got = float(row.iloc[0][col])
        assert got == float(ORIGIN_IDX), (
            f"LEAK in flow (b): meteo column {col!r} = {got}, expected clock({ORIGIN_IDX}) "
            f"(the origin timestamp). A value from a later index would mean a future observation "
            f"reached the feature vector."
        )

    lag_cols = {f"PM10_lag_{lag}": lag for lag in MADRID_LAGS}
    for col, lag in lag_cols.items():
        expected_idx = ORIGIN_IDX - lag
        got = float(row.iloc[0][col])
        assert got == TARGET_BASE + expected_idx, (
            f"LEAK in flow (b): {col} = {got}, expected clock({expected_idx}) i.e. PM10 at t-{lag}."
        )
        assert expected_idx < ORIGIN_IDX, "sanity: every lag must reference an index strictly before the origin"


def test_flow_b_feature_row_invariant_to_perturbing_the_future() -> None:
    """Strongest black-box check: perturb every meteo observation strictly
    AFTER the origin (t+1 .. end) to an out-of-range value, leaving
    everything at and before the origin untouched, and confirm the built
    feature row for that same origin is byte-for-byte identical to the
    unperturbed dataset's. If any future value leaked into the feature
    vector for any horizon, this would change under perturbation.
    """
    df_clean = _clock_df("timestamp", "PM10", MADRID_METEO_COLS)
    df_perturbed = _clock_df("timestamp", "PM10", MADRID_METEO_COLS, perturb_from_idx=ORIGIN_IDX + 1)
    origin = df_clean.loc[ORIGIN_IDX, "timestamp"]
    feature_cols = get_condition_feature_columns(df=df_clean, config=_PROD_CONFIG, condition="lags_meteo")

    rows = {}
    for label, df in (("clean", df_clean), ("perturbed", df_perturbed)):
        train_df = get_train_window(df, origin=origin, timestamp_col="timestamp", train_start="2020-01-01")
        test_df = get_test_window(df, origin=origin, horizon_max=25, timestamp_col="timestamp")
        origin_row_df = test_df.iloc[:1].copy()
        context_df = pd.concat([train_df, origin_row_df], ignore_index=True)
        rows[label] = build_origin_feature_row(context_df=context_df, origin=origin, config=_PROD_CONFIG, feature_cols=feature_cols)

    pd.testing.assert_frame_equal(rows["clean"].reset_index(drop=True), rows["perturbed"].reset_index(drop=True))


def test_flow_b_persistence_anchor_is_y_tminus1() -> None:
    df = _clock_df("timestamp", "PM10", MADRID_METEO_COLS)
    origin = df.loc[ORIGIN_IDX, "timestamp"]
    train_df = get_train_window(df, origin=origin, timestamp_col="timestamp", train_start="2020-01-01")

    preds = predict_persistence(train_df=train_df, config={"target_col": "PM10", "horizon_max": 24})
    expected = TARGET_BASE + (ORIGIN_IDX - 1)
    assert set(preds.values()) == {expected}, (
        f"Persistence anchor must be y_(t-1)={expected} for every horizon; got {preds}"
    )


def test_flow_b_end_to_end_run_backtest_invariant_to_future_meteo() -> None:
    """Full run_backtest() integration check (not just the unit-level
    feature builder): fit + predict on the clean vs. future-perturbed
    dataset and confirm xgboost_direct predictions for the shared origin
    are identical. A tiny, fast XGBoost config is used; this is a leakage
    check, not a skill benchmark.
    """
    config = dict(_PROD_CONFIG)
    config.update(
        {
            "experiment_name": "leak_test",
            "train_start": "2020-01-01",
            "test_start": None,  # set per-run below
            "test_end": None,
            "horizon_max": 4,
            "origin_stride_hours": 24,
            "min_train_rows": 100,
            "xgboost_params": {
                "n_estimators": 5,
                "max_depth": 2,
                "learning_rate": 0.3,
                "subsample": 1.0,
                "colsample_bytree": 1.0,
                "objective": "reg:squarederror",
                "random_state": 42,
                "n_jobs": 1,
            },
            "include_sarima": False,
            "sarima_max_train_rows": 1000,
            "sarima_order": [1, 0, 1],
            "sarima_seasonal_order": [1, 0, 0, 24],
            "dm_horizons": [1],
            "dm_loss": "squared_error",
        }
    )

    df_clean = _clock_df("timestamp", "PM10", MADRID_METEO_COLS)
    df_perturbed = _clock_df("timestamp", "PM10", MADRID_METEO_COLS, perturb_from_idx=ORIGIN_IDX + 1)
    origin_ts = df_clean.loc[ORIGIN_IDX, "timestamp"]
    config["test_start"] = str(origin_ts)
    config["test_end"] = str(origin_ts)

    import e2_met_madrid_shared as shared

    results = {}
    for label, df in (("clean", df_clean), ("perturbed", df_perturbed)):
        original_loader = shared.load_experiment_dataset
        shared.load_experiment_dataset = lambda cfg, _df=df: _df.copy()  # type: ignore[assignment]
        try:
            preds = run_backtest(config=config, condition="lags_meteo", include_references=False, max_origins=1)
        finally:
            shared.load_experiment_dataset = original_loader
        results[label] = preds.set_index("horizon")["y_pred"].to_dict()

    assert results["clean"] == results["perturbed"], (
        f"LEAK in flow (b) end-to-end run_backtest(): predictions differ when future meteo is "
        f"perturbed. clean={results['clean']} perturbed={results['perturbed']}"
    )


# ─────────────────────────────────────────────────────────────────────────
# Flow (a): generic engine (code/rolling_origin.py) -- dead code, but the
# task requires testing it explicitly.
# ─────────────────────────────────────────────────────────────────────────

ELCHE_METEO_COLS = [
    "temperature", "relative_humidity", "surface_pressure",
    "wind_speed", "wind_direction", "precipitation", "solar_radiation",
    "boundary_layer_height",
]
ELCHE_LAGS = [1, 2, 3, 6, 12, 24, 48, 168]


class _NoOpModel:
    def fit(self, X, y):  # noqa: N803
        self.fitted_ = True
        return self


def test_flow_a_run_single_origin_evaluation_leaks_future_meteo_for_h_gt_1() -> None:
    """rolling_origin.run_single_origin_evaluation builds `prepared_test`
    over the whole train+test window and reads
    `prepared_test.iloc[step - 1]` per horizon `step`. Because meteo columns
    are not lagged (see features.select_features_by_condition: meteo_core /
    meteo_extended are used as raw columns), row `step-1` for `step > 1` is
    timestamped at `origin + (step - 1)`, i.e. a genuinely future
    observation relative to the origin. This test proves it by value.
    """
    df = _clock_df("datetime", "value", ELCHE_METEO_COLS)
    origin = df.loc[ORIGIN_IDX, "datetime"]

    captured: dict[int, dict[str, float]] = {}

    def _capturing_predict(model, prepared_test, feature_cols, target_col, step):  # noqa: ANN001
        row = prepared_test.iloc[step - 1]
        captured[step] = {col: float(row[col]) for col in ELCHE_METEO_COLS}
        return 0.0

    run_single_origin_evaluation(
        df=df,
        origin=origin,
        condition="C3",
        horizon_max=24,
        model_factory=_NoOpModel,
        predict_function=_capturing_predict,
        lags=ELCHE_LAGS,
        timestamp_col="datetime",
        target_col="value",
    )

    # h = 1: row is exactly the origin row -> meteo clock must equal ORIGIN_IDX.
    for col in ELCHE_METEO_COLS:
        assert captured[1][col] == float(ORIGIN_IDX), (
            f"unexpected: even h=1 does not read the origin timestamp for {col}"
        )

    # h > 1: the hypothesis under test. Demonstrate that the meteo value
    # used moves in lock-step with the horizon, i.e. it is read from
    # origin + (h - 1), a future timestamp relative to t.
    leaking_horizons = []
    for step in (2, 6, 12, 24):
        expected_leak_value = float(ORIGIN_IDX + step - 1)
        actual = captured[step][ELCHE_METEO_COLS[0]]
        if actual == expected_leak_value:
            leaking_horizons.append(step)

    assert leaking_horizons == [2, 6, 12, 24], (
        f"expected flow (a) to leak meteo at every h>1 tested (2,6,12,24); "
        f"only leaked at {leaking_horizons}. captured={captured}"
    )


def test_flow_a_run_single_origin_evaluation_leaks_future_pm10_lag_for_h_gt_1() -> None:
    """Same mechanism, but for the PM10 lag_1 feature: because lags are
    computed on the train+test concatenation before slicing per horizon,
    lag_1 at horizon h ends up referencing the ACTUAL (not forecast) PM10
    value at origin + h - 2, which for h >= 2 is at or after the origin --
    i.e. it uses the true realised outcome of an earlier horizon as a
    feature, not a forecast issued at t.
    """
    df = _clock_df("datetime", "value", ELCHE_METEO_COLS)
    origin = df.loc[ORIGIN_IDX, "datetime"]

    captured: dict[int, float] = {}

    def _capturing_predict(model, prepared_test, feature_cols, target_col, step):  # noqa: ANN001
        row = prepared_test.iloc[step - 1]
        captured[step] = float(row["value_lag_1"])
        return 0.0

    run_single_origin_evaluation(
        df=df,
        origin=origin,
        condition="C1",
        horizon_max=24,
        model_factory=_NoOpModel,
        predict_function=_capturing_predict,
        lags=ELCHE_LAGS,
        timestamp_col="datetime",
        target_col="value",
    )

    # h = 1: lag_1 must be exactly y_(t-1) -- correct behaviour.
    assert captured[1] == TARGET_BASE + (ORIGIN_IDX - 1)

    # h = 24: lag_1 ends up at origin + 22, i.e. 23 hours *after* the true
    # issuance boundary (t - 1). This is a violation of "ningun lag usado
    # tiene timestamp >= t".
    idx_used_at_h24 = captured[24] - TARGET_BASE
    assert idx_used_at_h24 >= ORIGIN_IDX, (
        f"expected flow (a) to violate the lag<t rule at h=24 "
        f"(index used={idx_used_at_h24}, origin index={ORIGIN_IDX}); "
        f"if this now holds, flow (a) may have been fixed and the verdict should be re-checked."
    )


def test_flow_a_persistence_c0_anchor_is_y_tminus1() -> None:
    """The C0 (persistence) branch of run_single_origin_evaluation does not
    depend on `step`, and is expected to remain correctly anchored at
    y_(t-1) even though the non-baseline path (tested above) leaks.
    """
    df = _clock_df("datetime", "value", ELCHE_METEO_COLS)
    origin = df.loc[ORIGIN_IDX, "datetime"]

    result = run_single_origin_evaluation(
        df=df,
        origin=origin,
        condition="C0",
        horizon_max=24,
        model_factory=None,
        predict_function=None,
        lags=ELCHE_LAGS,
        timestamp_col="datetime",
        target_col="value",
    )
    expected = TARGET_BASE + (ORIGIN_IDX - 1)
    assert (result["y_pred"] == expected).all(), "C0 persistence anchor must be y_(t-1) for every horizon"


# ─────────────────────────────────────────────────────────────────────────
# Minimal runner (no pytest dependency)
# ─────────────────────────────────────────────────────────────────────────

def _run_all() -> int:
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    failures = 0
    for name, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {name}\n    {exc}")
        except Exception:  # noqa: BLE001
            failures += 1
            print(f"ERROR {name}")
            traceback.print_exc()
        else:
            print(f"PASS {name}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
