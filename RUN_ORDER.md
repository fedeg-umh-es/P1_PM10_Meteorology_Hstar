# RUN_ORDER.md

## Canonical Protocol

`E2-MET canonical protocol = Madrid PM10, h=1..24, full expanding rolling-origin over 2023 origins, train-only preprocessing inside each fold, persistence primary baseline, SARIMA secondary baseline, XGBoost-direct main comparison model, lags_only vs lags_meteo under identical splits/metrics, and DM-HLN inference only on the full run.`

## Prerequisites

```bash
cd /Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar
python3 - <<'PY'
import pandas as pd
from pathlib import Path

path = Path('data_processed/madrid_pm10_meteorology_experiment_base.csv')
df = pd.read_csv(path, parse_dates=['timestamp'])
required = ['timestamp', 'PM10', 'temp_c', 'humidity_pct', 'pressure_hpa', 'wind_speed_ms', 'wind_dir_deg', 'solar_rad_wm2', 'precip_mm']
missing = [c for c in required if c not in df.columns]
print('Missing columns:', missing if missing else 'None')
print('Rows:', len(df))
print('Date range:', df['timestamp'].min(), 'to', df['timestamp'].max())
print('PM10 missing %:', round(100 * df['PM10'].isna().mean(), 2))
for col in ['temp_c', 'humidity_pct', 'pressure_hpa', 'wind_speed_ms', 'wind_dir_deg', 'solar_rad_wm2', 'precip_mm']:
    print(f'{col} missing %:', round(100 * df[col].isna().mean(), 2) if col in df.columns else 'MISSING')
PY
```

## 1. Build or refresh the Madrid aligned dataset

```bash
cd /Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar
python3 code/build_madrid_experiment_base.py
```

## 2. Run both E2-MET conditions with shared rolling origins

```bash
cd /Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar
python3 code/e2_met_madrid_run.py --config code/e2_met_madrid_config.json --condition all
```

## 3. Build manuscript-ready tables

```bash
cd /Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar
python3 code/e2_met_madrid_tables.py --config code/e2_met_madrid_config.json
```

## 4. Inspect manuscript-facing outputs

```bash
cd /Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar
cat results/e2_met_madrid_pm10/manuscript_tables/table_hstar_summary.csv
cat results/e2_met_madrid_pm10/manuscript_tables/table_dm_lags_meteo_vs_lags_only.csv
```

## Optional: run only one condition

```bash
cd /Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar
python3 code/e2_met_madrid_run.py --config code/e2_met_madrid_config.json --condition lags_only
python3 code/e2_met_madrid_run.py --config code/e2_met_madrid_config.json --condition lags_meteo
```

## Full Pipeline

```bash
cd /Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar && \
python3 code/build_madrid_experiment_base.py && \
python3 code/e2_met_madrid_run.py --config code/e2_met_madrid_config.json --condition all && \
python3 code/e2_met_madrid_tables.py --config code/e2_met_madrid_config.json
```

## Manual Confirmations Before Full Run

1. `data_processed/madrid_pm10_meteorology_experiment_base.csv` is the canonical dataset for the manuscript run.
2. Meteorological variables used in `lags_meteo` are available at the forecast origin timestamp and are not future values.
3. The SARIMA order in `code/e2_met_madrid_config.json` is accepted as the frozen paper baseline before the full run.
4. Only the full run, not any smoke run, is used for manuscript claims.
5. `delta_H* ≈ 0` remains a valid publishable outcome and must not trigger protocol changes.

## Main outputs

- `results/e2_met_madrid_pm10/rolling_origins.csv`
- `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`
- `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`
- `results/e2_met_madrid_pm10/metrics/hstar_summary.csv`
- `results/e2_met_madrid_pm10/stats/dm_lags_meteo_vs_lags_only.csv`
- `results/e2_met_madrid_pm10/manuscript_tables/table_metrics_long.csv`
- `results/e2_met_madrid_pm10/manuscript_tables/table_xgboost_horizon_wide.csv`
- `results/e2_met_madrid_pm10/manuscript_tables/table_delta_lags_meteo_vs_lags_only.csv`
