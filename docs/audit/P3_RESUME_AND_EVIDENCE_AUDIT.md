# P3 Resume and Evidence Audit

## 1. Metadatos

- Fecha: 2026-08-01
- Auditor: Codex
- Directorio canónico: `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Operational_Meteorology`
- Canon: `P3_PROJECT_CANON.md`, versión 1.3
- Decisión H*: `P3_Hstar_Strict_Definition_Decision.md`
- Repositorio científico: `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland`
- Rama: `codex/p3-hstar-strict-manuscript-repair`
- HEAD: `f01a5ffc2f73252e27b35cda5e964387ff044e67`
- Naturaleza de la auditoría: lectura y verificación; no se modificaron código, manuscrito, resultados, figuras ni canon.

## 2. Veredicto

```text
SEQUENCE: P3_SEQUENCE_GATE_CLEARED
SCIENTIFIC STATE: P3_HOLD_AND_REPAIR
RESUME SCOPE: P3_RESUME_FOR_CONTROLLED_REPAIR_ONLY
MANUSCRIPT: NO_GO_CURRENT_WORKTREE
OVERLEAF: NOT_READY_FOR_OVERLEAF_COMPILATION
EXPERIMENTS: NO_RERUN_AUTHORIZED_OR_REQUIRED_FOR_THE_NUMERICAL_REPAIR
```

P2 ya no bloquea la secuencia, pero P3 no está listo para compilar ni enviar. Las salidas consolidadas permiten verificar los valores canónicos principales; el manuscrito en `HEAD`, dos figuras, el generador de la asociación y parte de la documentación siguen alineados con valores o definiciones anteriores. La reparación anterior no quedó completa.

Este informe no modifica por sí mismo el canon. `P3_PROJECT_CANON.md` continúa siendo la única fuente persistente de verdad.

## 3. Estado Git

- Remoto GitHub: `https://github.com/fedeg-umh-es/P1_PM10_Meteorology_Hstar.git`
- Comparación con `origin/main`: 3 commits por delante, 0 por detrás.
- Upstream configurado: `source-local/codex/p3-hstar-strict-manuscript-repair`.
- Estado del upstream: roto; `source-local` apunta a `/Users/fede/repos/P3_Madrid_Ireland`, que no existe como repositorio accesible.
- `git fetch --all --prune`: `origin` fue consultado correctamente; `source-local` falló por la ruta local ausente.
- Worktree inicial: sucio, con un cambio rastreado y archivos no rastreados.
- Cambio rastreado observado al inicio: `manuscripts/manuscript_main.tex`, 22 inserciones y 22 eliminaciones; revertía varias correcciones canónicas.
- Worktree final: sucio solo por los archivos no rastreados. Durante la auditoría, el manuscrito fue reemplazado externamente por el blob exacto de `HEAD` (`0d6c9c75a5f22baf12c3e469aeced538986ed180`). La auditoría no escribió el manuscrito ni ejecutó una operación Git capaz de producir ese cambio.
- Archivos no rastreados: cinco documentos duplicados en `docs/`, dos CSV duplicados en `outputs/` y `imports/` (265 archivos, aproximadamente 150 MB).
- Los cinco documentos y los dos CSV sueltos son copias byte a byte de artefactos ya rastreados en sus ubicaciones canónicas. `imports/` contiene paquetes históricos importados y no constituye nueva evidencia primaria.
- No se ejecutaron `pull`, `merge`, `rebase`, `reset`, `clean`, `stash`, `checkout`, `commit`, `push` ni PR.

Estado observado al inicio:

```text
## codex/p3-hstar-strict-manuscript-repair...source-local/codex/p3-hstar-strict-manuscript-repair [ahead 2]
 M manuscripts/manuscript_main.tex
?? docs/data_inventory.md
?? docs/meteorology_experiment_audit.md
?? docs/meteorology_vs_lags_protocol.md
?? docs/path_issues.md
?? docs/script_inventory.md
?? imports/
?? outputs/master_meteorology_diagnostic_table.csv
?? outputs/predictions_meteorology_experiment.csv
```

Estado observado al final:

```text
## codex/p3-hstar-strict-manuscript-repair...source-local/codex/p3-hstar-strict-manuscript-repair [ahead 2]
?? docs/data_inventory.md
?? docs/meteorology_experiment_audit.md
?? docs/meteorology_vs_lags_protocol.md
?? docs/path_issues.md
?? docs/script_inventory.md
?? imports/
?? outputs/master_meteorology_diagnostic_table.csv
?? outputs/predictions_meteorology_experiment.csv
```

## 4. Contrato canónico aplicado

- P3 es `Operational Meteorology`; el manuscrito Madrid–Irlanda actual es retrospectivo.
- La comparación informacional debe separar meteorología retrospectiva de meteorología operacional disponible en origen.
- La métrica estricta primaria es `H_strict_max_run`.
- `H_strict_from_h1` es un diagnóstico auxiliar y no puede sustituir silenciosamente a la métrica primaria.
- Irlanda debe describirse como `REGENERATED FROM RECOVERED SOURCE DATA`, no como recuperación de la ejecución original.
- La asociación de nueve sitios es positiva pero no significativa; no autoriza lenguaje causal.

## 5. Evidencia numérica verificada

### 5.1 Madrid

- Predicciones consolidadas: 34.752 filas.
- Orígenes: 362.
- Horizontes: 1..24.
- Condiciones/modelos presentes: XGBoost `lags_only`, XGBoost `lags_meteo`, persistencia y SARIMA.
- Recomputación desde `metrics_all_models.csv`:

| Condición | H relax | H strict desde h=1 | H strict max-run | Intervalo max-run |
|---|---:|---:|---:|---|
| lags only | 15 | 0 | 9 | h=3..11 |
| lags + meteo | 17 | 17 | 17 | h=1..17 |

- Resultado canónico verificable bajo `H_strict_max_run`: 9 → 17 h, `delta = +8 h`.
- Consecuencia: la definición local que exige comenzar en h=1 no es una mera diferencia de redacción; produciría 0 → 17 h y contradice las tablas y la afirmación +8.

Limitación de procedencia: `run_metadata.json` declara solo `lags_only`, 26.064 predicciones, 72 filas métricas y 0 filas DM, mientras que los archivos finales contienen 34.752 predicciones, 96 filas métricas y ambas condiciones. El historial muestra que el paquete fue ampliado en el commit SARIMA. La aritmética +8 es verificable desde los artefactos rastreados, pero el metadato no representa el bundle final y no existe un manifiesto de hashes equivalente al de Irlanda.

### 5.2 Irlanda regenerada

- Estaciones: 8.
- Orígenes estación-origen: 1.569.
- Horizontes: 1..24.
- Predicciones consolidadas: 150.624 filas.
- Todas las 16 combinaciones estación-condición XGBoost coinciden entre la recomputación desde métricas por horizonte y `hstar_summary_both_definitions.csv`.
- Henry Street Limerick, lags only: `from_h1 = 1`, `max_run = 17`, intervalo h=3..19, `relax = 24`.
- Henry Street Limerick, lags + meteo: `max_run = 24`.
- Resultado canónico: 17 → 24 h, `delta = +7 h`.
- Medias estrictas max-run: 21,875 h (lags only), 22,875 h (lags + meteo), `delta = +1,000 h`; redondeo de manuscrito: 21,9 / 22,9 / +1,0 h.
- Balance direccional DM-HLN: 24 favorecen lags + meteo, 7 favorecen lags only y 1 es indeterminado. Son direcciones, no conteos de significación.

El comparador de afirmaciones regeneradas conserva dos `MISMATCH`:

1. `23/8/1` del manuscrito anterior frente a `24/7/1` regenerado: discrepancia real que debe corregirse.
2. 16.555 observaciones descriptivas válidas de Edenderry frente a 16.784 filas fuente: no demuestra inconsistencia, porque las filas fuente pueden incluir PM10 ausente o inutilizable; el canon ya distingue ambos conteos.

### 5.3 Asociación rho1

- Con los nueve pares canónicos rho1–delta, la recomputación aritmética produce `n = 9` y `r = 0,554715086`, consistente con `r = 0,555`.
- `p = 0,121110` consta en el canon, pero no pudo recomputarse de forma independiente desde las series fuente porque los paneles procesados de Madrid e Irlanda no están en el clon.
- Interpretación permitida: asociación positiva, no estadísticamente significativa y compatible con la hipótesis.
- Interpretación no permitida: mecanismo demostrado, causalidad o que la persistencia “gobierna” el beneficio meteorológico.

## 6. Procedencia y reproducibilidad

| Artefacto | Estado | Evidencia |
|---|---|---|
| Predicciones consolidadas Madrid | PRESENT_AND_NUMERICALLY_VERIFIABLE | 34.752 filas; H* recomputado. |
| Metadato Madrid | STALE_OR_INCOMPLETE | Conteos y condiciones no describen los archivos finales. |
| Dataset procesado Madrid | REFERENCED_BUT_ABSENT | La configuración conserva una ruta absoluta del autor. |
| Predicciones consolidadas Irlanda | PRESENT_AND_NUMERICALLY_VERIFIABLE | 150.624 filas; esquema, estaciones, orígenes y H* verificados. |
| Ejecución original Irlanda | MISSING | No se retuvieron predicciones fila a fila de la ejecución original. |
| Evidencia Irlanda regenerada | PRESENT_WITH_PROVENANCE_LIMITS | Es regenerada desde datos fuente recuperados. |
| Panel procesado Irlanda | REFERENCED_BUT_ABSENT | El canon declara 187.857 x 17; no puede reconstruirse desde este clon. |
| Manifiesto de fuentes Irlanda | PRESENT_BUT_NOT_SELF_CONTAINED | Registra nueve CSV fuente, que no están versionados. |
| Manifiesto de salidas Irlanda | STALE_OR_PARTIAL | 31 entradas; 16 shards por condición están ausentes/excluidos y `merge_validation_report.md` no coincide con el SHA declarado. |
| Scripts productores | PRESENT_BUT_PATH_BOUND | Varias rutas absolutas apuntan a `/Users/federicogarciacrespi/Public/...`. |

Para los 15 archivos del manifiesto irlandés actualmente presentes, no hubo discrepancias de tamaño. La única discrepancia de hash fue `merge_validation_report.md`: esperado `bab82...`, observado `28296465e4ba6677a89d9048bf5de674334a4e7cd97cca59501c2282ef1435b9`. Los 16 shards ausentes son subconjuntos por estación/condición excluidos por la política Git; existe la consolidación rastreada, por lo que su ausencia no invalida por sí sola los cálculos, pero impide presentar el manifiesto como verificación completa del contenido actual.

## 7. Coherencia manuscrito–resultados

### 7.1 Cambio concurrente observado

Al inicio, el diff local de `manuscript_main.tex` revertía correcciones canónicas ya introducidas en `HEAD`:

- redefine H* strict como una secuencia obligatoriamente iniciada en h=1;
- cambia Henry Street de 17/+7 a 18/+6;
- cambia la media irlandesa de 21,9/22,9/+1,0 a 22,0/22,9/+0,9;
- elimina la declaración de evidencia irlandesa regenerada;
- sustituye el remoto correcto `fedeg-umh-es` por `fedeg`;
- elimina etiquetas explícitas `strict,max-run` de la tabla.

El diff desapareció durante la auditoría sin intervención del auditor y el archivo final coincide byte a byte con `HEAD`. Ya no forma parte del worktree final, pero se registra porque demuestra que el estado de trabajo cambió concurrentemente y porque no debe reintroducirse como base de reparación.

### 7.2 Defectos presentes en HEAD y en el worktree final

`HEAD` no completa la reparación:

- el resumen todavía presenta la definición desde h=1 y `+0,9 h`;
- otra tabla conserva Henry Street 18/+6 y la media 22,0/+0,9;
- discusión y conclusiones mantienen cifras antiguas en varios pasajes;
- el texto conserva formulaciones causales o mecanicistas incompatibles con `p = 0,121`;
- la carta de presentación conserva +0,9 y afirma que el mecanismo está explicado o que la persistencia gobierna el beneficio;
- la recomendación operacional excede la evidencia retrospectiva disponible.

Por ello, volver simplemente al contenido de `HEAD` no basta para declarar el manuscrito listo.

## 8. Figuras y scripts de figuras

Las nueve imágenes referenciadas por el TeX existen, pero existencia no equivale a validez.

- `ireland_figure_hstar_summary.png` muestra Henry Street lags-only = 18 y lags+meteo = 24. Es obsoleta respecto al valor canónico 17/+7.
- `figure_rho1_vs_delta_hstar.png` muestra Henry Street `delta = 6` y la leyenda `r = 0,58`, `p = 0,10`; es obsoleta respecto a +7, `r = 0,555`, `p = 0,121`.
- `madrid_figure_hstar_summary.png` muestra 9 y 17 bajo strict, coherente con `H_strict_max_run`.
- `code/e2_autocorrelation_analysis.py` lee la tabla irlandesa antigua, conserva rutas absolutas y genera el punto Henry Street antiguo; por tanto, no es aún un productor canónico de la figura corregida.
- `code/e2_met_ireland_figures.py` consume el árbol original `results/e2_met_ireland_pm10`, no el bundle regenerado validado.

El informe `docs/audit/P3_HSTAR_STRICT_MANUSCRIPT_REPAIR_REPORT.md` declara las figuras válidas y `READY_FOR_OVERLEAF_COMPILATION`, pero enumera siete rutas que no existen y no detecta las dos imágenes obsoletas. Su veredicto queda refutado por la inspección actual.

## 9. Compilación

- Las nueve rutas de imagen usadas por el TeX actual están presentes.
- No hay `pdflatex`, `latexmk` ni `tectonic` disponibles localmente.
- No se realizó compilación ni renderizado visual del PDF.
- La compilación en Overleaf debe ocurrir solo después de corregir texto, tablas y figuras.

## 10. Bloqueos verificados

| Bloqueo | Estado |
|---|---|
| Definición H* del manuscrito local | OPEN — contradice el canon y las métricas. |
| Valores Henry Street | OPEN — texto/tablas/figura conservan 18/+6 en distintos lugares. |
| Media Irlanda | OPEN — persisten 22,0/+0,9. |
| Figura H* Irlanda | OPEN — representa el valor anterior. |
| Figura rho1–delta | OPEN — usa +6 y estadísticos anteriores. |
| Lenguaje causal | OPEN — excede una asociación no significativa. |
| Framing operacional | OPEN — el estudio actual es retrospectivo. |
| Divulgación de regeneración | PRESENT en el manuscrito final; debe preservarse y extenderse de forma coherente al paquete editorial. |
| Carta de presentación | OPEN — cifras y causalidad antiguas. |
| Procedencia Madrid | PARTIAL — resultado recalculable, metadato final incompleto. |
| Manifiesto Irlanda | PARTIAL — hash documental obsoleto y shards excluidos. |
| Compilación final | PENDING. |

## 11. Reparación mínima autorizable

No se necesita reentrenar ni cambiar la definición en el código productor de métricas. La reparación mínima debe ser cerrada y trazable:

1. Preservar la captura inicial y el estado final antes de intervenir. No reintroducir el diff local observado al inicio, porque revertía el canon.
2. Alinear resumen, métodos, resultados, ambas tablas, discusión, conclusiones y carta con `H_strict_max_run`, 17/+7 y 21,9/22,9/+1,0.
3. Mantener `H_strict_from_h1` solo como diagnóstico auxiliar y explicar, cuando sea relevante, el intervalo max-run.
4. Regenerar la figura H* de Irlanda desde `hstar_summary_both_definitions.csv` y la figura rho1–delta desde una tabla canónica de nueve sitios; corregir el script para no leer resultados originales obsoletos.
5. Sustituir causalidad por asociación positiva no significativa y eliminar inferencias operacionales no sostenidas por una rama NWP disponible en origen.
6. Preservar el remoto correcto y la divulgación explícita `regenerated, not original run`; extender esta última a la carta si menciona procedencia.
7. Actualizar el metadato Madrid o añadir una nota de composición del bundle final; actualizar el manifiesto irlandés para distinguir archivos rastreados, shards deliberadamente excluidos y el hash actual del informe.
8. Corregir el informe de reparación anterior: rutas reales, figuras realmente verificadas y veredicto.
9. Compilar en Overleaf y ejecutar una última matriz claim–evidence contra el PDF renderizado.
10. Solo entonces emitir `READY_FOR_OVERLEAF_COMPILATION` o un estado editorial posterior.

## 12. Cambios realizados por esta auditoría

- Código: no.
- Manuscrito: no.
- Resultados: no.
- Figuras: no.
- Canon: no.
- Configuración Git: no.
- Commit: no.
- Push: no.
- PR: no.
- Informe de auditoría: sí, fuera del repositorio científico y dentro del directorio documental canónico de P3.

## 13. Siguiente paso

Ejecutar una reparación controlada del manuscrito en `HEAD`, la carta, los dos scripts/figuras obsoletos y la documentación de procedencia, sin reentrenar modelos. Deben conservarse las capturas inicial y final de esta auditoría para no reintroducir accidentalmente la reversión local observada al comienzo.
