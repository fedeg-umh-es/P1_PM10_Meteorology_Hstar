# P3 H* Strict Manuscript Repair Report

> **Correction note (P3 controlled repair, 2026-08-01).** This report previously
> listed seven figure paths that do not exist in the repository, marked the two
> obsolete figures under wrong filenames, and issued a premature
> `READY_FOR_OVERLEAF_COMPILATION` verdict. Those errors are corrected below.
> The authoritative, per-file account of the controlled repair is in
> `docs/audit/P3_CONTROLLED_REPAIR_REPORT.md`.

## Repository
- Path: /Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland
- Branch: codex/p3-hstar-strict-manuscript-repair
- Start SHA (original repair): bdc91fa3c05c324ca5c8c39a8222dc5931407fbc
- Controlled-repair base SHA: f01a5ffc2f73252e27b35cda5e964387ff044e67

## Canonical decision
- Decision: `2026-08-01-hstar-strict-definition`
- Primary metric: `H_strict_max_run` (longest contiguous positive-skill run anywhere within $h \in \{1, \dots, 24\}$)
- Auxiliary metric: `H_strict_from_h1` (uninterrupted positive-skill run starting at $h=1$)

## Evidence verification (re-verified in controlled repair)
- Madrid `H_strict_max_run`: lags_only = 9 (h=3..11), lags_meteo = 17 (h=1..17); recomputed from `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`.
- **Madrid ΔH\* = +8 h**: `ARITHMETICALLY_VERIFIABLE_FROM_TRACKED_OUTPUTS` (9 → 17). The processed base dataset is absent, so the run is not re-executable end-to-end, but the claim is reproducible from tracked metrics (see `results/e2_met_madrid_pm10/bundle_provenance.md`). This supersedes the earlier `BLOCKED_BY_INSUFFICIENT_EVIDENCE` label for the *arithmetic* of +8.
- Ireland: verified under `H_strict_max_run` across 8 stations (regenerated bundle).
- Henry Street: `lags_only` = 17 h, `lags_meteo` = 24 h, ΔH\* = +7 h (corrected from +6 h / 18 h).
- Ireland mean: `lags_only` = 21.9 h, `lags_meteo` = 22.9 h, ΔH\* = +1.0 h (corrected from +0.9 h / 22.0 h).
- DM directional balance (Ireland, 32 comparisons): 24 / 7 / 1, recomputed from the regenerated `stats/dm_lags_meteo_vs_lags_only.csv`.
- rho1 vs ΔH\* (nine sites): r = 0.554715 (recomputed from the canonical nine-site table), p = 0.121110 (inherited; raw-series recomputation unavailable). Manuscript form r = 0.555, p = 0.121, n = 9.

## Figure status (corrected filenames)

Actual figures referenced by `manuscripts/manuscript_main.tex`:

| Figure file (as referenced) | Metric | Status |
|---|---|---|
| `figures/madrid_figure_skill_curves.png` | Madrid skill curves | PRESENT (not re-rendered; out of scope) |
| `figures/madrid_figure_delta_skill.png` | Madrid ΔSkill | PRESENT (not re-rendered; out of scope) |
| `figures/madrid_figure_dm_significance.png` | Madrid DM-HLN | PRESENT; Madrid DM verified vs tracked `stats/` file |
| `figures/madrid_figure_hstar_summary.png` | Madrid H\* summary | PRESENT; shows 9 / 17 strict, consistent with max-run |
| `figures/ireland_figure_skill_by_station.png` | Ireland skill curves | PRESENT (not re-rendered; out of scope) |
| `figures/ireland_figure_delta_skill.png` | Ireland ΔSkill | PRESENT (not re-rendered; out of scope) |
| `figures/ireland_figure_dm_significance.png` | Ireland DM-HLN | PRESENT but built from the **original-run** DM data; the DM *table* in the manuscript is now regenerated (24/7/1). RENDER_FROM_REGENERATED_RECOMMENDED (residual) |
| `figures/ireland_figure_hstar_summary.png` | Ireland H\* summary | **OBSOLETE** (shows Henry St lags-only = 18). Producer corrected; PNG render pending (no local matplotlib) |
| `figures/figure_rho1_vs_delta_hstar.png` | rho1 vs ΔH\* | **OBSOLETE** (shows +6, r=0.58, p=0.10). Producer corrected; PNG render pending (no local matplotlib) |

The earlier table's seven paths (`madrid_figure_01_skill.png`, `…_02_dm.png`,
`…_03_hstar.png`, `ireland_figure_01_skill.png`, `…_02_dm.png`, `…_03_hstar.png`,
`ireland_figure_04_rho1_vs_deltahstar.png`) do **not** exist in the repository
and were incorrect.

## Producers corrected (this controlled repair)
- `code/e2_met_ireland_figures.py`: `make_fig4` now reads the regenerated
  `metrics/hstar_summary_both_definitions.csv`, uses `H_strict_max_run` (relax
  = `H_relax`), and writes to `manuscripts/figures/ireland_figure_hstar_summary`.
- `code/e2_autocorrelation_analysis.py`: rewritten to read the versioned
  canonical nine-site table `results/derived/nine_site_rho1_delta_hstar.csv`
  (no author-local absolute paths, no absent-dataset reads, no obsolete Ireland
  table); recomputes r from the table and inherits p; legend shows r = 0.555,
  p = 0.121, n = 9; writes to `manuscripts/figures/figure_rho1_vs_delta_hstar`.

## Provenance
- Madrid: `results/e2_met_madrid_pm10/bundle_provenance.md` (bundle composition; +8 arithmetically verifiable; processed dataset absent).
- Ireland: `results/e2_met_ireland_pm10_regenerated/output_manifest_classified.{md,csv}` (14 HASH_VERIFIED, 1 HASH_UPDATED, 16 DELIBERATELY_EXCLUDED_SHARD, 0 MISSING_UNEXPECTEDLY); stale `merge_validation_report.md` hash corrected in both `output_hashes.csv` copies.
- Disclosure: Ireland "regenerated, not original run" retained in Methods, Data and Code Availability, and Table footnote.

## Compilation status
- Local TeX: ABSENT (pdflatex / latexmk / tectonic not installed).
- Local matplotlib: ABSENT (the two obsolete PNGs cannot be rendered here).
- Overleaf/render compilation: PENDING.

## Residual risks
- The two obsolete PNGs are not yet re-rendered (no local matplotlib); producers and data are corrected so they render correctly in a matplotlib/Overleaf environment.
- `ireland_figure_dm_significance.png` is still built from original-run DM data and should be re-rendered from the regenerated DM to match the corrected DM table.
- PDF not compiled; visual verification of figures and PDF pending.

## Verdict
- `TEXT_AND_DATA_REPAIR_COMPLETE__FIGURE_RENDER_AND_OVERLEAF_COMPILATION_PENDING`
- **Not** `READY_FOR_OVERLEAF_COMPILATION` (figures not rendered, PDF not verified).
