# Table 4 — H* by station/model/criterion for Ireland, with a computationally-derived ceiling flag (previously hand-typed in the manuscript; ceiling='No (submaximal tie)' distinguishes Edenderry from a true ceiling effect, per compute_ceiling_flag)

| station | H_star_strict_lags_only | H_star_relax_lags_only | H_star_strict_lags_meteo | H_star_relax_lags_meteo | H_star_strict_sarima | H_star_relax_sarima | delta_H_star_strict | ceiling |
|---|---|---|---|---|---|---|---|---|
| Birr co offlay | 24 | 24 | 24 | 24 | 16 | 24 | 0 | Yes |
| Dublin Airport | 22 | 24 | 23 | 24 | 24 | 24 | 1 | No |
| Dundalk Co Louth | 24 | 24 | 24 | 24 | 18 | 24 | 0 | Yes |
| Pearse street dublin | 24 | 24 | 24 | 24 | 17 | 23 | 0 | Yes |
| Ringsend dublin | 24 | 24 | 24 | 24 | 9 | 20 | 0 | Yes |
| edenderry co offlay | 16 | 24 | 16 | 24 | 9 | 21 | 0 | No (submaximal tie) |
| henry street Limerick | 17 | 24 | 24 | 24 | 4 | 17 | 7 | No |
| porrlaoise co laois | 24 | 24 | 24 | 24 | 17 | 17 | 0 | Yes |

---
- producer: `audit_p1_tmp/phase11_regenerate_tables.py`
- HEAD SHA: `5596c1c87f8c466813a87f1305a2bbf377d7a98a`
- generated: 2026-08-02T14:39:24.966948+00:00
- source: `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv` sha256=`e8b262e0812da8c1243afcded5d621dcbed51d6dae56dc07a3fe9069c9484d8e`
