# Script Inventory

- `code/e2_met_ireland_run.py`: existing multi-station rolling-origin producer for lag-only and lag+meteorology forecasts.
- `code/e2_met_madrid_run.py`: existing one-station Madrid rolling-origin producer.
- `code/e2_met_madrid_shared.py`: shared feature construction, persistence, SARIMA, XGBoost-direct, metrics and DM helpers.
- `code/run_meteorology_dynamic_experiment.py`: compact downstream compiler for the decisive dynamic-fidelity table and figures.
- `code/e2_met_ireland_config.json` and `code/e2_met_madrid_config.json`: experiment configs; both contain pre-existing absolute paths and should be relativized before reuse in a clean rerun.
