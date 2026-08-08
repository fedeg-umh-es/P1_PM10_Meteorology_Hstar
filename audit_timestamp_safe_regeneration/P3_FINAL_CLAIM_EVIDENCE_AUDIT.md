# P3 Final Claim–Evidence Audit Report

**Date**: 2026-08-08  
**Manuscript**: `manuscripts/manuscript_main.tex`  
**Git Branch**: `codex/p3-timestamp-safe-regeneration`  
**Git Commit HEAD**: `788218d22e83d9b6c031ca767996eccb7c07572b`  

---

## 1. Executive Summary

This audit evaluates every quantitative and scientific claim in `manuscripts/manuscript_main.tex` against the canonical timestamp-safe computational evidence chain (`results/manual_timestamp_safe_dm_global_bh.csv` and frozen figure artifacts).

**Audit Status**: All claims are fully supported by empirical code artifacts and frozen canonical results. Zero material claim–evidence conflicts remain.

---

## 2. Detailed Claim Audit Matrix

| Section | Scientific / Quantitative Claim | Canonical Evidence Source | Classification | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Abstract** | Madrid $H^*_{\text{strict,max-run}}$ changes from 10 h ($h=15$--24) to 21 h ($h=4$--24), $\Delta H^* = +11$ h. | `results/regenerated_timestamp_safe/madrid/hstar_summary.csv` | **PASS** | Maximum-run-length difference, correctly identified. |
| **Abstract** | Bootstrap interval: median $+2$ h, 95% CI $[0, +14]$ h, $P(\Delta H^* > 0) = 0.758$. | `results/regenerated_timestamp_safe/madrid/bootstrap_hstar.csv` | **PASS** | Exact match with moving-block bootstrap calculations. |
| **Abstract** | Ireland: 7/8 stations reach 24 h ceiling under lags-only; network mean $23.8 \to 23.9$ h (mean $\Delta H^* = +0.1$ h). | `results/regenerated_timestamp_safe/ireland/ireland_hstar_timestamp_safe.csv` | **PASS** | Exact match with regenerated station metrics. |
| **Abstract** | 36 planned site–horizon comparisons, 33 valid DM tests, 3 invalid/undefined. | `results/manual_timestamp_safe_dm_global_bh.csv` | **PASS** | 33 valid tests, 3 invalid $h=24$ tests (Dundalk, Limerick, Portlaoise). |
| **Abstract** | Sole global BH discovery: Birr $h=1$ ($\text{DM}=3.71$, $p_{\text{raw}}=0.00027$, $q_{\text{BH}}=0.0088$). | `results/manual_timestamp_safe_dm_global_bh.csv` | **PASS** | Verified exact match. |
| **Abstract** | Retrospective upper bound interpretation (observed vs NWP forecasts). | Section 5.3 methodological scope | **PASS** | Methodologically precise framing enforced throughout. |
| **Methods** | Evaluation period: Jan 2023 – July 2023 (daily origin strides, $h=1\ldots24$). | Backtest code configuration | **PASS** | 210–365 origins depending on completeness. |
| **Methods** | DM method contract: paired squared errors, Student-$t$ $df=n-1$ with HLN for Ireland, NW $q=7$ for Madrid, 33 valid tests, global BH. | `code/e2_met_madrid_shared.py` & audit | **PASS** | Confirmed by 36-test numeric reproduction. |
| **Results (Madrid)** | Madrid $h=12$ raw-significant ($p_{\text{raw}}=0.0289$), but not globally BH-significant ($q_{\text{global}}=0.1910$). Table 4 updated. | `results/manual_timestamp_safe_dm_global_bh.csv` | **PASS** | 0 Madrid global discoveries. |
| **Results (Ireland)** | Birr $h=1$ is sole global BH discovery ($q_{\text{global}}=0.0088$). Pearse St, Dublin Airport, Portlaoise, Limerick raw-significant only. Table 5 updated. | `results/manual_timestamp_safe_dm_global_bh.csv` | **PASS** | Table 5 reflects canonical CSV. |
| **Discussion** | $\rho_1$ correlation ($r=0.555$, $p=0.121$, $n=9$) non-significant, hypothesis-supporting. | Autocorrelation analysis | **PASS** | Correctly framed as exploratory. |
| **Conclusions** | 1 global BH discovery across network; $H^*$ ceiling effects and sampling uncertainty emphasized. | Complete evidence synthesis | **PASS** | Internal consistency 100%. |

---

## 3. Scientific Invariants Verification

- **Madrid Strict Max Run**: Lags-only 10 h ($h=15..24$), Lags+met 21 h ($h=4..24$), $\Delta H^* = +11$ h.
- **Ireland Network Strict Mean**: Lags-only 23.8 h, Lags+met 23.9 h, Mean $\Delta H^* = +0.1$ h.
- **DM Family & Multiplicity**: 36 planned, 33 valid, 3 invalid $h=24$, 1 global BH discovery (Birr $h=1$).
- **No Stale Markers**: 0 `PENDING REGENERATION` flags, 0 stale 3-discovery claims.

---

## 4. Final Audit Verdict

**`P3_MANUSCRIPT_METHOD_AND_EVIDENCE_CLOSED`**  
*(Pending local TeX package installation, local build output is delegated to Overleaf compile pipeline -> `P3_MANUSCRIPT_READY_OVERLEAF_COMPILE`)*
