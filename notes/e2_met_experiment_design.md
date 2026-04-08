# E2-MET Madrid PM10 Experiment Design

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
