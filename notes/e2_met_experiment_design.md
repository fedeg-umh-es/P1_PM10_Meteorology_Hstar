# E2-MET Madrid PM10 Experiment Design

## Canonical Protocol

`E2-MET canonical protocol = Madrid PM10, h=1..24, full expanding rolling-origin over 2023 origins, train-only preprocessing inside each fold, persistence primary baseline, SARIMA secondary baseline, XGBoost-direct main comparison model, lags_only vs lags_meteo under identical splits/metrics, and DM-HLN inference only on the full run.`

## Scope

- Dataset: `data_processed/madrid_pm10_meteorology_experiment_base.csv`
- Target: hourly `PM10`
- Domain: Madrid, station 24, Casa de Campo
- Comparison of interest:
  - Condition A: `lags_only`
  - Condition B: `lags_meteo`
- Baseline: persistence
- Classical reference: SARIMA
- Core ML model: XGBoost-direct

## Scientific Question

Does adding meteorological exogenous variables improve operational predictability beyond lag-only information under identical rolling-origin evaluation?

The core result may be null:
- `delta_skill ≈ 0`
- `delta_H* ≈ 0`

That null result remains publishable and scientifically informative.

## Minimum Viable Design

- Train window:
  - expanding
  - starts at `2019-01-01 00:00:00`
  - ends strictly before each origin
- Test origins:
  - inside `2023-01-01 00:00:00` to `2023-12-31 23:00:00`
  - stride `24` hours
- Forecast horizon:
  - `h = 1..24`
  - taken from the already implemented Madrid branch in the repo
- Same origins, same horizons, same metrics, same persistence baseline for both conditions.

## Two Conditions, Identical Protocol

| Element | Condition A | Condition B |
|---|---|---|
| Label | `lags_only` | `lags_meteo` |
| Features | PM10 lags + calendar | PM10 lags + calendar + meteorology |
| Main model | XGBoost-direct | XGBoost-direct |
| Primary baseline | persistence | persistence |
| Secondary baseline | SARIMA | SARIMA |
| Folds | identical | identical |
| Horizon set | identical | identical |
| Metrics | identical | identical |

The only intended difference between A and B is the inclusion of meteorological covariates.

## Features

- Shared lag block:
  - `PM10_lag_1`
  - `PM10_lag_2`
  - `PM10_lag_3`
  - `PM10_lag_6`
  - `PM10_lag_12`
  - `PM10_lag_24`
  - `PM10_lag_48`
  - `PM10_lag_168`
- Shared calendar block:
  - `hour_of_day`
  - `day_of_week`
  - `month`
  - `julian_day`
- Meteo block:
  - `temp_c`
  - `humidity_pct`
  - `pressure_hpa`
  - `wind_speed_ms`
  - `wind_dir_deg`
  - `solar_rad_wm2`
  - `precip_mm`

## Train-Only Preprocessing

- Lag features are constructed inside each fold using only historical target values.
- Missing target values are never imputed for scoring.
- For lag construction only, PM10 history is forward-filled backward in time order, matching the current Madrid branch behaviour.
- Feature imputation for XGBoost uses train-window medians only.
- No scaler or imputer is fitted on the full dataset.

## Leakage Controls

| Risk | Control |
|---|---|
| Global preprocessing | Feature imputation statistics are fitted on fold-train only |
| Future target leakage | Train window ends strictly before each origin |
| Asymmetric folds between A/B | Both conditions reuse the same rolling origins |
| Random split contamination | No random splits are used anywhere |
| Meteorological leakage | Only meteorology available at the forecast origin timestamp may be used |

## Models

- Persistence:
  - mandatory baseline
  - last observed PM10 repeated for all horizons
- SARIMA:
  - univariate reference
  - fitted only on the train window
  - current scaffold default:
    - order `(1,0,1)`
    - seasonal order `(1,0,0,24)`
  - this order is operational, not scientifically frozen
- XGBoost-direct:
  - one model per horizon
  - same hyperparameters in both conditions
  - no aggressive tuning

SARIMA is part of the canonical workflow as an active secondary baseline.

## Metrics

- Per horizon:
  - `RMSE`
  - `MAE`
  - `Skill_RMSE` vs persistence
  - `Skill_MAE` vs persistence
- Horizon summaries:
  - `H`
  - `H_star_relax`
  - `H_star_strict`
- Statistical comparison:
  - Diebold-Mariano with HLN correction
  - `lags_only` vs `lags_meteo`
  - default horizons: `h=1` and `h=7`
  - default loss: squared error

## Outputs

Per-run outputs:
- `predictions_all_models.csv`
- `metrics_all_models.csv`
- `hstar_summary.csv`
- `dm_lags_meteo_vs_lags_only.csv`

Manuscript-facing outputs:
- `table_metrics_long.csv`
- `table_hstar_summary.csv`
- `table_dm_lags_meteo_vs_lags_only.csv`
- `table_xgboost_horizon_wide.csv`
- `table_delta_lags_meteo_vs_lags_only.csv`

## Output Layout

- `results/e2_met_madrid_pm10/rolling_origins.csv`
- `results/e2_met_madrid_pm10/predictions/`
- `results/e2_met_madrid_pm10/metrics/`
- `results/e2_met_madrid_pm10/stats/`
- `results/e2_met_madrid_pm10/manuscript_tables/`

## Publication Logic

- The comparison is valid even if:
  - `delta_skill ≈ 0`
  - `delta_H* ≈ 0`
  - DM is non-significant
- That null result remains publishable because both conditions are evaluated under identical rolling-origin evidence.
- Smoke-run outputs are pipeline-validation artifacts only and are not manuscript evidence.

## Interpretation Matrix

| Result pattern | Interpretation |
|---|---|
| `delta_H* > 0` and DM significant | Meteorological variables improve operational predictability |
| `delta_H* ≈ 0` and DM non-significant | Meteorology adds no measurable operational value beyond lags |
| `delta_H* < 0` and DM significant | Meteorological variables degrade operational skill and require inspection |
| Positive numerical deltas without significance | Directional trend only; report as inconclusive |

## Manual Confirmations Before Full Run

1. The canonical Madrid base dataset covers the intended 2019 to 2023 window without unexpected shrinkage.
2. Meteorological columns used by `lags_meteo` are observed at the prediction origin timestamp and are not future values.
3. The SARIMA order in the canonical config is accepted as the final paper baseline setting, or is updated once before the full run and then frozen.
4. The full run, not the smoke run, is the source of any manuscript claims.
