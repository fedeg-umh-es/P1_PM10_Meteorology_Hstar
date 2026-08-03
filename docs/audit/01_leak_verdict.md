# Fase 1 — GATE de fuga (bloqueante)

Tests: `tests/test_no_leakage.py`. Ejecución:

```
source .venv_audit/bin/activate
python3 tests/test_no_leakage.py
```

Resultado: **7/7 tests pasan**, es decir, cada aserción (incluidas las que
esperaban demostrar la fuga en el flujo (a)) se cumplió exactamente como se
predijo. Salida completa:

```
PASS test_flow_a_persistence_c0_anchor_is_y_tminus1
PASS test_flow_a_run_single_origin_evaluation_leaks_future_meteo_for_h_gt_1
PASS test_flow_a_run_single_origin_evaluation_leaks_future_pm10_lag_for_h_gt_1
PASS test_flow_b_end_to_end_run_backtest_invariant_to_future_meteo
PASS test_flow_b_feature_row_invariant_to_perturbing_the_future
PASS test_flow_b_origin_feature_row_meteo_timestamp_equals_origin_for_every_horizon
PASS test_flow_b_persistence_anchor_is_y_tminus1

7/7 passed
```

## Método

Dataset sintético trazable: cada columna meteorológica y el propio PM10 se
fijan a una función determinista y estrictamente creciente del índice
horario ("reloj": `PM10[i] = 1000 + i`, `meteo_col[i] = i`). Cualquier
timestamp que entre incorrectamente en el vector de features es
identificable por su valor numérico, sin inspeccionar código. Se añadió
además un test de perturbación de caja negra: se reconstruye el dataset
dejando intactos todos los valores en `t <= origen` y sustituyendo **todos**
los valores meteorológicos en `t > origen` por un rango fuera de escala
(`99000+i`); si el vector de features de ese origen cambia, hay fuga futura;
si no cambia, no la hay. Se probó tanto a nivel de función unitaria
(`build_origin_feature_row`) como end-to-end (`run_backtest()` completo con
XGBoost real, hiperparámetros reducidos por velocidad).

## Veredicto por flujo

### (a) `code/rolling_origin.py` — `run_single_origin_evaluation` / `run_rolling_backtest`

**ROJO.**

Mecanismo exacto: en `run_single_origin_evaluation` (líneas 214-223 de
`code/rolling_origin.py`), `prepared_test` se construye aplicando
`_prepare_supervised_frame` sobre `pd.concat([train_df, test_df])` — es
decir, calendario y lags se computan fila a fila sobre toda la ventana
futura, no una sola vez en el origen — y luego el bucle de predicción
accede a `prepared_test.iloc[step - 1]` para cada horizonte `step` (línea
246). Como las columnas meteorológicas de `features.select_features_by_condition`
(condición C2/C3) **no están rezagadas** — se leen tal cual de la fila —,
la fila `step-1` para `step > 1` está fechada en `origen + (step-1)`, una
observación estrictamente futura respecto al origen `t`. Lo mismo ocurre
con el lag_1 de PM10: al estar calculado por `.shift()` sobre la
concatenación completa, en `step=24` termina leyendo el valor **real** de
PM10 en `t+22`, no un valor conocido en el momento de emitir el pronóstico.

Confirmado por valor:
`test_flow_a_run_single_origin_evaluation_leaks_future_meteo_for_h_gt_1` —
para h∈{2,6,12,24} el valor meteorológico capturado coincide exactamente
con `clock(origen + h - 1)`, es decir, con el timestamp objetivo, no con el
del origen.
`test_flow_a_run_single_origin_evaluation_leaks_future_pm10_lag_for_h_gt_1` —
en h=24 el `lag_1` de PM10 usa el índice `origen+22` (`>= t`), violando la
regla "ningún lag usado tiene timestamp >= t".

**Alcance:** ninguno sobre los resultados publicados. La Fase 0
(`docs/audit/00_inventory.md` §1) estableció que `run_single_origin_evaluation`
/ `run_rolling_backtest` no son invocados por ningún script del repositorio
(`e2_met_madrid_run.py`, `e2_met_ireland_run.py`, `smoke_test.py` sólo usan
las utilidades no-fugosas `generate_rolling_origins`, `get_train_window`,
`get_test_window`); pertenecen además a un proyecto distinto (RVVCCA/Elche,
según `code/config.py`). No afectan ni a Madrid ni a Irlanda. Se recomienda
eliminar o corregir esta función muerta para que no quede como trampa para
un futuro reuso.

### (b) `code/e2_met_madrid_shared.py` — `run_backtest` / `build_origin_feature_row` / `predict_xgboost_direct` (motor de producción, compartido por Madrid e Irlanda)

**VERDE.**

Mecanismo verificado: `predict_xgboost_direct` construye el vector de
features **una sola vez por origen**, vía `build_origin_feature_row`, que
selecciona la única fila de `context_df` cuyo timestamp es exactamente
igual a `origen` (`prepared.loc[prepared[timestamp_col] == origin]`,
`e2_met_madrid_shared.py:123`). Esa misma fila —sin diferencias— se pasa a
`XGBoostDirectForecaster.predict()`, que la reutiliza para los 24 modelos
horizonte-específicos (`code/models/xgboost_model.py:80-83`: mismo
`X_future` para todo `horizon`). Por construcción no hay forma de que un
valor meteorológico fechado después de `t` entre en el vector de features
de ningún horizonte.

Confirmado por valor:
- `test_flow_b_origin_feature_row_meteo_timestamp_equals_origin_for_every_horizon`:
  las 7 columnas meteorológicas de Madrid = `clock(origen)` exactamente, y
  cada uno de los 8 lags de PM10 = `clock(origen - lag)` exactamente.
- `test_flow_b_feature_row_invariant_to_perturbing_the_future`: sustituir
  **todos** los valores meteorológicos en `t > origen` por valores fuera de
  escala no cambia el vector de features del origen (`assert_frame_equal`
  exacto).
- `test_flow_b_end_to_end_run_backtest_invariant_to_future_meteo`: con la
  misma perturbación, un `run_backtest()` completo (XGBoost real, no mock)
  produce predicciones numéricamente idénticas horizonte a horizonte.
- `test_flow_b_persistence_anchor_is_y_tminus1`: `predict_persistence`
  devuelve `y_{t-1}` para los 24 horizontes, simétrico con el modelo.

**Interpretación importante — esto NO es un veredicto de disponibilidad
operativa.** El vector de features usa meteorología observada
**exactamente en `t`** (no en `t+h`), no meteorología rezagada (`< t`) ni
un pronóstico meteorológico emitido antes de `t`. Esto significa:
- No hay fuga de horizonte futuro (`t+1..t+24`), que era la hipótesis
  concreta a refutar en este encargo. Refutada.
- Persiste la pregunta, ya documentada y sin resolver en
  `docs/PROG_P2_01_METEOROLOGICAL_AVAILABILITY_CONTRACT.md` (clase "D": sin
  evidencia de latencia de publicación), de si una observación meteorológica
  fechada en `t` estaría realmente disponible en el instante de emitir el
  pronóstico en un despliegue operativo real. Esta auditoría no cambia esa
  clasificación; la reafirma de forma independiente y por valor, no sólo
  por lectura de código.

## GATE 1

El flujo que generó los resultados publicados — flujo (b) — es **VERDE**.
**Se continúa a la Fase 2.**

El flujo (a) es ROJO pero está confirmado, por trazabilidad de la Fase 0 y
por el propio grafo de imports (`grep` sobre todo `code/`), como código
muerto ajeno a Madrid/Irlanda: no bloquea el avance.
