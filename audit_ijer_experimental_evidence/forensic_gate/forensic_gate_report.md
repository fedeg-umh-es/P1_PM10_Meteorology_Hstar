# Forensic gate — IJER Madrid–Ireland experimental evidence audit

**Repository (confirmed local):** `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland`
**Branch:** `codex/p1-editorial-computational-audit`
**HEAD commit:** `18d0f830b1b7bf92684d5443c7b544d571e2a3b5` (2026-08-02T17:01:29+02:00, "audit(p1): verify protocol and regenerate canonical tables and figures")
**Working tree:** dirty — a very large number of staged additions under `.venv/` (a committed Python virtualenv). This is unrelated to the experimental evidence and was not touched by this audit. No commits, branches, or pushes were made by this audit.
**Audit date:** 2026-08-05
**Audit method:** direct, independent recomputation from tracked primary artefacts (SHA-256 hashing, pandas recomputation of skill/H\*/bootstrap statistics from raw prediction and resample files), cross-read of pre-existing forensic documentation already committed in this repo (`docs/audit/`, `results/e2_met_ireland_pm10/run_metadata.json`, `results/e2_met_madrid_pm10/bundle_provenance.md`, `results/e2_met_ireland_pm10_regenerated/output_manifest_classified.md`). No experiment was rerun, no figure was regenerated, no manuscript file was edited, no COVID sensitivity (E5) was executed, no Ridge model was added.

---

## Pre-existing audit material: a caveat

Before presenting new findings, note that `audit_ijer_experimental_evidence/experimental_evidence_audit.md` (committed earlier in this same directory) is a **hollow template** — every specific value (repo path, branch, commit, script names, classifications) is blank. It reads as a finished, "all-clear" audit but contains no verifiable content. It should not be cited as evidence of anything and is flagged here so it is not mistaken for a completed check. By contrast, `audit_ijer_experimental_evidence/claim_evidence_matrix.csv` and `experiment_inventory.csv` in the same directory are populated and were used as a starting map for this audit; their claims were independently re-verified below rather than trusted at face value.

Separately, this repository already contains a substantial, honest internal forensic trail — `results/e2_met_ireland_pm10/run_metadata.json`, `results/e2_met_madrid_pm10/bundle_provenance.md`, `results/e2_met_ireland_pm10_regenerated/output_manifest_classified.md`, and `docs/audit/P3_PROJECT_CANON.md` (status: **HOLD AND REPAIR**) — written by a prior session that explicitly documents gaps rather than concealing them. This audit independently re-verified the numeric claims in that material rather than assuming they were correct.

---

## Task 1 — Madrid primary evidence

All seven headline Madrid numbers were **independently recomputed by this audit** from tracked primary files (not merely read from a summary table):

| Claim | Manuscript value | Independently recomputed | Match |
|---|---|---|---|
| N origins (full year 2023) | 362 | `nunique(origin)` in `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv` = 362 | ✅ |
| H\*_strict, lags-only | 9 | max positive-skill run (h=3..11) recomputed from raw `skill_rmse_vs_persistence` in `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv` | ✅ |
| H\*_strict, lags+meteo | 17 | max positive-skill run (h=1..17), same file | ✅ |
| ΔH\* | +8 | 17−9 | ✅ |
| Bootstrap median ΔH\* | +3.0 | `median()` of the 2000 Madrid rows in `results/ijer/e3_hstar_uncertainty/hstar_bootstrap_all_resamples.parquet` (block_len=7) | ✅ |
| 95% CI | [-8, +12] | 2.5/97.5 percentiles of the same 2000 resamples | ✅ |
| P(ΔH\*>0) | 0.7445 | mean(delta_h_strict>0) over the same 2000 resamples | ✅ |

Full detail, hashes, and per-claim provenance are in `madrid_primary_evidence.csv`.

**What backs this:** `predictions_all_models.csv` (34,752 rows, origin-level y_true/y_pred) → `metrics_all_models.csv` (per-horizon skill) → `canonical_hstar_results.csv` / `canonical_common_window_results.csv` (H\*, ΔH\*) is a coherent, hash-verifiable chain. The bootstrap chain is separately verifiable: `experiment_manifest.json` for E3 documents seed=20260802, B=2000, block_len=7 days, and the raw 2000×9-station resample table (`hstar_bootstrap_all_resamples.parquet`) reproduces the manuscript's median/CI/P exactly when filtered to Madrid.

**What is missing / contradicted (metadata-output contradiction):**
- `data_processed/madrid_pm10_meteorology_experiment_base.csv` — the exact input dataset named in `code/e2_met_madrid_config.json` — is **absent** from this clone (`data_processed/` contains only `.gitkeep`). The config's `dataset_path` and `results_dir` (in `config_snapshot.json`) resolve to `/Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar/...`, a different machine's home directory. The pipeline is therefore **not re-executable end-to-end** from this clone, only re-verifiable from its tracked outputs onward.
- `results/e2_met_madrid_pm10/run_metadata.json` records **only** the first `lags_only` sub-run (`conditions_run: ["lags_only"]`, 26,064 prediction rows, 0 DM rows). The tracked bundle actually contains `lags_only` + `lags_meteo` + `persistence` + `sarima` (34,752 rows, 96 metric rows, DM available). This is a genuine metadata/output mismatch — but it is **already disclosed** in `results/e2_met_madrid_pm10/bundle_provenance.md`, which explains the bundle was assembled additively across two commits and that the historical metadata describes only the first of those commits.
- No SHA-256 hash manifest exists for the Madrid bundle (unlike Ireland's `output_hashes.csv`). This audit computed hashes for the key Madrid files itself; they are recorded in `madrid_primary_evidence.csv` for future reuse.

**Classification: `PRIMARY_EVIDENCE_PRESENT_REPRODUCTION_FAILED`.**
Justification: origin-level predictions and the raw 2000-resample bootstrap table are genuine primary evidence, not just derived summary tables, and every headline number was independently reproduced from them by this audit. But end-to-end reproduction from the original raw input dataset is impossible in this clone (dataset absent, path points to another machine), and the run's own metadata is incomplete/contradicts the final tracked bundle (honestly flagged, but still a defect). This falls short of `PRIMARY_EVIDENCE_CERTIFIED` (which would require a clean, hash-verified, re-executable chain with accurate metadata) but is well above `OUTPUTS_ONLY_NO_PRIMARY_EVIDENCE`.

---

## Task 2 — Temporal protocol

Verified directly in `code/rolling_origin.py` (`get_train_window`) and `code/e2_met_madrid_shared.py` (`predict_sarima`):

1. **XGBoost real protocol:** strictly **expanding window**, `train_start ≤ t < origin`, uncapped. `code/rolling_origin.py:get_train_window()` docstring: *"Return the expanding training window up to origin minus one step."* Verified numerically in `protocol_by_model_and_origin.csv`: for Madrid (`train_start=2019-01-01`), the origin `2023-01-01` already trains on 35,064 hourly rows (≈4 years, 2019–2022); by origin `2023-12-30` this has grown to 43,776 rows (≈5 years, 2019 through most of 2023). XGBoost is **never** restricted to 2020–2022, and the training set is **not** the same size at every origin.

2. **What "training 2020–2022" means in the manuscript:** it is the caption of Table 1 (descriptive statistics: mean/SD/ρ₁ of the raw PM10 series), not a statement about the model's per-origin training window. The manuscript's own Methods section (§"Backtesting protocol", line 157) states the correct mechanics accurately: *"We adopt a rolling-origin, expanding-window backtesting scheme. For each forecast origin t, the training window covers observations up to t−1."* So there is no outright contradiction between the Methods text and the code — but Table 1's blanket "Training: 2020–2022" label, read in isolation, is easy to misread as describing the model training window, and it does not disclose that Madrid's `train_start` is actually 2019-01-01 (one year earlier than the label implies) or that XGBoost's window keeps expanding through all of 2023.

3. **SARIMA real protocol:** takes the *same* expanding `train_df` as XGBoost, then **caps** it to the most recent `sarima_max_train_rows=17520` (~2 calendar years) via `.iloc[-17520:]`. Code comment: *"Cap training window to avoid Kalman-filter memory crash on long series."* This means SARIMA's effective training window **slides forward** with each origin — it is the most recent 2 years ending at t−1, not a fixed 2020–2022 window either. For the very first 2023 origins this window happens to approximate 2021–2022; by December 2023 origins it has slid to roughly 2022–2023.

4. **Are the differences justified?** Yes, and they are disclosed in the manuscript's Model Specifications section, which states SARIMA uses "the most recent 17,520 training observations (2 calendar years)" — this exact figure and rationale (Kalman-filter tractability) match the code. The XGBoost vs. SARIMA window-size asymmetry is a defensible, disclosed practical necessity (SARIMA state-space fitting does not scale to multi-year hourly series the way XGBoost does), not a hidden inconsistency. It does not affect the primary Madrid meteo-vs-lags-only comparison, since both `lags_only` and `lags_meteo` XGBoost conditions always share the identical (expanding) training window at every origin.

5. **Does the text match the execution?** The Methods section (backtesting protocol + SARIMA paragraph) is accurate. Table 1's "Training: 2020–2022" caption is a **different, narrower usage** (the window over which descriptive statistics were computed) that is not clearly disambiguated from the model-training-window concept described elsewhere, and does not mention that Madrid's actual `train_start=2019-01-01` precedes it.

**Classification: `PROTOCOL_DIFFERENT_BUT_JUSTIFIED`.**
The XGBoost/SARIMA window difference is real, disclosed, and methodologically justified. The "2020–2022" table caption vs. expanding-window mechanics is a documentation-clarity gap, not a computational defect — the code faithfully implements the protocol the Methods section describes.

### A second, independent protocol discrepancy found in Task 2/3

The manuscript's Model Specifications section states: *"nine concurrent meteorological covariates measured at forecast origin t are added"* — worded generically, as if it applies to both sites. It matches Ireland's config (`code/e2_met_ireland_config.json`: `rain, temp, wetb, dewpt, vappr, rhum, msl, wdsp, wddir` — 9 features) but **not** Madrid's (`code/e2_met_madrid_config.json`: `temp_c, humidity_pct, pressure_hpa, wind_speed_ms, wind_dir_deg, solar_rad_wm2, precip_mm` — **7** features). Madrid is the site carrying the paper's headline ΔH\*=+8 finding, and its actual predictor set differs both in name and count from what the Methods section states. See `meteorological_feature_delivery.csv`.

---

## Task 3 — Meteorological features, incl. Portlaoise h=24

Per-station × horizon checks (`identical_prediction_checks.csv`, xgboost_direct, lags_only vs lags_meteo, all computed directly from `predictions_all_models.csv` for Madrid and the regenerated `predictions_all_models.csv` for Ireland — see caveat below):

- **No station × horizon combination has identical predictions between `lags_only` and `lags_meteo`.** `max_abs_pred_diff` is strictly positive everywhere it is computable (e.g. Portlaoise h=24: 13.37; Madrid h=24: 54.55; Pearse Street h=24: 62.27). This is strong indirect evidence that meteorological features **were** delivered to the model and were **not** constant — an undelivered or constant feature would leave XGBoost's tree splits, and therefore its predictions, numerically unchanged.
- **Portlaoise h=24 specifically:** `canonical_dm_multiple_testing.csv` records `dm_stat`, `dm_hln_stat`, and all p-values as blank/NaN, with `favours=undetermined`, for exactly this one station×horizon (the only NaN row among all 36). This is the "zero variance" pattern referenced in the audit brief. Root-caused directly in `code/e2_met_madrid_shared.py:diebold_mariano_test()` (lines ~575–590): the DM long-run variance estimator is an **unweighted** (rectangular-kernel) Newey–West-style sum, `gamma0 + 2·Σ(cov_lag for lag in 1..horizon-1)`, with no Bartlett/triangular tapering. This estimator is not guaranteed positive-semi-definite; at `max_lag_hac=23` with `n=212`, it evaluated to ≤0 for Portlaoise h=24 only, triggering the function's own `"undetermined"` fallback branch (`if not np.isfinite(long_run_var) or long_run_var <= 0`).
- Cross-checked against the actual predictions: Portlaoise h=24 predictions differ substantially between conditions (`max_abs_pred_diff=13.37`), and the *raw* (unweighted-kernel-free) loss-differential variance is `3208.76` — clearly non-zero. So the "zero" is a property of the **DM test's HAC variance estimator at high horizon/low n**, not of the underlying predictions or features.

**Diagnosis for Portlaoise h=24:** none of the six offered categories is a literal fit. `IDENTICAL_PREDICTIONS_BY_MODEL_BEHAVIOUR` is ruled out (predictions clearly differ). `METEOROLOGICAL_FEATURES_NOT_DELIVERED` / `..._CONSTANT_OR_MISSING` are ruled out by the same evidence, and by every other horizon at Portlaoise showing valid, well-behaved DM statistics. `SUPPORT_ALIGNMENT_ERROR` is ruled out — `n_common=212` for lags_only and lags_meteo at h=24 matches every other horizon at that station exactly. `DUPLICATE_OR_REUSED_OUTPUT` is ruled out by the large, non-repeating loss variance. The verified root cause is a **numerical artefact of the DM-HLN long-run variance estimator** (non-PSD rectangular-kernel HAC at `max_lag=23`, `n=212`) — a real, verified, but narrowly-scoped statistical-computation issue, closest in spirit to `UNKNOWN_NOT_VERIFIABLE` only in the sense that the DM significance itself is undetermined, but the *cause* of that indeterminacy has in fact been verified here, not left unknown.

**Feature delivery, more generally:** the raw processed datasets (Madrid: `data_processed/madrid_pm10_meteorology_experiment_base.csv`; Ireland: the 187,857×17 processed panel) are not present in this clone, so column-level non-constancy and missingness cannot be inspected directly from raw data, and no design-matrix hashes exist (feature matrices are built on the fly per origin and never persisted). The indirect evidence above (systematic, non-trivial prediction divergence at every station×horizon) is the best available substitute and is consistent across all 9 sites. See `meteorological_feature_delivery.csv` for the imputation logic (train-only median fill, `code/e2_met_madrid_shared.py:fit_train_feature_medians/apply_feature_medians`) and the Madrid-vs-Ireland feature-count mismatch noted in Task 2.

---

## Task 4 — Common support by station × horizon

Computed directly from prediction origin sets (`common_support_by_station_horizon.csv`). Headline: within each station, `lags_only` and `lags_meteo` origin sets are **perfectly aligned at every horizon** (`n_origins_common = n_origins_lags_only = n_origins_lags_meteo`, coverage 100%, `exclusion_reason=none`) — i.e., every DM-HLN and H\* comparison genuinely uses paired losses over identical cases, confirming the "identical origins/valid target pairs" contract in `docs/audit/P3_PROJECT_CANON.md` §5.

Cross-station support varies substantially, driven by real raw-data availability, not by a pipeline defect:

| Station | n (constant across h) | First date | Last date |
|---|---:|---|---|
| Madrid Casa de Campo | 362 | 2023-01-01 | 2023-12-30 |
| Birr, Pearse St., Ringsend, Portlaoise | 212 | 2023-01-01 | 2023-07-31 |
| Edenderry | 211 | 2023-01-01 | 2023-07-31 |
| Henry Street Limerick | 211 | 2023-01-01 | 2023-07-31 |
| **Dundalk** | **154** | 2023-01-01 | **2023-06-03** |
| **Dublin Airport** | **145** | 2023-01-01 | **2023-05-25** |

**Dublin Airport and Dundalk** have materially shorter evaluation windows than the other 7 sites (145 and 154 origins vs. ~211–212), ending in late May / early June 2023 rather than end of July. This traces to real gaps in the raw source files (`source_csv_manifest.csv`: Dublin Airport period ends 2023-05-26; consistent with the truncated evaluation window). It is disclosed in the manuscript abstract ("145 to 212 origins") but not broken out per-station in the main text — a minor completeness gap, not a fabrication risk, since Dublin Airport's own DM-HLN and H\* results (both independently re-verifiable in `canonical_dm_multiple_testing.csv` / `canonical_hstar_results.csv`) are internally computed over its own true n=145 support throughout.

**Portlaoise** has full, unbroken support (212 origins, all 24 horizons) — its h=24 DM-HLN indeterminacy (Task 3) is unrelated to support/coverage.

**Caveat on the Ireland evidence base used for Tasks 3–4:** per `docs/audit/P3_PROJECT_CANON.md` §7 and `results/e2_met_ireland_pm10/run_metadata.json`, the original Ireland execution's `run_metadata.json` does not exist anywhere in this repository's history, and the original per-run outputs were never committed (`code/e2_met_ireland_config.json` hardcodes a dataset path on the original author's machine). The Ireland numbers checked in this audit come from `results/e2_met_ireland_pm10_regenerated/`, explicitly labelled `"REGENERATED FROM RECOVERED SOURCE DATA — NOT the recovered original execution"`. This audit independently confirmed that regenerated bundle's own internal hash manifest (`predictions_all_models.csv` SHA-256 matches `output_hashes.csv`) and that its DM-HLN directional counts (24 favour lags_meteo / 7 favour lags_only / 1 undetermined, Ireland-only) match `docs/audit/P3_PROJECT_CANON.md` exactly — but this is regenerated evidence, not the original run.

---

## Task 5 — Figures

`figure_traceability.csv` covers all figures found in the repo. Summary:

- The **4 figures actually `\includegraphics`-referenced** in `manuscripts/manuscript_main.tex` (`figures/ijer/figure_1..4`) were all produced in the same regeneration batch as the canonical CSVs they draw from (2026-08-04, same session as `results/ijer/canonical/*`), and trace cleanly: Figure 1 → `results/ijer/e1_common_window/madrid_*_skill_by_horizon.csv`; Figures 2–4 → `results/ijer/canonical/canonical_hstar_uncertainty.csv` and `canonical_dm_multiple_testing.csv` via `code/regenerate_ijer_figures_and_tables_codex.py`. **Current.**
- **6 additional figures** exist under `manuscripts/figures/` (`madrid_figure_*`, `ireland_figure_hstar_summary`, `figure_rho1_vs_delta_hstar`) with older timestamps (2026-08-01/02, i.e. **before** the 2026-08-04 canonical regeneration) and are **not referenced anywhere** in `manuscript_main.tex`'s `\includegraphics` calls. They are orphaned leftovers from an earlier pipeline iteration — harmless as long as they stay unused, but stale relative to the current canonical numbers and should not be reused without regeneration.
- **rho1 figure:** no rho1 figure is included in the compiled manuscript; ρ₁ is reported as text/table only (n=9, r=0.555, p=0.121, `docs/audit/P3_PROJECT_CANON.md` §10). `figure_rho1_vs_delta_hstar.pdf` exists but is orphaned (see above) — no risk to the compiled document, but its content was not independently re-verified since it is unused.
- **Henry Street H\*:** current canonical value is `H*_strict(lags_only)=17`, `H*_strict(lags_meteo)=24`, `ΔH*=+7` (`canonical_hstar_results.csv`); the manuscript text at lines 235–306 uses `+7` throughout, matching. `docs/audit/P3_PROJECT_CANON.md` §8 documents that an earlier value (`18h`/`+6`) was superseded — the manuscript already reflects the corrected value, not the stale one.
- **Madrid values in figures:** Figure 1 draws on the same `madrid_full_year_skill_by_horizon.csv` / `madrid_jan_jul_skill_by_horizon.csv` this audit independently reproduced from raw metrics (Task 1) — consistent.
- **Censored stations:** the 5 ceiling-censored Irish stations (Birr, Dundalk, Pearse St., Ringsend, Portlaoise, all `lags_only H*=24`) shown in Figure 4 match `canonical_hstar_results.csv` exactly (`is_ceiling_censored=True` for all 5, `False` for the other 4 sites).

---

## Summary table

| Task | Classification |
|---|---|
| 1. Madrid primary evidence | `PRIMARY_EVIDENCE_PRESENT_REPRODUCTION_FAILED` |
| 2. Temporal protocol | `PROTOCOL_DIFFERENT_BUT_JUSTIFIED` (SARIMA/XGBoost window asymmetry disclosed and justified; Table 1 "2020–2022" caption is a documentation-clarity gap, not a code defect) |
| 3. Meteorological features / Portlaoise h=24 | Root cause verified: DM-HLN long-run variance estimator numerical failure at high horizon/low n — not a data-pipeline defect. No station×horizon shows literally identical predictions. |
| 4. Common support | Within-station alignment perfect (100% paired); cross-station coverage genuinely uneven (Dublin Airport 145, Dundalk 154 vs. ~211–212 elsewhere), traced to real raw-data gaps. |
| 5. Figures | 4 referenced figures are current and traceable; 6 unreferenced figures are stale/orphaned but harmless. |

See `blocking_issues.md` for the consolidated list of items that block or do not block submission, and the final verdict.
