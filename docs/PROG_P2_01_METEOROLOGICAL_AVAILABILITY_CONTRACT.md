# PROG-P2-01 — Meteorological availability contract

**Status:** completed as a methodological contract
**Date:** 2026-07-28
**Project:** P2 — Operational Meteorology
**Repository:** `fedeg-umh-es/P1_PM10_Meteorology_Hstar`

## 1. Purpose

This contract defines which information may legally enter each forecast at rolling origin `t` and prevents retrospective meteorological observations from being interpreted as operationally available predictors without evidence.

The contract applies to the Madrid and Ireland E2-MET experiments.

## 2. Forecast issue-time convention

For the existing code, the rolling origin `t` is the first timestamp of the test window.

- Training data contain rows with timestamp strictly earlier than `t`.
- The target forecast is evaluated at `t+h`, for `h=1..24`.
- The feature vector used by XGBoost is constructed at timestamp `t`.
- The current implementation appends the first row of the test window to the training context and reads its calendar and meteorological fields.

Therefore, the current `lags_meteo` condition uses **meteorological observations timestamped at `t`**, not meteorological forecasts for `t+h`.

## 3. Availability classes

Every predictor must be assigned to one of these classes.

| Class | Meaning | Permitted in an operational forecast issued at `t`? |
|---|---|---|
| A | Deterministic calendar information known in advance | Yes |
| B | Target or meteorological observation with timestamp `< t` | Yes |
| C | Observation timestamped exactly at `t`, with verified publication before issue time | Yes, only with latency evidence |
| D | Observation timestamped exactly at `t`, but publication latency unknown | No operational claim; hindcast only |
| E | Numerical weather prediction or other forecast genuinely issued before or at `t` | Yes, with issue-time/version provenance |
| F | Observation or analysis timestamped after `t` | No; future leakage |

## 4. Predictor-level contract

### PM10 autoregressive predictors

| Predictor | Current construction | Class | Decision |
|---|---|---|---|
| `PM10_lag_1` | PM10 at `t-1` | B | Allowed |
| `PM10_lag_2` | PM10 at `t-2` | B | Allowed |
| `PM10_lag_3` | PM10 at `t-3` | B | Allowed |
| `PM10_lag_6` | PM10 at `t-6` | B | Allowed |
| `PM10_lag_12` | PM10 at `t-12` | B | Allowed |
| `PM10_lag_24` | PM10 at `t-24` | B | Allowed |
| `PM10_lag_48` | PM10 at `t-48` | B | Allowed |
| `PM10_lag_168` | PM10 at `t-168` | B | Allowed |

The lag generator applies shifts to the time-ordered target history. The origin-row target itself is not included as an unlagged predictor.

### Calendar predictors

| Predictor | Class | Decision |
|---|---|---|
| `hour_of_day` | A | Allowed |
| `day_of_week` | A | Allowed |
| `month` | A | Allowed |
| `julian_day` | A | Allowed |

### Madrid meteorological predictors

| Predictor | Current timestamp | Current class | Operational decision |
|---|---|---|---|
| `temp_c` | `t` | D | Hindcast-only until latency is verified |
| `humidity_pct` | `t` | D | Hindcast-only until latency is verified |
| `pressure_hpa` | `t` | D | Hindcast-only until latency is verified |
| `wind_speed_ms` | `t` | D | Hindcast-only until latency is verified |
| `wind_dir_deg` | `t` | D | Hindcast-only until latency is verified |
| `solar_rad_wm2` | `t` | D | Hindcast-only until latency is verified |
| `precip_mm` | `t` | D | Hindcast-only until latency is verified |

### Ireland meteorological predictors

The Ireland runner reuses the same feature-building function and likewise supplies the first row of the test window as the origin feature row. Consequently, all meteorological variables used by the Ireland configuration are also class D unless their source-specific publication latency is documented.

## 5. Current implementation audit

The relevant implementation path is:

1. `get_train_window()` selects timestamps `< t`.
2. `get_test_window()` starts at timestamp `t`.
3. `run_backtest()` passes `test_df.iloc[:1]` as `origin_row_df`.
4. `predict_xgboost_direct()` concatenates that row with the training data.
5. `build_origin_feature_row()` selects the row timestamped exactly at `t` and reads the configured meteorological columns directly.

This design does **not** read meteorological observations at `t+1 ... t+24`. It therefore avoids direct future-horizon leakage.

However, it assumes that observations timestamped at `t` were available when the forecast was issued. The repository currently contains no source-level latency, ingestion-time or release-time evidence establishing that assumption.

## 6. Compliance verdict

**Conditionally compliant.**

- **Compliant as a retrospective/hindcast comparison** of whether contemporaneous meteorological state at the origin adds information beyond PM10 lags.
- **Not yet compliant as a real-time operational forecasting experiment**, because availability of the `t` meteorological observations has not been demonstrated.

## 7. Fatal issues

For a manuscript claim of real-time operational forecasting, the following blocks credibility:

1. No explicit forecast issue time within the hour.
2. No documented publication or ingestion latency for Madrid meteorological observations.
3. No documented publication or ingestion latency for Ireland meteorological observations.
4. No recorded `available_at` or `issued_at` field in the modelling dataset or prediction artefacts.
5. The label `lags_meteo` does not distinguish contemporaneous observations from lagged observations or weather forecasts.

These are not fatal for a clearly labelled retrospective hindcast study.

## 8. Softer issues

1. Forward-filling PM10 before lag construction may bridge missing intervals; this needs a gap-aware audit in PROG-P2-02.
2. Meteorological missing values are replaced with medians fitted on the training fold, which is leakage-safe but should be reported.
3. The same meteorological origin vector is used for all horizons `h=1..24`; the experiment does not test horizon-specific weather forecasts.
4. Source timestamps may represent interval start, interval end or aggregation label; this has not been documented.
5. Time-zone and daylight-saving treatment require explicit verification.

## 9. Minimum viable repair

The smallest defensible repair is to preserve the existing experiment but narrow its interpretation:

1. Rename the scientific condition conceptually as `origin_observed_meteo`, while retaining `lags_meteo` as a historical artefact identifier if changing outputs would break traceability.
2. Describe the study as a **retrospective rolling-origin hindcast using meteorological state observed at the forecast origin**.
3. Prohibit claims that the experiment uses future weather forecasts or proves deployable real-time gains.
4. Add source-specific latency evidence before upgrading class D predictors to class C.
5. In PROG-P2-02, mechanically verify that no meteorological timestamp later than `origin` enters any feature vector.

A stricter real-time arm would require either:

- meteorological observations timestamped strictly before `t`; or
- archived weather forecasts with `issued_at <= t` and valid times covering `t+1 ... t+24`.

That would be a distinct experiment and must not replace the current frozen evidence silently.

## 10. Manuscript wording guard

### Allowed now

- “Meteorological state observed at the forecast origin was added to lag and calendar predictors.”
- “The analysis is a retrospective rolling-origin hindcast.”
- “No meteorological observations beyond the forecast origin were used.”
- “Operational deployability depends on source-specific data latency.”

### Not allowed now

- “All predictors were available in real time.”
- “The model uses operational weather forecasts.”
- “The reported gain demonstrates deployable forecasting improvement.”
- “The protocol is fully leakage-free” without the pending timestamp and gap audit.

## 11. Required evidence to upgrade the contract

For each data source and variable, record:

- observation timestamp semantics;
- timezone;
- aggregation interval;
- nominal publication time;
- worst-case publication latency;
- actual ingestion timestamp, if available;
- revisions or quality-control delay;
- whether the value was known before forecast issuance.

Without these fields, contemporaneous meteorology remains class D.

## 12. Next task

**PROG-P2-02 — Audit leakage and rolling-origin protocol.**

The audit must test the implementation mechanically, with particular attention to timestamp alignment, forward-filled PM10 lags, origin-row meteorology, train-only preprocessing, shared origins and prediction-level provenance.