# Ireland E2-MET evidence — REGENERATED — NOT ORIGINAL RUN

This directory contains a **freshly regenerated** Ireland E2-MET experiment,
executed from the 9 recovered source CSVs
(`Finalised_merged_datasets-20260508T212701Z-3-001.zip`,
SHA-256 `8036a0b60a34a07a62a51bcbb5b65ec6d8416557ffcadb97803892302c35851d`),
using the repository's own unmodified `code/e2_met_ireland_run.py` and
`code/e2_met_ireland_config.json`. It is **not** the original run that
produced the numbers in `manuscripts/manuscript_main.tex` — that original
run's row-level artifacts were never committed to git and are not
recoverable (see `results/e2_met_ireland_pm10/validation/evidence_validation_report.md`
for the full prior recovery attempt). This directory instead answers a
different, narrower question: *does re-running the same, unmodified pipeline
against a from-scratch build of the same recovered raw data reproduce the
manuscript's numbers?*

**Label: `REGENERATED — NOT ORIGINAL RUN`.**

## What was (and was not) changed

**Not changed:** stations, train/test periods, forecast horizons (1..24),
origin stride (24h), lags, calendar features, meteorological features,
XGBoost hyperparameters (incl. `random_state: 42`), SARIMA order/seasonal
order, DM horizons/loss, `random_seed: 42`, the persistence baseline, or any
evaluation metric. All are byte-identical to `code/e2_met_ireland_config.json`
(diff-verified at config-generation time).

**Changed (portability / execution strategy only):**
- `dataset_path` / `results_dir` in a temporary config copy (the committed
  config hardcodes an author-local absolute macOS path; see
  `code/e2_met_ireland_config.json` and the original recovery's root-cause
  analysis).
- `code/build_ireland_experiment_base.py` gained `--input-dir`/`--out-csv`/
  `--out-md` CLI flags (no processing-rule changes) so it can build from any
  directory, not just `~/Downloads/`.
- Execution was parallelized as 8 single-station subprocess invocations of
  the unmodified script (4 concurrent, using its own pre-existing `--station`
  flag) rather than one sequential 8-station run, to fit within available
  session time (~4h wall-clock instead of an estimated ~17h sequential). See
  `parallelization_equivalence.md` for the full equivalence argument and
  `merge_validation_report.md` for the empirical post-merge verification.

## Contents

- `README.md` — this file.
- `config_snapshot.json` — the portable config actually used (verbatim
  fields except `dataset_path`/`results_dir`, matching `code/e2_met_ireland_config.json`).
- `run_metadata.json` — start/end times, execution strategy, row counts,
  per-station-shard metadata.
- `predictions/predictions_all_models.csv` — combined row-level predictions,
  all 8 stations, both conditions, all 3 models, all 24 horizons (150,624
  rows). Per-station-condition files also exist on disk but are not git
  version-tracked (strict subset of the combined file; see `.gitignore`).
- `metrics/metrics_all_models.csv` — RMSE/MAE/skill per station × condition ×
  model × horizon (768 rows).
- `metrics/hstar_summary.csv` — H*_strict (as currently computed by
  `code/e2_met_ireland_run.py`, i.e. `H_strict_max_run`) and H*_relax per
  station × condition × model.
- `metrics/hstar_summary_both_definitions.csv` — `H_strict_from_h1` and
  `H_strict_max_run` computed and kept **separately** (see
  `hstar_definition_discrepancy.md`).
- `stats/dm_lags_meteo_vs_lags_only.csv` — Diebold-Mariano-HLN test results
  per station × horizon.
- `manifests/source_csv_manifest.csv` — name, size, SHA-256, rows, columns,
  period, inclusion status for each of the 9 recovered source CSVs (the CSVs
  themselves are not committed).
- `manifests/source_zip_manifest.txt` — ZIP file SHA-256 verification record.
- `row_count_discrepancy_analysis.md` — reconciliation of the regenerated
  panel's 187,857 rows against the task brief's cited 188,817 figure (not
  reproducible from any accounting tried; treated as unverified).
- `parallelization_equivalence.md` — why the 8-parallel-process execution
  strategy is scientifically equivalent to a sequential run.
- `hstar_definition_discrepancy.md` — the manuscript's Methods prose defines
  `H*_strict` as a run starting at h=1, but its own tables match the
  "longest run anywhere" definition the code actually computes; documented,
  not silently resolved.
- `merge_validation_report.md` — post-merge structural QC (station set,
  origin counts, horizon coverage, uniqueness, causality, valid-pair parity,
  no Madrid mixing) — all PASS.
- `output_hashes.csv` — SHA-256 of every file in this directory.
- `manuscript_claim_comparison.csv` — all 76 manuscript claims compared
  against these regenerated, merged outputs (57 MATCH, 17 ROUNDING_MATCH,
  2 MISMATCH — see below).

## Consolidated dataset (not committed, per repo policy)

`data_processed/ireland_pm10_meteorology_hourly.csv` (187,857 rows × 17
columns, 8 stations; SHA-256 `a320e2958e1beb0beb568879c4510bc8cb5e4d7fc58e2b46b6cc4d40a9a74546`)
is **not** committed to git, consistent with `reports/output_versioning_policy.md`'s
existing "do not track by default" rule for this exact file. It is fully
reproducible from the recovered source CSVs (whose hashes are in
`manifests/source_csv_manifest.csv`) via:

```
python3 code/build_ireland_experiment_base.py --input-dir <path-to-9-CSVs>
```

## Summary of results

- 8 stations, 1,569 total rolling origins (Birr 212, Dublin Airport 145,
  Dundalk 154, Pearse St. 212, Ringsend 212, Edenderry 211, Henry St. 211,
  Portlaoise 212) — all origins satisfy `train_end < origin` and
  `forecast_timestamp > origin` (verified, see `merge_validation_report.md`).
- 76/76 manuscript claims compared: **57 MATCH, 17 ROUNDING_MATCH, 2
  MISMATCH, 0 SOURCE_NOT_FOUND** (the original evidence-recovery pass had 32
  SOURCE_NOT_FOUND claims — all descriptive-statistics and ρ1 claims are now
  resolved because this regeneration has the actual row-level dataset).
- The 2 remaining MISMATCHes: (1) DM-HLN favours count 24/7/1 vs. the
  manuscript's 23/8/1 (one cell differs out of 32); (2) Edenderry's total row
  count (16,784 regenerated vs. 16,555 implied by the manuscript's own
  descriptive table) — both already flagged as open, unresolved discrepancies
  in the prior evidence-recovery pass and not newly introduced by this
  regeneration.
- See `hstar_definition_discrepancy.md` for the H*_strict definition finding.

No results here overwrite or modify `results/e2_met_ireland_pm10/` (the prior
recovery's documentary evidence) or any Madrid results
(`results/e2_met_ireland_pm10_madrid_pm10` — not applicable; Madrid results
live at `results/e2_met_madrid_pm10/`, untouched by this work). The
manuscript (`manuscripts/manuscript_main.tex`) is not modified.
