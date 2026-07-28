# PROG-P2-00 — Provenance audit and repository authority decision

**Audit date:** 2026-07-28  
**Repository audited:** `fedeg-umh-es/P1_PM10_Meteorology_Hstar`  
**Read-only scope:** repository history, Git-tracked artefacts and GitHub branch/PR metadata. No experiment, training, regeneration or manuscript file was executed or changed.  
**Audited head:** `dd3602f297b4cb26dd6b96e3a5a3dbcecc1d465c` (`main`)  
**Decision:** **REPO_PARCIAL**

## Decision and closure state

This is the authoritative *computational* repository for P2/E2-MET: it contains the canonical Madrid and Ireland configurations, runners, rolling-origin implementation, versioned output artefacts and the merged Ireland evidence-recovery history. The historical `P1_` repository prefix is not a current programme assignment.

It is **not a complete provenance archive**. The canonical Madrid base dataset and the Ireland consolidated experiment base are ignored/untracked, their source raw files are absent, and the original Ireland row-level outputs were never committed. Consequently **PROG-P2-00 remains open**: the repository authority is settled, but a full data-provenance freeze is not.

This document supersedes the completion status in `docs/PROG_P2_00_CANONICAL_FREEZE.md`; that document remains the historical configuration-freeze record.

## Repository, branches and pull requests

| Ref | Commit / state | Classification |
|---|---|---|
| `main` | `dd3602f297b4cb26dd6b96e3a5a3dbcecc1d465c`, 2026-07-28 | Canonical audit ref; includes the prior P2 identity freeze (`26ccca6`) and Ireland regeneration merge (`1aad811`). |
| `claude/regenerate-ireland-evidence-wz7nc4` | `bdd17f8806778397a9322243182b00fa99fb06ce` | Historical PR #3 head; merged. Do not use as a separate evidence line. |
| `claude/recover-ireland-evidence` | `e9ad733bf12ca08fd8d8f184986bac5760e407c4` | Historical PR #2 head; merged. Do not use as a separate evidence line. |
| `claude/resume-data-pipeline-o6kpU` | `4d56c61ea3abaa6292738f8fa9d1c0b1a8f47fdb` | Historical, unmerged data-pipeline branch; not canonical. |
| `claude/review-experiment-results-3uUgY` | `742295df60ea710738fdf0559a242082fbcbd6d5` | Historical, unmerged path-only branch; not canonical. |
| `claude/update-readme-content-Y3iwO` | `2207bde90eb33b002c3b1088267478e4b09270d1` | PR #1 remains open; documentation-only and not canonical. |

| PR | State | Merge commit | Audit disposition |
|---|---|---|---|
| #1 — Update README | OPEN | — | No provenance role; leave open, do not merge as part of P2-00. |
| #2 — Recover and version Ireland evidence | MERGED | `bd9998d25b6c2d63d2bc9355fc4997f2873cf2cc` | Historical recovery layer. |
| #3 — Regenerate Ireland experiment evidence | MERGED | `1aad811dab0083396dc5c7eee5abebc34276514c` | Current regenerated Ireland evidence layer; explicitly not the original run. |

## Configurations and experiment boundaries

| Domain | Canonical config / runner | Period and stations | State |
|---|---|---|---|
| Madrid | `code/e2_met_madrid_config.json`; `code/e2_met_madrid_run.py` | Casa de Campo; train 2019-01-01 onward; test 2023-01-01 through 2023-12-31; hourly, horizons 1–24, stride 24 h | Config and tracked outputs present; underlying aligned CSV absent. |
| Ireland original | `code/e2_met_ireland_config.json`; `code/e2_met_ireland_run.py` | Eight stations: Birr, Dublin Airport, Dundalk, Pearse St., Ringsend, Edenderry, Henry St. Limerick, Portlaoise; train from 2020-01-01; test 2023-01-01 through 2023-08-01; hourly, horizons 1–24, stride 24 h | Config present; original consolidated input and original result CSVs absent. |
| Ireland regenerated | `results/e2_met_ireland_pm10_regenerated/` | Same eight stations; recovered source CSV inventory spans 2020-06-30/2021-08-31 to 2023-08-03, station-dependent | Recreated evidence, never to be relabelled as original. PR #3 documents 187,857 panel rows × 17 columns and 1,569 total origins. |

Both configs specify 300-tree XGBoost-direct (`max_depth=4`, `learning_rate=0.05`, `n_jobs=1`, seed 42), persistence and SARIMA, conditions `lags_only` / `lags_meteo`, and train-only fold preprocessing as intended by the code. This audit does not certify operational availability of meteorology: `docs/PROG_P2_01_METEOROLOGICAL_AVAILABILITY_CONTRACT.md` classifies present origin-time meteorology as retrospective/hindcast-only pending latency evidence.

## Dataset provenance and artefact inventory

| Artefact | Location | Size / SHA-256 | Classification and status |
|---|---|---|---|
| Madrid aligned base | `data_processed/madrid_pm10_meteorology_experiment_base.csv` | Not available | **MISSING.** Ignored by `.gitignore`; required by the config through an author-local absolute path. Raw Madrid sources likewise not tracked. |
| Ireland consolidated base | `data_processed/ireland_pm10_meteorology_hourly.csv` | Not available | **MISSING.** Ignored by `.gitignore`; required by the config through an author-local absolute path. |
| Ireland recovered source manifest | `results/e2_met_ireland_pm10_regenerated/manifests/source_csv_manifest.csv` | 1,772 bytes; `f83d2ab882ce642d3e76cc4ca5b3ba1cab5fed17cc80adc3a33055161eb32781` | Tracked manifest of 9 source CSVs: file names, station, dates, rows, bytes and individual SHA-256. The source CSVs and ZIP are not tracked. |
| Ireland source ZIP identity | `results/e2_met_ireland_pm10_regenerated/manifests/source_zip_manifest.txt` | 266 bytes; `bd197cae1a8ddab7517c2e5e9e4b2b1ea815ecafb57af41762195f0ba726a6b0` | Tracked identity record: `Finalised_merged_datasets-20260508T212701Z-3-001.zip`, source hash `8036a0b60a34a07a62a51bcbb5b65ec6d8416557ffcadb97803892302c35851d`; archive itself absent. |
| Original Ireland outputs | `results/e2_met_ireland_pm10/` | See `manifests/files_manifest.csv` | **DOCUMENTARY RECOVERY, NOT ORIGINAL NUMERICAL OUTPUTS.** Original predictions, metrics, DM statistics and run metadata are recorded as `NOT_FOUND`; recovered config, scripts, station manifest and manuscript-source values are tracked. |
| Regenerated Ireland predictions | `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv` | 14,729,573 bytes; `e8b262e0812da8c1243afcded5d621dcbed51d6dae56dc07a3fe9069c9484d8e` | **REGENERATED — NOT ORIGINAL RUN.** |
| Regenerated Ireland metrics | `results/e2_met_ireland_pm10_regenerated/metrics/metrics_all_models.csv` | 114,918 bytes; `9ef85270253046979160281fb900465a9161635088486607f71d7aae503442a0` | **REGENERATED — NOT ORIGINAL RUN.** |
| Regenerated Ireland H* | `results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary.csv` | 1,626 bytes; `3bedec78958528ea8d4b4499f92c248f4d40966c5cf65f6397b2bba9bdf409e4` | **REGENERATED — NOT ORIGINAL RUN.** A definition discrepancy is separately documented. |
| Regenerated Ireland DM-HLN | `results/e2_met_ireland_pm10_regenerated/stats/dm_lags_meteo_vs_lags_only.csv` | 2,971 bytes; `b60990088171c23e98425040c1ce367d732808fc562c3969165b769d909d3aac` | **REGENERATED — NOT ORIGINAL RUN.** |
| Madrid predictions (combined) | `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv` | 2,629,099 bytes; `e4a7edd656385df4f160176f0952a410848dc456cd5842981f191124189ea85c` | Tracked, but run metadata reports only `lags_only`, whereas combined output includes historical artefact layers; provenance not fully resolved. |
| Madrid metrics | `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv` | 12,897 bytes; `8ba9d94a4dd194c1ee1c07c513b0d714aaaa129032207bd74dd46a29c21a22ba` | Tracked; source input absent. |
| Madrid H* | `results/e2_met_madrid_pm10/metrics/hstar_summary.csv` | 167 bytes; `31cc1f67e67af54ac5f1d8d6f1b8c855bb400d23a93b01dfbb5b4a007449a71b` | Tracked; source input absent. |
| Madrid DM-HLN | `results/e2_met_madrid_pm10/stats/dm_lags_meteo_vs_lags_only.csv` | 349 bytes; `c078db6f10c9f6103a4e20f843a9617c53fa85851477ebbbf16b4a5cfb0a7cc5` | Tracked; source input absent. |

The comprehensive Ireland source inventory is already stored in `reports/ireland_dataset_inventory.csv` (9 source files; station/date/rows/columns and quality flags) and its regenerated source manifest provides the corresponding SHA-256 values. No equivalent versioned Madrid raw-data manifest exists.

## Verified discrepancies, duplicates and dependencies

1. **Missing external inputs:** both configured dataset paths are absolute author-local paths and their files are ignored. Reproduction therefore depends on external Madrid open-data extracts and on the recovered Ireland archive.
2. **Original versus regenerated Ireland evidence:** the `e2_met_ireland_pm10` tree is a recovery manifest, while `e2_met_ireland_pm10_regenerated` is a regenerated run. They must remain separate and neither can substitute silently for the unavailable original numerical outputs.
3. **Ireland H* definition inconsistency:** `hstar_definition_discrepancy.md` records that manuscript prose and the historic code/table convention differ; the regenerated output stores both definitions. No resolution is made by this audit.
4. **Madrid provenance gap:** the tracked `run_metadata.json` describes a 2026-05-15 `lags_only` run (362 origins, 26,064 predictions) while the combined prediction file is present as a larger historical artefact. With the base CSV absent, the combined provenance cannot be closed.
5. **Ireland source quality/station differences:** the source inventory records Rathmines as excluded and station-specific timestamp, duplicate, negative-value and coverage issues. Those are data-quality facts, not permissions to modify the frozen evidence.
6. **Operational dependency:** source publication/ingestion latency is absent for both domains. Current meteorology is therefore not to be called operationally available; this is documented in P2-01, not repaired here.

## Reproduction checks (read-only)

At a checkout of the audited commit, verify this inventory without executing an experiment:

```bash
git rev-parse HEAD
git branch -r
gh pr list --repo fedeg-umh-es/P1_PM10_Meteorology_Hstar --state all --limit 50
shasum -a 256 results/e2_met_ireland_pm10_regenerated/{predictions/predictions_all_models.csv,metrics/metrics_all_models.csv,metrics/hstar_summary.csv,stats/dm_lags_meteo_vs_lags_only.csv}
shasum -a 256 results/e2_met_madrid_pm10/{predictions/predictions_all_models.csv,metrics/metrics_all_models.csv,metrics/hstar_summary.csv,stats/dm_lags_meteo_vs_lags_only.csv}
git check-ignore -v data_processed/madrid_pm10_meteorology_experiment_base.csv data_processed/ireland_pm10_meteorology_hourly.csv
```

## Exact blocker and next action

**Blocker to completing PROG-P2-00:** obtain or preserve immutable copies of the two configured base datasets (or approved raw-source packages), with source URLs/licences, retrieval date, timezone/timestamp semantics, station mapping, row count and SHA-256; then link them to the committed configurations and output hashes. The current repository cannot supply these absent files.

**Next action:** keep PROG-P2-00 open under this blocker. Do not run/retrain anything. If the source packages are supplied, add a data-provenance manifest only (no experiment execution), then reassess whether the closure condition is met.
