# Ireland E2-MET evidence — recovery status

This directory did not exist on `main` before this recovery (branch
`claude/recover-ireland-evidence`, base commit `54569072ae525974838a84950cb0e31cf83cd5a2`).
It is being created to close the documentary blocker identified by the remote
audit: `manuscripts/manuscript_main.tex` cites detailed Ireland E2-MET
results (Section 4.2, Tables `tab:ireland_hstar`/`tab:ireland_dm`/`tab:rho1`,
four figures) whose source directory, `results/e2_met_ireland_pm10/`, was
never committed to this repository.

**Read `validation/evidence_validation_report.md` first.** In short:

- The original row-level predictions, per-station metrics, DM-HLN stats, and
  `run_metadata.json` for the Ireland run **could not be recovered or
  regenerated**. They were never committed to git (confirmed across the
  full, unshallowed history of every branch and PR ref), and regeneration is
  blocked because the source dataset
  (`data_processed/ireland_pm10_meteorology_hourly.csv`) was also never
  committed — `code/e2_met_ireland_config.json` points to it at an absolute
  path on the original author's local machine.
- What **was** recoverable: the exact configuration used
  (`config_snapshot.json`, copied verbatim from the still-tracked
  `code/e2_met_ireland_config.json`), and a committed, git-tracked summary
  document, `reports/ireland_e2_met_results_interpretation.md`, whose
  H\*-strict values and DM-HLN favours-counts match the manuscript's Table
  `tab:ireland_hstar`/`tab:ireland_dm` exactly. That document is the
  strongest surviving corroboration that the manuscript's Ireland numbers
  came from a real, executed run — but it is a summary, not row-level
  evidence, and it cannot by itself let anyone re-derive or independently
  verify the manuscript's per-horizon skill curves, `rho1` values, or exact
  descriptive statistics.
- A **separate, later pipeline** (`code/run_meteorology_dynamic_experiment.py`)
  left real, committed row-level Ireland predictions and per-station-horizon
  metrics elsewhere in this repository
  (`outputs/metrics/predictions_meteorology_experiment.csv`,
  `outputs/tables/master_meteorology_diagnostic_table.csv`). These are
  **not** the manuscript's source data: independently recomputing
  `H*_strict` from them, using the manuscript's own definition, disagrees
  with the manuscript for 3 of 8 stations. They are documented in
  `validation/evidence_validation_report.md` and `manifests/files_manifest.csv`
  but were deliberately **not copied into this directory**, to avoid
  misrepresenting their provenance.

## Contents

- `README.md` — this file.
- `config_snapshot.json` — verbatim copy of `code/e2_met_ireland_config.json` at this commit.
- `run_metadata.json` — reconstructed from code/config/repo evidence only; run-specific fields (exact timestamp, per-station `n_origins`) are `NOT_VERIFIED`, not invented.
- `manifests/stations_manifest.csv` — per-station row-count cross-check between the manuscript and `reports/ireland_experiment_setup.md`.
- `manifests/files_manifest.csv` — full artifact-by-artifact recovery ledger (found / not found / why), with hashes for everything that was found.
- `tables/manuscript_source_values.csv` — claim-by-claim comparison of every quantitative Ireland claim in `manuscripts/manuscript_main.tex` against whatever evidence could be located.
- `validation/evidence_validation_report.md` — full narrative recovery report and verdict.

No `predictions/`, `metrics/`, or `stats/` subdirectories were created here:
per the task's own instructions, files are not created just to satisfy a
directory layout when no real evidence backs them.
