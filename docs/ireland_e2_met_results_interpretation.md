---
title: "ireland_e2_met_results_interpretation"
categoria: "PERSONAL"
sub_area: "Personal"
tags:
  - personal
  - recurso
---

# 📌 ireland_e2_met_results_interpretation

## 🧠 Síntesis y Puntos Clave (TDAH-friendly)
- Source run: `results/e2_met_ireland_pm10/run_metadata.json`
- Dataset: `data_processed/ireland_pm10_meteorology_hourly.csv`
- **Protocol: expanding** rolling-origin, train-only feature imputation, persistence baseline, XGBoost-direct comparison, `lags_only` vs `lags_meteo`.
- **- Full** run completed, not a smoke test.
- **- Conditions:** `lags_only`, `lags_meteo`.
- - Stations: 8.

## 📄 Contenido Detallado / Referencia
# Ireland E2-MET PM10 Results Interpretation

Source run: `results/e2_met_ireland_pm10/run_metadata.json`  
Dataset: `data_processed/ireland_pm10_meteorology_hourly.csv`  
Protocol: expanding rolling-origin, train-only feature imputation, persistence baseline, XGBoost-direct comparison, `lags_only` vs `lags_meteo`.

## Run status

- Full run completed, not a smoke test.
- Conditions: `lags_only`, `lags_meteo`.
- Stations: 8.
- Horizons: `h = 1..24`.
- Prediction rows: 150624.
- Metrics rows: 768.
- DM-HLN rows: 32.

## Main scientific reading

Adding meteorology produces a positive but heterogeneous improvement over lag-only XGBoost across stations and horizons.

The strongest station-level average gains in RMSE skill are:

| Station | Mean delta Skill RMSE | Positive horizons | Negative horizons |
|---|---:|---:|---:|
| Birr co offlay | 0.048 | 22 | 2 |
| Dundalk Co Louth | 0.035 | 20 | 4 |
| Pearse street dublin | 0.034 | 21 | 3 |
| henry street Limerick | 0.026 | 21 | 3 |
| edenderry co offlay | 0.021 | 14 | 10 |
| Ringsend dublin | 0.018 | 20 | 4 |
| porrlaoise co laois | 0.017 | 18 | 6 |
| Dublin Airport | -0.011 | 11 | 13 |

`Dublin Airport` is the main counterexample: meteorology helps at some short horizons but is negative on average across the 24-hour horizon set.

## H* interpretation

`H_star_relax` saturates at 24 hours for both conditions in all stations. Therefore, the relaxed horizon is not discriminative in this full run.

`H_star_strict` shows limited additional separation:

| Station | Strict H* lags_only | Strict H* lags_meteo | Delta |
|---|---:|---:|---:|
| Dublin Airport | 22 | 23 | 1 |
| henry street Limerick | 18 | 24 | 6 |
| all other stations | unchanged | unchanged | 0 |

The correct manuscript framing is that meteorology changes magnitude and consistency of skill more than the relaxed predictability horizon.

## DM-HLN interpretation

The DM-HLN comparison was run at the configured horizons `h = 1, 6, 12, 24`.

Counts by outcome:

| Favours | Count |
|---|---:|
| `lags_meteo` | 23 |
| `lags_only` | 8 |
| `undetermined` | 1 |

Station-level pattern:

| Station | lags_meteo | lags_only | undetermined |
|---|---:|---:|---:|
| Birr co offlay | 4 | 0 | 0 |
| Dublin Airport | 2 | 2 | 0 |
| Dundalk Co Louth | 3 | 1 | 0 |
| Pearse street dublin | 4 | 0 | 0 |
| Ringsend dublin | 3 | 1 | 0 |
| edenderry co offlay | 2 | 2 | 0 |
| henry street Limerick | 3 | 1 | 0 |
| porrlaoise co laois | 2 | 1 | 1 |

This supports a cautious claim of station-dependent meteorological value, not a universal improvement claim.

## Manuscript-safe claims

1. Under identical rolling-origin splits, the meteorological condition improves average RMSE skill in 7 of 8 stations.
2. The gain is heterogeneous across stations and horizons; `Dublin Airport` is the main negative-average case.
3. `H_star_relax` is uninformative for discrimination here because both conditions retain positive skill through 24 hours in every station.
4. `H_star_strict` improves only in `Dublin Airport` and `henry street Limerick`; it is unchanged elsewhere.
5. DM-HLN tests at selected horizons favour `lags_meteo` in 23 of 32 station-horizon comparisons, but this should be reported as horizon-specific evidence rather than a blanket dominance claim.

## Claims to avoid

- Do not claim that meteorology universally improves PM10 forecasting in Ireland.
- Do not claim that meteorology extends `H_star_relax`; it does not under the current 24-hour horizon cap.
- Do not use smoke-test findings as manuscript evidence.
- Do not compare stations without noting differences in coverage and station-specific data quality rules.

## Tables and figures to cite

- `results/e2_met_ireland_pm10/manuscript_tables/table_delta_skill_meteo_vs_lags.csv`
- `results/e2_met_ireland_pm10/manuscript_tables/table_station_hstar_wide.csv`
- `results/e2_met_ireland_pm10/manuscript_tables/table_dm_lags_meteo_vs_lags_only.csv`
- `results/e2_met_ireland_pm10/figures/figure_skill_by_station.png`
- `results/e2_met_ireland_pm10/figures/figure_delta_skill.png`
- `results/e2_met_ireland_pm10/figures/figure_hstar_summary.png`
- `results/e2_met_ireland_pm10/figures/figure_dm_significance.png`


---
*Procesado automáticamente por Antigravity (Smart Router)*
