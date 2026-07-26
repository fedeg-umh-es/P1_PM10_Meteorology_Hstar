# Ireland E2-MET Evidence Recovery — Validation Report

- Date: 2026-07-26
- Repository: `fedeg-umh-es/P1_PM10_Meteorology_Hstar`
- Base branch: `main`
- Base commit: `54569072ae525974838a84950cb0e31cf83cd5a2` ("Add meteorology dynamic fidelity experiment")
- Working branch: `claude/recover-ireland-evidence`
- Scope: recover, verify, and version the evidence for the Ireland E2-MET results cited in `manuscripts/manuscript_main.tex`. No manuscript rewriting, no P1/P3 work, no origin/nwp/oracle redesign.

## 1. Procedencia de la evidencia

### 1.1 Manuscript claim inventory (Step 1)

`manuscripts/manuscript_main.tex` (886 lines) cites Ireland results in:
Abstract (lines 80-83), Section 2.2 "Ireland" (207-264, including descriptive
Table `tab:descriptive` at 230-256), Section 4.2 "Ireland: station-level H*
and meteorology benefit" (435-508, including `tab:ireland_hstar` at 469-497
and `tab:ireland_dm` at 510-536), Section 5.1 discussion (558-604, including
the ρ₁ table `tab:rho1` at 786-818 and the combined scatter figure), Section
5.3 (628-635), and Conclusions (672-713). Four dedicated Ireland figures are
included: `ireland_figure_skill_by_station.png`,
`ireland_figure_delta_skill.png`, `ireland_figure_dm_significance.png`,
`ireland_figure_hstar_summary.png`. Every individual quantitative claim
extracted from these sections is enumerated, row by row, in
`../tables/manuscript_source_values.csv` (76 rows).

### 1.2 Evidence search (Steps 2-4)

Full-repository search (`find`, `grep -RniE`) for `Ireland|Irish|EPA|
e2_met_ireland|ireland_pm10|lags_only|lags_meteo` and the alternate-name list
in the task brief was performed against the complete working tree. Results
are enumerated in `../manifests/files_manifest.csv`. Summary:

- **A real, committed Ireland pipeline exists**: `code/e2_met_ireland_run.py`,
  `code/e2_met_ireland_config.json`, `code/e2_met_ireland_tables.py`,
  `code/e2_met_ireland_figures.py`, `code/build_ireland_experiment_base.py`,
  `code/audit_ireland_datasets.py`, `code/e2_autocorrelation_analysis.py`,
  plus committed reports (`reports/ireland_experiment_setup.md`,
  `reports/ireland_dataset_inventory.{md,csv}`,
  `reports/ireland_e2_met_results_interpretation.md`,
  `reports/output_versioning_policy.md`).
- **No `results/e2_met_ireland_pm10/` directory of any kind exists anywhere
  in the tracked tree** (confirmed before this recovery began).
- **No raw or processed Ireland dataset exists in the repository**
  (`data_processed/` contains only `.gitkeep`).
- **A separate, later pipeline** (`code/run_meteorology_dynamic_experiment.py`,
  added in the same commit as the repository's current HEAD) produced real,
  committed row-level Ireland artifacts under `outputs/` — but, as detailed
  in Section 3 below, these do **not** reproduce the manuscript's numbers.

### 1.3 Git history search (Step 3)

The repository's initial shallow clone (used by the prior remote-access
audit) showed only one commit reachable from `main`, which led that audit to
conclude `main`'s history had been squashed. **That conclusion was an
artifact of the shallow clone, not a fact about the repository.** After
`git fetch --unshallow`, `main` resolves to a full, linear, 27-commit history
going back to two independent initial commits (merged at `63723f7`). This
correction is recorded here because it materially changes the recovery
picture: nothing was destructively squashed away.

`git ls-remote` against the full remote additionally revealed two branches
not visible in the original audit's shallow clone:
`claude/resume-data-pipeline-o6kpU` (`4d56c61...`) and
`claude/review-experiment-results-3uUgY` (`742295d...`). Both were fetched
and their full trees inspected:

- `claude/resume-data-pipeline-o6kpU` — `results/` contains only `.gitkeep`.
- `claude/review-experiment-results-3uUgY` — `results/` contains only the
  Madrid E2-MET tree (`results/e2_met_madrid_pm10/...`), identical in kind to
  what is already on `main`. No Ireland content.

`git log --all --oneline -- 'results/e2_met_ireland_pm10/*'` was run against
every ref reachable from the remote (`main`, both branches above,
`refs/pull/1/head`, `refs/pull/1/merge`) and returns **zero commits**. The
Ireland results directory has never existed in this repository's git history,
on any branch, at any point.

`git log --all --oneline --name-only -- '*ireland*' '*Ireland*'` shows the
Ireland pipeline was added in a single commit, `7f97608887e876906dcde6a50d48302565447ac4`
("Add Ireland E2-MET experiment workflow", 14 May 2026), which added the
code and reports listed in §1.2 but **no `results/` content** — confirming
the omission was present from the very first commit that introduced Ireland
work, not a later deletion.

### 1.4 Local/untracked search (Step 4)

`git status --ignored` inside the repository clone returns nothing. A scoped
`find /workspace -maxdepth 4 -iname '*ireland*' -o -iname '*irish*' -o
-iname '*e2_met_ireland*'` outside the repository clone returns nothing.
No local untracked Ireland artifacts exist anywhere in this session's
environment.

## 2. Root cause (why the evidence is missing)

Two independent, mutually reinforcing pieces of committed evidence explain
the gap precisely, without speculation:

1. **`code/e2_met_ireland_config.json`** — the config `code/e2_met_ireland_run.py`
   reads by default — hardcodes:
   - `"dataset_path": "/Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar/data_processed/ireland_pm10_meteorology_hourly.csv"`
   - `"results_dir": "/Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar/results/e2_met_ireland_pm10"`

   Both are absolute paths on the original author's local machine, **not**
   paths inside this git repository. Running the script with its committed
   default config therefore never wrote its outputs into a location git
   could track, regardless of intent.
2. **`reports/output_versioning_policy.md`** (committed in the same commit
   that added the Ireland pipeline) explicitly states the repository's own
   policy: `results/e2_met_ireland_pm10/predictions/*.csv`,
   `metrics/*.csv`, and `stats/*.csv` are **"Do not track by default"**, and
   `manuscript_tables/*.csv`, `figures/*`, `config_snapshot.json`, and
   `run_metadata.json` should be tracked **"selectively if the paper needs
   frozen artifacts."** The paper does need them — it cites them by
   filename — but this selective-tracking step was never carried out.
   `docs/audit/path_issues.md` (also committed) independently lists
   `code/e2_met_ireland_config.json` and `code/e2_met_ireland_figures.py`/
   `code/e2_autocorrelation_analysis.py` as files with known author-local
   absolute paths "requiring cleanup before a fully portable rerun" — the
   repository's own prior audit already flagged exactly this problem.

## 3. The "meteorology dynamic fidelity experiment" — a distinct, non-matching pipeline

`code/run_meteorology_dynamic_experiment.py` (added in commit `5456907`, the
current HEAD, "Add meteorology dynamic fidelity experiment") is a **separate**
pipeline that computes additional fidelity diagnostics (`phi_h`, `r_h`,
`kge_h`, alongside `skill_h`/`rmse`) for Ireland. Its own documentation
(`results/meteorology_experiment_closure.md`) states verbatim: *"this run
compiles existing rolling-origin forecasts rather than refitting them."*
Its source code (`code/run_meteorology_dynamic_experiment.py:17`) hardcodes:

```python
SOURCE_PREDICTIONS = ROOT / "results" / "e2_met_ireland_pm10" / "predictions" / "predictions_all_models.csv"
```

and raises `FileNotFoundError` if that file is absent. This is direct code
evidence that `results/e2_met_ireland_pm10/predictions/predictions_all_models.csv`
**did exist on the author's local disk** at some point after the original
Ireland run — corroborating that a real run happened — but it was never
committed to git, consistent with `output_versioning_policy.md`, and no
longer exists anywhere this session can reach.

**This pipeline's own outputs do not reproduce the manuscript's numbers.**
Independently recomputing `H*_strict` from `outputs/tables/master_meteorology_diagnostic_table.csv`
(384 rows, 8 stations × 24 horizons × 2 conditions), applying the
manuscript's own literal definition ("the length of the longest consecutive
positive-skill run beginning at h=1", `manuscript_main.tex:359-361`), gives:

| Station | Manuscript `H*_strict` (lags_only / lags_meteo) | Recomputed from `master_meteorology_diagnostic_table.csv` | `skill_h(h=1)` in that file |
|---|---|---|---|
| Dublin Airport | 22 / 23 | **0 / 0** | lags_only=−0.107, lags_meteo=−0.070 |
| edenderry co offlay | 16 / 16 | **7 / 7** | breaks at h=8: lags_only=−0.058, lags_meteo=−0.105 |
| henry street Limerick | 18 / 24 | **0 / 24** | lags_only(h=1)=−0.006 (negative) |

`H*_relax` matches the manuscript exactly for all 8 stations in this file
(saturates at 24 everywhere, as the manuscript also reports), but
`H*_strict` genuinely disagrees for 3 of 8 stations because the underlying
`skill_h(h=1)` values are of the opposite sign from what the manuscript's
Table `tab:ireland_hstar` requires. This is classified as **UNRESOLVED** in
`../tables/manuscript_source_values.csv`'s MISMATCH rows: the evidence does
not indicate which run is "correct," only that they are demonstrably
different runs of nominally the same experiment, and only the earlier one's
raw predictions were ever the manuscript's actual source (per
`reports/ireland_e2_met_results_interpretation.md`'s exact numeric match —
see §4). Per the task's rules, this file was **not** copied into
`results/e2_met_ireland_pm10/` as if it were the manuscript's source, and
the manuscript was **not** modified to match it — the mismatch is real,
unresolved, and does not meet the bar (evidence source is ambiguous, not
"inequívoca") for a documentary correction.

## 4. The one committed document that does corroborate the manuscript

`reports/ireland_e2_met_results_interpretation.md` (committed at `7f97608`,
still present at HEAD) states its own source as
`results/e2_met_ireland_pm10/run_metadata.json` — i.e., it is a **summary of
the original, now-uncommitted run**, not an independent computation. Its
numbers match the manuscript exactly:

- `H*_strict`: Dublin Airport 22→23, Henry St. Limerick 18→24, "all other
  stations: unchanged" — **identical** to `manuscript_main.tex` Table
  `tab:ireland_hstar`.
- `H*_relax`: "saturates at 24 hours for both conditions in all stations" —
  **identical** to the manuscript.
- DM-HLN favours counts: `lags_meteo=23, lags_only=8, undetermined=1` out of
  32 station-horizon cells, with an **identical** per-station breakdown
  (verified by independently deriving the same table directly from the
  manuscript's own `tab:ireland_dm` DM-statistic signs — both sources agree
  to the cell).

This is strong, git-tracked, non-fabricated corroboration that the
manuscript's Ireland Table 3/Table 4 numbers came from a real, executed run
distinct from (and inconsistent with) the later
`run_meteorology_dynamic_experiment.py` pipeline. It is a **summary
document**, not row-level evidence — it cannot be used to regenerate skill
curves, verify `ρ1`, or verify descriptive statistics, and it was not
authored as a frozen "manuscript table" artifact, so it carries less
evidentiary weight than a row-level CSV would.

## 5. Ficha del experimento (Step 5)

```text
Experiment ID: e2_met_ireland_pm10
Dataset: data_processed/ireland_pm10_meteorology_hourly.csv (NOT VERIFIED to exist anywhere reachable; absent from repo)
Stations: Birr co offlay, Dublin Airport, Dundalk Co Louth, Pearse street dublin,
          Ringsend dublin, edenderry co offlay, henry street Limerick, porrlaoise co laois (8; matches manuscript)
Target: PM10
Frequency: hourly
Training window: expanding, train_start=2020-01-01 00:00:00 (code/e2_met_ireland_config.json)
Forecast horizons: 1..24 (config + manuscript agree)
Origins: test_start=2023-01-01, test_end=2023-08-01, stride=24h (daily) -- exact per-station n_origins NOT VERIFIED
Stride: 24 hours (origin_stride_hours in config)
Models: persistence, sarima, xgboost_direct (lags_only / lags_meteo)
Baseline: persistence
Meteorological condition: lags_only vs lags_meteo (9 concurrent-observed meteo variables; NOT NWP forecasts, per manuscript's own framing)
Preprocessing: min_train_rows=8760; SARIMA truncated to sarima_max_train_rows=17520 (config, matches manuscript Methods)
Random seed: 42 (config + manuscript Table "Fixed XGBoost hyperparameters")
Entry point: code/e2_met_ireland_run.py
Config: code/e2_met_ireland_config.json
Expected output directory: results/e2_met_ireland_pm10/ (per script's ensure_results_dirs call -- but config's results_dir is an author-local absolute path, see Section 2)
```

## 6. Validación metodológica mínima (Step 6)

Based on direct reading of `code/e2_met_ireland_run.py`,
`code/rolling_origin.py` (shared with the already-audited Madrid pipeline),
and `code/e2_met_ireland_config.json`:

| Control | Estado | Evidencia |
|---|---|---|
| Rolling-origin temporal order | VERIFICADO | `get_train_window`/`get_test_window` (shared `rolling_origin.py`, same module Madrid uses) strictly split train (`< origin`) vs. test (`>= origin`) by timestamp. |
| `train_end < forecast_date` | VERIFICADO | Same mechanism; origins are generated only within `[test_start, test_end]`, training window is always strictly before the origin. |
| Preprocessing train-only | PARCIALMENTE VERIFICADO | `fit_xgboost_direct(train_df=train_df, ...)` is called with only the train slice per origin; internals of feature scaling/imputation (in `e2_met_madrid_shared.py`) were not read line-by-line in this pass. |
| Baseline computed on same pairs as model | VERIFICADO | Persistence, SARIMA, and XGBoost predictions are generated inside the same per-origin loop against the same `test_df`/`y_true`. |
| Equal valid pairs, model vs. persistence | VERIFICADO | Same loop, same origins/horizons for all models by construction (`rows.append` blocks share the same `origin`/`horizon` iteration). |
| No off-by-one in lags | PARCIALMENTE VERIFICADO | Configured lags `[1,2,3,6,12,24,48,168]` match the manuscript exactly; exact indexing in the shared feature-builder was not exhaustively re-derived in this pass. |
| No future-observed meteorology treated as operational | PARCIALMENTE VERIFICADO | Meteorology is concurrent with the origin timestamp `t` (not future relative to `t`), so no leakage in the strict causal sense; but the "this is a retrospective upper bound, not operational" caveat exists only in manuscript prose (lines 316-322) and is **not** enforced by any code flag anywhere in this repository — same finding as the prior remote P2 audit. |
| `n_origins` traceable | NO VERIFICADO | No committed artifact records per-station origin counts; manuscript only states an approximate range ("210-365 origins per station," line 281). |
| Stations and periods consistent | PARCIALMENTE VERIFICADO | Station identities and counts (8) are consistent everywhere; but per-station row counts show real discrepancies between the manuscript's implied totals and `reports/ireland_experiment_setup.md` — see `../manifests/stations_manifest.csv` (5 of 8 stations differ by more than 1 row, up to 229 rows for Edenderry). |
| Metrics reported by horizon | PARCIALMENTE VERIFICADO | The methodology computes and the manuscript reports per-horizon (h=1..24) metrics; the underlying committed metrics files for Ireland do not exist to verify this directly. |
| Metadata coherent with outputs | INCONSISTENTE | No `run_metadata.json` exists for the original run at all. The later `run_meteorology_dynamic_experiment.py` pipeline's own outputs are internally self-consistent but numerically disagree with the manuscript for 3 of 8 stations (Section 3). |
| No mixing between Madrid and Ireland | VERIFICADO | Separate config files, separate scripts, separate (intended) results directories, separate manuscript sections/tables throughout; no cross-contamination found. |

No claim of "operational" status is made anywhere for the `lags_meteo`
condition in this recovery — consistent with the manuscript's own framing of
it as a retrospective upper bound.

## 7. Recuperación de artefactos (Step 7) — case-by-case

| Artifact | Case | Outcome |
|---|---|---|
| `code/e2_met_ireland_config.json` (→ `config_snapshot.json`) | A (in git, unmodified) | Recovered — copied verbatim, hash recorded in `../manifests/files_manifest.csv`. |
| `reports/ireland_e2_met_results_interpretation.md`, `ireland_experiment_setup.md`, `ireland_dataset_inventory.{md,csv}`, `docs/audit/{meteorology_experiment_audit,path_issues}.md` | A (already in git) | Used as corroborating evidence in place; not moved (already properly versioned at their existing paths). |
| Row-level predictions, per-station metrics, DM stats, `run_metadata.json` (original run) | D | **NOT RECOVERED.** Never committed (full unshallowed history search, all branches/PR refs); not regenerable (source dataset absent from repo and only ever existed at an author-local path). |
| `outputs/tables/master_meteorology_diagnostic_table.csv`, `outputs/metrics/predictions_meteorology_experiment.csv` | B (exist locally in git elsewhere in the repo) | Validated (schema, row/station counts) and found to **disagree** with the manuscript for 3/8 stations' `H*_strict`. Documented as an auxiliary, non-canonical dataset; **not copied** into `results/e2_met_ireland_pm10/` to avoid misattributing provenance. |
| Descriptive statistics (Mean/SD/P95 per station), `ρ1` per station | D | **NOT RECOVERED.** No committed artifact contains PM10 concentration distributions or autocorrelation values for Ireland; `code/e2_autocorrelation_analysis.py` requires the same absent raw dataset plus the absent Ireland H* table. |
| 4 Ireland manuscript figures (`manuscripts/figures/ireland_figure_*.png`) | A (already in git) | Present and unmodified; explicitly **not** treated as proof of validity (no source table exists to regenerate or numerically verify them), per the audit rule against inferring figure correctness from PNG presence alone. |

## 8. Coincidencia con el manuscrito (Step 14 summary)

Full detail in `../tables/manuscript_source_values.csv` (76 claim rows):

| Status | Count |
|---|---|
| MATCH | 31 |
| ROUNDING_MATCH | 3 |
| MISMATCH | 10 |
| SOURCE_NOT_FOUND | 32 |

The 31 MATCH + 3 ROUNDING_MATCH rows are dominated by `H*_strict`/`H*_relax`
values corroborated against `reports/ireland_e2_met_results_interpretation.md`
(a summary document, not row-level evidence) and 3 stations' row counts
matching `reports/ireland_experiment_setup.md` to within 1 row. The 10
MISMATCH rows are the same 8 `H*_strict` cells compared instead against the
non-canonical `master_meteorology_diagnostic_table.csv` dataset (3 genuine
numeric disagreements, doubled across both conditions where applicable) plus
5 stations whose row counts differ from the manuscript's implied totals by
8-229 rows. The 32 SOURCE_NOT_FOUND rows are entirely descriptive statistics
(Mean/SD/P95 PM10, 24 rows) and `ρ1` autocorrelation values (8 rows), none of
which have any committed source.

## 9. Discrepancias (Step 16 classification)

- **Station row counts (5 of 8 stations, `../manifests/stations_manifest.csv`)**:
  classified **UNRESOLVED**. `reports/ireland_experiment_setup.md`'s totals
  are pre-split (no train/eval boundary), so the gap versus the manuscript's
  train+eval sums cannot be attributed with certainty to the manuscript's
  stated per-origin missing-data exclusion (`manuscript_main.tex:194`)
  without the row-level dataset. Not corrected in the manuscript — the
  underlying source data needed to resolve it is absent.
- **`H*_strict` for Dublin Airport, Edenderry, Henry St. Limerick vs.
  `master_meteorology_diagnostic_table.csv`**: classified **UNRESOLVED**
  (candidate explanations — a later non-identical rerun, or a materially
  different data snapshot — are both consistent with the evidence, and
  cannot be adjudicated without the missing original row-level predictions).
  Not a manuscript error by default; not confirmed correct either.

No manuscript edits were made. No discrepancy met the bar in the task's own
rules for a documentary correction (unambiguous source, purely documentary,
minimal, scientifically inert) — every discrepancy found traces back to
missing source data, not to an unambiguous, correctable documentation typo.

## 10. Tests (Step 17)

`tests/test_meteorology_experiment_outputs.py` (the repository's only test
file) tests the **later** `master_meteorology_diagnostic_table.csv`/
`predictions_meteorology_experiment.csv` schema (column presence, null
checks, horizon/condition enumeration, absolute-path hygiene) — it does not
test `code/e2_met_ireland_run.py` or anything under
`results/e2_met_ireland_pm10/`, because nothing under that path has ever
existed for it to test.

- Test present: YES (for the auxiliary dataset only; NO test exists for the original `e2_met_ireland_run.py` pipeline).
- Test executed: NO (`python3 -m pytest` — pytest is not installed in this session's environment).
- Test result: NOT EXECUTED.
- CI status: NO CI CONFIGURED (`.github/workflows/` absent from this repository, confirmed via `mcp__github__actions_list` returning zero workflows in the prior remote audit).

No new test was added in this recovery: the task scopes new tests to
validating "el esquema recuperado," and nothing row-level was recovered to
write a schema test against.

## 11. Limitations

- The original Ireland row-level predictions, metrics, DM statistics, and
  `run_metadata.json` are unrecoverable in this session: not in git history,
  not local, not regenerable (source dataset absent).
- Exact per-station `n_origins`, descriptive PM10 statistics (Mean/SD/P95),
  and `ρ1` autocorrelation values cannot be verified from any committed
  artifact.
- `reports/ireland_e2_met_results_interpretation.md` corroborates several
  headline manuscript numbers but is a summary, not primary evidence — it
  cannot substitute for row-level verification.
- The row-count and `H*_strict` discrepancies documented in Sections 8-9
  remain open and unresolved; they are documented, not fixed.
- pytest is not installed in this session, so no test execution (new or
  existing) could be independently verified beyond static inspection.

## 12. Veredicto de recuperación

```text
PARTIALLY RECOVERED
```

Justification: real, non-invented evidence was recovered and versioned
(exact configuration, and independent corroboration via a committed summary
document for several headline manuscript numbers), and every gap and
discrepancy is documented with a specific, evidenced root cause rather than
hidden or guessed at. However, the row-level predictions, per-station
metrics, and `ρ1`/descriptive statistics that would let a third party fully
verify or regenerate the manuscript's Ireland results are not recoverable in
this session, so this does not reach `RECOVERED AND VERIFIED`. It exceeds
`NOT RECOVERED` because real, verifiable, git-traceable evidence — not
merely absence — was established for the majority of the manuscript's
headline `H*` and DM-HLN claims.

This report does not issue a new global P2 verdict; that remains the
responsibility of a subsequent, separate scientific audit pass.
