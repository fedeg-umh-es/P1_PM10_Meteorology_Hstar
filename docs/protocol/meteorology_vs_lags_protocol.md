# Meteorology vs Lags Protocol

Stations included: Birr co offlay, Dublin Airport, Dundalk Co Louth, Pearse street dublin, Ringsend dublin, edenderry co offlay, henry street Limerick, porrlaoise co laois.

- Target: hourly `PM10`.
- Horizons: `h = 1..24`, preserving the current E2-MET convention.
- Baseline: persistence, evaluated at the same origins and horizons.
- Rolling-origin: expanding windows, test origins in 2023, 24-hour stride, station-wise evaluation.
- Preprocessing: lags and calendar features are generated inside each train/origin context; numeric missing features are imputed with train-window medians only in the upstream rolling script.
- Missingness: stations require usable PM10 and all selected meteorological covariates over the joint period; remaining fold-level missing values are handled train-only.
- Lag features: `PM10` lags `[1, 2, 3, 6, 12, 24, 48, 168]` plus calendar features.
- Meteorology features: `rain`, `temp`, `wetb`, `dewpt`, `vappr`, `rhum`, `msl`, `wdsp`, `wddir`.
- Conditions: `lag_only` and `lag_plus_met`.
- Model family in this pass: `xgboost_direct`, already supported by the repo. No new model family or tuning is introduced.
- Exclusion criteria: missing processed PM10+meteorology panel, less than one year of joint hourly data, median time step other than one hour, or meteorology coverage below 95% in any selected covariate.
- Final diagnostics: `skill_h` versus persistence, `phi_h` as forecast-to-observed standard deviation ratio, `r_h` as forecast-observation correlation, `beta_h` as mean ratio, and `KGE_h` from `(r_h, phi_h, beta_h)`.
