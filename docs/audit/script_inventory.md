# Script Inventory

- `code/e2_met_ireland_run.py`: existing multi-station rolling-origin producer for lag-only and lag+meteorology forecasts.
- `code/e2_met_madrid_run.py`: existing one-station Madrid rolling-origin producer.
- `code/e2_met_madrid_shared.py`: shared feature construction, persistence, SARIMA, XGBoost-direct, metrics and DM helpers.
- `code/run_meteorology_dynamic_experiment.py`: compact downstream compiler for the decisive dynamic-fidelity table and figures.
- `code/e2_met_ireland_config.json` and `code/e2_met_madrid_config.json`: experiment configs; both contain pre-existing absolute paths and should be relativized before reuse in a clean rerun.
- `code/hstar_metrics.py`: H* Methodological Contract v1.2.1 -- loss matrices, the three H* variants (`Hstar_strict_from_h1`, `Hstar_strict_max_run`, `Hstar_relax`) with ceiling flags, and Moving-Block Bootstrap CI for `Delta H*`. Read-only; consumes existing predictions/metrics, never re-runs a model.
- `code/export_results_summary_v1_2_1.py`: orchestrates `hstar_metrics.py` over the Madrid and Ireland-regenerated results directories and writes `results/results_summary_v1.2.1.csv`/`.json`. See `docs/protocol/hstar_v1_2_1_contract.md`.
