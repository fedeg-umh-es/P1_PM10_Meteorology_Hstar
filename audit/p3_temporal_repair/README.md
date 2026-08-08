# P3 timestamp-safe repair

This directory records the deterministic repair attempt. The code now resolves
origins, PM10 lags, and targets by exact timestamps. Missing exact timestamps
remain invalid, and duplicate timestamps raise an error.

The Ireland input was reconstructed deterministically from
`P1_PM10_Meteorology_Hstar/Finalised_merged_datasets-...zip` (187,857 rows,
8 stations) and used for complete timestamp validation plus a one-origin smoke
run. The required historical Madrid 2019--2023 aligned PM10+meteorology input is
not present: the Madrid CSVs found in P1 cover 2024--2026. Using old predictions
as model inputs would not be regeneration and is explicitly prohibited.

Bootstrap contract recovered: paired moving-block resampling of forecast
origins; block length 7 origins; 2,000 replicates; seed 20260802; persistence,
lags-only, and lags+meteorology dimensions resampled jointly; percentile 95%
interval (2.5th and 97.5th percentiles). It cannot be rerun on repaired
predictions until the Madrid source dataset is restored and the full expensive
Ireland backtest is completed.
