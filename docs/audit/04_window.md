# Fase 4 — Simetría temporal de la ventana de evaluación de Madrid

Script: `code/audit_phase4_madrid_window.py`. Fuente: la misma
`results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`
row-level de la Fase 2 (hash `e4a7edd656385df4...`); no se reentrena nada.
Cada origen ya tiene su predicción calculada con una ventana de
entrenamiento expansiva específica de ese origen (verificado VERDE en la
Fase 1), así que subconjuntar por fecha de origen para decidir qué cuenta
en el resumen no reintroduce fuga.

## ¿Cuál es la ventana real?

El manuscrito contiene una contradicción interna explícita:

- Metodología (línea 280): *"The evaluation period is 1 January 2023 -- 31
  July 2023 (31 weeks, yielding approximately 210--365 origins per
  station)."*
- Pie de `tab:descriptive` (línea 234): *"evaluation: Jan--Jul 2023."*
- Pero la tabla `tab:madrid_dm` (líneas 424-427) da tamaños muestrales
  DM de n=354/356/346/354, y el texto de resultados (líneas 388-397) da
  H*_strict=9/17. Estas cifras **sólo son reproducibles con los 362
  orígenes que van del 1 de enero al 30 de diciembre de 2023**, no con los
  ~212 orígenes de una ventana enero-julio.

Verificado directamente sobre `predictions_all_models.csv`:
`origin.min() = 2023-01-01`, `origin.max() = 2023-12-30`, 362 orígenes
únicos. Filtrando a `origin <= 2023-07-31` quedan exactamente 212 orígenes.

**La ventana real con la que se computaron las cifras publicadas es
enero–diciembre de 2023 (362 orígenes), no enero–julio.** La cifra de 212
orígenes SÍ es consistente con el rango "210–365 orígenes" que la propia
Metodología anticipa, y es simétrica con Irlanda (145–212 orígenes por
estación, evaluación enero–agosto 2023) — pero **no es la ventana
efectivamente usada** para las cifras de las Tablas de Resultados.

## Dos ejecuciones etiquetadas

| | PRIMARIA (simétrica con Irlanda) | SENSIBILIDAD (todo lo disponible) |
|---|---|---|
| Ventana | 2023-01-01 -- 2023-07-31 | 2023-01-01 -- 2023-12-30 |
| n orígenes | 212 | 362 (= lo publicado) |
| H*_strict,max-run lags_only | 9 | 9 |
| H*_strict,max-run lags_meteo | **19** | 17 |
| ΔH*_strict,max-run | **+10 h** | **+8 h** (= lo publicado) |
| H*_strict,from-h1 lags_only | 0 | 0 |
| H*_strict,from-h1 lags_meteo | **0** | 17 |
| ΔH*_strict,from-h1 | 0 | 17 |
| H*_relax lags_only / lags_meteo | 15 / 21 | 15 / 17 |
| Bootstrap IC95% ΔH*_max-run (bloque=7d, 2000 remuestras, semilla 20260803) | **[0, 12]**, media 3.94 | [−8, +13], media 3.08 |
| DM h=1 (n, p) | 210, 0.716 | 354, 0.243 |
| DM h=6 (n, p) | 211, 0.838 | 356, 0.961 |
| DM h=12 (n, p) | 206, **0.045** | 346, **0.012** |
| DM h=24 (n, p) | 210, 0.277 | 354, 0.398 |

Artefactos: `results/audit/madrid_window_sensitivity/window_summary.csv`,
`window_dm.csv`, `window_comparison.json` (curvas S(h) completas incluidas).

## Lectura de las diferencias

1. **ΔH*_strict,max-run no es estable frente a la ventana de evaluación.**
   +8h con los 362 orígenes publicados, +10h con los 212 orígenes que la
   propia Metodología del manuscrito dice haber usado. Ninguna de las dos
   cifras es "más correcta" en abstracto — son estimaciones sobre datos
   distintos — pero sólo una de ellas es la que el texto metodológico
   describe, y no es la que aparece en las tablas de Resultados.

2. **H*_strict,from-h1(lags_meteo) es todavía más sensible a la ventana**:
   pasa de 0 (enero–julio) a 17 (enero–diciembre). Es decir, bajo la
   ventana que el manuscrito dice haber usado, la propia definición en
   prosa de `H*_strict` (racha desde h=1, líneas 359-361) da **0** para
   ambas condiciones, no 9 y 17. La discrepancia de definición ya señalada
   en la Fase 2 se agrava, no se resuelve, si se toma en serio la ventana
   enero-julio del texto metodológico.

3. **La única significación DM que sobrevive a la corrección de Bonferroni
   en el manuscrito (h=12, p=0.012 < α_adj=0.0125) deja de sobrevivir bajo
   la ventana enero–julio**: p=0.045 > 0.0125. Con los 212 orígenes que el
   propio texto metodológico dice haber evaluado, ningún horizonte del test
   DM-HLN es significativo tras la corrección por comparaciones múltiples
   que el propio manuscrito aplica (líneas 373-376).

4. El intervalo de bootstrap para ΔH* también cambia de forma sustancial:
   [0, +12] (enero-julio, nunca cruza a valores negativos aunque tampoco
   excluye 0 con margen) frente a [−8, +13] (enero-diciembre, cruza cero
   ampliamente). Ninguno de los dos coincide con la cifra de referencia del
   encargo ([−7, +12]; Fase 2 ya documentó que esa cifra no existe en el
   repositorio).

Ningún hallazgo de esta fase modifica el manuscrito ni recomienda qué
ventana "debería" usarse; se limita a mostrar, con evidencia recomputada,
cuánto dependen las cifras principales (ΔH*, significación DM) de cuál de
las dos ventanas —la declarada en el texto o la efectivamente usada en las
tablas— se adopta como definitiva.
