# Canonical Input Schema Mapping

## Madrid Dataset
- Path: `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`
- Station Column: (Implicit) "Madrid"
- Origin Column: `origin`
- Forecast Timestamp Column: `forecast_timestamp`
- Horizon Column: `horizon`
- Condition Column: `condition` (values: `reference`, `lags_only`, `lags_meteo`)
- Model Column: `model` (values: `persistence`, `sarima`, `xgboost_direct`)
- Observed Column: `y_true`
- Predicted Column: `y_pred`

## Ireland Dataset
- Path: `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv`
- Station Column: `station`
- Origin Column: `origin`
- Forecast Timestamp Column: `forecast_timestamp`
- Horizon Column: `horizon`
- Condition Column: `condition` (values: `reference`, `lags_meteo`, `lags_only`)
- Model Column: `model` (values: `persistence`, `sarima`, `xgboost_direct`)
- Observed Column: `y_true`
- Predicted Column: `y_pred`
