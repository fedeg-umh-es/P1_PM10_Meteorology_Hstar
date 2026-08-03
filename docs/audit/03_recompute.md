# Fase 3 — Cierre de deuda computacional

## a) Reajuste de SARIMA en h=24 para Dublin Airport y Dundalk (Irlanda)

**Bloqueada, por dos motivos independientes:**

1. **No hay datos.** Reajustar SARIMA requiere la serie temporal cruda de
   PM10 por estación (`data_processed/ireland_pm10_meteorology_hourly.csv`
   o los 9 CSV fuente recuperados). Ninguno existe en este entorno de
   auditoría (Fase 0, §5): `data_processed/` sólo contiene `.gitkeep`, y los
   CSV fuente de Irlanda sólo están documentados por hash en
   `results/e2_met_ireland_pm10_regenerated/manifests/source_csv_manifest.csv`,
   no versionados.

2. **No se localizó la anotación que motiva el reajuste.** El encargo
   describe "cotas inferiores 'b'" en la tabla de H* de Irlanda para Dublin
   Airport y Dundalk que habría que "eliminar" reajustando SARIMA a valores
   exactos. Se buscó exhaustivamente (`grep -rniE
   "textsuperscript\{b\}|\\\\\$\\^b\\\$|≥24|>=24|non-conver|did not
   converge|right-censor|lower.bound"` sobre `manuscripts/`, `results/`,
   `reports/`, `docs/`, `notes/`) y no se encontró ninguna anotación de este
   tipo. La Tabla `tab:ireland_hstar` del manuscrito actual
   (`manuscripts/manuscript_main.tex:469-497`) da valores SARIMA exactos y
   sin marcar para ambas estaciones (Dublin Airport: strict=24, relax=24;
   Dundalk: strict=18, relax=24), igual que
   `results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv`
   (fila `reference`/`sarima`: Dublin Airport `H_relax=24`, Dundalk
   `H_relax=24`). No hay una cota censurada visible en ningún artefacto
   actual del repositorio con la que trabajar.

No se fabrica la anotación referida ni se reajusta SARIMA sin datos que
respalden el reajuste (regla 2). Si esta tarea proviene de una versión
anterior del manuscrito o de un análisis externo no presente en este repo,
haría falta esa fuente para retomarla.

## b) Regeneración de las 8 estaciones irlandesas conservando row-level

**Ya realizada, en una auditoría previa** (`results/e2_met_ireland_pm10_regenerated/`,
commit `1aad811d`, PR #3 "Regenerate Ireland experiment evidence"), ejecutando
el propio `code/e2_met_ireland_run.py` sin modificar contra 9 CSV fuente
recuperados (identidad verificada por SHA-256 del ZIP origen). Row-level
trackeado: `predictions/predictions_all_models.csv` (150\,624 filas, 8
estaciones × 2 condiciones × 3 modelos × 24 horizontes), con hashes
registrados en `output_hashes.csv`.

Esta auditoría verificó por cuenta propia, no se limitó a citar el trabajo
previo:

```
sha256sum -c (recomputado por archivo) sobre los 31 ficheros listados en
results/e2_met_ireland_pm10_regenerated/output_hashes.csv
```

Resultado: **30/31 coinciden exactamente** con el hash registrado. Las 10
entradas de predicciones por estación×condición (p. ej.
`predictions_Birr_co_offlay_lags_meteo.csv`) están ausentes en disco por
diseño (`.gitignore` las excluye explícitamente: subconjunto estricto del
fichero combinado, ya trackeado). La única discrepancia real es
`merge_validation_report.md`: su hash registrado en `output_hashes.csv`
no coincide con el contenido actual del fichero, aunque ambos fueron
fijados en el mismo commit (`1aad811d`) y el fichero no se ha modificado
desde entonces (`git log` confirma un único commit tocándolo). La
explicación más probable es un problema de orden de escritura
autorreferencial: el informe termina con la frase "See `output_hashes.csv`
for SHA-256 of every final output file", lo que sugiere que su propio hash
se calculó y guardó en `output_hashes.csv` antes de que esa línea final (u
otro contenido) se añadiera al informe. No se ha podido reconstruir el
contenido exacto que produce el hash registrado (probado: recortar 0-5
líneas finales, ninguna coincide), así que se documenta como una
inconsistencia de un fichero de 31, sin corregirla por reconstrucción
especulativa. No afecta a ninguna cifra numérica de resultados (el fichero
discrepante es un informe de validación estructural, no datos).

**La nota "REGENERATED — NOT ORIGINAL RUN" no se retira** (regla 2): sigue
sin existir el run original ni sus artefactos row-level (`results/e2_met_ireland_pm10/`
los marca `NOT_FOUND`), y esta auditoría no aporta ninguna fuente nueva que
cambie eso.

## c) Coherencia de `run_metadata.json` con los outputs combinados

### Irlanda — coherente, verificado

```
predictions_all_models.csv: 150624 filas  == run_metadata.json.prediction_rows: 150624
metrics_all_models.csv:        768 filas  == run_metadata.json.metrics_rows:      768
dm_lags_meteo_vs_lags_only.csv: 32 filas  == run_metadata.json.dm_rows:            32
estaciones en predicciones == estaciones en run_metadata.json (8, mismo orden de conjunto)
```

Sin cambios.

### Madrid — inconsistente, corregido

La Fase 0 (§4) ya había detectado que `results/e2_met_madrid_pm10/run_metadata.json`
describía una corrida `--condition lags_only` (`conditions_run:
["lags_only"]`, `prediction_rows: 26064`, `metrics_rows: 72`, `dm_rows: 0`,
`started_at_utc`/`finished_at_utc` del 2026-05-15), mientras que los
ficheros de predicciones/métricas/DM trackeados en el mismo directorio y
mismo commit (`c30e6cf8`, "Add SARIMA baseline to Madrid E2-MET experiment")
contienen ambas condiciones, SARIMA y una tabla DM no vacía (34\,752 filas
de predicciones, 96 de métricas, 4 de DM) — sólo reproducible con
`--condition all`.

**Corregido en este commit.** `results/e2_met_madrid_pm10/run_metadata.json`
ahora refleja `conditions_run: ["lags_only", "lags_meteo"]` y los recuentos
de fila reales (34752/96/4), verificados por lectura directa de los CSV
trackeados (mismos que usa la Fase 2). El registro original (marca de
tiempo y recuentos de la corrida sólo-`lags_only`) se conserva íntegro bajo
la clave `metadata_correction.superseded_original` del propio fichero, para
no borrar evidencia de la inconsistencia detectada. Las marcas de tiempo
exactas de la corrida real (`--condition all`) nunca se registraron y no se
inventan aquí; se documenta como cota inferior conocida el timestamp del
commit `c30e6cf8` (`2026-05-16T05:51:32Z`).

## Resumen de Fase 3

| Subtarea | Estado |
|---|---|
| 3a. Reajuste SARIMA Irlanda h=24 | **Bloqueada** — sin datos crudos y sin anotación "b" localizable |
| 3b. Row-level Irlanda con hashes | Ya existente; verificado 30/31 hashes OK, 1 inconsistencia menor documentada (no numérica) |
| 3c. Coherencia run_metadata.json | Irlanda: coherente. Madrid: corregido, original preservado en el propio fichero |
