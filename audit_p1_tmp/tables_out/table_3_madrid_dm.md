# Table 3 — DM-HLN test results for Madrid: lags + met. vs. lags only (recomputed from row-level predictions; note NOTE below on the evaluation-window discrepancy)

| horizon | n | dm_statistic | p_value | p_value_bonferroni_adjusted | favours |
|---|---|---|---|---|---|
| 1 | 354 | 1.169 | 0.2432 | 0.9727 | lags_meteo |
| 6 | 356 | -0.0484 | 0.9614 | 1.0 | lags_only |
| 12 | 346 | 2.5159 | 0.0123 | 0.0493 | lags_meteo |
| 24 | 354 | 0.8469 | 0.3976 | 1.0 | lags_meteo |

---
- producer: `audit_p1_tmp/phase11_regenerate_tables.py`
- HEAD SHA: `5596c1c87f8c466813a87f1305a2bbf377d7a98a`
- generated: 2026-08-02T14:39:24.966948+00:00
- source: `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv` sha256=`e4a7edd656385df4f160176f0952a410848dc456cd5842981f191124189ea85c`
