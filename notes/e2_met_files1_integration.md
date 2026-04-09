# files1 Integration Note

## Files Inspected In `/Users/federicogarciacrespi/Downloads/files1`

- `EXPERIMENT_DESIGN.md`
- `e2_config.py`
- `RUN_ORDER.md`
- `shared_protocol.py`
- `run_condA_lags.py`
- `run_condB_meteo.py`
- `run_dm_comparison.py`

## What Was Reusable

- Documentation structure for:
  - explicit scientific question
  - leakage-control table
  - interpretation matrix for `delta_H*`
  - manual pre-run confirmation checklist
  - stepwise execution instructions
- The idea of making the A/B symmetry explicit in the design document.

## What Was Rejected

- Any reference to Elche.
- Any assumption of daily data.
- Any assumption of `h=1..7`.
- Any alternate dataset such as `pm10_clean.csv`.
- Any alternate output layout such as `results_e2`.
- Any alternate source layout such as `e2_met/src`.
- Any wording that treated SARIMA as missing or placeholder.
- The external Python runner files as canonical code, because the repo already has a canonical Madrid pipeline.

## What Was Changed To Align With Canonical Madrid `h=1..24`

- Domain normalized to Madrid PM10, station 24, Casa de Campo.
- Horizon normalized to `h=1..24`.
- Protocol normalized to the existing canonical 2023 rolling-origin setup with `24` hour stride.
- Baselines normalized to:
  - persistence primary baseline
  - SARIMA secondary baseline
- Main comparison normalized to:
  - `lags_only`
  - `lags_meteo`
  - XGBoost-direct
- Output references normalized to:
  - `results/e2_met_madrid_pm10/...`

## Repo Files Modified Or Created

- Modified:
  - `/Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar/notes/e2_met_experiment_design.md`
  - `/Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar/RUN_ORDER.md`
- Created:
  - `/Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar/notes/e2_met_files1_integration.md`

## Validation Performed

The edited canonical files were checked to ensure they no longer contain incompatible references such as:
- `Elche`
- `daily`
- `h=1..7`
- placeholder SARIMA wording
- `results_e2`
- `e2_met/src`

No remaining incompatible references were left in the edited canonical files.
