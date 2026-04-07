# P1 — Experimental Design

## 1. Objective

This paper quantifies the horizon-dependent marginal value of meteorological exogenous variables in multi-step PM10 forecasting under strict rolling-origin evaluation. The central comparison is between a parsimonious lag-only baseline and progressively richer meteorological input sets. The main scientific question is whether meteorological information adds operational value as forecast horizon increases, and when that gain becomes negligible or negative. Rolling-origin is the credibility mechanism of the study, not its primary contribution.

## 2. Experimental Conditions

- **C0 = persistence**
  - Models: Persistence.
  - Variable groups: current PM10 only.
  - Comparative purpose: reference baseline for all horizons and anchor for skill score computation.

- **C1 = lag-only**
  - Models: ARIMA, SARIMA, XGBoost-direct, LSTM-MIMO.
  - Variable groups: PM10 autoregressive lags; calendar features where applicable.
  - Comparative purpose: parsimonious non-meteorological benchmark.

- **C2 = lag + meteo core**
  - Models: XGBoost-direct, LSTM-MIMO.
  - Variable groups: PM10 lags, calendar features, and the thermo meteorological subset.
  - Comparative purpose: measure the marginal gain of a compact meteorological configuration relative to C1.

- **C3 = lag + meteo extended**
  - Models: XGBoost-direct, LSTM-MIMO.
  - Variable groups: PM10 lags, calendar features, and the extended meteorological set.
  - Comparative purpose: test whether a broader meteorological configuration improves on C2 and C1.

## 3. Dataset and Split

The target variable is hourly PM10 concentration at the Elche Cat. 4 urban background station. The training period is 2017–2022 and the test period is 2023. Forecasting is evaluated in a multi-step setting over horizon \(h = 1, \ldots, H\), where \(H\) remains `[to be fixed in implementation]`. Meteorological covariates may come from ERA5 reanalysis or a local meteorological station. If ERA5 is used as the primary source, the study must be declared explicitly as a retrospective upper-bound assessment.

## 4. Features by Condition

- **Autoregressive lags**
  - PM10 lags \(t-1, t-2, \ldots, t-p\).
  - Seasonal lags for SARIMA where required.

- **Calendar features**
  - Hour of day.
  - Day of week.
  - Month.
  - Julian day.

- **Meteorological exogenous variables**
  - Temperature.
  - Relative humidity.
  - Wind speed.
  - Wind direction.
  - Surface pressure.
  - Precipitation.
  - Solar radiation.
  - Boundary-layer height, if available.

- **Meteorological subgroups**
  - **Core:** temperature, relative humidity, and surface pressure.
  - **Extended:** all available meteorological variables under consideration.

## 5. Rolling-Origin Protocol

Evaluation uses an expanding-window rolling-origin design. Any scaler is fitted only on the current training window. Lag features are constructed only from observations available before each prediction origin. The 2023 test period is never used for model fitting, scaler fitting, or preprocessing. Forecast performance is computed separately at each horizon and then summarized horizon by horizon under the same out-of-sample protocol.

## 6. Models

- Persistence.
- ARIMA.
- SARIMA.
- XGBoost-direct.
- LSTM-MIMO.

Any model-specific settings, including lag depth, ARIMA/SARIMA orders, and final training details, remain `[to be fixed in implementation]`.

## 7. Outputs and Metrics

- RMSE.
- MAE.
- Skill score vs persistence.
- \u0394Skill / \u0394SS for C2 and C3 relative to C1.
- H*(relax).
- H*(strict).

H* must be interpreted with inferential support, using DM/HLN testing or bootstrap confidence intervals.

## 8. Expected Artifacts

- Horizon-wise metrics tables in CSV format.
- Horizon-wise skill curves.
- Lag-only vs lag+meteo comparison plots.
- H* summary table.
- Per-fold results tables.

## 9. Declared Limitations

- Availability and quality of meteorological variables may constrain the final comparison.
- If ERA5 is the main source, the experiment is retrospective and should be interpreted as an upper-bound configuration.
- Boundary-layer height may be unavailable or inconsistently usable and should remain optional.

## 10. Implementation Order

1. data loading
2. feature construction
3. rolling-origin engine
4. baselines
5. ML models
6. metrics and inference
7. result export
