# Fase 0 — Inventario y trazabilidad

Auditor: sesión de auditoría computacional `claude/audit-p1-meteorology-0ehg5v`.
Fecha: 2026-08-03. Commit base de la auditoría: `370490a` (`main`, antes de
crear esta rama).

## 1. ¿Qué flujo generó los resultados publicados?

Hay dos motores de rolling-origin en el repo:

- **(a) motor genérico** `code/rolling_origin.py` + `code/features.py` +
  `code/config.py`. `config.py` declara explícitamente un proyecto distinto:
  `TARGET_VARIABLE="PM10"`, `SITE_NAME="Elche"`,
  `DATASET_SOURCE="Red Valenciana de Vigilancia y Control de la
  Contaminación Atmosférica"` — es el scaffold del proyecto RVVCCA/Elche
  (commit inicial `69db0113`, 2026-04-07), no de Madrid ni de Irlanda.
  Sus funciones de alto nivel `run_single_origin_evaluation` /
  `run_rolling_backtest` **no son invocadas por ningún script del repo**
  (verificado con `grep -rn "run_single_origin_evaluation\|run_rolling_backtest"`
  sobre todo `code/`: los únicos matches son la propia definición dentro de
  `rolling_origin.py`). Es código muerto para efectos de los resultados de
  Madrid/Irlanda.

- **(b) motor de producción** `code/e2_met_madrid_shared.py`
  (`run_backtest`, `predict_xgboost_direct`, `build_origin_feature_row`,
  `predict_persistence`, `predict_sarima`, `diebold_mariano_test`), invocado
  por `code/e2_met_madrid_run.py` (Madrid) y reutilizado por
  `code/e2_met_ireland_run.py` (Irlanda, vía
  `run_backtest_for_station`, que "mirrors the logic of
  e2_met_madrid_shared.run_backtest"). Este motor sólo importa de
  `rolling_origin.py` las utilidades de bajo nivel no-fugosas:
  `generate_rolling_origins`, `get_train_window`, `get_test_window`.

**Conclusión: el flujo (b) `e2_met_madrid_shared.py` es el que generó los
resultados de Madrid e Irlanda citados en el manuscrito.** El motor genérico
(a) pertenece a otro proyecto y no está conectado al pipeline E2-MET. Esto
se confirma también por trazabilidad de configuración: `RUN_ORDER.md` y
`CANONICAL_PROTOCOL.md` sólo documentan el flujo (b); no mencionan
`rolling_origin.run_rolling_backtest` en ningún punto.

Evidencia adicional de que las cifras trackeadas en
`results/e2_met_madrid_pm10/` corresponden al motor (b): los valores
recomputables a partir de `metrics/hstar_summary.csv` y
`stats/dm_lags_meteo_vs_lags_only.csv` coinciden exactamente (a la precisión
mostrada) con los citados en `manuscripts/manuscript_main.tex` líneas
389-397 y 424-427 (ver tabla de verificación more abajo).

## 2. Configs usadas

| Config | Dataset declarado | Estado del dataset |
|---|---|---|
| `code/e2_met_madrid_config.json` | `data_processed/madrid_pm10_meteorology_experiment_base.csv` (ruta absoluta autor-local `/Users/federicogarciacrespi/...`) | **AUSENTE.** `data_processed/` sólo contiene `.gitkeep`; `.gitignore` excluye `data_processed/*`. El script `code/build_madrid_experiment_base.py` referenciado en `RUN_ORDER.md` **no existe en el repo** (verificado con `find . -iname "*build*madrid*"`, cero resultados). |
| `code/e2_met_ireland_config.json` | `data_processed/ireland_pm10_meteorology_hourly.csv` (misma ruta absoluta autor-local) | **AUSENTE** en su forma original. Existe una versión **regenerada** (no original) reconstruible desde 9 CSV fuente recuperados cuyos hashes están en `results/e2_met_ireland_pm10_regenerated/manifests/source_csv_manifest.csv`; los propios CSV fuente y el ZIP no están trackeados, sólo sus hashes. |

Ambas configs son idénticas en hiperparámetros de fondo: XGBoost 300 árboles,
`max_depth=4`, `learning_rate=0.05`, `subsample=colsample_bytree=0.9`,
`random_state=42`, `n_jobs=1`; SARIMA(1,0,1)(1,0,0)$_{24}$, tope de
entrenamiento 17\,520 filas; lags `[1,2,3,6,12,24,48,168]`; DM en
`h∈{1,6,12,24}`, pérdida cuadrática; `origin_stride_hours=24`;
`min_train_rows=8760`.

**Nota:** `e2_met_madrid_config.json.train_start = "2019-01-01"`, pero el
manuscrito (líneas 202-205, 282-283) describe el periodo de entrenamiento
como "2020–2022" y afirma que "origins in early 2023 draw on three years of
history". Con `train_start=2019-01-01` los orígenes de enero de 2023
arrastran realmente ~4 años de historial, no 3. Discrepancia menor,
reportada aquí sin corregir el manuscrito (regla 2).

## 3. Artefactos row-level: qué existe y qué falta

| Artefacto | Existe | SHA-256 (primeros 16 hex) | Commit que lo fijó | Cubre |
|---|---|---|---|---|
| `data_processed/madrid_pm10_meteorology_experiment_base.csv` (dataset base Madrid) | **NO** | — | nunca trackeado | — |
| `data_processed/ireland_pm10_meteorology_hourly.csv` (dataset base Irlanda, original) | **NO** | — | nunca trackeado | — |
| `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv` (row-level, 34\,752 filas) | Sí | `e4a7edd656385df4` | `c30e6cf8` (2026-05-16, "Add SARIMA baseline...") | Madrid, ambas condiciones + referencia, 362 orígenes, h=1..24 |
| `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv` | Sí | `8ba9d94a4dd194c1` | `c30e6cf8` | Madrid, 96 filas de métricas |
| `results/e2_met_madrid_pm10/metrics/hstar_summary.csv` | Sí | `31cc1f67e67af54a` | `c30e6cf8` | Madrid, H*_strict/H*_relax por modelo×condición |
| `results/e2_met_madrid_pm10/stats/dm_lags_meteo_vs_lags_only.csv` | Sí | `c078db6f10c9f610` | `c30e6cf8` | Madrid, DM-HLN h∈{1,6,12,24} |
| `results/e2_met_madrid_pm10/run_metadata.json` | Sí | `9534eb595f0be8dd` | `c30e6cf8` | **INCONSISTENTE** (ver §4) |
| `results/e2_met_ireland_pm10/` | Sí (documental) | ver `manifests/files_manifest.csv` | `bd9998d2` (PR#2) | Recuperación documental: config, scripts, manifiestos. Predicciones/métricas/DM **originales marcadas `NOT_FOUND`** |
| `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv` (row-level, 150\,624 filas) | Sí | `e8b262e0812da8c1` | `1aad811d` (PR#3, 2026-07-26) | Irlanda, 8 estaciones, ambas condiciones, **REGENERADO — NO es la corrida original** |
| `results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary.csv` / `hstar_summary_both_definitions.csv` | Sí | `3bedec78958528ea` | `1aad811d` | Irlanda regenerado; incluye ambas definiciones de H*_strict (max-run y from-h1) |
| `results/e2_met_ireland_pm10_regenerated/stats/dm_lags_meteo_vs_lags_only.csv` | Sí | `b60990088171c23e` | `1aad811d` | Irlanda regenerado, DM-HLN |
| 9 CSV fuente Irlanda (recuperados) | **NO** (sólo manifiesto con hashes) | ver `manifests/source_csv_manifest.csv` | — | Impide refit de SARIMA u otra regeneración desde cero |
| `manuscripts/manuscript_main.tex` | Sí | `1f440fab4cb292e0` | histórico | Texto auditado |

## 4. Hallazgo: `run_metadata.json` de Madrid está desactualizado respecto a los outputs trackeados

`results/e2_met_madrid_pm10/run_metadata.json` declara:

```
"started_at_utc": "2026-05-15T10:01:03...",
"conditions_run": ["lags_only"],
"n_origins": 362,
"prediction_rows": 26064,
"metrics_rows": 72,
"dm_rows": 0
```

Pero los ficheros trackeados en el mismo directorio (mismo commit `c30e6cf8`)
tienen: `predictions_all_models.csv` = 34\,752 filas con condiciones
`{lags_only, lags_meteo, reference}` y modelos
`{persistence, sarima, xgboost_direct}`; `metrics_all_models.csv` = 96 filas
(4 combinaciones condición×modelo × 24 horizontes); `dm_lags_meteo_vs_lags_only.csv`
= 4 filas no vacías. Esto sólo es reproducible ejecutando
`e2_met_madrid_run.py --condition all` (ver lógica de `include_references`
y del cálculo DM en `code/e2_met_madrid_run.py:40-99`, que sólo llena `dm_rows`
cuando `args.condition == "all"`).

**Interpretación:** el `run_metadata.json` trackeado corresponde a una
corrida anterior (`--condition lags_only`, sin SARIMA, sin DM), y quedó
desactualizado cuando el commit `c30e6cf8` ("Add SARIMA baseline to Madrid
E2-MET experiment") volvió a ejecutar el pipeline completo
(`--condition all`) y sobrescribió predicciones/métricas/DM pero **no**
`run_metadata.json`. Esto se corrige en la Fase 3c.

## 5. Bloqueo de datos primarios (afecta Fases 2–4)

Ni el dataset base de Madrid ni el consolidado de Irlanda existen en este
entorno de auditoría, ni son reconstruibles sin salir del repositorio
(fuentes: portal de datos abiertos del Ayuntamiento de Madrid; ZIP de EPA
Irlanda recuperado cuyo hash está documentado pero cuyo contenido no está
presente). Esto ya estaba documentado como bloqueo abierto en
`docs/PROG_P2_00_PROVENANCE_AUDIT.md` (2026-07-28) y sigue sin resolverse.

**Consecuencia para esta auditoría:**
- Fase 1 (fuga) **no depende** de estos datasets: se verifica con datos
  sintéticos inyectados, tal como pide el encargo.
- Fase 2 (evidencia primaria Madrid) se puede ejecutar **desde los
  artefactos row-level ya trackeados**
  (`predictions_all_models.csv`), recomputando S(h)/H*/bootstrap/DM. Esto
  verifica el pipeline estadístico de forma independiente pero **no**
  el entrenamiento del modelo desde cero. Etiqueta: `REPRODUCED`, no
  `VERIFIED_PRIMARY`.
- Fase 3a (reajuste de SARIMA en Irlanda) requiere las series crudas de
  PM10 por estación (Dublin Airport, Dundalk), que no existen en este
  entorno. **Bloqueada.** Además, no se localizó en el manuscrito actual
  ninguna anotación de "cota inferior" (superíndice `b` o similar) en la
  tabla de H* de Irlanda para esas dos estaciones — búsqueda exhaustiva en
  `manuscripts/`, `results/`, `reports/`, `docs/`, `notes/` sin resultados.
  Se documenta como hallazgo, no se fabrica la anotación referida.
- Fase 4 (simetría temporal) **sí es ejecutable** sin el dataset base: los
  362 orígenes de Madrid (2023-01-01 a 2023-12-30) ya están en
  `predictions_all_models.csv`, así que basta con filtrar por fecha de
  origen para construir las ventanas PRIMARIA (ene-jul) y SENSIBILIDAD
  (ene-dic) sin reentrenar nada.

## 6. Verificación cruzada manuscrito ↔ artefactos trackeados (Madrid)

| Cifra | Manuscrito (línea) | `hstar_summary.csv` / `dm_...csv` trackeados | Coincide |
|---|---|---|---|
| H*_strict lags_only | 9 (L389) | 9 | Sí |
| H*_relax lags_only | 15 (L390) | 15 | Sí |
| H*_strict SARIMA | 8 (L390) | 8 | Sí |
| H*_relax SARIMA | 20 (L391) | 20 | Sí |
| H*_strict lags_meteo | 17 (L394) | 17 | Sí |
| H*_relax lags_meteo | 17 (L395) | 17 | Sí |
| ΔH*_strict | +8 (L397) | 17−9=8 | Sí |
| DM h=1: n=354, p=0.243 | L424 | n=354, p=0.243186 | Sí |
| DM h=6: n=356, p=0.961 | L425 | n=356, p=0.961428 | Sí |
| DM h=12: n=346, p=0.012 | L426 | n=346, p=0.012327 | Sí |
| DM h=24: n=354, p=0.398 | L427 | n=354, p=0.397639 | Sí |

Todas las cifras Madrid citadas en el manuscrito coinciden exactamente con
los artefactos row-level actualmente trackeados en `results/e2_met_madrid_pm10/`.
Esto no certifica que el pipeline esté libre de fuga (eso es la Fase 1), sólo
que estos ficheros son efectivamente la fuente de las cifras publicadas.

## 7. Reproducibilidad del entorno

No existía un entorno Python con el stack declarado (`pandas`, `numpy`,
`sklearn`, `statsmodels`, `xgboost`, `pyarrow`) en este contenedor. Se creó
`.venv_audit/` (excluido de git) con exactamente esos paquetes:

```
python3 -m venv .venv_audit
source .venv_audit/bin/activate
pip install pandas numpy scikit-learn statsmodels xgboost pyarrow scipy
```

Versiones instaladas: pandas 3.0.5, numpy 2.4.6, scikit-learn 1.9.0,
statsmodels 0.14.6, xgboost 3.2.0, pyarrow 25.0.0, scipy 1.17.1. Esto no
añade dependencias nuevas al proyecto: son exactamente las librerías del
stack declarado en el encargo; no hay `requirements.txt` previo en el repo
para fijar versiones exactas, por lo que estas versiones quedan registradas
aquí como parte del contrato de reproducibilidad de esta auditoría.

## 8. Siguiente paso

Fase 1 — GATE de fuga, bloqueante. Ver `docs/audit/01_leak_verdict.md`.
