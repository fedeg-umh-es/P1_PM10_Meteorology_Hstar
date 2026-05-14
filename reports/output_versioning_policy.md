# Output Versioning Policy

Default policy for this repository:

- Version source code, configs, protocol notes, audit reports, compact manuscript tables, and final interpretation reports.
- Do not version raw data, processed full datasets, full prediction dumps, or heavyweight generated artifacts by default.
- Keep reproducible outputs regenerable from scripts plus config snapshots.

## Recommended tracking

Track:

- `code/e2_met_ireland_config.json`
- `code/e2_met_ireland_run.py`
- `code/e2_met_ireland_tables.py`
- `code/e2_met_ireland_figures.py`
- `code/e2_met_comparison_figures.py`
- `code/build_ireland_experiment_base.py`
- `code/audit_ireland_datasets.py`
- `reports/ireland_experiment_setup.md`
- `reports/ireland_dataset_inventory.md`
- `reports/ireland_dataset_inventory.csv`
- `reports/ireland_e2_met_results_interpretation.md`
- `reports/output_versioning_policy.md`

Track selectively if the paper needs frozen artifacts:

- `results/e2_met_ireland_pm10/manuscript_tables/*.csv`
- `results/e2_met_ireland_pm10/figures/*.png`
- `results/e2_met_ireland_pm10/figures/*.pdf`
- `results/e2_met_ireland_pm10/config_snapshot.json`
- `results/e2_met_ireland_pm10/run_metadata.json`

Do not track by default:

- `data_processed/ireland_pm10_meteorology_hourly.csv`
- `results/e2_met_ireland_pm10/predictions/*.csv`
- `results/e2_met_ireland_pm10/metrics/*.csv`
- `results/e2_met_ireland_pm10/stats/*.csv`
- `__pycache__/`
- `*.pyc`
- `.claude/`
- accidental local key files.

## Reason

The manuscript evidence should be reproducible from the scripts, config, and documented dataset build rules. Large intermediate outputs can be regenerated and should not obscure code review unless a release or paper artifact requires freezing them.
