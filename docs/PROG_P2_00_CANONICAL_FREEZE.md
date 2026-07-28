# PROG-P2-00 — Canonical repository, datasets and configuration freeze

**Status:** superseded by `docs/PROG_P2_00_PROVENANCE_AUDIT.md` (the repository identity is frozen, but the raw-data provenance closure remains partial)
**Freeze date:** 2026-07-28
**Canonical branch:** `main`
**Canonical commit at freeze:** `1aad811dab0083396dc5c7eee5abebc34276514c`

## 1. Project identity

This repository is the canonical computational repository for **P2 — Operational Meteorology**, historically named **E2-MET**.

- Canonical repository: `fedeg-umh-es/P1_PM10_Meteorology_Hstar`
- Historical local path: `/Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar`
- Naming warning: the `P1_` prefix is historical and must not be interpreted as the current scientific project identifier. The repository belongs operationally to **P2**.
- Rejected as P2 canonical repository: `fedeg-umh-es/e2-met-validation`. Despite the historical E2-MET name, that repository evaluates univariate PM10 models and does not contain the canonical meteorological-predictor experiment.

## 2. Canonical scientific question

Estimate the incremental value of meteorological predictors for hourly PM10 forecasting under leakage-free rolling-origin evaluation, comparing identical models and temporal splits under:

1. `lags_only`
2. `lags_meteo`

The main comparison model is XGBoost-direct, persistence is the primary baseline, and SARIMA is the secondary baseline.

## 3. Canonical Madrid experiment

- Location: Madrid
- Air-quality station: Casa de Campo
- Target: hourly PM10
- Training start: `2019-01-01 00:00:00`
- Test interval: `2023-01-01 00:00:00` to `2023-12-31 23:00:00`
- Forecast horizons: `h=1..24`
- Origin stride: 24 hours
- Validation: expanding rolling-origin
- Minimum training rows: 8,760
- Preprocessing: train-only inside each fold
- Conditions: `lags_only` and `lags_meteo` with shared origins and metrics

### Canonical Madrid dataset

`data_processed/madrid_pm10_meteorology_experiment_base.csv`

Required columns:

- `timestamp`
- `PM10`
- `temp_c`
- `humidity_pct`
- `pressure_hpa`
- `wind_speed_ms`
- `wind_dir_deg`
- `solar_rad_wm2`
- `precip_mm`

Raw Madrid air-quality and meteorological data are not tracked in Git. Their documented source is the Ayuntamiento de Madrid Open Data Portal.

## 4. Canonical Ireland extension

- Domain: eight Irish monitoring stations
- Stations: Birr, Dublin Airport, Dundalk, Pearse St., Ringsend, Edenderry, Limerick and Portlaoise
- Period: training 2020–2022; evaluation January–August 2023, subject to station coverage
- Target: hourly PM10
- Forecast horizons: `h=1..24`
- Protocol: same comparison logic as Madrid
- Data source: EPA Ireland

This extension is part of the current repository evidence, but Madrid remains the reference experiment for the canonical configuration file and run order.

## 5. Frozen configuration

Canonical configuration file:

`code/e2_met_madrid_config.json`

Frozen values:

- lags: `[1, 2, 3, 6, 12, 24, 48, 168]`
- calendar features: hour of day, day of week, month, Julian day
- meteorological features: temperature, humidity, pressure, wind speed, wind direction, solar radiation, precipitation
- XGBoost: 300 estimators, depth 4, learning rate 0.05, subsample 0.9, column subsample 0.9, `n_jobs=1`, seed 42
- SARIMA enabled: order `(1,0,1)`, seasonal order `(1,0,0,24)`, maximum train rows 17,520
- DM-HLN checkpoints: horizons 1, 6, 12 and 24
- DM loss: squared error

Any change to these values requires a new ADR or an explicit amendment to this freeze document.

## 6. Canonical execution order

The authoritative execution sequence is `RUN_ORDER.md`:

1. Build or refresh the aligned Madrid dataset with `code/build_madrid_experiment_base.py`.
2. Execute both experimental conditions using `code/e2_met_madrid_run.py --config code/e2_met_madrid_config.json --condition all`.
3. Generate manuscript-facing tables using `code/e2_met_madrid_tables.py`.
4. Inspect the canonical outputs before using any result in the manuscript.

Smoke runs are not valid evidence for manuscript claims.

## 7. Canonical output artefacts

Madrid outputs:

- `results/e2_met_madrid_pm10/rolling_origins.csv`
- `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`
- `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`
- `results/e2_met_madrid_pm10/metrics/hstar_summary.csv`
- `results/e2_met_madrid_pm10/stats/dm_lags_meteo_vs_lags_only.csv`
- `results/e2_met_madrid_pm10/manuscript_tables/table_metrics_long.csv`
- `results/e2_met_madrid_pm10/manuscript_tables/table_xgboost_horizon_wide.csv`
- `results/e2_met_madrid_pm10/manuscript_tables/table_delta_lags_meteo_vs_lags_only.csv`

Ireland evidence is stored under:

- `results/e2_met_ireland_pm10/`

Comparative evidence is stored under:

- `results/comparison_madrid_ireland/`

## 8. Freeze boundaries

This task freezes identity and provenance only. It does **not** assert that:

- meteorological variables are operationally available at forecast origin;
- all preprocessing is demonstrably train-only;
- all outputs were generated from the frozen commit;
- the manuscript and repository are fully synchronized;
- current numerical claims have passed a fresh reproducibility audit.

Those checks belong to PROG-P2-01 and PROG-P2-02.

## 9. Next mandatory task

**PROG-P2-01 — Construct the meteorological availability contract.**

The contract must classify each meteorological predictor by what is genuinely available at forecast origin and distinguish observed contemporaneous values, lagged observations, forecasts and future leakage.
