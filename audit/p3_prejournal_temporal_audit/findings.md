# VERDICT

MATERIAL_PIPELINE_BLOCKER

# VERIFIED FACTS

- The Madrid prediction artifact contains 362 origins from 2023-01-01 through 2023-12-30, not a January--July evaluation window. Its complete DM pairs are 354, 356, 346, and 354 at h=1,6,12,24.
- For every audited station and horizon, lags-only and lags+meteorology have identical origin sets before complete-pair filtering.
- `n` in the DM table is the count of complete paired loss observations after matching by origin and verification timestamp; it is not an hourly-observation count.
- Training rows are restricted to timestamps strictly earlier than the forecast origin (`code/rolling_origin.py:68-84`). Direct targets are shifted only within that training frame (`code/models/xgboost_model.py:97-125`), so no future target at or after the origin enters model fitting.
- At the traced Madrid origin 2023-01-01 00:00, persistence and XGBoost lag 1 both use the latest available PM10 at 2022-12-31 23:00; XGBoost meteorology and calendar features are timestamped at the origin, and the h=1 target is 2023-01-01 01:00.
- The pipeline generates origins and forecast horizons by row position, then takes every 24th row (`code/rolling_origin.py:36-65,87-107`; `code/e2_met_madrid_shared.py:297-304,346-379`), rather than enforcing timestamp differences of exactly 24 and h hours.
- The artifact contains 241 unique station--origin--horizon cases with mislabeled clock leads: Madrid 1 case/1 origin, Edenderry 148 cases/12 origins, and Henry Street 92 cases/7 origins. Madrid origin 2023-11-22 h=24 verifies at 2023-11-25 00:00, an actual 72-hour lead. Edenderry includes an h=1 target only one minute after its origin and h=24 leads up to 63 hours.
- PM10 lags are formed with `.shift(lag)` after sorting and forward-filling, so they denote previous rows, not guaranteed previous clock hours when timestamps are missing or minute-offset (`code/e2_met_madrid_shared.py:57-62`).
- Pearse Street has a complete timestamp grid over its available source window. Edenderry and Henry Street have respectively 61 and 66 missing hourly timestamps; their prediction artifacts also contain minute-offset timestamps.

# DISCREPANCIES

1. **Evaluation period.** Manuscript: evaluation is 2023-01-01--2023-07-31 (`manuscripts/manuscript_main.tex:253-254`). Artifact: Madrid origins extend to 2023-12-30 (`results/predictions_all_models.csv`; `origin_count_audit.csv`). Impact: the reported Madrid DM sample sizes and associated results describe a substantially longer window than declared. Classification: `DOCUMENTATION_ERROR`, with deterministic reconciliation required before submission.
2. **Forecast-origin stride.** Manuscript: forecast origin advances exactly 24 h (`manuscripts/manuscript_main.tex:248-251`). Pipeline: it selects every 24th existing row (`code/e2_met_madrid_shared.py:297-304`). Observed origin gaps include 72 h in Madrid and 21--63 h in Edenderry/Henry. Impact: daily-origin dependence and evaluation timing are not uniformly what the manuscript states. Classification: `PIPELINE_ERROR`.
3. **Meaning of horizon h.** Manuscript: h=1,...,24 are lead hours. Pipeline: `get_test_window` slices future rows and scores `test_df.iloc[horizon]` (`code/rolling_origin.py:87-107`; `code/e2_met_madrid_shared.py:346-379`). Impact: some nominal horizons correspond to leads from one minute to 72 hours, contaminating horizon-specific RMSE, Skill, H*, and DM for affected rows. Classification: `PIPELINE_ERROR`.
4. **Persistence notation.** Manuscript: persistence is yhat_(t+h)=y_t while training excludes t (`manuscripts/manuscript_main.tex:248-263`). Pipeline: persistence uses the last nonmissing target strictly before origin (`code/e2_met_madrid_shared.py:205-212`), the same newest PM10 represented by XGBoost lag 1. Impact: no unfair information set was found, but the formula is a `NOTATION_ERROR`.
5. **Coverage description.** Manuscript describes approximately 210--365 origins per station (`manuscripts/manuscript_main.tex:253-255`). Artifacts contain only 145 for Dublin Airport and 154 for Dundalk because their source files terminate on 2023-05-26 and 2023-06-04. Impact: station-specific evaluation windows and effective sample sizes require explicit disclosure. Classification: `DOCUMENTATION_ERROR`.

# LEAKAGE ASSESSMENT

- **verified safe:** training data satisfy timestamp < origin; direct targets remain inside the pre-origin training frame; representative Madrid and Pearse cutoffs are temporally ordered; lags-only and lags+meteorology are paired on identical origin/verification support.
- **potential issue:** forecast-origin meteorological values are concurrent observations. Their operational availability is not established by persisted feature-delivery metadata, although the manuscript acknowledges they are not NWP forecasts.
- **actual leakage:** none demonstrated in the audited code or artifacts.
- **unverifiable:** the processed Madrid and Ireland design matrices are not tracked, so exact feature values and per-origin feature timestamps cannot be reconstructed for every run; the original Ireland execution is represented by a regenerated artifact bundle.

# MINIMAL CORRECTIONS REQUIRED

- **A. manuscript only:** correct the Madrid evaluation-period description, persistence notation, and station-specific origin coverage. These edits are necessary but not sufficient.
- **B. deterministic tables:** regenerate origin-count, metrics, H*, DM tables, and dependent figures after the temporal-grid correction; do not reconcile the current row-based results by prose alone.
- **C. pipeline:** regularize each station to an hourly clock grid or construct lags, origins, targets, and verification timestamps by explicit timestamp joins; require `verification_time = origin + h hours` and a true 24-hour origin stride before refitting.
- **D. no change required:** retain the canonical H* definitions; retain strict pre-origin target cutoff; retain common paired support between the two XGBoost conditions.
