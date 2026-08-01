# P2 H* Strict Repository Preparation

## Identity normalization

- Current programme identity: **P2 — Operational Meteorology** (historically E2-MET).
- Decision: `REMAINS_P2`; no P2-to-P3 renumbering is authorized or recorded.
- Historical remote alias: `fedeg-umh-es/P1_PM10_Meteorology_Hstar`.
- Current local path after normalization: `/Users/fede/repos/P2_Operational_Meteorology`.
- Current work branch after normalization: `codex/p2-identity-normalization`.
- Provenance note: this preparation record was originally committed at
  `aa00a1821786509b7028fb689478ced476aebc6a` with a non-authoritative P3 title,
  branch, and directory label. Those historical strings did not supersede the
  committed P2 identity freeze.

## Historical environment snapshot

- Host: MacBook-Neo-de-fede.local
- User: fede
- Date: 2026-08-01T11:46:50+02:00
- Original working directory: `/Users/fede/repos/P3_Madrid_Ireland`
- Git version: git version 2.50.1 (Apple Git-155)
- LaTeX toolchain: pdflatex / latexmk not installed locally (compilation deferred to Overleaf cloud environment)

## Repository

- Remote: https://github.com/fedeg-umh-es/P1_PM10_Meteorology_Hstar.git (historical repository name)
- Current local path: `/Users/fede/repos/P2_Operational_Meteorology`
- Base branch: `main`
- Base SHA: `370490a266fc2d3901b21340340e5047b33cf3a4`
- Current work branch: `codex/p2-identity-normalization`
- Original preparation branch: `codex/p3-hstar-strict-manuscript-repair` (historical, non-authoritative label)
- Original worktree status: Clean

## Baseline compilation

- Main file: `./manuscripts/manuscript_main.tex`
- Command: N/A (local LaTeX engine pdflatex not present)
- Result: BASELINE_COMPILE_FAILED (local pdflatex binary absent; Overleaf cloud compilation required)
- Generated PDF: None (deferred to Overleaf)
- Relevant warnings: Local LaTeX environment missing pdflatex.

## Manuscript inventory

- Main manuscript files:
  - `manuscripts/manuscript_main.tex`
  - `manuscripts/cover_letter.tex`
  - `manuscripts/references.bib`
- Supplement files: Integrated within `manuscript_main.tex`
- Tables:
  - Table 1 (Descriptive PM10 stats, line 244)
  - Table 2 (Madrid DM-HLN tests, line 418)
  - Table 3 (Ireland DM-HLN tests, line 512)
  - Table 4 (Ireland H* summary, line 471)
  - Table 5 (9-site H* and autocorrelation summary, lines 797-811)
- Figures:
  - `manuscripts/figures/madrid_figure_01_skill.png`
  - `manuscripts/figures/madrid_figure_02_dm.png`
  - `manuscripts/figures/madrid_figure_03_hstar.png`
  - `manuscripts/figures/ireland_figure_01_skill.png`
  - `manuscripts/figures/ireland_figure_02_dm.png`
  - `manuscripts/figures/ireland_figure_03_hstar.png`
  - `manuscripts/figures/ireland_figure_04_rho1_vs_deltahstar.png`
- Availability statements: Section 4 / Data Availability in `manuscript_main.tex`

## H* references found

- `manuscripts/manuscript_main.tex:359`: Definition of $H^*_{\text{strict}}$ as longest positive skill run (`H_strict_max_run`). Needs explicit differentiation from `H_strict_from_h1`.
- `manuscripts/manuscript_main.tex:397`: Madrid $\Delta H^*_{\text{strict}} = +8$~h claim. Dependent on `H_strict_max_run`.
- `manuscripts/manuscript_main.tex:451`: Henry Street Limerick $\Delta H^*_{\text{strict}} = +6$~h. Requires update to +7~h (17~h) per decision.
- `manuscripts/manuscript_main.tex:460`: Ireland mean $\bar{\Delta H^*} = +0.9$~h. Requires update to +1.0~h per decision.
- `manuscripts/manuscript_main.tex:801-811`: Table 5 summary values across 9 sites.

## Primary evidence inventory

- Artifact: Madrid primary metrics and predictions
  - Status: PRESENT
  - Path: `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`
  - Notes: Full row-level predictions, metrics, and metadata present and verified.
- Artifact: Original Ireland run row-level predictions and metrics
  - Status: MISSING
  - Path: `results/e2_met_ireland_pm10/`
  - Notes: Never committed to git in original run; documented in `evidence_validation_report.md`.
- Artifact: Regenerated Ireland run primary metrics and predictions
  - Status: PRESENT (REGENERATED_NOT_TRACKED / REGENERATED)
  - Path: `results/e2_met_ireland_pm10_regenerated/metrics/metrics_all_models.csv`
  - Notes: Regenerated from recovered source dataset; includes both `H_strict_max_run` and `H_strict_from_h1` metrics.

## Blocking issues

- None for repository preparation phase.
- Local TeX compilation remains unavailable because `pdflatex` is not installed.
- Scientific or manuscript repair remains outside this identity-normalization change.

## Readiness verdict

`READY_FOR_P2_MANUSCRIPT_REPAIR`
