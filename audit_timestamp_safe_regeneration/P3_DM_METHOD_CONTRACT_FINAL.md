# P3 Diebold–Mariano Method & Contract Audit (Final Timestamp-Safe Verification)

**Date**: 2026-08-08
**Git Branch**: `codex/p3-timestamp-safe-regeneration`
**Git Commit HEAD**: `788218d22e83d9b6c031ca767996eccb7c07572b`
**Verdict**: `DM_METHOD_CONTRACT_CONFIRMED`

---

## 1. Executive Summary

This audit establishes the exact computational provenance and mathematical formulation of the Diebold–Mariano (DM) statistical tests generated for paper P3 (Madrid–Ireland PM10 multi-horizon forecasting).

All 36 planned site–horizon comparisons (4 horizons $\times$ 9 monitoring sites) were audited against the authoritative timestamp-safe prediction files and canonical result table `results/manual_timestamp_safe_dm_global_bh.csv`. 

Every single DM statistic, $p$-value, sample size $n$, and decision rule matches the computational code with **0 mismatches across all 36 tests**.

---

## 2. Definitive DM Method Specifications

### 2.1 Common Pairing & Loss Differential
- **Pairing**: Daily forecast origins matched at exact forecast verification timestamps $(t, h)$ under a strict, non-overlapping rolling-origin backtesting design.
- **Loss Function**: Squared Error Loss, $L(e) = e^2$.
- **Loss Differential**:
  $$d_t = e_{\text{lags\_only}, t}^2 - e_{\text{lags\_meteo}, t}^2 = (y_t - \hat{y}_{t, \text{lags\_only}})^2 - (y_t - \hat{y}_{t, \text{lags\_meteo}})^2$$
- **Directional Convention**: $\bar{d} > 0 \implies \text{DM} > 0$, indicating that `lags+meteo` achieves lower RMSE than `lags_only` (favours meteorology).

### 2.2 Irish Network Implementation (`code/e2_met_madrid_shared.py::diebold_mariano_test`)
- **Autocovariance Lag Rule**: $k \in \{1, \ldots, \text{max\_lag}\}$, where $\text{max\_lag} = \max(0, h - 1)$. Unweighted autocovariances.
- **Small-Sample Adjustment**: Harvey, Leybourne & Newbold (HLN, 1997) finite-sample correction factor:
  $$\text{hln} = \sqrt{\frac{n + 1 - 2h + \frac{h(h-1)}{n}}{n}}$$
  $$\text{DM}_{\text{HLN}} = \text{DM}_{\text{raw}} \times \text{hln}$$
- **Reference Distribution**: Student-$t$ distribution with $df = n - 1$:
  $$p_{\text{raw}} = 2 \cdot S_{t, n-1}(|\text{DM}_{\text{HLN}}|)$$

### 2.3 Madrid Implementation (`results/regenerated_timestamp_safe/madrid/dm_lags_meteo_vs_lags_only.csv`)
- **Autocovariance Lag Rule**: Newey–West / Bartlett kernel with fixed truncation lag parameter $q = 7$:
  $$\hat{V}(d) = \hat{\gamma}_0 + 2 \sum_{k=1}^{7} \left(1 - \frac{k}{8}\right) \hat{\gamma}_k$$
- **Reference Distribution**: Asymptotic Standard Normal distribution $N(0, 1)$ without HLN factor:
  $$\text{DM} = \frac{\bar{d}}{\sqrt{\hat{V}(d)/n}}, \quad p_{\text{raw}} = 2 \cdot \Phi(-|\text{DM}|)$$

### 2.4 Multiplicity Control & Invalid Test Protocol
- **Family Size**: 36 planned tests across 9 sites $\times$ 4 horizons ($h \in \{1, 6, 12, 24\}$).
- **Invalid Tests**: 3 tests at $h=24$ (`Dundalk Co Louth`, `henry street Limerick`, `porrlaoise co laois`) had missing DM values due to undefined variance / insufficient sequence length. These are retained as **undefined (`DM undefined`)** and excluded from the multiplicity correction family.
- **Global Benjamini–Hochberg (BH)**: Applied strictly across the **33 valid tests**.
  - **Sole Global Discovery**: `Birr co offlay` at $h=1$ ($\text{DM} = 3.708854$, $p_{\text{raw}} = 0.000267$, $q_{\text{global\_BH}} = 0.008804$).
  - **No other test survives global BH adjustment** (including Madrid $h=12$, $p_{\text{raw}}=0.0289$, $q_{\text{global\_BH}}=0.1910$).

---

## 3. Diagnostic Reproduction Summary

| Site | Horizon ($h$) | $n$ | Calculated DM | Calculated $p_{\text{raw}}$ | Canonical CSV DM | Canonical CSV $p_{\text{raw}}$ | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Madrid** | 1 | 185 | 1.019288 | 0.308066 | 1.019288 | 0.308066 | **MATCH** |
| **Madrid** | 6 | 185 | 1.456561 | 0.145238 | 1.456561 | 0.145238 | **MATCH** |
| **Madrid** | 12 | 185 | 2.184209 | 0.028947 | 2.184209 | 0.028947 | **MATCH** |
| **Madrid** | 24 | 185 | 0.551787 | 0.581094 | 0.551787 | 0.581094 | **MATCH** |
| **Birr** | 1 | 210 | 3.708854 | 0.000267 | 3.708854 | 0.000267 | **MATCH (Sole Discovery)** |
| **Pearse St** | 12 | 212 | 2.494002 | 0.013399 | 2.494002 | 0.013399 | **MATCH** |
| **Dublin Airport** | 24 | 145 | 2.324122 | 0.021518 | 2.324122 | 0.021518 | **MATCH** |
| **Limerick** | 24 | 204 | `NaN` | `NaN` | `NaN` | `NaN` | **MATCH (Undefined)** |
| **Portlaoise** | 24 | 212 | `NaN` | `NaN` | `NaN` | `NaN` | **MATCH (Undefined)** |
| **Dundalk** | 24 | 143 | `NaN` | `NaN` | `NaN` | `NaN` | **MATCH (Undefined)** |

**Total Comparisons**: 36 / 36 Matched  
**Verdict**: `DM_METHOD_CONTRACT_CONFIRMED`
