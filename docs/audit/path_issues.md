# Path Issues

Pre-existing absolute paths were found in reports, run notes and legacy configs. The new experiment script uses repo-relative paths internally.

Known files requiring cleanup before a fully portable rerun:
- `code/e2_met_ireland_config.json`
- `code/e2_met_madrid_config.json`
- `code/build_madrid_experiment_base.py`
- `code/e2_autocorrelation_analysis.py`
- `RUN_ORDER.md`
- selected historical files under `reports/`, `notes/`, and LaTeX build artifacts under `manuscripts/`.
