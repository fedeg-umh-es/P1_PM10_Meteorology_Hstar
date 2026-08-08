---
title: "e2_met_madrid_shared.py"
categoria: "PERSONAL"
sub_area: "Personal"
tags:
  - personal
  - recurso
---

# 📌 e2_met_madrid_shared.py

## 🧠 Síntesis y Puntos Clave (TDAH-friendly)
- **from __future__** import annotations
- import json
- **from pathlib** import Path
- **from typing** import Any
- **import numpy** as np
- **import pandas** as pd
- **from scipy.stats** import t as student_t
- **from sklearn.metrics** import mean_absolute_error, mean_squared_error

## 📄 Contenido Detallado / Referencia
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import t as student_t
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX

from models.xgboost_model import XGBoostDirectForecaster, make_direct_targets
from rolling_origin import generate_rolling_origins, get_test_window, get_train_window


def load_json_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).expanduser().resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    config["config_path"] = str(config_path)
    return config


def ensure_results_dirs(results_dir: str | Path) -> dict[str, Path]:
    base = Path(results_dir).expanduser().resolve()
    paths = {
        "base": base,
        "predictions": base / "predictions",
        "metrics": base / "metrics",
        "stats": base / "stats",
        "manuscript_tables": base / "manuscript_tables",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def load_experiment_dataset(config: dict[str, Any]) -> pd.DataFrame:
    dataset_path = Path(config["dataset_path"]).expanduser().resolve()
    timestamp_col = config["timestamp_col"]
    df = pd.read_csv(dataset_path, parse_dates=[timestamp_col])
    df = df.sort_values(timestamp_col).drop_duplicates(subset=[timestamp_col], keep="last")
    return df.reset_index(drop=True)


def add_calendar_features(df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
    out = df.copy()
    ts = pd.to_datetime(out[timestamp_col])
    out["hour_of_day"] = ts.dt.hour.astype(int)
    out["day_of_week"] = ts.dt.dayofweek.astype(int)
    out["month"] = ts.dt.month.astype(int)
    out["julian_day"] = ts.dt.dayofyear.astype(int)
    return out


def add_target_lags(df: pd.DataFrame, target_col: str, lags: list[int]) -> pd.DataFrame:
    out = df.copy()
    history = pd.to_numeric(out[target_col], errors="coerce").ffill()
    for lag in lags:
        out[f"{target_col}_lag_{lag}"] = history.shift(lag)
    return out


def get_lag_columns(target_col: str, lags: list[int]) -> list[str]:
    return [f"{target_col}_lag_{lag}" for lag in lags]


def get_condition_feature_columns(
    df: pd.DataFrame,
    config: dict[str, Any],
    condition: str,
) -> list[str]:
    target_col = config["target_col"]
    lags = config["lags"]
    lag_cols = get_lag_columns(target_col=target_col, lags=lags)
    calendar_cols = list(config["calendar_features"])
    meteo_cols = [col for col in config["meteo_features"] if col in df.columns]

    if condition == "lags_only":
        return lag_cols + calendar_cols
    if condition == "lags_meteo":
        return lag_cols + calendar_cols + meteo_cols
    raise ValueError(f"Unknown condition: {condition}")


def build_train_frame(
    train_df: pd.DataFrame,
    config: dict[str, Any],
    feature_cols: list[str],
) -> tuple[pd.DataFrame, dict[int, pd.Series], list[str]]:
    timestamp_col = config["timestamp_col"]
    target_col = config["target_col"]
    lags = config["lags"]
    horizon_max = int(config["horizon_max"])

    prepared = add_calendar_features(train_df, timestamp_col=timestamp_col)
    prepared = add_target_lags(prepared, target_col=target_col, lags=lags)
    lag_cols = get_lag_columns(target_col=target_col, lags=lags)
    prepared = prepared.dropna(subset=lag_cols).reset_index(drop=True)
    prepared, y_by_horizon = make_direct_targets(
        df=prepared,
        target_col=target_col,
        horizon_max=horizon_max,
    )
    usable_features = [col for col in feature_cols if col in prepared.columns]
    return prepared, y_by_horizon, usable_features


def build_origin_feature_row(
    context_df: pd.DataFrame,
    origin: pd.Timestamp,
    config: dict[str, Any],
    feature_cols: list[str],
) -> pd.DataFrame:
    timestamp_col = config["timestamp_col"]
    target_col = config["target_col"]
    lags = config["lags"]

    prepared = add_calendar_features(context_df, timestamp_col=timestamp_col)
    prepared = add_target_lags(prepared, target_col=target_col, lags=lags)
    prepared[timestamp_col] = pd.to_datetime(prepared[timestamp_col])
    row = prepared.loc[prepared[timestamp_col] == pd.Timestamp(origin), :]
    usable_features = [col for col in feature_cols if col in row.columns]
    return row[usable_features].iloc[[0]].copy() if not row.empty else pd.DataFrame(columns=usable_features)


def fit_train_feature_medians(train_frame: pd.DataFrame, feature_cols: list[str]) -> pd.Series:
    if not feature_cols:
        return pd.Series(dtype=float)
    return train_frame[feature_cols].median(numeric_only=True)


def apply_feature_medians(df: pd.DataFrame, feature_cols: list[str], medians: pd.Series) -> pd.DataFrame:
    out = df.copy()
    for col in feature_cols:
        if col in out.columns:
            fill_value = medians[col] if col in medians.index and pd.notna(medians[col]) else 0.0
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(fill_value)
    return out


def impute_target_train_only(series: pd.Series) -> pd.Series:
    out = pd.to_numeric(series, errors="coerce").copy()
    out = out.ffill()
    fill_value = float(out.median()) if out.notna().any() else 0.0
    return out.fillna(fill_value)


def fit_xgboost_direct(
    train_df: pd.DataFrame,
    config: dict[str, Any],
    condition: str,
) -> tuple[XGBoostDirectForecaster | None, pd.Series, list[str]]:
    feature_cols = get_condition_feature_columns(df=train_df, config=config, condition=condition)
    train_frame, y_by_horizon, usable_features = build_train_frame(
        train_df=train_df,
        config=config,
        feature_cols=feature_cols,
    )
    if not usable_features:
        return None, pd.Series(dtype=float), usable_features
    if len(train_frame) < max(200, int(config["min_train_rows"]) // 2):
        return None, pd.Series(dtype=float), usable_features

    medians = fit_train_feature_medians(train_frame=train_frame, feature_cols=usable_features)
    train_X = apply_feature_medians(train_frame[usable_features], usable_features, medians)

    model = XGBoostDirectForecaster(
        horizon_max=int(config["horizon_max"]),
        xgb_params=dict(config["xgboost_params"]),
    )
    model.fit(train_X, y_by_horizon)
    return model, medians, usable_features


def predict_xgboost_direct(
    model: XGBoostDirectForecaster | None,
    train_df: pd.DataFrame,
    origin_row_df: pd.DataFrame,
    origin: pd.Timestamp,
    config: dict[str, Any],
    condition: str,
    medians: pd.Series,
    usable_features: list[str],
) -> dict[int, float]:
    horizon_max = int(config["horizon_max"])
    if model is None or not usable_features:
        return {h: np.nan for h in range(1, horizon_max + 1)}

    context_df = pd.concat([train_df, origin_row_df], ignore_index=True)
    x_row = build_origin_feature_row(
        context_df=context_df,
        origin=origin,
        config=config,
        feature_cols=usable_features,
    )
    if x_row.empty:
        return {h: np.nan for h in range(1, horizon_max + 1)}
    x_row = apply_feature_medians(x_row, usable_features, medians)
    preds = model.predict(x_row)
    return {h: float(preds[h][0]) for h in range(1, horizon_max + 1)}


def predict_persistence(train_df: pd.DataFrame, config: dict[str, Any]) -> dict[int, float]:
    target_col = config["target_col"]
    horizon_max = int(config["horizon_max"])
    history = pd.to_numeric(train_df[target_col], errors="coerce").dropna()
    if history.empty:
        return {h: np.nan for h in range(1, horizon_max + 1)}
    last_value = float(history.iloc[-1])
    return {h: last_value for h in range(1, horizon_max + 1)}


def predict_sarima(train_df: pd.DataFrame, config: dict[str, Any]) -> dict[int, float]:
    target_col = config["target_col"]
    horizon_max = int(config["horizon_max"])
    if not bool(config.get("include_sarima", False)):
        return {h: np.nan for h in range(1, horizon_max + 1)}

    y_train = impute_target_train_only(train_df[target_col])

    # Cap training window to avoid Kalman-filter memory crash on long series.
    # 2 years of hourly data is sufficient for SARIMA convergence.
    sarima_max_rows = int(config.get("sarima_max_train_rows", 17520))
    if len(y_train) > sarima_max_rows:
        y_train = y_train.iloc[-sarima_max_rows:]

    try:
        model = SARIMAX(
            y_train,
            order=tuple(config["sarima_order"]),
            seasonal_order=tuple(config["sarima_seasonal_order"]),
            enforce_stationarity=False,
            enforce_invertibility=False,
            simple_differencing=False,
        )
        result = model.fit(disp=False, maxiter=120)
        forecast = result.get_forecast(steps=horizon_max).predicted_mean
        return {h: float(forecast.iloc[h - 1]) for h in range(1, horizon_max + 1)}
    except Exception:
        return {h: np.nan for h in range(1, horizon_max + 1)}


def generate_shared_origins_file(df: pd.DataFrame, config: dict[str, Any], output_path: str | Path) -> pd.DataFrame:
    origins = generate_rolling_origins(
        df=df,
        timestamp_col=config["timestamp_col"],
        test_start=config["test_start"],
        test_end=config["test_end"],
        horizon_max=int(config["horizon_max"]) + 1,
    )
    stride = int(config["origin_stride_hours"])
    origins = origins[::stride]
    out = pd.DataFrame({"origin": pd.to_datetime(origins)})
    out.to_csv(Path(output_path).expanduser().resolve(), index=False)
    return out


def run_backtest(
    config: dict[str, Any],
    condition: str,
    include_references: bool = True,
    max_origins: int | None = None,
) -> pd.DataFrame:
    df = load_experiment_dataset(config)
    timestamp_col = config["timestamp_col"]
    target_col = config["target_col"]
    horizon_max = int(config["horizon_max"])
    train_start = config["train_start"]

    origins = generate_rolling_origins(
        df=df,
        timestamp_col=timestamp_col,
        test_start=config["test_start"],
        test_end=config["test_end"],
        horizon_max=horizon_max + 1,
    )
    origins = origins[:: int(config["origin_stride_hours"])]
    if max_origins is not None:
        origins = origins[:max_origins]

    rows: list[dict[str, Any]] = []
    for origin in origins:
        train_df = get_train_window(
            df=df,
            origin=origin,
            timestamp_col=timestamp_col,
            train_start=train_start,
        )
        test_df = get_test_window(
            df=df,
            origin=origin,
            horizon_max=horizon_max + 1,
            timestamp_col=timestamp_col,
        )
        if len(train_df) < int(config["min_train_rows"]):
            continue
        if len(test_df) < horizon_max + 1:
            continue

        persistence_preds = predict_persistence(train_df=train_df, config=config)
        sarima_preds = predict_sarima(train_df=train_df, config=config)

        model, medians, usable_features = fit_xgboost_direct(
            train_df=train_df,
            config=config,
            condition=condition,
        )
        model_preds = predict_xgboost_direct(
            model=model,
            train_df=train_df,
            origin_row_df=test_df.iloc[:1].copy(),
            origin=origin,
            config=config,
            condition=condition,
            medians=medians,
            usable_features=usable_features,
        )

        for horizon in range(1, horizon_max + 1):
            y_true = pd.to_numeric(pd.Series([test_df[target_col].iloc[horizon]]), errors="coerce").iloc[0]
            if include_references:
                rows.extend(
                    [
                        {
                            "origin": pd.Timestamp(origin),
                            "forecast_timestamp": pd.Timestamp(test_df[timestamp_col].iloc[horizon]),
                            "horizon": horizon,
                            "condition": "reference",
                            "model": "persistence",
                            "y_true": y_true,
                            "y_pred": persistence_preds[horizon],
                        },
                        {
                            "origin": pd.Timestamp(origin),
                            "forecast_timestamp": pd.Timestamp(test_df[timestamp_col].iloc[horizon]),
                            "horizon": horizon,
                            "condition": "reference",
                            "model": "sarima",
                            "y_true": y_true,
                            "y_pred": sarima_preds[horizon],
                        },
                    ]
                )
            rows.append(
                {
                    "origin": pd.Timestamp(origin),
                    "forecast_timestamp": pd.Timestamp(test_df[timestamp_col].iloc[horizon]),
                    "horizon": horizon,
                    "condition": condition,
                    "model": "xgboost_direct",
                    "y_true": y_true,
                    "y_pred": model_preds[horizon],
                }
            )

    preds = pd.DataFrame(rows)
    return preds.sort_values(["model", "condition", "origin", "horizon"]).reset_index(drop=True)


def compute_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    if predictions.empty:
        return pd.DataFrame(
            columns=["condition", "model", "horizon", "n_eval", "mae", "rmse"]
        )
    for (condition, model, horizon), group in predictions.groupby(["condition", "model", "horizon"]):
        valid = group.dropna(subset=["y_true", "y_pred"])
        if valid.empty:
            mae = np.nan
            rmse = np.nan
            n_eval = 0
        else:
            mae = mean_absolute_error(valid["y_true"], valid["y_pred"])
            rmse = float(np.sqrt(mean_squared_error(valid["y_true"], valid["y_pred"])))
            n_eval = int(len(valid))
        records.append(
            {
                "condition": condition,
                "model": model,
                "horizon": int(horizon),
                "n_eval": n_eval,
                "mae": float(mae) if pd.notna(mae) else np.nan,
                "rmse": float(rmse) if pd.notna(rmse) else np.nan,
            }
        )
    return pd.DataFrame(records).sort_values(["model", "condition", "horizon"]).reset_index(drop=True)


def attach_skill_against_persistence(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return metrics.copy()

    baseline = (
        metrics[metrics["model"] == "persistence"][["horizon", "mae", "rmse"]]
        .drop_duplicates(subset=["horizon"])
        .rename(columns={"mae": "mae_persistence", "rmse": "rmse_persistence"})
    )
    out = metrics.merge(baseline, on="horizon", how="left")
    out["skill_mae_vs_persistence"] = 1.0 - (out["mae"] / out["mae_persistence"])
    out["skill_rmse_vs_persistence"] = 1.0 - (out["rmse"] / out["rmse_persistence"])
    out.loc[out["model"] == "persistence", ["skill_mae_vs_persistence", "skill_rmse_vs_persistence"]] = np.nan
    return out


def derive_hstar_from_metrics(metrics: pd.DataFrame, horizon_max: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (condition, model), group in metrics.groupby(["condition", "model"]):
        if model == "persistence":
            rows.append(
                {
                    "condition": condition,
                    "model": model,
                    "H": int(horizon_max),
                    "H_star_relax": 0,
                    "H_star_strict": 0,
                }
            )
            continue
        skill = (
            group.set_index("horizon")["skill_rmse_vs_persistence"]
            .reindex(range(1, horizon_max + 1))
            .to_numpy()
        )
        pos = np.where(skill > 0)[0]
        h_relax = int(pos.max() + 1) if len(pos) > 0 else 0
        best = 0
        current = 0
        for value in skill:
            if pd.notna(value) and value > 0:
                current += 1
                best = max(best, current)
            else:
                current = 0
        rows.append(
            {
                "condition": condition,
                "model": model,
                "H": int(horizon_max),
                "H_star_relax": h_relax,
                "H_star_strict": int(best),
            }
        )
    return pd.DataFrame(rows).sort_values(["model", "condition"]).reset_index(drop=True)


def _loss_series(df: pd.DataFrame, loss: str) -> pd.Series:
    errors = pd.to_numeric(df["y_true"], errors="coerce") - pd.to_numeric(df["y_pred"], errors="coerce")
    if loss == "squared_error":
        return errors.pow(2)
    if loss == "absolute_error":
        return errors.abs()
    raise ValueError(f"Unsupported DM loss: {loss}")


def diebold_mariano_test(
    preds_a: pd.DataFrame,
    preds_b: pd.DataFrame,
    horizon: int,
    loss: str = "squared_error",
) -> dict[str, Any]:
    cols = ["origin", "forecast_timestamp", "horizon", "y_true", "y_pred"]
    left = preds_a.loc[preds_a["horizon"] == horizon, cols].rename(columns={"y_pred": "y_pred_a"})
    right = preds_b.loc[preds_b["horizon"] == horizon, cols].rename(columns={"y_pred": "y_pred_b"})
    merged = left.merge(
        right[["origin", "forecast_timestamp", "horizon", "y_pred_b"]],
        on=["origin", "forecast_timestamp", "horizon"],
        how="inner",
        validate="one_to_one",
    ).dropna(subset=["y_true", "y_pred_a", "y_pred_b"])

    if len(merged) < 10:
        return {
            "horizon": horizon,
            "n": int(len(merged)),
            "dm_stat": np.nan,
            "p_value": np.nan,
            "mean_loss_diff": np.nan,
            "favours": "undetermined",
        }

    loss_a = _loss_series(merged.rename(columns={"y_pred_a": "y_pred"}), loss=loss)
    loss_b = _loss_series(merged.rename(columns={"y_pred_b": "y_pred"}), loss=loss)
    d = loss_a - loss_b
    n = len(d)
    mean_d = float(d.mean())

    gamma0 = float(((d - mean_d) ** 2).sum() / n)
    weighted_sum = 0.0
    max_lag = max(0, horizon - 1)
    for lag in range(1, max_lag + 1):
        cov = float(((d.iloc[lag:] - mean_d) * (d.iloc[:-lag] - mean_d).to_numpy()).sum() / n)
        weighted_sum += 2.0 * cov
    long_run_var = gamma0 + weighted_sum
    if not np.isfinite(long_run_var) or long_run_var <= 0:
        return {
            "horizon": horizon,
            "n": int(n),
            "dm_stat": np.nan,
            "p_value": np.nan,
            "mean_loss_diff": mean_d,
            "favours": "undetermined",
        }

    dm_stat = mean_d / np.sqrt(long_run_var / n)
    h = int(horizon)
    hln = np.sqrt((n + 1 - 2 * h + (h * (h - 1) / n)) / n)
    dm_hln = float(dm_stat * hln)
    p_value = float(2.0 * student_t.sf(abs(dm_hln), df=n - 1))
    favours = "lags_meteo" if mean_d > 0 else "lags_only"

    return {
        "horizon": horizon,
        "n": int(n),
        "dm_stat": dm_hln,
        "p_value": p_value,
        "mean_loss_diff": mean_d,
        "favours": favours,
    }


---
*Procesado automáticamente por Antigravity (Smart Router)*
