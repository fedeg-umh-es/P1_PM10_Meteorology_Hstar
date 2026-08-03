# RESULTS_CANONICAL.md

Tabla de toda cifra numérica relevante que aparece en
`manuscripts/manuscript_main.tex`, su valor recomputado por esta auditoría
(rama `claude/audit-p1-meteorology-0ehg5v`), y su etiqueta de evidencia.
Ver `results/NUMBERS_FOR_MANUSCRIPT.json` para el mismo contenido en
formato máquina, y `docs/audit/00_inventory.md` .. `05_calibration.md` para
el detalle de cada fase.

**Ninguna cifra alcanza `VERIFIED_PRIMARY`** en este entorno: los datasets
base de Madrid e Irlanda no existen aquí (`docs/audit/00_inventory.md`
§5), así que nada se reentrenó desde cero. Todo lo etiquetado `REPRODUCED`
se recalculó directamente desde predicciones row-level ya trackeadas en
git, con el mismo código de producción verificado libre de fuga en la
Fase 1.

## Madrid

| Cifra del manuscrito | Valor manuscrito | Valor recomputado | Estado | Evidencia |
|---|---:|---:|---|---|
| H*_strict lags_only | 9 | 9 | COINCIDE | REPRODUCED |
| H*_relax lags_only | 15 | 15 | COINCIDE | REPRODUCED |
| H*_strict SARIMA | 8 | 8 | COINCIDE | REPRODUCED |
| H*_relax SARIMA | 20 | 20 | COINCIDE | REPRODUCED |
| H*_strict lags_meteo | 17 | 17 | COINCIDE | REPRODUCED |
| H*_relax lags_meteo | 17 | 17 | COINCIDE | REPRODUCED |
| ΔH*_strict | +8 | +8 | COINCIDE | REPRODUCED |
| DM h=1: n, p | 354, 0.243 | 354, 0.243 | COINCIDE | REPRODUCED |
| DM h=6: n, p | 356, 0.961 | 356, 0.961 | COINCIDE | REPRODUCED |
| DM h=12: n, p | 346, 0.012 | 346, 0.012 | COINCIDE | REPRODUCED |
| DM h=24: n, p | 354, 0.398 | 354, 0.398 | COINCIDE | REPRODUCED |
| ρ₁ (2020-2022) | 0.957 | — (transcrito, no recomputado: dataset ausente) | — | TRANSCRIBED_FROM_MANUSCRIPT |
| H*_strict,from-h1 lags_only | *(no reportado con este nombre)* | 0 | NUEVO | REPRODUCED |
| H*_strict,from-h1 lags_meteo | *(no reportado con este nombre)* | 17 | NUEVO | REPRODUCED |
| IC95% de ΔH* | *("≈[-7,+12]" en el encargo de auditoría, no en el manuscrito)* | **[-8, +13]** (bootstrap bloques móviles, semilla 20260803) | N/A — cifra de referencia no existe en el repo | REPRODUCED (nuevo) |
| Calibración nula H*_strict,max-run (lags_only=9) | *(no existía)* | mediana nula=9.0, p95=24, 57% de permutaciones ≥9 | NUEVO | REPRODUCED |
| ΔH*_strict, ventana ene-jul (la que la Metodología dice usar) | *(no reportado por separado)* | **+10h** (no +8h) | NUEVO — discrepancia de ventana | REPRODUCED |
| DM h=12, ventana ene-jul | *(no reportado por separado)* | n=206, p=0.045 (no sobrevive Bonferroni α_adj=0.0125) | NUEVO — discrepancia de ventana | REPRODUCED |

**Discrepancias de prosa/definición encontradas (no se corrigió el
manuscrito, regla del encargo):**
- La descripción de Resultados (L387-389) dice que `lags_only` tiene skill
  positivo "from h=1 through approximately h=11"; la curva S(h) recomputada
  muestra S(h=1)=-0.006 y S(h=2)=-0.026 (negativos). La racha real de 9h es
  h=3-11, no h=1-11.
- Metodología (L359-361) define `H*_strict` como racha desde h=1
  ("from-h1"); las tablas de Resultados usan en realidad "racha más larga
  en cualquier punto" ("max-run"). Mismo patrón que ya se había documentado
  para Irlanda.
- Metodología (L280) y pie de `tab:descriptive` (L234) declaran la
  evaluación como enero-julio 2023; las cifras de las tablas de Resultados
  sólo son reproducibles con la ventana enero-diciembre 2023 (362 orígenes
  trackeados en `predictions_all_models.csv`, no ~212).

## Irlanda (8 estaciones)

Recomputado en una auditoría previa (`results/e2_met_ireland_pm10_regenerated/`,
PR#3, commit `1aad811d`), verificado por hash de forma independiente en
esta auditoría (Fase 3b: 30/31 ficheros de `output_hashes.csv` coinciden
byte a byte). No se recomputó de nuevo en esta sesión por ausencia del
dataset consolidado de Irlanda en este entorno.

| Cifra del manuscrito | Valor manuscrito | Valor regenerado (PR#3) | Estado | Evidencia |
|---|---:|---:|---|---|
| H*_strict por estación×condición (30 de 32 celdas) | ver `tab:ireland_hstar` | idéntico | COINCIDE | REPRODUCED_PRIOR_AUDIT |
| Henry St. Limerick, H*_strict lags_only | 18 | 17 | ROUNDING_MATCH (Δ=1h) | REPRODUCED_PRIOR_AUDIT |
| ΔH*_strict medio | +0.9h | +0.9h (redondeado; exacto=1.0 según nota IE-035) | ROUNDING_MATCH | REPRODUCED_PRIOR_AUDIT |
| DM-HLN, conteo de "favours" (23/8/1) | 23/8/1 | 24/7/1 | MISMATCH (1 celda de 32) | REPRODUCED_PRIOR_AUDIT |
| ρ₁ medio Irlanda | 0.850 | 0.850 | COINCIDE | REPRODUCED_PRIOR_AUDIT |
| 8 descriptivos por estación (n, media, SD, P95) | tab:descriptive | 57/76 MATCH, 17 ROUNDING_MATCH globalmente | mayormente COINCIDE | REPRODUCED_PRIOR_AUDIT |

Detalle completo de las 76 comparaciones:
`results/e2_met_ireland_pm10_regenerated/manuscript_claim_comparison.csv`.

**Bloqueado en esta auditoría (Fase 3a):** reajuste de SARIMA en h=24 para
Dublin Airport y Dundalk. No hay series crudas de Irlanda en este entorno,
y no se localizó en ningún artefacto del repo la anotación de "cota
inferior" que motivaría el reajuste — la tabla actual del manuscrito
(L484-497) da valores SARIMA exactos, sin marcar, para ambas estaciones.

## ρ₁ vs ΔH*_strict (n=9, Madrid + 8 estaciones irlandesas)

| | Manuscrito | Recomputado | Evidencia |
|---|---:|---:|---|
| OLS: r, p, n | 0.58, 0.10, 9 | 0.579, 0.103, 9 | REPRODUCED (coincide) |
| Tobit censurado (β₁, nuevo) | *(no existía en el manuscrito)* | 52.40 (vs. 32.12 del OLS, +63%) | REPRODUCED (nuevo) |

Ambos modelos se reportan como diagnóstico de dirección/magnitud, no como
evidencia inferencial válida con n=9 (así lo reconoce también el propio
manuscrito para el OLS).

## Gate de fuga (Fase 1, bloqueante)

| Flujo | Veredicto | Alcance |
|---|---|---|
| `code/e2_met_madrid_shared.py` (motor de producción, Madrid + Irlanda) | **VERDE** | Genera las cifras publicadas; sin fuga futura demostrada por valor |
| `code/rolling_origin.py::run_single_origin_evaluation` (motor genérico) | ROJO | Código muerto, proyecto RVVCCA/Elche, no invocado por Madrid/Irlanda — sin impacto en resultados publicados |

## Figuras

`figures/audit/` (generadas por `code/audit_build_figures.py`):
`madrid_skill_curves_recomputed.png`,
`madrid_bootstrap_delta_hstar_histogram.png`,
`madrid_delta_hstar_window_sensitivity.png`,
`madrid_null_calibration_max_run.png`,
`rho1_delta_hstar_ols_vs_tobit.png`.
