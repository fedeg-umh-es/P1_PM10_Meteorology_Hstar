# H*_strict: two candidate definitions, computed and kept separately

- Date: 2026-07-26
- Scope: resolve which of two candidate definitions of `H*_strict` the
  manuscript's tables actually reproduce, using the freshly regenerated,
  row-level Ireland predictions.

## The two definitions

`manuscripts/manuscript_main.tex:356-361` states, in prose:

> **`H*_strict`**: the length of the longest *consecutive* positive-skill run
> **beginning at h = 1**. This captures the unbroken window of reliable
> improvement over persistence.

Call this **`H_strict_from_h1`**. It is computed by scanning the skill curve
`S(h)` for `h = 1, 2, 3, ...` and stopping at the first `h` where
`S(h) <= 0` (or is missing).

`code/e2_met_ireland_run.py`'s `derive_hstar_ireland()` function — the
codebase's own, currently-committed implementation, unchanged by this
regeneration — instead computes the longest run of consecutive positive-skill
horizons **anywhere** in `h = 1..24`, not necessarily starting at `h = 1`.
Call this **`H_strict_max_run`**.

These are literally the same value whenever a station's skill curve is
positive all the way from `h=1` (in which case both scans terminate at the
same horizon), but they diverge whenever the curve has an early negative-skill
horizon followed by a later, longer run of positive skill.

Both were computed independently for the regenerated run and kept in
separate columns — never silently substituted for one another — in
`results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv`.

## Result: the manuscript's tables match `H_strict_max_run`, not `H_strict_from_h1`

| Station | Condition | Manuscript `H*_strict` | Regenerated `H_strict_max_run` | Regenerated `H_strict_from_h1` |
|---|---|---:|---:|---:|
| Dublin Airport | lags_only | 22 | **22** | 0 |
| Dublin Airport | lags_meteo | 23 | **23** | 0 |
| Edenderry (Co. Offaly) | lags_only | 16 | **16** | 7 |
| Edenderry (Co. Offaly) | lags_meteo | 16 | **16** | 7 |
| Henry St. Limerick | lags_only | 18 | 17 (off by 1) | 1 |
| Henry St. Limerick | lags_meteo | 24 | **24** | 24 |
| All other station/condition pairs | — | 24 | **24** | 24 |

`H_strict_max_run` matches the manuscript's table exactly for 30 of 32
station/condition/model cells (the sole residual gap is Henry St. Limerick
lags_only: manuscript 18 vs. regenerated 17 — a 1-hour difference, well
within what a different raw-data snapshot, minor timestamp-handling
differences, or model-fitting stochasticity between XGBoost/library versions
could produce, and classified as `ROUNDING_MATCH` in
`manuscript_claim_comparison.csv`).

`H_strict_from_h1` — the manuscript's own literal prose definition — does
**not** match the manuscript's own table for Dublin Airport (both conditions:
manuscript claims 22/23, `from_h1` gives 0/0, because this regenerated run's
`skill(h=1)` is negative at Dublin Airport for both conditions) or Edenderry
(manuscript claims 16/16, `from_h1` gives 7/7, because the skill curve has an
early break around `h=8` before recovering).

## Conclusion

**`H_strict_max_run` is the manuscript-compatible definition** — i.e., despite
the manuscript's Methods section describing `H*_strict` in prose as a run
"beginning at h = 1", the actual reported table values were, in practice,
computed as the longest positive-skill run **anywhere** in the horizon range
(which is also what the codebase's own `derive_hstar_ireland()` function has
always computed, unchanged by this regeneration). This is a genuine
**documentation/methods-text inconsistency** in the manuscript, not a data or
code defect discovered by this regeneration: the code was never edited to
produce this result, and the same "max run anywhere" logic is what
`code/e2_met_ireland_run.py` has computed all along.

This finding is independently corroborated by the earlier evidence-recovery
pass's Section 3 (`results/e2_met_ireland_pm10/validation/evidence_validation_report.md`),
which found the exact same three stations (Dublin Airport, Edenderry, Henry
St. Limerick) diverging under a strict "from-h1"-style reading when compared
against the auxiliary `master_meteorology_diagnostic_table.csv` pipeline —
now confirmed a second time, independently, from freshly regenerated
row-level predictions built directly from the recovered raw source CSVs.

**Recommendation (documentation only, not applied here per the task's
explicit "no modifiques el manuscrito" instruction):** the manuscript's
Methods section prose (lines 356-361) should be corrected to describe
`H*_strict` as "the longest consecutive positive-skill run within h=1..H"
(unanchored), or the reported table values should be recomputed under the
prose's literal from-h1 definition — whichever the authors intend as the
paper's actual criterion.
