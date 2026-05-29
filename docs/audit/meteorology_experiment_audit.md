# Meteorology Experiment Audit

The repo already contains an E2 meteorology line with processed PM10+meteorology datasets, rolling-origin scripts, prediction outputs, metrics, figures and a manuscript draft.

Priority design files inspected: `01_scope_protocol.md`, `CANONICAL_PROTOCOL.md`, and `notes/e2_met_canonical_protocol.md`.

Current evaluation protocol found: expanding rolling-origin, hourly horizons `h = 1..24`, daily origin stride, train-only feature imputation, persistence as primary baseline, and XGBoost-direct as the main lag-only vs lag+meteorology comparison model.

For the minimum decisive experiment, the multi-station Ireland processed dataset is used because it supports station-level consistency checks with reliable meteorology coverage. Madrid remains a usable one-station branch but cannot answer cross-station consistency by itself.

No new absolute paths are introduced by the added code.

## Station Table

| station_id | pm10_available | meteorology_available | joint_period_available | usable_for_experiment | notes |
| --- | --- | --- | --- | --- | --- |
| Birr co offlay | True | True | 2020-09-04 00:00:00 to 2023-08-01 00:00:00 | True | rows=25465; joint_rows=25456; pm10_nonnull=1.000; min_met_nonnull=1.000 |
| Dublin Airport | True | True | 2020-06-30 02:00:00 to 2023-05-26 23:00:00 | True | rows=25462; joint_rows=25462; pm10_nonnull=1.000; min_met_nonnull=1.000 |
| Dundalk Co Louth | True | True | 2020-06-30 02:00:00 to 2023-06-04 20:00:00 | True | rows=25675; joint_rows=25596; pm10_nonnull=0.997; min_met_nonnull=1.000 |
| Pearse street dublin | True | True | 2021-01-22 07:00:00 to 2023-08-01 00:00:00 | True | rows=22098; joint_rows=22096; pm10_nonnull=1.000; min_met_nonnull=1.000 |
| Ringsend dublin | True | True | 2020-06-30 02:00:00 to 2023-08-01 00:00:00 | True | rows=27047; joint_rows=27037; pm10_nonnull=1.000; min_met_nonnull=1.000 |
| edenderry co offlay | True | True | 2021-08-31 17:00:00 to 2023-08-03 13:00:00 | True | rows=16784; joint_rows=16617; pm10_nonnull=0.990; min_met_nonnull=1.000 |
| henry street Limerick | True | True | 2021-06-30 10:00:00 to 2023-08-03 18:00:00 | True | rows=18279; joint_rows=18236; pm10_nonnull=0.998; min_met_nonnull=0.999 |
| porrlaoise co laois | True | True | 2020-06-30 02:00:00 to 2023-08-01 00:00:00 | True | rows=27047; joint_rows=27042; pm10_nonnull=1.000; min_met_nonnull=1.000 |
