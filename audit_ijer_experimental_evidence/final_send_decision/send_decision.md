# Canonical manuscript

- **File Path:** `manuscripts/manuscript_main.tex` (reproduced stand-alone in `manuscript_ijer_package/manuscript_main.tex`)
- **Journal Target:** International Journal of Environmental Research (IJER, Springer Nature)
- **Title:** "When does meteorology extend useful PM10 forecast skill? A multi-site rolling-origin evaluation against persistence"
- **Authors:** Federico García Crespí (Universidad Miguel Hernández de Elche, Spain)

# Repository state

- **Ruta del Repositorio:** `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland`
- **Rama Actual:** `codex/p1-editorial-computational-audit`
- **HEAD Commit:** `18d0f830b1b7bf92684d5443c7b544d571e2a3b5`
- **Working Tree State:** Cleaned of TODO comments, synchronized table citations, cover letter updated to target IJER. standalone zip package assembled.

# Origin count resolution

**`ORIGIN_COUNTS_RESOLVED`**

- **Madrid (Full Year 2023):** Assembles **362 unique origins** (daily stride, 365 days of 2023 minus 3 days of missing data). Paired evaluations with valid targets count is **354** (at h=1) because of 8 missing PM10 target observations in the test window.
- **Ireland (Jan-Jul 2023 Common Window):** Assembles **212 candidate origins** (daily stride, 212 days). Unique origin counts per station in predictions vary between **145 and 212** due to missing EPA station PM10 targets or missing local meteorological covariates (e.g. Dublin Airport: 145 origins, Dundalk: 154 origins, Birr: 212 origins).
- **Explanation:** The numbers "3000" and "1500" mentioned in earlier reviews are incorrect for rolling origins. They were likely confusions with sample sizes or configuration limits. The actual rolling origin backtest counts are 362 (Madrid) and 145--212 (Ireland), as verified directly from the source prediction CSV files.

# Absolute metrics

**`ABSOLUTE_METRICS_READY`**

- Absolute MAE and RMSE error metrics are fully calculated and exist in the canonical results:
  - Madrid: `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`
  - Ireland: `results/e2_met_ireland_pm10_regenerated/manuscript_tables/table_metrics_long.csv`
- All models (`xgboost_direct` lags_only and lags_meteo) and baselines (`persistence`, `sarima`) are evaluated on identical test origin-horizon pairs (perfect support equality).
- Reconstructed skill scores from absolute errors match reported percentages with double-precision accuracy (max difference ~3e-16).
- An absolute metrics summary has been exported as `absolute_metrics_final.csv`. It is recommended to include this as a supplementary table prior to journal proofing.

# Meteorological timing

**`METEOROLOGY_WORDING_VALID`**

- Meteorological predictors in the features matrix are observed variables measured exactly at forecast origin $t$ (`temp_c`, `humidity_pct`, `wind_speed_ms`, `pressure_hpa`).
- No future weather observations ($t+h, h \ge 1$) are used.
- Operationally, because publication latency was unverified, these predictors are correctly classified as Class D retrospective observations.
- The manuscript correctly frames these inputs as a "retrospective upper bound" rather than real-time operational NWP integration.

# E5 status

**`C_MISSING_NON_BLOCKING`**

- Experiment E5 (sensitivity to multi-year post-COVID training window) was not executed because pre-2023 raw features are not present locally.
- The manuscript draws no empirical conclusions from E5 and correctly frames this as a study limitation in Section 5.3 and the Code Availability statement. It does not block submission.

# Claim-evidence status

- All 9 quantitative claims (C1 to C9) are fully **`SUPPORTED`** by canonical data files, generating python scripts, and are correctly transcribed in the manuscript text and tables.
- No discrepancies remain.

# Package completeness

- **Manuscript:** `manuscript_main.tex` is complete, cleaned of internal TODOs, and synchronizes the citation of Table 1 (`tab:study_design`).
- **Tables:** All 6 tables (`table_1` to `table_5` and `table_s1`) are exported in LaTeX `.tex` format.
- **Figures:** All 4 figures (`figure_1` to `figure_4`) are exported in high-quality PDF format.
- **Class File:** `sn-jnl.cls` is present.
- **References:** `references.bib` database is complete.
- **Cover Letter:** `cover_letter.tex` is updated with the correct target journal (IJER) and relevance statements.
- **ZIP File:** `manuscript_ijer_package.zip` built successfully.

# Blocking issues

- None.

# Non-blocking limitations

- Pre-2023 meteorological features are unavailable locally, preventing the E5 sensitivity check. This is acknowledged in the text.
- Real-time API latency is unverified, so meteorological inputs at origin $t$ are framed as a retrospective upper bound. This is acknowledged in the text.

# Final decision

**`SEND_TO_IJER`**

The manuscript, tables, figures, and cover letter have been audited, updated, and packaged. There are no remaining blocking issues, and all quantitative claims are fully supported by empirical data. The package is ready for immediate submission.
