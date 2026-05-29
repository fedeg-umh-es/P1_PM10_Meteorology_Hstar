# Meteorology Experiment Closure

- Stations entered: Birr co offlay, Dublin Airport, Dundalk Co Louth, Pearse street dublin, Ringsend dublin, edenderry co offlay, henry street Limerick, porrlaoise co laois.
- Models entered: `xgboost_direct`; persistence is the reference baseline.
- Horizons evaluated: `1..24`.
- Outputs generated: `outputs/metrics/predictions_meteorology_experiment.csv`, `outputs/tables/master_meteorology_diagnostic_table.csv`, and figures in `outputs/figures`.
- Limitations blocking strong inference: station type metadata is not present in the processed dataset; this run compiles existing rolling-origin forecasts rather than refitting them; legacy configs still contain absolute paths.

go: meteorology improves accuracy but fidelity gains are mixed
