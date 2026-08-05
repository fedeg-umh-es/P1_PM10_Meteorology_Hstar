# Phase 1 — Real meteorological covariate count (Madrid, `lags_meteo`)

**Scope:** P1 only. Read-only verification; no retraining, no feature/hyperparameter changes.

## Config actually tied to the tracked `predictions_all_models.csv`

Two config copies were checked and are byte-identical in their `meteo_features` field:

- `code/e2_met_madrid_config.json` (live config)
- `results/e2_met_madrid_pm10/config_snapshot.json` (frozen snapshot written alongside the tracked Madrid bundle — this is the authoritative record of what actually produced `predictions_all_models.csv`, since it is a run-time snapshot rather than a possibly-since-edited source file)

```
meteo_features = ["temp_c", "humidity_pct", "pressure_hpa", "wind_speed_ms",
                   "wind_dir_deg", "solar_rad_wm2", "precip_mm"]
```

```
METEO_FEATURES_DECLARED = 7
```

An identical check against the imported historical copy
(`imports/2026-08-01/.../P1_PM10_Meteorology_Hstar-audit/results/e2_met_madrid_pm10/run_metadata.json`)
is byte-for-byte identical to the current one — no alternate/older Madrid config with 9 meteo
features exists anywhere reachable in this workspace.

## Column-presence filter in the actual code path

`code/e2_met_madrid_shared.py:get_condition_feature_columns()`:

```python
meteo_cols = [col for col in config["meteo_features"] if col in df.columns]
...
if condition == "lags_meteo":
    return lag_cols + calendar_cols + meteo_cols
```

This filter can only **remove** columns from the declared list (if a declared name is absent from
the dataframe at runtime); it never adds columns beyond `config["meteo_features"]`. Therefore:

```
METEO_FEATURES_ACTUALLY_USED <= 7   (upper bound, by construction of the filter)
```

## Why the exact used-count and per-column coverage cannot be pinned down further

The dataframe this filter actually ran against —
`data_processed/madrid_pm10_meteorology_experiment_base.csv` — is **not present** in this clone
(`data_processed/` contains only `.gitkeep`; confirmed again in this session). It is also absent
from the imported historical snapshot
(`imports/2026-08-01/.../P1_PM10_Meteorology_Hstar-audit/data_processed/` — same `.gitkeep` only).
No column-presence log, feature-importance dump, or persisted design matrix exists anywhere in
this repository for the Madrid run. Consequently:

- **Whether all 7 declared columns existed in `df.columns` at runtime** cannot be verified directly.
- **Per-column NaN coverage** cannot be verified directly.
- **Whether XGBoost's `.fit()` actually received all 7** (as opposed to fewer, if some were filtered
  out silently) cannot be verified directly from the feature-selection step alone.

## Indirect behavioural evidence (bound, not proof, of nonzero usage)

Using the tracked `predictions_all_models.csv` (Madrid, xgboost_direct, `lags_only` vs `lags_meteo`),
every one of the 24 evaluated horizons shows a strictly nonzero maximum absolute prediction
difference between conditions (range: 7.6–62.3 depending on horizon; see the forensic-gate audit's
`identical_prediction_checks.csv` for the full table). A feature set that was entirely absent or
100%-constant at runtime would leave XGBoost's tree splits — and therefore its predictions —
numerically unchanged relative to `lags_only`. This is consistent with **at least a nontrivial
subset** of the 7 declared columns having been genuinely present, non-constant, and used by the
fitted trees. It does **not** establish that all 7 were used, nor rule out that some subset (e.g.
5 of 7) drove the entire effect while the rest were silently dropped or constant.

## Result

```
METEO_FEATURES_DECLARED       = 7
METEO_FEATURES_ACTUALLY_USED  = UNKNOWN_NOT_VERIFIABLE_LOCALLY (upper-bounded by 7; raw
                                 Madrid dataset absent from every copy of this workspace,
                                 so column-presence and per-column coverage cannot be
                                 checked directly)
METEO_FEATURES_LIST (declared) = ["temp_c", "humidity_pct", "pressure_hpa", "wind_speed_ms",
                                   "wind_dir_deg", "solar_rad_wm2", "precip_mm"]
```

## Manuscript cross-check

`manuscripts/manuscript_main.tex`, "XGBoost — lags + meteorology" paragraph, states: *"nine
concurrent meteorological covariates measured at forecast origin $t$ are added."* This is **not**
what the config that generated the tracked Madrid predictions declares (7, not 9), and the Madrid
list of variable names (`temp_c`, `humidity_pct`, `pressure_hpa`, `wind_speed_ms`, `wind_dir_deg`,
`solar_rad_wm2`, `precip_mm`) does not match the 9-item Irish list named in the Data section
(`rain, temp, wetb, dewpt, vappr, rhum, msl, wdsp, wddir`). The Data section's Madrid paragraph in
fact describes the *Irish* 9-variable list under the "Madrid" heading — i.e. the manuscript's
Section 2.1 (Madrid) meteorological variable list appears to have been copied from the Ireland
config rather than describing Madrid's actual 7-variable config. This is a text/config mismatch on
the paper's own dataset description, independent of and additional to the "nine" count in the
Methods section. No code or data was changed to produce this finding; it is a direct read of
`config_snapshot.json` against `manuscript_main.tex`.
