# P1 — Overleaf Handoff Report

Computational audit of the "Does meteorology extend the useful forecast
horizon for urban PM10?" (H\*) manuscript. Read-only w.r.t. `.tex`/`.bib`;
manuscript editing happens in Overleaf, not here.

## 1. Veredicto computacional

**VERIFIED_WITH_DOCUMENTATION_ERRORS.**

The manuscript's central, headline claim — meteorology extends
$H^*_{strict}$ by +8h at Madrid and +1.0h (mean) across eight Irish
stations, via XGBoost lags-only vs. lags+meteorology — is **exactly
reproducible** from the row-level predictions already committed to this
repository, using the repository's own unmodified functions. This was
verified independently for Madrid and for two Irish stations (Henry St.
Limerick, Dublin Airport), matching every reported number to full
precision (H\*, RMSE skill, DM-HLN statistics and p-values).

Two real defects were found and are detailed below: a documentation error
(Madrid's stated evaluation window doesn't match the data actually used)
and a code bug affecting SARIMA's reported numbers specifically (not the
primary XGBoost comparison). Additionally, a moving-block bootstrap shows
the headline +8h point estimate has enormous resampling uncertainty that
the manuscript does not currently disclose — this is the single most
important thing for the next revision to address.

Not blocking publication as-is, but three changes are strongly
recommended before further submission (see §8-13).

## 2. HEAD SHA canónico

`5596c1c87f8c466813a87f1305a2bbf377d7a98a` on branch
`codex/p3-hstar-strict-manuscript-repair`
(remote: `https://github.com/fedeg-umh-es/P1_PM10_Meteorology_Hstar.git`).

This audit's own changes are committed separately on a new branch,
`codex/p1-editorial-computational-audit`, branched from the above (see §16
and the closing commit section of this repo's audit).

Note on repo identity: the expected path
`$WORKSPACE_ROOT/P1_PM10_Meteorology_Hstar` does not exist locally; this
repository lives at `P3_Madrid_Ireland/` in the same workspace, but its
`origin` remote is the exact, unambiguous match for P1. This is a local
folder-naming quirk, not a repository-identity issue.

## 3. Archivos fuente canónicos

- `code/e2_met_madrid_shared.py` — single shared implementation of feature
  construction, model fitting/prediction, skill, H\*, and DM-HLN, imported
  by both `e2_met_madrid_run.py` and `e2_met_ireland_run.py`.
- `code/rolling_origin.py`, `code/features.py` — origin generation and
  lag/calendar feature construction (also used by the shared module).
- `code/models/xgboost_model.py` — direct multi-horizon XGBoost wrapper
  and target construction (`make_direct_targets`).
- `code/e2_met_madrid_config.json`, `code/e2_met_ireland_config.json` —
  experiment configs (see §6 for a real discrepancy between them).
- `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv` —
  Madrid row-level predictions (362 origins × 24 horizons × 4
  model/condition combinations).
- `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv`
  — Ireland row-level predictions, **regenerated** (not the original run;
  see §9 of the audit / `results/e2_met_ireland_pm10_regenerated/README.md`
  for the full, pre-existing provenance chain, which this audit reviewed
  and confirms is accurate).

**Raw and processed input data (`data_raw/`, `data_processed/`) are
gitignored and are empty on this machine** — only `.gitkeep` placeholders
exist. This blocked full end-to-end re-execution of the pipeline (see §15).
All verification in this report was done against the already-computed,
already-committed row-level predictions, which is sufficient to confirm
manuscript-vs-code consistency but not to redo the missing-data or
training-period audits from raw data.

## 4. Tablas regeneradas

CSV + Markdown (no LaTeX), in `audit_p1_tmp/tables_out/`, each with a
producer script, source file, source/output SHA-256, timestamp, and HEAD
SHA recorded in its `.md` file and in `audit_p1_tmp/tables_out/table_manifest.json`:

- `table_3_madrid_dm.csv` / `.md` — Madrid DM-HLN, recomputed from raw
  predictions; matches manuscript Table 3 exactly, now with a Bonferroni-
  adjusted p-value column that the current pipeline doesn't compute.
- `table_4_ireland_hstar.csv` / `.md` — Ireland H\* by station, matches
  manuscript Table 4 exactly, now with a **computed** ceiling flag
  (`compute_ceiling_flag`, added this audit) instead of a hand-typed
  "Yes/No" column — correctly labels Edenderry `"No (submaximal tie)"`.
- `table_5_ireland_dm.csv` / `.md` — Ireland DM-HLN, all stations, matches
  manuscript Table 5 exactly.
- `table_6_rho1_hstar.csv` / `.md` — extends Table 4 with an
  evaluation-period (2023) $\rho_1$, reconstructed from saved predictions.
  **This is not the training-period (2020-2022) $\rho_1$ the manuscript
  reports** — that period's raw data is unavailable locally (see §15).

**Not regenerated:** Table 1 (descriptive statistics) and Table 2
(XGBoost hyperparameters, which is static config, not data-derived) — both
need raw/processed data this machine doesn't have.

## 5. Figuras regeneradas

None in this pass (Phase 12 not completed — see §15). Two figures
(Ireland Fig. 6 "meteorology benefit per station" and Fig. 8 "H\* summary")
were already regenerated and fixed for a legend-overlap rendering bug in a
**prior** session (commit `5596c1c`, unrelated to this computational
audit) — that fix stands and required no changes here.

A new bootstrap-uncertainty output was produced instead of a figure:
`audit_p1_tmp/skill_bootstrap_intervals_madrid.csv` (95% CI band per
horizon for both XGBoost conditions) and
`audit_p1_tmp/hstar_bootstrap_summary_madrid.csv` /
`hstar_bootstrap_summary_henry_st.csv` — see §7 for why this matters more
than another figure would.

## 6. Cifras antiguas incorrectas

1. **Methods §3.1** states: *"The evaluation period is 1 January 2023 – 31
   July 2023 (31 weeks...)"*. This is **wrong for Madrid**.
   `code/e2_met_madrid_config.json` has `"test_end": "2023-12-31 23:00:00"`,
   and Madrid's saved predictions confirm 362 origins running from
   2023-01-01 through 2023-12-30 — essentially the full calendar year, not
   31 weeks. Ireland's config (`test_end: "2023-08-01"`) does match the
   stated window. The two sites silently used different evaluation
   windows; the text describes only one.
2. SARIMA's reported $H^*_{strict}$/$H^*_{relax}$/RMSE values throughout
   (Table 4, Table 6, Figures 1/4/5, and the SARIMA paragraph in §5.1) were
   computed by comparing each forecast against the wrong target timestamp
   — see §7 for the mechanism. The manuscript accurately reports what the
   code produced (no manuscript-vs-code mismatch), but what the code
   produced does not measure what the label says.

## 7. Cifras nuevas verificadas

- Madrid, Henry St. Limerick, Dublin Airport H\*/DM: **exact** reproduction
  from raw predictions (see the audit's Phase 5/6 output; not repeated
  here to avoid duplicating tables already in §4).
- **New: bootstrap 95% CI for Madrid, block-bootstrap over origins
  (block=7 days, n=2000 resamples, seed=20260802):**

  | Quantity | Point estimate (manuscript) | Bootstrap median | 95% CI |
  |---|---:|---:|---:|
  | $H^*_{strict}$ lags only | 9 | 11 | [7, 24] |
  | $H^*_{strict}$ lags+met | 17 | 15 | [8, 24] |
  | $\Delta H^*_{strict}$ | **+8** | 3 | **[-8, +12]** |
  | P(Δ>0) | — | — | 74.5% |

  The headline "+8h" sits inside a 95% interval that **includes zero and
  negative values**. This is a direct, quantified confirmation that
  $H^*_{strict,max\text{-}run}$ is a highly discrete statistic (a run
  length around $S(h)=0$ crossings) that is not robust to resampling —
  exactly the instability check Phase 7 of this audit was designed to
  surface. Henry St. Limerick's +7h (Ireland's other headline exception)
  shows the same pattern: bootstrap CI **[-10, +12]**, P(Δ>0)=69.5%.

  This does **not** mean the finding is false — the point estimate and
  its mechanism (autocorrelation-persistence regime) remain the best
  available reading of the data — but reporting "+8h" as a bare point
  estimate materially overstates its precision.

## 8. Cambios obligatorios en Methods

- Correct §3.1's evaluation-period sentence: either state that Madrid's
  window is Jan-Dec 2023 (full year) while Ireland's is Jan-Jul 2023, or
  re-run Madrid restricted to Jan-Jul 2023 for consistency with the
  stated design (a decision for the author, not this audit — flagged in
  §15 as needing your call, not a computational fix).
- Add one sentence to the $H^*$ definition subsection noting that
  $H^*_{strict,max\text{-}run}$ is evaluated under a moving-block
  bootstrap in the Results, given its demonstrated volatility (§7).

## 9. Cambios obligatorios en Results

- Report the bootstrap 95% CI alongside the point estimate for
  $\Delta H^*_{strict}$ at both Madrid and Henry St. Limerick (§7's table
  is ready to paste, in whatever units/format Overleaf needs).
- If Table 6 is edited again, use `table_4_ireland_hstar.csv`'s `ceiling`
  column as the source of truth for the Ceiling column — it is now
  computationally derived, not hand-typed.

## 10. Cambios obligatorios en Discussion

- §5.1's SARIMA paragraph reports numbers that need to be recomputed once
  the alignment fix (§7 of the audit, code change in
  `e2_met_madrid_shared.py::predict_sarima`) is re-run against real data
  — the direction of the change cannot be predicted without re-running
  (could make SARIMA look better or worse; the fix removes a systematic
  one-step-too-far comparison, it doesn't have a predictable sign on
  RMSE). Until re-run, the SARIMA discussion should carry a footnote that
  its figures are under revision.
- The $\Delta H^*$ vs. $\rho_1$ narrative (Figure 9, Table 6) should
  acknowledge the bootstrap instability from §7 — the "increases
  monotonically" language for the four unconstrained sites is a
  point-estimate reading of a metric now shown to have wide resampling
  uncertainty at exactly those sites.

## 11. Cambios obligatorios en Conclusions

- Finding #1 ("Meteorology can substantially extend $H^*$...") should be
  qualified with the bootstrap CI, not stated as a bare +8h/+1.0h pair.

## 12. Afirmaciones que deben eliminarse o debilitarse

- Any phrasing that treats +8h as a precise, stable number (rather than a
  point estimate with a wide, zero-including interval) should be
  softened. Interestingly, the manuscript's currently-uncommitted local
  edits (106 lines changed in `manuscript_main.tex`, made outside this
  audit — see the earlier composition-review turns in this session)
  **already move in exactly this direction** — softening "attributed to"
  to "associated with... pending external validation." That edit and
  this audit's bootstrap finding independently point the same way.

## 13. Limitaciones que deben añadirse

- $H^*_{strict,max\text{-}run}$ instability under moving-block bootstrap
  (§7) — the single most important addition.
- SARIMA's reported metrics are pending recomputation after the
  alignment fix (§6/§7 of the audit).
- Madrid's evaluation window differs from Ireland's (§6) in a way the
  current text doesn't disclose.
- $\rho_1$ for Table 6 in this handoff uses the **evaluation-period**
  series where the manuscript uses **training-period** — flagged, not
  silently substituted (§4).

## 14. Referencias bibliográficas que requieren corrección

None found. All 10 `references.bib` entries were previously verified
(prior session, composition review) to be cited in-text and match; this
computational audit did not touch citations and found nothing that would
require a new reference.

## 15. Cuestiones todavía bloqueadas

- `data_raw/` and `data_processed/` are gitignored and empty locally
  (only `.gitkeep`). **BLOCKED_BY_MISSING_ARTIFACTS** for: full missing-
  data/gap audit (Phase 4), training-period $\rho_1$ recomputation
  (Phase 8), and re-running the corrected SARIMA code against real data
  (needed to produce final, correct SARIMA numbers for Table 4/6 and
  Figures 1/4/5).
- Madrid figure regeneration (Phase 12) needs the same raw/processed data.
- `models/lstm_model.py` exists in `code/models/` but is never imported by
  any script that produced a reported result — unclear if it's dead code
  from an earlier iteration or an unreported experiment. Worth a one-line
  clarification either way.
- `code/e2_met_ireland_run.py` has its own **inline** duplicate of the
  H\*/skill logic (lines ~251-270) instead of calling the shared
  `derive_hstar_from_metrics`. It currently agrees with the shared
  implementation (verified via the exact-match checks in §7), but the
  duplication is a maintenance risk if the two drift apart later — worth
  consolidating.
- `manuscript_main.tex` had 106 uncommitted lines of concurrent editing
  from outside this session when this audit began; per your instruction
  this audit did not touch it, but whoever is editing it should see this
  report before finalizing, since §7's bootstrap numbers and §6's Madrid
  evaluation-window issue are new since that edit was made.

## 16. Lista exacta de archivos que Overleaf debe sustituir

**None of these are `.tex`/`.bib` — Overleaf editing translates the
findings above into manuscript prose; these are the data files an editor
would pull numbers/tables from:**

- `audit_p1_tmp/tables_out/table_3_madrid_dm.{csv,md}`
- `audit_p1_tmp/tables_out/table_4_ireland_hstar.{csv,md}`
- `audit_p1_tmp/tables_out/table_5_ireland_dm.{csv,md}`
- `audit_p1_tmp/tables_out/table_6_rho1_hstar.{csv,md}`
- `audit_p1_tmp/skill_bootstrap_intervals_madrid.csv`
- `audit_p1_tmp/hstar_bootstrap_summary_madrid.csv`
- `audit_p1_tmp/hstar_bootstrap_summary_henry_st.csv`

No manuscript figure files need substitution from this audit (Ireland
Fig. 6/8 were already handled in a prior, unrelated session).

---

## MODIFIED_LATEX_FILES: NO
## MODIFIED_BIB_FILES: NO
## CREATED_COMMIT: (see closing commit on branch codex/p1-editorial-computational-audit)
## PUSH_PERFORMED: NO
