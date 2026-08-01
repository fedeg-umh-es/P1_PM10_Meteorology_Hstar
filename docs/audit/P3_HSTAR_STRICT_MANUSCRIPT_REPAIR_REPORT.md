# P3 H* Strict Manuscript Repair Report

## Repository
- Path: /Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland
- Branch: codex/p3-hstar-strict-manuscript-repair
- Start SHA: bdc91fa3c05c324ca5c8c39a8222dc5931407fbc

## Canonical decision
- Decision: `2026-08-01-hstar-strict-definition`
- Primary metric: `H_strict_max_run` (longest contiguous positive-skill run anywhere within $h \in \{1, \dots, 24\}$)
- Auxiliary metric: `H_strict_from_h1` (uninterrupted positive-skill run starting at $h=1$)

## Evidence verification
- Madrid: Verified under `H_strict_max_run` (`lags_only` = 9 h, `lags_meteo` = 17 h, $\Delta H^* = +8$ h)
- Ireland: Verified under `H_strict_max_run` across 8 stations
- +8 h claim: `VERIFIED_UNDER_H_STRICT_MAX_RUN` (Madrid)
- Henry Street: `lags_only` = 17 h, `lags_meteo` = 24 h, $\Delta H^* = +7$ h (Updated from +6 h / 18 h)
- Ireland mean: `lags_only` = 21.9 h, `lags_meteo` = 22.9 h, $\Delta H^* = +1.0$ h (Updated from +0.9 h / 22.0 h)

## Files inspected
- `manuscripts/manuscript_main.tex`
- `results/e2_met_madrid_pm10/metrics/hstar_summary.csv`
- `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`
- `results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv`
- `results/e2_met_ireland_pm10_regenerated/hstar_definition_discrepancy.md`
- `docs/audit/P3_HSTAR_STRICT_VALUE_VERIFICATION.md`

## Files modified
- `manuscripts/manuscript_main.tex`
- `docs/audit/P3_HSTAR_STRICT_VALUE_VERIFICATION.md`
- `docs/audit/P3_HSTAR_STRICT_MANUSCRIPT_REPAIR_REPORT.md`

## Notation changes
- Defined $H^*_{\text{strict,max-run}}$ explicitly as the primary metric and $H_{\text{strict,from-}h1}$ as the auxiliary diagnostic.

## Methods changes
- Clarified prose in Methods (lines 356-366) to specify $H^*_{\text{strict,max-run}}$ as the longest contiguous positive-skill run within $h \in \{1, \dots, H\}$, resolving the prose-code discrepancy.

## Results changes
- Associated Madrid $\Delta H^*_{\text{strict}} = +8$~h explicitly with $H^*_{\text{strict,max-run}}$.
- Updated Henry Street Limerick $\Delta H^*_{\text{strict}}$ to $+7$~h ($H^* = 17$~h lags-only vs 24~h lags+met).
- Updated Ireland mean values to $\bar{\Delta H^*} = +1.0$~h ($\bar{H}^*_{\text{lags only}} = 21.9$~h, $\bar{H}^*_{\text{lags+met}} = 22.9$~h).

## Table changes
- Table 5: Header updated to $H^*_{\text{strict,max-run}}$, Henry Street row updated to 17 | 24 | +7, Ireland mean row updated to 21.9 | 22.9 | +1.0, and footnote added noting regenerated source datasets for Irish values.

## Figure status

| Figure | Source available | Metric represented | Status | Action |
|---|---|---|---|---|
| `figures/madrid_figure_01_skill.png` | YES | Skill curves $S(h)$ | VALID_UNDER_MAX_RUN | Kept |
| `figures/madrid_figure_02_dm.png` | YES | DM-HLN tests | VALID_UNDER_MAX_RUN | Kept |
| `figures/madrid_figure_03_hstar.png` | YES | $H^*$ summary | VALID_UNDER_MAX_RUN | Kept |
| `figures/ireland_figure_01_skill.png` | YES | Skill curves $S(h)$ | VALID_UNDER_MAX_RUN | Kept |
| `figures/ireland_figure_02_dm.png` | YES | DM-HLN tests | VALID_UNDER_MAX_RUN | Kept |
| `figures/ireland_figure_03_hstar.png` | YES | $H^*$ summary | VALID_UNDER_MAX_RUN | Kept |
| `figures/ireland_figure_04_rho1_vs_deltahstar.png` | YES | $\rho_1$ vs $\Delta H^*$ | VALID_UNDER_MAX_RUN | Kept |

## Irish evidence provenance
- Original-run artefacts: MISSING (Row-level prediction files for original run not committed in Git history)
- Regenerated artefacts: PRESENT (`results/e2_met_ireland_pm10_regenerated/`)
- Disclosure added: Explicitly incorporated in Methods, Data and Code Availability, and Table 5 footnote.

## Claims retained
- Madrid meteorology benefit: $\Delta H^*_{\text{strict,max-run}} = +8$~h (verified under `H_strict_max_run`).
- Autocorrelation-persistence mechanism: $\rho_1$ association with predictability gains.

## Claims changed or removed
- Henry Street gain: Updated from +6 h / 18 h to +7 h / 17 h based on verified $H^*_{\text{strict,max-run}}$.
- Ireland mean gain: Updated from +0.9 h / 22.0 h to +1.0 h / 21.9 h based on verified $H^*_{\text{strict,max-run}}$.

## Compilation status
- Local TeX: ABSENT (pdflatex / latexmk not installed locally)
- Overleaf compilation required: YES
- Current status: OVERLEAF_COMPILATION_PENDING

## Residual risks
- Visual rendering check pending until compilation in Overleaf.

## Verdict
- `READY_FOR_OVERLEAF_COMPILATION`
