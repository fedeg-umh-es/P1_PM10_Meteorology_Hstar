# Table 6 — rho1 and H* (extends Table 4 with rho1). NOTE: rho1_evaluation_period_2023 is computed from the 2023 evaluation window reconstructed from saved predictions (training-period 2020-2022 rho1, as reported in the manuscript, could not be recomputed locally: data_raw/ and data_processed/ are gitignored and empty on this machine -- see P1_OVERLEAF_HANDOFF.md).

| station | H_star_strict_lags_only | H_star_relax_lags_only | H_star_strict_lags_meteo | H_star_relax_lags_meteo | H_star_strict_sarima | H_star_relax_sarima | delta_H_star_strict | ceiling | rho1_evaluation_period_2023 |
|---|---|---|---|---|---|---|---|---|---|
| Birr co offlay | 24 | 24 | 24 | 24 | 16 | 24 | 0 | Yes | 0.8067 |
| Dublin Airport | 22 | 24 | 23 | 24 | 24 | 24 | 1 | No | 0.8935 |
| Dundalk Co Louth | 24 | 24 | 24 | 24 | 18 | 24 | 0 | Yes | 0.789 |
| Pearse street dublin | 24 | 24 | 24 | 24 | 17 | 23 | 0 | Yes | 0.8411 |
| Ringsend dublin | 24 | 24 | 24 | 24 | 9 | 20 | 0 | Yes | 0.6619 |
| edenderry co offlay | 16 | 24 | 16 | 24 | 9 | 21 | 0 | No (submaximal tie) | 0.7941 |
| henry street Limerick | 17 | 24 | 24 | 24 | 4 | 17 | 7 | No | 0.8724 |
| porrlaoise co laois | 24 | 24 | 24 | 24 | 17 | 17 | 0 | Yes | 0.8854 |

---
- producer: `audit_p1_tmp/phase11_regenerate_tables.py`
- HEAD SHA: `5596c1c87f8c466813a87f1305a2bbf377d7a98a`
- generated: 2026-08-02T14:39:24.966948+00:00
- source: `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv` sha256=`e8b262e0812da8c1243afcded5d621dcbed51d6dae56dc07a3fe9069c9484d8e`
