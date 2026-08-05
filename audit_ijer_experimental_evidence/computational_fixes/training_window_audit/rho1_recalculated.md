# Phase 3 — Real per-origin training window vs. the manuscript's "2020–2022" label

**Scope:** P1 only. Read-only computation of calendar windows and nominal row counts from
`code/e2_met_madrid_config.json` and the 362 tracked Madrid evaluation origins
(`results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`). No manuscript edit, no
retraining, no data regeneration.

## Confirmed: `train_start` is 2019-01-01, not 2020-01-01

`code/e2_met_madrid_config.json`: `"train_start": "2019-01-01 00:00:00"`. This is the value
actually passed to `code/rolling_origin.py:get_train_window(train_start=...)` for every one of
the 362 Madrid origins — confirmed identical in `results/e2_met_madrid_pm10/config_snapshot.json`
(the frozen run-time snapshot). There is no code path in this repository that restricts Madrid's
XGBoost training data to 2020 onward.

## XGBoost effective training window, across all 362 origins

Computed for every origin (`window_size_by_origin.csv`, full 362-row table):

```
xgboost_n_train_rows_nominal_hourly:
  min = 35,064 rows  (origin = 2023-01-01; window = 2019-01-01 .. 2022-12-31, exactly 4 years)
  max = 43,776 rows  (origin = 2023-12-30; window = 2019-01-01 .. 2023-12-29, ~4.997 years)
```

("Nominal" = calendar hours between `train_start` and the origin; the true row count could be
marginally lower if the raw series has missing hours — the raw dataset is not present locally
to check this exactly, see limitation below.)

**At every single evaluation origin, XGBoost's real training window already includes all of
2019 (not just 2020 onward) and grows to include part of 2023 itself for origins later in the
year.** It is never restricted to 2020–2022, and it is not constant in size across origins (it
grows by exactly 1 row per 24-hour stride, consistent with the expanding-window definition
verified in the forensic-gate audit).

## SARIMA effective training window, across all 362 origins

`sarima_max_train_rows = 17,520` (`code/e2_met_madrid_config.json`), applied via
`.iloc[-17520:]` in `code/e2_met_madrid_shared.py:predict_sarima()`.

```
sarima_capped_at_17520 = True for all 362/362 origins
  (the expanding window already exceeds 17,520 rows at the very first
   2023 origin — 35,064 > 17,520 — so SARIMA is capped at every origin,
   with no exceptions)

sarima_train_start_effective:
  first origin (2023-01-01): 2021-01-01  (window = 2021-01-01 .. 2022-12-31)
  last  origin (2023-12-30): 2021-12-30  (window = 2021-12-30 .. 2023-12-29)
```

**SARIMA's actual training window never overlaps with the year 2020 at any of the 362 origins.**
Its earliest possible start (at the very first evaluation origin) is already 2021-01-01, and it
slides forward continuously through the evaluation year, ending in December 2023 data by the
final origin — i.e. by the second half of 2023, roughly a third of SARIMA's own training window
is itself drawn from the 2023 evaluation year (pre-origin, so no leakage — but it is not
"2020–2022" data).

## Contrast with Table 1 ("Training (2020–2022)", $n=25{,}630$)

A literal calendar window of 2020-01-01 00:00 to 2023-01-01 00:00 (i.e. "2020, 2021, 2022")
contains 26,304 nominal hourly slots. Table 1 reports $n=25{,}630$ valid observations for that
row, i.e. 674 missing hours (~2.6%) — a plausible completeness rate for a genuine fixed
2020–2022 calendar window. This is consistent with Table 1's "Training: 2020–2022" column being
computed over an actual, literal, fixed 2020-01-01–2022-12-31 window used **only for the
descriptive statistics in Table 1** (mean, SD, P95, and the $\rho_1=0.957$ figure quoted in
§2.1) — a window that is **disjoint from and not representative of** either model's actual
per-origin training window as verified above (XGBoost: 2019-01-01 onward, expanding, always
≥35,064 rows; SARIMA: a sliding 2-year window that starts no earlier than 2021-01-01).

## ρ1 recalculation on the models' real windows — BLOCKED, not verifiable locally

The task requests recomputing $\rho_1$ (lag-1 autocorrelation) over (a) the real training window
at the first evaluation origin, and (b) the real training window at the last evaluation origin,
to show the true range against the "2020–2022" label.

**This numeric recomputation cannot be performed in this session.** It requires the raw hourly
Madrid \PMten{} series (`data_processed/madrid_pm10_meteorology_experiment_base.csv` or an
equivalent raw source), which — as already established in the forensic-gate audit — is **absent**
from this clone (`data_processed/` contains only `.gitkeep`) and from the one other local copy of
this project (`imports/2026-08-01/.../P1_PM10_Meteorology_Hstar-audit/data_processed/`, same
`.gitkeep`-only state). No other PM10 time series for Madrid exists anywhere in this authorized
repository (`data_raw/rvvcca/` is Elche PM10 data, an unrelated station used by a different
project, and was not touched).

```
RHO1_FIRST_ORIGIN_WINDOW (2021-01-01 .. 2022-12-31, if computed) = NOT_VERIFIABLE_LOCALLY (raw data absent)
RHO1_LAST_ORIGIN_WINDOW  (2019-01-01 .. 2023-12-29, if computed) = NOT_VERIFIABLE_LOCALLY (raw data absent)
```

What **is** established with certainty, independent of the missing raw series, is that neither of
these two windows is "2020–2022": the first-origin SARIMA-equivalent window (2021–2022) starts a
year after the labelled period begins, and the last-origin XGBoost window (2019 through most of
2023) spans five years, not three, and is not centered on 2020–2022 at all. Whatever the true
$\rho_1$ values are on these windows, they are $\rho_1$ values for **different, non-overlapping
periods** than the one named in the manuscript, and neither matches the $n=25{,}630$ / 2020–2022
window Table 1 actually reports. This is sufficient to establish the discrepancy the editorial
correction needs to address, even without the exact recomputed $\rho_1$ figures.

## Summary for editorial use

```
Manuscript text:        "training period (2020--2022)" (Section 2.1, Table 1 caption)
XGBoost actual window:   2019-01-01 -> t-1, expanding (35,064 to 43,776 rows across the 362
                          origins) -- never bounded at 2022, always includes part of 2023 for
                          origins after 2023-01-01
SARIMA actual window:    sliding 2-year (17,520-row) window ending at t-1 -- earliest possible
                          start 2021-01-01, latest possible start 2021-12-30; never includes 2020
Table 1 descriptive n:   consistent with a literal, separate, fixed 2020-01-01--2022-12-31 window
                          (26,304 nominal hours, 25,630 valid -> 97.4% complete) used ONLY for
                          descriptive statistics, not for either model's actual training data
```

See `window_size_by_origin.csv` for the full per-origin table (362 rows: origin date, XGBoost
effective train-end and nominal row count, SARIMA effective train-start and capped-row count).
