# P1_PM10_Meteorology_Hstar

Repositorio local base para P1:
"valor marginal de la meteorología" bajo el marco H* Operational Predictability.

Estado actual:
- Repo separado del proyecto Madrid-Valencia.
- Git inicializado solo en local.
- Estructura base creada.
- Scripts reutilizados del pipeline H* copiados en `code/`.

Scripts copiados como base:
- `build_daily_pm_series.py`
- `extract_station_series.py`
- `prepare_daily_regular_series.py`
- `query_eea_stations_v2.py`
- `run_rolling_skill.py`

Observación:
- Estos scripts cubren la base de extracción, regularización temporal, evaluación rolling-origin, métricas y H*.
- Aún no implementan comparación explícita `lag-only` vs `meteorology/exogenous`.
- Aún no incluyen pipeline de meteorología ni modelos `LSTM-MIMO`.

Estructura:
- `code/`
- `data_raw/`
- `data_processed/`
- `results/`
- `figures/`
- `notes/`
