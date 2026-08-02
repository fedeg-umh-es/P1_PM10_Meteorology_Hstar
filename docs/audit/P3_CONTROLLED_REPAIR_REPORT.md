# P3 Controlled Repair Report

- **Date:** 2026-08-01 (Europe/Madrid)
- **Project:** P3 — Operational Meteorology (canon v1.3; `P3_SEQUENCE_GATE_CLEARED`, `P3_HOLD_AND_REPAIR`)
- **Repository:** `…/03_Investigacion/repos/P3_Madrid_Ireland`
- **Branch / base HEAD:** `codex/p3-hstar-strict-manuscript-repair` / `f01a5ffc2f73252e27b35cda5e964387ff044e67`
- **Nature:** controlled manuscript + producer + provenance repair. No model retrained; no primary prediction/metric/dataset/config/canon modified; no commit/push/PR.

## Canonical values re-verified from primary evidence (read-only)

| Quantity | Value | Source |
|---|---|---|
| Madrid H\*strict max-run | 9 (h3–11) → 17 (h1–17), Δ = +8 | `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv` |
| Henry St. Limerick | 17 → 24, Δ = +7 (from_h1 = 1) | `…ireland…regenerated/metrics/hstar_summary_both_definitions.csv` |
| Ireland means (max-run) | 21.875→21.9 / 22.875→22.9 / +1.0 | same |
| DM directional balance | 24 / 7 / 1 (32 comparisons) | `…regenerated/stats/dm_lags_meteo_vs_lags_only.csv` |
| rho1 vs ΔH\* | r = 0.554715→0.555; p = 0.121110→0.121 (inherited); n = 9 | `results/derived/nine_site_rho1_delta_hstar.csv` |

No value was changed to match the manuscript; the manuscript was aligned to the evidence.

## Per-file record

### `manuscripts/manuscript_main.tex`
- **Initial:** HEAD blob `0d6c9c75`. Partially repaired; stale values remained.
- **Change:** Abstract strict definition → max-run primary + from-h1 auxiliary; abstract Δ +0.9→+1.0; "governed by"→"associated with". Ireland H\* table: Henry 18→17, mean 22.0→21.9, SARIMA-relax mean 21.6→21.3, Δ +0.9→+1.0. Ireland DM table + narrative replaced with **regenerated** DM values (Birr h1 2.68/0.008; Pearse h6 3.08/0.002, h12 3.26/0.001; Dublin Airp. h24 4.42/<0.001) and the 24/7/1 statement added. Discussion: Dublin-Airport Δ "(0"→"+1"; scatter r=0.58,p=0.10 → r=0.555,p=0.121,n=9; operational paragraph reframed as retrospective upper bound; SARIMA mean 22.0→21.9. Conclusions: "mechanism governs"→"interpretation is consistent with"; 22.0→21.9; operational recommendation reframed with NWP-arm caveat. rho1-scatter caption r/p corrected.
- **Evidence:** metrics/DM CSVs above; nine-site table.
- **Verification:** post-edit grep shows no `+0.9`, `22.0`(stray), `+6`, `23/8/1`, `r = 0.58`, `p = 0.10`, `governs`, `mechanistically`, or stale `18` (remaining `18` is Dundalk SARIMA strict = 18, correct). Madrid DM table left intact (verified vs tracked `stats/`).
- **Final:** aligned to canon; producer/data unchanged.

### `manuscripts/cover_letter.tex`
- **Initial:** HEAD blob `837668ec`.
- **Change:** Madrid ρ1 ≈0.90→≈0.96; Ireland ρ1 ≈0.82→≈0.85; +0.9→+1.0; "mechanistically explained by"→"interpret … in terms of"; "governed by"→"shaped by"; "governs both the skill…"→"is associated with…"; operational "guidance … justify their cost" → retrospective upper bound + hypothesis, no demonstrated operational value.
- **Verification:** grep shows no `+0.9`, `governs`, `mechanistically`, `0.90`, `0.82`.
- **Final:** consistent with manuscript.

### `code/e2_met_ireland_figures.py`
- **Initial:** `make_fig4` read `table_station_hstar_summary.csv` (original tree) with `H_star_strict`; saved to results tree.
- **Change:** `make_fig4` now reads `results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv`, uses `H_strict_max_run` (relax `H_relax`), writes to `manuscripts/figures/ireland_figure_hstar_summary.{png,pdf}`; `main()` made robust (figs 1–3 skipped if original tables absent).
- **Verification:** `py_compile` OK; data mapping confirms Henry lags_only=17, lags_meteo=24. **PNG not rendered here (no local matplotlib).**
- **Final:** producer canonical; render pending matplotlib env.

### `code/e2_autocorrelation_analysis.py`
- **Initial:** absolute path `/Users/federicogarciacrespi/Public/…`; recomputed ρ1 from **absent** processed datasets; read obsolete Ireland H\* table; scipy dependency; legend r/p at 2 dp.
- **Change:** rewritten to read `results/derived/nine_site_rho1_delta_hstar.csv`; repo-relative paths; recompute r with numpy and cross-check against canon (aborts if |Δr|>1e-4); inherit p = 0.121110 (documented: raw-series recomputation unavailable); legend r=0.555, p=0.121, n=9; writes to `manuscripts/figures/figure_rho1_vs_delta_hstar.{png,pdf}`.
- **Verification:** `py_compile` OK; numpy check → r=0.554715, Henry Δ=7, Madrid Δ=8. **PNG not rendered here (no local matplotlib).**
- **Final:** producer canonical; render pending matplotlib env.

### `results/derived/nine_site_rho1_delta_hstar.csv` (created)
- Nine canonical (site, ρ1, H\*strict max-run lags_only/lags_meteo, Δ, provenance) rows. ρ1 from canonical nine-site table; H\* from regenerated bundle (Ireland) / tracked outputs (Madrid). Recomputed Pearson r = 0.554715.

### `results/e2_met_madrid_pm10/bundle_provenance.md` (created)
- Documents metadata-vs-bundle mismatch (26,064/72/0 vs 34,752/96/DM present), commit assembly (`3440bf2`→`c30e6cf`), +8 arithmetically verifiable, processed dataset absent. Historical `run_metadata.json` left unchanged.

### `results/e2_met_ireland_pm10_regenerated/output_manifest_classified.{md,csv}` (created)
- 31 entries classified: 14 HASH_VERIFIED, 1 HASH_UPDATED (`merge_validation_report.md`), 16 DELIBERATELY_EXCLUDED_SHARD, 0 MISSING_UNEXPECTEDLY. Notes package is not self-contained (source CSVs / processed panel absent).

### `results/e2_met_ireland_pm10_regenerated/output_hashes.csv` and `results/output_hashes.csv`
- **Change:** single stale hash for `merge_validation_report.md` corrected `bab82f…` → `28296465…` (size 2723 unchanged, content had legitimately changed). No other line touched.

### `docs/audit/P3_HSTAR_STRICT_MANUSCRIPT_REPAIR_REPORT.md`
- Corrected: real figure filenames, true obsolete-figure identification, Madrid +8 status, compile status, and verdict (no longer `READY_FOR_OVERLEAF_COMPILATION`).

## Actions NOT taken
- No model retrained; no primary predictions/metrics/DM/datasets/config/canon modified; no other project touched.
- No commit, push, or PR.
- The two obsolete PNGs were **not** re-rendered (no local matplotlib) and no PDF was compiled (no local TeX).

## Verdict
`TEXT_AND_DATA_REPAIR_COMPLETE__FIGURE_RENDER_AND_OVERLEAF_COMPILATION_PENDING`

Local completion criteria met: H\* definition coherent; canonical figures in text and letter; causality controlled; retrospective framing explicit; provenance transparent; producers no longer depend on obsolete/absent Ireland artefacts; manifests coherent. **Not met locally:** figure PNG re-render (no matplotlib) and PDF compile/visual review (no TeX). Therefore neither `P3_REPAIR_COMPLETE_PENDING_OVERLEAF` (requires corrected figures rendered) nor `READY_FOR_FINAL_CLAIM_EVIDENCE_AUDIT` (requires compiled PDF) can be issued yet.
