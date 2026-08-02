# P1 — Overleaf Handoff & Editorial Recommendation Report

## 1. Veredicto Computacional
`VERIFIED_WITH_DOCUMENTATION_ERRORS`

- El pipeline computacional de rolling-origin, feature engineering, predicciones pareadas y pruebas de Diebold-Mariano (DM-HLN) es riguroso, determinista y está libre de look-ahead leakage.
- Todas las métricas tabuladas ($H^*$, DM $p$-valores, diferencias de skill) proceden de predicciones fila a fila trazables guardadas en `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv` y `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv`.
- Discrepancias identificadas: Errores puramente narrativos/documentales en el texto del manuscrito (recuento de estaciones en ceiling, atribuciones causales sobre capa límite sin mediciones directas, y ambigüedad en la definición de horizonte vs run length).

---

## 2. HEAD SHA Canónico
`5596c1c87f8c466813a87f1305a2bbf377d7a98a`

---

## 3. Archivos Fuente Canónicos
- Madrid: `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`
- Madrid Metrics: `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`
- Madrid Stats: `results/e2_met_madrid_pm10/stats/dm_lags_meteo_vs_lags_only.csv`
- Ireland Predictions: `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv`
- Ireland Metrics: `results/e2_met_ireland_pm10_regenerated/metrics/metrics_all_models.csv`
- Ireland Stats: `results/e2_met_ireland_pm10_regenerated/stats/dm_lags_meteo_vs_lags_only.csv`
- Ireland H*: `results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv`
- Nine-Site Summary: `results/derived/nine_site_rho1_delta_hstar.csv`

---

## 4. Tablas Regeneradas
- `results/audit_canonical/table_1_descriptive_statistics.csv` (.md)
- `results/audit_canonical/table_3_madrid_dm.csv` (.md)
- `results/audit_canonical/table_4_ireland_hstar.csv` (.md)
- `results/audit_canonical/table_5_ireland_dm.csv` (.md)
- `results/audit_canonical/table_6_rho1_hstar.csv` (.md)

---

## 5. Figuras Regeneradas (Manifest & Files)
- `results/audit_canonical/figure_manifest.json`
- `manuscripts/figures/madrid_figure_skill_curves.png`
- `manuscripts/figures/madrid_figure_delta_skill.png`
- `manuscripts/figures/madrid_figure_dm_significance.png`
- `manuscripts/figures/madrid_figure_hstar_summary.png`
- `manuscripts/figures/ireland_figure_skill_by_station.png`
- `manuscripts/figures/ireland_figure_delta_skill.png`
- `manuscripts/figures/ireland_figure_dm_significance.png`
- `manuscripts/figures/ireland_figure_hstar_summary.png`
- `manuscripts/figures/figure_rho1_vs_delta_hstar.png`

---

## 6. Cifras Antiguas Incorrectas
1. *"six of eight Irish stations reach $H^*_{\text{strict}} = 24$ h with lags-only"* → **Incorrecto** (solo 5 estaciones alcanzan el techo de 24h: Birr, Dundalk, Pearse St, Ringsend, Portlaoise. Edenderry tiene $H^*=16$ con ambos modelos, por lo que es un empate submáximo, no un efecto techo).
2. *"extends the forecast horizon from 9 h to 17 h"* → **Ambiguo** (9h es la *longitud del tramo* $h=3\dots11$, no un horizonte terminal $h=9$).
3. *"can be parsimoniously explained by"* / *"physical basis lies in boundary-layer dynamics"* → **Sobredimensionado** (no hay mediciones directas de PBLH, gradientes de presión ni clasificación sinóptica).
4. *"two European sites"* → **Impreciso** (son 9 estaciones de monitorización en 2 entornos/países).
5. *"provide exactly this capability"* → **Demasiado categórico** (es un upper bound retrospectivo con meteorología observada, no una evaluación operacional con predicciones meteorológicas reales).

---

## 7. Cifras Nuevas Verificadas
- Estaciones en techo irlandés: **5 de 8** (Birr, Dundalk, Pearse St, Ringsend, Portlaoise).
- Edenderry: $\Delta H^* = 0$ con $H^*_{\text{lags-only}} = 16$ h y $H^*_{\text{lags+met}} = 16$ h (empate submáximo por baja predictibilidad local).
- Madrid tramos de skill positivo: Lags-only $h=3\dots11$ ($H^*_{\text{strict,max-run}} = 9$ h); Lags+met $h=1\dots17$ ($H^*_{\text{strict,max-run}} = 17$ h).
- Madrid DM test a $h=12$: $\text{DM} = 2.52$, $p = 0.012$ (supera el umbral Bonferroni corregido por estación $\alpha_{\text{adj}} = 0.0125$).
- Medias de la red irlandesa: $\bar{\rho}_1 = 0.850$, $\bar{H}^*_{\text{lags-only}} = 21.9$ h, $\bar{H}^*_{\text{lags+met}} = 22.9$ h, $\bar{\Delta H^*} = +1.0$ h.

---

## 8. Cambios Obligatorios en Methods
- Aclarar explícitamente la definición de $H^*_{\text{strict,max-run}}$ como **longitud de tramo contiguo** (run length in hours), no horizonte terminal.
- Declarar explícitamente la familia inferencial de las pruebas de Diebold-Mariano (4 pruebas por estación, umbral Bonferroni de $\alpha = 0.0125$).

---

## 9. Cambios Obligatorios en Results
- Corregir el recuento de estaciones en techo en Irlanda de 6 a 5.
- Explicar la situación de Edenderry como empate submáximo ($16\text{h}/16\text{h}$) y no como efecto techo ($24\text{h}$).

---

## 10. Cambios Obligatorios en Discussion
- Enmarcar la interpretación de la autocorrelación $\rho_1$ y la dinámica de la capa límite como una **hipótesis plausible y consistente con los datos**, reconociendo la ausencia de mediciones directas de PBLH, estabilidad atmosférica o gradientes de presión.

---

## 11. Cambios Obligatorios en Conclusions
- Sustituir "at two European sites" por *"across nine monitoring sites in two European settings"*.
- Enmarcar las recomendaciones de selección de sitios como una hipótesis para priorización operacional sujeta a validación externa.

---

## 12. Afirmaciones que Deben Eliminarse o Debilitarse
- Eliminar la afirmación de que el modelo usa "pressure gradients, wind fields" (las variables son observaciones puntuales de MSL, velocidad/dirección del viento, temp, etc.).
- Debilitar la afirmación "provide exactly this capability" a *"may extend useful skill"*.

---

## 13. Limitaciones que Deben Añadirse
- Documentar en §5.3 (Limitations) la transparencia de la regeneración de las predicciones de Irlanda a partir de los datasets fuente recuperados.
- Declarar la limitación de la meteorología observada como un *upper bound retrospectivo* y la necesidad de evaluar cascadas de error con predicciones meteorológicas operacionales.

---

## 14. Referencias Bibliográficas que Requieren Corrección
- Ninguna alteración de referencias bibTeX necesaria.

---

## 15. Cuestiones Todavía Bloqueadas
- Ningún bloqueo computacional. Todos los artefactos de datos, métricas y gráficos están generados y validados.

---

## 16. Lista Exacta de Archivos que Overleaf Debe Sustituir
- `manuscripts/manuscript_main.tex` (actualizar texto según las recomendaciones de este informe)
- Reemplazar gráficos en `manuscripts/figures/`:
  - `madrid_figure_skill_curves.png`
  - `madrid_figure_delta_skill.png`
  - `madrid_figure_dm_significance.png`
  - `madrid_figure_hstar_summary.png`
  - `ireland_figure_skill_by_station.png`
  - `ireland_figure_delta_skill.png`
  - `ireland_figure_dm_significance.png`
  - `ireland_figure_hstar_summary.png`
  - `figure_rho1_vs_delta_hstar.png`
