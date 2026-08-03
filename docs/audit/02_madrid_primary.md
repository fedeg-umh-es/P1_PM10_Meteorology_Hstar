# Fase 2 — Evidencia primaria de Madrid

Script: `code/audit_phase2_madrid_recompute.py`. Ejecución:

```
source .venv_audit/bin/activate
python3 code/audit_phase2_madrid_recompute.py
```

Fuente única: `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`
(row-level, 34\,752 filas, 362 orígenes, hash `e4a7edd656385df4...`, ver
Fase 0). **El dataset base `data_processed/madrid_pm10_meteorology_experiment_base.csv`
no existe en este entorno**, así que este script no reentrena nada: recalcula
S(h), las tres variantes de H*, ΔH*, el bootstrap y el DM-HLN directamente
desde las predicciones ya generadas por el motor verificado VERDE en la
Fase 1. Etiqueta de evidencia para todo lo que sigue: **`REPRODUCED`** (no
`VERIFIED_PRIMARY`; esa etiqueta exigiría reentrenar desde el dataset base).
Semilla del bootstrap fija y registrada: `20260803`.

Salidas versionadas en `results/audit/madrid_recompute/`: `skill_curves_S_h.csv`,
`hstar_variants.csv`, `bootstrap_summary.json`,
`bootstrap_delta_hstar_replicates.csv` (2000 réplicas), `dm_recomputed.csv`,
`manuscript_comparison.csv`, `delta_hstar_from_h1.json`.

## S(h) y H* recomputados

| Modelo/condición | H*_strict,max-run | H*_strict,from-h1 | H*_relax |
|---|---:|---:|---:|
| SARIMA | 8 | 0 | 20 |
| lags_only (XGBoost) | 9 | **0** | 15 |
| lags_meteo (XGBoost) | 17 | **17** | 17 |

Horizontes con S(h)>0: `lags_only` = {3,4,5,6,7,8,9,10,11,15} (racha
consecutiva más larga: h=3–11, 9 horas — coincide con el máximo del
encargo); `lags_meteo` = {1,...,17} (racha consecutiva desde h=1 hasta
h=17, 17 horas).

ΔH*_strict,max-run = 17 − 9 = **+8 h** — `VERIFIED` frente al manuscrito
(coincide exactamente, ver `manuscript_comparison.csv`, columna `status`,
las 13 cifras comparadas dan `COINCIDE`).

ΔH*_strict,from-h1 = 17 − 0 = **+17 h** — cifra que el manuscrito **no
reporta** bajo ese nombre.

## Hallazgo: la prosa del manuscrito describe mal su propia curva de skill de `lags_only`

El manuscrito define `H*_strict` en el texto metodológico (líneas 359-361)
como *"the length of the longest consecutive positive-skill run **beginning
at h = 1**"* — es decir, la definición `from-h1`. Pero en Resultados (línea
388) afirma: *"The lags-only XGBoost achieves positive skill from h = 1
through approximately h = 11 before falling below zero, yielding
H*_strict = 9 h"*.

Esto es internamente inconsistente con la propia curva S(h) recomputada
desde las predicciones trackeadas: S(h=1) = −0.0058 y S(h=2) = −0.0263 para
`lags_only` — **negativas, no positivas**. La racha positiva de 9 horas
existe, pero es h=3–11, no h=1–11 (que serían 11 horas, no 9). El valor
numérico publicado (H*_strict=9) coincide con lo que el código realmente
computa (`max-run`, la racha más larga en cualquier punto de 1..24, igual
que `derive_hstar_from_metrics` en `e2_met_madrid_shared.py`), pero el
texto que lo acompaña describe un escenario (racha desde h=1) que no
ocurrió. Esto reproduce, ahora para Madrid, el mismo tipo de discrepancia
metodológica que la auditoría de Irlanda ya había documentado en
`results/e2_met_ireland_pm10_regenerated/hstar_definition_discrepancy.md`
para Dublin Airport, Edenderry y Henry St. Limerick: la definición en prosa
(`from-h1`) y la definición efectivamente tabulada (`max-run`) no son la
misma función, y el texto narrativo de Resultados fue escrito asumiendo
`from-h1` incluso cuando el valor citado es `max-run`.

**No se modifica el manuscrito (regla 1/2).** Se deja constancia aquí, con
las 24 filas de S(h) versionadas en
`results/audit/madrid_recompute/skill_curves_S_h.csv` como evidencia
reproducible.

## Bootstrap de bloques móviles sobre ΔH*_strict,max-run

Bloque = 7 orígenes consecutivos (7 días, dado `origin_stride_hours=24`),
2000 remuestras, semilla `20260803`.

| | Valor |
|---|---:|
| Punto estimado (muestra completa) | +8 h |
| Media del bootstrap | +3.08 h |
| Desviación estándar del bootstrap | 5.49 h |
| IC95% (percentiles 2.5/97.5) | **[−8, +13] h** |

El encargo cita como referencia a verificar "ΔH* = +8 h, IC95% ≈ [−7, +12]".
**Esa cifra de IC95% no existe en ningún artefacto de este repositorio**
(`grep` exhaustivo de `[-7` / `+12]` / `IC95` / `bootstrap` / `confidence
interval` sobre `manuscripts/`, `results/`, `reports/`, `docs/`, `notes/`,
sin resultados fuera de paquetes de terceros en `.venv_audit/`); el
manuscrito actual no reporta ningún intervalo de confianza para ΔH*. Se
trata, por tanto, de un análisis nuevo producido por esta auditoría, no de
una cifra a la que "coincidir". El intervalo aquí computado, **[−8, +13]**,
es la evidencia primaria de esta fase — no se ajusta para parecerse al
[−7, +12] del encargo (regla 2).

**Interpretación:** el punto estimado ΔH*=+8h no es robusto bajo
remuestreo por bloques de la serie de orígenes: el intervalo cruza cero, y
la media del bootstrap (+3.08h) es menos de la mitad del punto estimado.
Esto es coherente con que `H*_strict,max-run` es un **máximo sobre 24
ventanas candidatas** (sesgo positivo por selección, ver Fase 5) aplicado
dos veces (una para `lags_only`, otra para `lags_meteo`) y luego restado;
la resta de dos máximos ruidosos y correlacionados en el tiempo produce una
distribución bootstrap mucho más dispersa que el propio punto estimado
sugiere.

## DM-HLN recomputado

Idéntico a `results/e2_met_madrid_pm10/stats/dm_lags_meteo_vs_lags_only.csv`
y a la Tabla `tab:madrid_dm` del manuscrito (`COINCIDE` en las 8 columnas
comparadas: p-valor y n en h∈{1,6,12,24}). Se recomputó reusando
`e2_met_madrid_shared.diebold_mariano_test`, la misma función de producción,
para no introducir una implementación estadística distinta de la que generó
las cifras publicadas.

## GATE 2 — etiquetado de evidencia

| Cifra | Etiqueta |
|---|---|
| H*_strict,max-run (los 3 modelos) | REPRODUCED |
| H*_strict,from-h1 (los 3 modelos) | REPRODUCED (nuevo, no publicado) |
| H*_relax (los 3 modelos) | REPRODUCED |
| ΔH*_strict,max-run = +8h | REPRODUCED — coincide con manuscrito |
| ΔH*_strict,from-h1 = +17h | REPRODUCED (nuevo, no publicado) |
| Bootstrap IC95% [−8,+13] | REPRODUCED (nuevo; no hay cifra publicada equivalente) |
| DM-HLN (4 horizontes) | REPRODUCED — coincide con manuscrito |

Ninguna cifra alcanza `VERIFIED_PRIMARY` en esta auditoría: esa etiqueta
requeriría reentrenar desde `data_processed/madrid_pm10_meteorology_experiment_base.csv`,
ausente en este entorno (Fase 0, §5).
