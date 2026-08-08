---
title: "e2_met_repo_audit"
categoria: "PERSONAL"
sub_area: "Personal"
tags:
  - personal
  - recurso
---

# 📌 e2_met_repo_audit

## 🧠 Síntesis y Puntos Clave (TDAH-friendly)
- - `code/build_madrid_experiment_base.py`
- **- Reusable** as the Madrid PM10 + meteorology aligned dataset builder.
- **- Already** materializes `data_processed/madrid_pm10_meteorology_experiment_base.csv`.
- - `code/run_madrid_rolling.py`
- **- Reusable** as proof that Madrid hourly rolling-origin forecasting is already operational.
- **- Contains** the stabilized XGBoost-direct setup, horizon loop, persistence-relative skill, and H* derivation.

## 📄 Contenido Detallado / Referencia
# E2-MET Repo Audit

## Reusable Pieces Already Present

- `code/build_madrid_experiment_base.py`
  - Reusable as the Madrid PM10 + meteorology aligned dataset builder.
  - Already materializes `data_processed/madrid_pm10_meteorology_experiment_base.csv`.
- `code/run_madrid_rolling.py`
  - Reusable as proof that Madrid hourly rolling-origin forecasting is already operational.
  - Contains the stabilized XGBoost-direct setup, horizon loop, persistence-relative skill, and H* derivation.
- `code/rolling_origin.py`
  - Reusable for strict temporal windows.
  - Already provides `generate_rolling_origins`, `get_train_window`, and `get_test_window`.
- `code/models/persistence.py`
  - Reusable persistence baseline implementation.
- `code/models/xgboost_model.py`
  - Reusable direct multi-horizon XGBoost wrapper.
- `code/run_rolling_skill.py`
  - Reusable formulas for RMSE/MAE, skill vs persistence, and H* descriptors.
  - Also shows a clean SARIMA reference implementation path, but only inside the older daily script.
- `code/data_loader.py` and `code/features.py`
  - Reusable only as generic utilities.
  - Not adopted directly for E2-MET because their current defaults are still tied to placeholder repo-level config.

## Gaps Identified

- No clean E2-MET scaffold dedicated to the Madrid comparison `lags-only` vs `lags+meteo`.
- No shared output layout for:
  - common rolling-origin origins
  - per-condition prediction exports
  - manuscript-ready tables
  - Diebold-Mariano inference
- No current script producing DM tests for `lags-only` vs `lags+meteo`.
- No single config file snapshotting the Madrid E2-MET run.
- SARIMA existed conceptually in repo design, but not as a Madrid-specific experiment runner.

## Audit Conclusion

The repo already had the hard parts needed for a minimum viable E2-MET branch:
- Madrid experiment base dataset
- strict rolling-origin utilities
- persistence baseline
- direct XGBoost model
- skill and H* formulas

What was missing was not methodology, but experiment packaging:
- one clean config
- one clean runner
- one clean evaluation/export path
- one clean stats/table layer


---
*Procesado automáticamente por Antigravity (Smart Router)*
