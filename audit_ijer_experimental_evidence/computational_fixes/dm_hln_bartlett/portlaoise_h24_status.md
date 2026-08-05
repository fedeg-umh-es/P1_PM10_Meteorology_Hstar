# Phase 2 — Portlaoise h=24 under a Bartlett-weighted DM-HLN kernel

**Scope:** P1 only. Parallel (non-destructive) recomputation of the DM-HLN long-run variance
estimator. `code/e2_met_madrid_shared.py:diebold_mariano_test()` was **not modified** — a
separate function (`diebold_mariano_test_bartlett`) was written, called against the same
tracked `predictions_all_models.csv` files (Madrid: `results/e2_met_madrid_pm10/predictions/`;
Ireland: `results/e2_met_ireland_pm10_regenerated/predictions/`) that
`code/run_e4_multiple_testing.py` uses, with identical model/condition pairing, identical
`max_lag = horizon - 1` per horizon (documented convention already in the original code — kept
unchanged here), and identical Harvey–Leybourne–Newbold correction. Only the long-run variance
kernel changed: unweighted rectangular sum → Bartlett (triangular, Newey–West) weighted sum,
`weight(lag) = 1 - lag/(max_lag+1)`.

## Result for Portlaoise, h=24

| | Rectangular (canonical, current manuscript) | Bartlett (this audit) |
|---|---|---|
| long-run variance | ≤0 (non-finite/invalid) | **1429.92** (finite, positive) |
| `dm_hln_stat` | NaN | **0.9055** |
| `p_raw` | NaN | **0.3662** |
| `favours` | `undetermined` | `lags_meteo` |
| Bonferroni-global | N/A | NS (p=1.00) |
| FDR-global | N/A | NS (p=0.603) |
| FDR-station | N/A | NS (p=0.366) |

```
PORTLAOISE_H24_STATUS = DM_VALID_UNDER_BARTLETT
```

The Bartlett kernel resolves the non-positive-definiteness that produced the `undetermined`
result under the rectangular kernel (root cause identified in the prior forensic-gate audit:
an unweighted long-run variance sum is not guaranteed PSD at `max_lag=23, n=212`). Under
Bartlett, Portlaoise h=24 becomes a **valid, non-significant** test (`favours=lags_meteo`,
p_raw=0.366) — it now simply joins the pool of non-significant direction-only comparisons
rather than being excluded. This changes the global multiplicity denominator from `m=35`
(35 valid tests, 1 excluded) to `m=36` (all 36 planned tests now computable).

## IMPORTANT: other tests change significance status under Bartlett

Recomputing all 36 planned station×horizon tests with the identical Bartlett kernel (not just
Portlaoise) shows that the rectangular kernel's long-run variance estimates were systematically
**too small** at several other station×horizon combinations — the Bartlett kernel's larger,
more conservative variance estimates flip 4 additional tests' significance status. These are
**not** cosmetic: two of them are the manuscript's only two claims of "survives global
Bonferroni correction," reported in the Abstract, Results §4.5/§3.6, and Discussion.

| Station | h | Rectangular status | Bartlett status | Levels affected |
|---|---|---|---|---|
| **Dublin Airport** | **24** | `p_bonf_global=0.0007` → **SIG** | `p_bonf_global=1.000` (`p_raw=0.207`) → **NS** | Bonferroni-global, FDR-global, FDR-station — all flip SIG→NS |
| **Pearse Street Dublin** | **12** | `p_bonf_global=0.0463` → **SIG** | `p_bonf_global=0.336` → **NS** | Bonferroni-global, FDR-global flip SIG→NS; FDR-station stays SIG (0.0187) |
| Pearse Street Dublin | 6 | `p_fdr_global=0.0272` → SIG | `p_fdr_global=0.112` → NS | FDR-global flips SIG→NS; FDR-station stays SIG in both |
| Madrid Casa de Campo | 12 | `p_fdr_station=0.0493` → SIG | `p_fdr_station=0.0703` → NS | FDR-station flips SIG→NS (the only significance claim this comparison had) |

**Consequence for the manuscript's current text:** under the rectangular kernel, exactly two
comparisons survive strict global Bonferroni correction (Dublin Airport h=24, Pearse Street
Dublin h=12) — this is stated explicitly in the Abstract ("Conversely, skill gains at Dublin
Airport (h=24, ...) and Pearse Street Dublin (h=12, ...) maintain significance under strict
global Bonferroni control"). Under the Bartlett kernel, **both of these lose Bonferroni-global
significance**, and Madrid's h=12 within-site-FDR claim (the abstract's other headline
significance claim) also loses significance. No comparison in the entire 9-station × 4-horizon
grid survives global Bonferroni correction under the Bartlett kernel.

This is a computational-verification finding only. No manuscript text was edited in this
session, and no experiment was rerun or retrained — only the long-run variance estimator inside
the (separately implemented, non-canonical) DM-HLN test statistic was changed, applied
read-only against the existing tracked predictions.

See `dm_results_bartlett.csv` (full 36-row Bartlett results with multiplicity-adjusted p-values)
and `dm_comparison_rectangular_vs_bartlett.csv` (side-by-side, all 36 rows, with
`status_changed_any_level` flag) for complete figures.
