# Fase 6 (memo de decisión) — Qué hacer con los hallazgos antes de someter

Este documento no modifica `manuscripts/` (sigue la regla del encargo de
auditoría). Traduce los hechos computacionales de las Fases 0-5 en
decisiones concretas que sólo los autores pueden tomar, con una
recomendación explícita en cada una. Es el puente entre esta auditoría y
una futura sesión de edición del `.tex`.

## Lectura honesta del estado actual

El paper **no está listo para someter tal cual está**. No porque haya
fraude o error de cálculo —el pipeline está limpio (GATE 1 VERDE) y las
cifras publicadas son exactamente las que el código produce—, sino porque
hay **dos inconsistencias internas verificables entre lo que el texto dice
que se hizo y lo que las tablas realmente muestran** (Decisiones A y B) y
**un resultado central más frágil de lo que el manuscrito comunica**
(Decisión C). Un revisor competente, o un intento de réplica, encontraría
las tres. Ninguna es difícil de arreglar; las tres requieren una decisión
de los autores, no más código.

## Decisión A — Ventana de evaluación de Madrid

**Hecho:** Metodología (L280) y pie de `tab:descriptive` (L234) dicen
"1 enero – 31 julio 2023". Las tablas de Resultados sólo son
reproducibles con "1 enero – 30 diciembre 2023" (362 orígenes, no ~212).

**Opción 1 (mínima):** corregir el texto para que diga enero-diciembre.
Cambia el relato de "simétrico con Irlanda" (que hoy es falso: Irlanda
evalúa hasta agosto 2023, Madrid hasta diciembre) mismo sin tocar ninguna
cifra publicada.

**Opción 2 (más fiel al diseño declarado):** adoptar enero-julio como
ventana primaria — recalcular Tablas/Figuras de Madrid con los valores de
`results/audit/madrid_window_sensitivity/` (ΔH*_max-run=+10h, no +8h; DM
h=12 dejaría de ser el único resultado "significativo" tras Bonferroni).
Reporta enero-diciembre como sensibilidad en anexo, si se quiere conservar
esa evidencia.

**Mi recomendación:** Opción 2. La simetría con Irlanda es un argumento
de diseño que el propio paper usa para justificar la comparabilidad
Madrid-Irlanda (Introducción, L164-165); dejarlo como está pero con el
texto "corregido" a la ventana real debilita ese argumento sin que el
lector lo note. Es más trabajo, pero es la versión que sostiene mejor bajo
escrutinio.

## Decisión B — Definición de H*_strict (prosa vs. código)

**Hecho:** Metodología (L359-361) define H*_strict como "racha positiva
que empieza en h=1". El código (`derive_hstar_from_metrics`,
`e2_met_madrid_shared.py`) y las tablas usan en realidad "racha positiva
más larga en cualquier punto de 1..24". Para Madrid, `lags_only` tiene
S(h) negativo en h=1-2 — la definición en prosa daría H*_strict=0, no 9.
Mismo patrón ya documentado para Irlanda
(`results/e2_met_ireland_pm10_regenerated/hstar_definition_discrepancy.md`).

**Opción 1 (mínima):** corregir la prosa para describir lo que el código
realmente calcula ("longest consecutive positive-skill run within
h=1..H", sin "beginning at h=1"). No cambia ningún número publicado.

**Opción 2:** recalcular todo bajo la definición "from-h1" tal como está
escrita. Cambia sustancialmente el relato central (ΔH*_from-h1 = +17h en
la ventana publicada, +0h en la ventana enero-julio — ver
`results/audit/madrid_recompute/` y `results/audit/madrid_window_sensitivity/`).

**Mi recomendación:** Opción 1. "Racha más larga en cualquier punto" es
una operacionalización razonable y defendible de "horizonte útil" por sí
misma; no hace falta que sea la que originalmente se pretendía escribir.
Es el arreglo de menor riesgo y no obliga a rehacer ninguna cifra.

## Decisión C — Robustez de ΔH*_strict = +8h

**Hecho:** el bootstrap de bloques móviles da IC95%=[-8,+13] (cruza cero);
la calibración nula por permutación muestra que H*_strict,max-run=9h para
`lags_only` ocurre por azar el 57% de las veces bajo skill nulo. El único
resultado DM que sobrevive a Bonferroni (h=12) depende de la ventana
(Decisión A).

**Esto no es un error a corregir — es información que falta en el
manuscrito actual.** El paper hoy presenta ΔH*=+8h sin cuantificar su
incertidumbre.

**Mi recomendación:** incorporar el bootstrap y, como mínimo, mencionar la
fragilidad del punto estimado en la Discusión. La base más defendible para
la afirmación central "la meteorología ayuda en Madrid" no es
ΔH*_strict=+8h por sí solo, sino el DM-HLN en h=12 — y ese resultado
depende de la Decisión A. Esto puede debilitar la fuerza retórica del
abstract/conclusiones; es preferible que los autores lo decidan
conscientemente a que lo encuentre un revisor.

## Decisión D — Provenance de datos (bloqueante para reclamar reproducibilidad)

**Hecho:** ni el dataset base de Madrid ni el consolidado de Irlanda
existen en ningún entorno auditado (este ni, según
`docs/PROG_P2_00_PROVENANCE_AUDIT.md`, el de la auditoría anterior). Nada
alcanza `VERIFIED_PRIMARY`.

**Acción que sólo tú puedes hacer:** localizar y restaurar (o volver a
descargar de las fuentes documentadas: portal de datos de Madrid, EPA
Irlanda) los ficheros base, y decidir si se versionan (aunque sea
comprimidos) o se documentan con manifiesto de hashes como se hizo para
Irlanda. Sin esto, cualquier afirmación de reproducibilidad en el paper
(p.ej. el enlace a GitHub en L727) es parcialmente falsa: el código
reproduce el pipeline, pero no desde cero.

## Orden recomendado si decides actuar

1. Decisión D primero (sin datos, las Decisiones A/B/C no se pueden
   recalcular de verdad, sólo documentar).
2. Decisión B (barata, sin riesgo, arregla una inconsistencia real).
3. Decisión A (cara pero importante — determina qué cifra final se
   publica).
4. Decisión C (redacción de Discusión, una vez A esté resuelta).

Ninguna de estas decisiones se ha aplicado a `manuscripts/main.tex` en
esta rama. Este documento es la entrada para quien la aplique.
