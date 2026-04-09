# RUN_ORDER.md

## Canonical Protocol

`E2-MET canonical protocol = Madrid PM10, h=1..24, full expanding rolling-origin over 2023 origins, train-only preprocessing inside each fold, persistence primary baseline, SARIMA secondary baseline, XGBoost-direct main comparison model, lags_only vs lags_meteo under identical splits/metrics, and DM-HLN inference only on the full run.`

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

## Optional: run only one condition

```bash
cd /Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar
python3 code/e2_met_madrid_run.py --config code/e2_met_madrid_config.json --condition lags_only
python3 code/e2_met_madrid_run.py --config code/e2_met_madrid_config.json --condition lags_meteo
```

## Main outputs

- `results/e2_met_madrid_pm10/rolling_origins.csv`
- `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`
- `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`
- `results/e2_met_madrid_pm10/metrics/hstar_summary.csv`
- `results/e2_met_madrid_pm10/stats/dm_lags_meteo_vs_lags_only.csv`
- `results/e2_met_madrid_pm10/manuscript_tables/table_metrics_long.csv`
- `results/e2_met_madrid_pm10/manuscript_tables/table_xgboost_horizon_wide.csv`
- `results/e2_met_madrid_pm10/manuscript_tables/table_delta_lags_meteo_vs_lags_only.csv`
