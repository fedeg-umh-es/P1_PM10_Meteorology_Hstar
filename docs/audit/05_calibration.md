# Fase 5 (opcional) — Calibración

Se ejecuta porque las Fases 1-4 no arrojaron ningún GATE en rojo (Fase 1
VERDE; Fases 2-4 son recomputaciones/discrepancias documentadas, no fugas
ni errores de código). Script: `code/audit_phase5_calibration.py`. Semilla
fija y registrada: `20260803`.

## a) Calibración nula de H*_strict,max-run

`H*_strict,max-run` es un máximo sobre 24 ventanas candidatas (la racha
positiva más larga en cualquier punto de h=1..24), por lo que tiene sesgo
positivo por selección incluso si la habilidad real fuese cero en todos
los horizontes. Se estima la distribución nula por **permutación por
origen**: para cada uno de los 362 orígenes de Madrid se decide, con una
moneda justa, si se intercambian las etiquetas modelo/persistencia para
**los 24 horizontes de ese origen a la vez** (no horizonte a horizonte);
esto preserva la correlación real entre horizontes dentro de un mismo
origen —presente en los datos reales por la persistencia atmosférica— en
vez de asumir horizontes independientes, que sería una calibración más
optimista de lo que los datos justifican. Se recomputa S(h) y su max-run
bajo cada permutación, 5000 repeticiones, y se compara contra el
H*_strict,max-run observado de `lags_only` (9h, Fase 2).

| | Valor |
|---|---:|
| H*_strict,max-run observado (lags_only) | 9 |
| Media de la distribución nula | 10.21 |
| Mediana de la distribución nula | 9.0 |
| Percentil 95 de la distribución nula | 24.0 |
| Percentil 99 de la distribución nula | 24.0 |
| Fracción de permutaciones con max-run ≥ 9 | **0.573** |

Artefactos: `results/audit/calibration/null_max_run_draws.csv` (5000
réplicas), `null_calibration_summary.json`.

**Interpretación:** bajo esta calibración, un valor de `H*_strict,max-run`
igual o mayor que el observado (9h) para `lags_only` frente a persistencia
ocurre por puro azar en el 57% de las permutaciones que destruyen
cualquier diferencia sistemática real entre modelo y persistencia. La
mediana nula (9.0) coincide exactamente con el valor observado. Esto no
significa que `lags_only` no tenga ninguna habilidad real —el DM-HLN y la
forma de la curva S(h) sugieren que sí la tiene en h=3-11 (Fase 2)— sino
que **la estadística `H*_strict,max-run` por sí sola, tomada como
"racha positiva más larga en cualquier punto de 24 horizontes", es una
estadística con un sesgo de selección tan grande que un valor de 9h no es,
por sí mismo, evidencia fuerte de habilidad real** sin acompañarlo de un
test explícito como el DM-HLN. Esto es consistente con la amplitud del
intervalo de bootstrap de ΔH* encontrada en la Fase 2 ([−8, +13]) y la
Fase 4 (sensible a la ventana de evaluación): varias líneas de evidencia
independientes apuntan en la misma dirección — el punto estimado
ΔH*_strict,max-run=+8h es frágil.

**Alcance de la calibración:** se calculó explícitamente para
`lags_only` frente a persistencia, que es el término de referencia de
`H*_strict,max-run=9h` citado en el manuscrito. La misma lógica de
permutación es aplicable a `lags_meteo` (H*_strict,max-run=17h); no se
recalculó aquí por no ser estrictamente necesario para el punto que el
encargo pide calibrar, pero el script es reutilizable para ese caso
cambiando el par de condiciones de entrada.

## b) ρ₁ vs ΔH*_strict: scatter, OLS y Tobit (n=9)

Tabla transcrita literalmente de `manuscripts/manuscript_main.tex:801-809`
(`tab:rho1`): Madrid + 8 estaciones irlandesas, ρ₁ y ΔH*_strict de cada
sitio, con un indicador de "techo" (`ceiling`) para los 6 sitios donde el
modelo `lags_only` ya alcanza `H*_strict=24h` — en esos sitios, ΔH* está
**censurado en 0**: la ganancia latente de la meteorología no puede
observarse porque no hay margen por encima de las 24h del horizonte
máximo evaluado. Edenderry tiene ΔH*=0 pero el propio manuscrito (nota a
pie `a`) lo atribuye a baja predictibilidad, no a un techo, y se trata como
no censurado, siguiendo esa misma distinción.

Guardado en `results/audit/calibration/rho1_delta_hstar_table.csv`.

### OLS (control de que la tabla transcrita es la misma que usó el manuscrito)

`r = 0.579`, `p = 0.103`, `n = 9` — coincide con el `r = 0.58, p = 0.10, n = 9`
citado en el manuscrito (`manuscripts/manuscript_main.tex:872`), confirmando
que la tabla transcrita reproduce los datos de origen de esa regresión.

### Tobit (censura por la derecha en 0 para los 6 sitios con techo)

Modelo ajustado por máxima verosimilitud (`scipy.optimize.minimize`,
Nelder-Mead; log-verosimilitud implementada a mano en
`code/audit_phase5_calibration.py::tobit_negloglik`, sin dependencias
nuevas):

| | OLS | Tobit (censurado) |
|---|---:|---:|
| Pendiente (β₁) | 32.12 | **52.40** |
| Intercepto (β₀) | −26.03 | −41.44 |
| σ | — | 0.896 |

**El Tobit da una pendiente ~63% más pronunciada que el OLS.** Esto es el
comportamiento esperado de un modelo censurado: el OLS, al tratar los 6
ceros censurados como observaciones exactas en vez de como "como mínimo
este valor pero limitado por el techo", atenúa (sesga hacia cero) la
pendiente estimada de la relación real entre ρ₁ y el beneficio latente de
la meteorología.

**Ninguno de los dos modelos sostiene una afirmación inferencial con
n=9.** El OLS ya lo reconoce el propio manuscrito (p=0.10, no
significativo al 5%). El Tobit, con 6 de 9 observaciones censuradas y sólo
3 grados de libertad efectivos no censurados, no tiene ni siquiera errores
estándar fiables con este tamaño muestral (no se reportan, para no
sugerir una precisión que los datos no sostienen). Se presenta únicamente
como diagnóstico de dirección y magnitud del sesgo de atenuación, no como
alternativa inferencial válida al OLS.

## GATE / cierre de Fase 5

No es un gate bloqueante — es diagnóstico. Ambos resultados (a y b)
refuerzan, desde ángulos distintos, la misma conclusión ya visible en las
Fases 2 y 4: **la cifra ΔH*_strict,max-run=+8h en Madrid es correcta como
recomputación aritmética de los datos publicados, pero es estadísticamente
frágil** — no distinguible del azar bajo una calibración nula por
permutación que preserva la correlación real entre horizontes, sensible a
la ventana de evaluación (Fase 4), y con un intervalo de bootstrap que
cruza cero (Fase 2). Ninguno de estos hallazgos altera el valor numérico
en sí (que sigue siendo `VERIFIED`/`REPRODUCED` frente al manuscrito); acota
su fuerza como evidencia.
