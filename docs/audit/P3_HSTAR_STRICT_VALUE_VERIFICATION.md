# P3 H* Strict Value Verification

## Repository
- Path: /Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland
- Branch: codex/p3-hstar-strict-manuscript-repair
- Start SHA: bdc91fa3c05c324ca5c8c39a8222dc5931407fbc

## Computational contract
- Implementation file: `code/run_rolling_skill.py` / `code/e2_met_madrid_run.py` / `code/compare_ireland_regenerated_to_manuscript.py`
- Relevant function: `derive_hstar_from_metrics` / `compute_hstar_both_defs`
- Strict-skill criterion: $S_m(h) > 0$ relative to persistence baseline ($S_m(h) = 1 - \text{RMSE}_m(h)/\text{RMSE}_p(h) > 0$)
- Baseline: Persistence ($\hat{y}_{t+h\mid t} = y_t$)
- Horizon range: $h \in \{1, 2, \dots, 24\}$ hours
- Unit: Hours (h)

## Madrid
- System: XGBoost-direct (`lags_meteo`)
- Comparator: XGBoost-direct (`lags_only`)
- H_strict_max_run values: `lags_meteo` = 17 h, `lags_only` = 9 h
- H_strict_from_h1 values: `lags_meteo` = 17 h, `lags_only` = 9 h
- Maximum-run horizons: `lags_meteo` $h \in [1, 17]$, `lags_only` $h \in [1, 9]$
- Delta: $\Delta H^*_{\text{strict,max-run}} = 17 - 9 = +8$ h
- Status of +8 h claim: `VERIFIED_UNDER_H_STRICT_MAX_RUN`
- Supporting files: `results/e2_met_madrid_pm10/metrics/hstar_summary.csv`, `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`

## Ireland

| Station | H_strict_max_run (lags_only) | H_strict_max_run (lags_meteo) | Comparator | Delta max-run | Verification status |
|---|---:|---:|---:|---:|---|
| Birr (Co. Offaly) | 24 | 24 | XGBoost | 0 h | Verified |
| Dublin Airport | 22 | 23 | XGBoost | +1 h | Verified |
| Dundalk (Co. Louth) | 24 | 24 | XGBoost | 0 h | Verified |
| Pearse St. Dublin | 24 | 24 | XGBoost | 0 h | Verified |
| Ringsend Dublin | 24 | 24 | XGBoost | 0 h | Verified |
| Edenderry (Co. Offaly) | 16 | 16 | XGBoost | 0 h | Verified |
| Henry St. Limerick | 17 | 24 | XGBoost | +7 h | Verified (Updated from +6 h / 18 h) |
| Portlaoise (Co. Laois) | 24 | 24 | XGBoost | 0 h | Verified |

## Henry Street
- Previous manuscript value: 18 h (`lags_only`), $\Delta H^* = +6$ h
- Verified value: 17 h (`lags_only`), 24 h (`lags_meteo`), $\Delta H^* = +7$ h
- Maximum-run interval: `lags_only` $h \in [3, 19]$ (length 17 h)
- Status: `VERIFIED_UNDER_H_STRICT_MAX_RUN`

## Ireland mean
- Stations included: 8 stations (Birr, Dublin Airport, Dundalk, Pearse St, Ringsend, Edenderry, Henry St Limerick, Portlaoise)
- Values averaged (`lags_only`): `[24, 22, 24, 24, 24, 16, 17, 24]`
- Full-precision mean (`lags_only`): 21.875 h
- Displayed rounded mean (`lags_only`): 21.9 h (Updated from 22.0 h)
- Values averaged (`lags_meteo`): `[24, 23, 24, 24, 24, 16, 24, 24]`
- Full-precision mean (`lags_meteo`): 22.875 h
- Displayed rounded mean (`lags_meteo`): 22.9 h
- Mean Delta ($\Delta H^*$): $22.875 - 21.875 = 1.000$ h $\approx$ +1.0 h (Updated from +0.9 h)
- Status: `VERIFIED`

## Evidence provenance
- Madrid: `VERIFIED_PRIMARY` (Full row-level predictions, metrics, and metadata committed)
- Ireland: `VERIFIED_REGENERATED_ONLY` (Regenerated from recovered source datasets; original run row-level predictions not committed in Git history)

## Verification verdict
- `VERIFIED`
