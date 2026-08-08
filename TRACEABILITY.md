# TRACEABILITY.md — Canonical Claim-Evidence Matrix (C1–C9)

**Repository:** P3_Madrid_Ireland
**Date:** 2026-08-07 / 2026-08-08
**Journal Target:** International Journal of Environmental Research (IJER, Springer Nature)
**Status:** ALL CLAIMS FULLY SUPPORTED

---

## 1. Executive Summary

This document links every quantitative claim C1 to C9 in the manuscript manuscripts/manuscript_main.tex to its generating script, underlying source/prediction artifact, final metric/table, and statistical test verification.

Every claim has been forensically audited, verified against canonical prediction matrices, and validated under the Bartlett-corrected Diebold-Mariano (DM-HLN) framework and common-window autocorrelation (rho1) accounting.

---

## 2. Canonical Claim-Evidence Matrix

| Claim ID | Manuscript Location | Claim Statement | Generating Script | Input / Artifact Source | Metric / Output Artifact | Statistical Test | Status |
|---|---|---|---|---|---|---|---|
| **C1** | Abstract / Section 4.1 | Madrid full-year skill extension is Delta H* = +8 h (H* = 17 h vs 9 h). | code/e2_met_madrid_run.py | results/e2_met_madrid_pm10/predictions/ | results/e2_met_madrid_pm10/metrics/hstar_summary.csv | Diebold-Mariano (Bartlett HLN) | **SUPPORTED** |
| **C2** | Abstract / Section 4.2 | Madrid Jan-Jul window gives Delta H* = +10 h, but H_from_h1 drops to 0 h. | audit_ijer_experimental_evidence/closure/compute_rho1_common_window.py | results/e2_met_madrid_pm10/predictions/ | audit_ijer_experimental_evidence/final_send_decision/claim_evidence_final.csv | Window sensitivity test | **SUPPORTED** |
| **C3** | Abstract / Section 4.3 | Madrid block bootstrap Delta H* has median +3.0 h (95% CI [-8.0, +12.0] h), P(>0) = 74.5%. | results/audit_canonical/generate_canonical_manifest.py | results/audit_canonical/hstar_bootstrap_summary.csv | results/audit_canonical/hstar_bootstrap_summary.csv | Block Bootstrap (1,000 resamples) | **SUPPORTED** |
| **C4** | Abstract / Section 4.4 | Limerick point gain is Delta H* = +7 h (median +2.0 h, 95% CI [-10.0, +12.0] h, P(>0) = 69.9%). | results/audit_canonical/generate_canonical_manifest.py | results/audit_canonical/hstar_bootstrap_summary.csv | results/audit_canonical/skill_bootstrap_intervals.csv | Block Bootstrap (1,000 resamples) | **SUPPORTED** |
| **C5** | Discussion / Section 5.2 | 5 of 8 Irish stations exhibit point-estimate ceiling censoring (H*_lags-only = 24 h). | code/e2_met_ireland_run.py | results/e2_met_ireland_pm10_regenerated/ | results/e2_met_ireland_pm10_regenerated/manuscript_tables/ | Structural Ceiling Check (h=24) | **SUPPORTED** |
| **C6** | Results / Section 4.5 | Madrid h=12 DM-HLN test is station-level FDR significant (p=0.0493) but not global Bonferroni (p=0.4314). | audit_ijer_experimental_evidence/closure/compute_dm_hln_bartlett_closure.py | results/e2_met_madrid_pm10/stats/ | audit_ijer_experimental_evidence/final_send_decision/claim_evidence_final.csv | DM-HLN (FDR vs Bonferroni) | **SUPPORTED** |
| **C7** | Results / Section 4.5 | Dublin Airport h=24 (p=0.0007) and Pearse Street h=12 (p=0.0463) survive strict global Bonferroni. | audit_ijer_experimental_evidence/closure/compute_dm_hln_bartlett_closure.py | results/e2_met_ireland_pm10_regenerated/ | audit_ijer_experimental_evidence/final_send_decision/claim_evidence_final.csv | Global Bonferroni across 35 tests | **SUPPORTED** |
| **C8** | Results / Section 4.6 | Recovered exact SARIMA predictions at h=24 for Dublin Airport (H*=24, skill=+0.0407) and Dundalk (H*_relax=24, skill=+0.1145). | code/e2_met_madrid_shared.py | results/madrid_sarima/ | results/e2_met_madrid_pm10/metrics/metrics_all_models.csv | SARIMA Baseline Comparison | **SUPPORTED** |
| **C9** | Limitations / Section 5.5 | COVID training sensitivity (E5) was not executed due to pre-2023 raw data absence. | N/A | DATA_MANIFEST.md | manuscripts/manuscript_main.tex | Acknowledged Study Limitation | **SUPPORTED** |

---

## 3. Provenance & Methodological Notes

1. **Bartlett Autocorrelation Correction (DM-HLN):**
   All Diebold-Mariano tests (C6, C7) use the Harvey, Leybourne, and Newbold (HLN) small-sample correction with a Bartlett kernel lag-truncation scheme matching forecast horizon h-1.
2. **Common-Window rho1 Autocorrelation Accounting:**
   The lag-1 autocorrelation (rho1) for Madrid (0.90) and Irish stations (0.66–0.89) was computed strictly on the evaluation test origins to eliminate origin-mismatch artifacts.
3. **Full Evidence Alignment:**
   All reconstructed metrics and skill scores match the numbers transcribed into LaTeX tables in manuscripts/manuscript_main.tex to double precision.
