# P3 pre-journal temporal audit

Closed, read-only audit of temporal protocol evidence for P3. No manuscript,
model, dataset, scientific result, or H* definition was modified. The audit
uses the tracked code and prediction/inventory artifacts in this repository.

The subsequent repair attempt and its reproducibility gate are recorded in
`audit/p3_temporal_repair/`; this closed audit remains the immutable baseline.

## Scope

- B1: forecast-origin counts and actual clock spacing;
- B2: information set at forecast origin;
- B3: direct-target cutoff, clock-time horizon semantics, and paired support;
- B4: source-file timestamp coverage and PM10 missingness.

## Primary evidence

- `code/rolling_origin.py`
- `code/e2_met_madrid_shared.py`
- `code/models/xgboost_model.py`
- `code/e2_met_madrid_config.json`
- `code/e2_met_ireland_config_regenerated.json`
- `results/predictions_all_models.csv`
- `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv`
- `reports/ireland_dataset_inventory.csv`
- `audit_ijer_experimental_evidence/forensic_gate/protocol_by_model_and_origin.csv`

## Interpretation notes

`n_dm_pairs` counts complete paired squared-error observations after matching
lags-only and lags+meteorology on origin and verification timestamp. It is not
the number of raw hourly observations. `origin_stride_hours` reports observed
clock spacing; where the pipeline selected every 24 rows on an irregular grid,
the distinct clock deltas are retained explicitly.
