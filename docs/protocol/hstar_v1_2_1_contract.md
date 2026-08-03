# H* Methodological Contract v1.2.1

Formalizes, as three separately named and separately reported metrics, the
useful-forecast-horizon diagnostics computed on top of the E2-MET canonical
protocol (`CANONICAL_PROTOCOL.md`). Implemented in `code/hstar_metrics.py`
and orchestrated by `code/export_results_summary_v1_2_1.py`. Read-only:
neither module re-runs, re-fits, or re-seeds persistence, SARIMA, or
XGBoost -- both consume the already-persisted `predictions_all_models.csv`
/ `metrics_all_models.csv` / `dm_lags_meteo_vs_lags_only.csv` artifacts.

## Why three variants, formally separated

`manuscripts/manuscript_main.tex:356-361` defines `H*_strict` in prose as a
positive-skill run *beginning at h=1*. The codebase's own, unchanged
`derive_hstar_from_metrics()` / `derive_hstar_ireland()` functions have
always computed the longest positive-skill run *anywhere* in `h=1..24`
instead, and the manuscript's own published tables match that
"anywhere" computation, not its prose --
see `results/e2_met_ireland_pm10_regenerated/hstar_definition_discrepancy.md`
for the full audit trail (Dublin Airport and Edenderry diverge between the
two readings).

Rather than silently picking one reading or re-litigating which one the
manuscript "really" meant, v1.2.1 keeps both, under explicit, non-ambiguous
names, plus the pre-existing last-passage variant:

| v1.2.1 name | Definition | Prior code name (kept, unchanged) |
|---|---|---|
| `Hstar_strict_from_h1` | Length of the contiguous positive-skill run starting at `h=1`. The first horizon with `S(h) <= 0` (or missing) ends the streak. | Not previously a named summary column; ad hoc in the Ireland regeneration's `hstar_summary_both_definitions.csv`. |
| `Hstar_strict_max_run` | Longest contiguous positive-skill run located anywhere in `h=1..H_max`. | `H_star_strict` / `H_strict_max_run` (manuscript-matching). |
| `Hstar_relax` | Last horizon `h` with `S(h) > 0` (last-passage time); intermediate failures and recoveries are allowed. | `H_star_relax` / `H_relax`. |

All three are computed from the same skill curve `S(h) = 1 -
RMSE_m(h)/RMSE_persistence(h)` (identical to the manuscript's Eq. for
`S_m(h)`), with a missing/NaN horizon treated as a skill failure, matching
the pre-existing pipelines' convention.

`code/hstar_metrics.py`'s `derive_hstar_v1_2_1_table()` reproduces
`hstar_summary_both_definitions.csv` and the legacy
`results/e2_met_madrid_pm10/metrics/hstar_summary.csv` exactly (regression
tests: `tests/test_hstar_metrics_v1_2_1.py`).

## Administrative ceiling censoring at H_max = 24

Every variant carries a paired `ceiling_constrained_<variant>` boolean,
`True` iff the computed H* equals `H_max` (24). A ceiling-constrained value
is administratively censored, not an estimate of a true, uncensored useful
horizon: the run (or the last-passage time) may extend past the evaluated
horizon range, and the reported value is a lower bound, not a point
estimate. This matters most for `Delta H*` interpretation -- see
`tab:rho1` in the manuscript, where several Irish stations already reach
`H*_strict = 24` under `lags_only`, mechanically constraining
`Delta H*` to `0` regardless of the true meteorology benefit.

`results_summary_v1.2.1.csv` additionally reports a single consolidated
`ceiling_flag` column matching the manuscript's own `tab:rho1` "Ceiling"
column semantics: `True` iff `ceiling_constrained_strict_max_run_lags_only`
is `True` (the `lags_only` model already saturates `Hstar_strict_max_run`,
so meteorology has no ceiling room left to add skill under that variant).

## Loss matrices L_model(d, f, h) / L_baseline(d, f, h)

`compute_loss_matrix()` takes the row-level `predictions_all_models.csv`
(one row per station `d`, origin `f`, horizon `h`, condition, model) and
adds per-row `loss_squared_error` / `loss_absolute_error` columns, without
aggregating or dropping any row. Rows with `model == "persistence"` are
`L_baseline(d, f, h)`; every other row is `L_model(d, f, h)`. This is
persisted per dataset as `metrics/loss_matrix_full.parquet` -- the primary,
fine-grained artifact backing every skill/H*/DM/bootstrap computation
downstream. Parquet was chosen over CSV for these specific files purely for
size (a wide, densely-typed CSV of the same content would roughly double
the tracked repository size for the Ireland panel); nothing about the
schema depends on the file format, and the loader (`compute_loss_matrix`,
called via `pandas.read_parquet`) round-trips identically to a CSV read.

## Delta H* and its 95% Moving-Block Bootstrap CI

`Delta H* = H*(lags_meteo) - H*(lags_only)` for the `xgboost_direct` model,
computed for all three variants. Row-level forecast errors at nearby
origins are serially dependent (rolling-origin forecasts share overlapping
target windows), so a naive i.i.d. bootstrap over origins would
underestimate variance. `moving_block_bootstrap_delta_hstar()` instead:

1. Builds three aligned `origin x horizon` pivot tables of squared error
   (`lags_only`, `lags_meteo`, `persistence`) for one station, restricted
   to origins common to all three.
2. Resamples *blocks* of consecutive origins (length `L`, default
   `L = round(n_origins^(1/3))`, floor 2 -- a standard block-length
   heuristic for block bootstrap; both `L` and `n_boot` are recorded per
   station in `bootstrap_delta_hstar_v1_2_1.csv` for full traceability) to
   fill a resampled origin sequence of the same length `n_origins`, with
   replacement across blocks.
3. Recomputes `RMSE(h)` for each of the three series from the resampled
   rows, then `S(h)`, then all three H* variants for `lags_only` and
   `lags_meteo`, then `Delta H*` -- all within the same replicate, so the
   `lags_meteo`/`lags_only` comparison stays paired.
4. Repeats for `n_boot` replicates (default 1000, fixed
   `random_state=42` for reproducibility of this analysis script only --
   independent of, and not a substitute for, the frozen XGBoost
   `random_state: 42` used at fit time) and reports the `[2.5, 97.5]`
   percentile interval.

The point estimate reported alongside the CI is computed the same way, on
the unresampled (identity) origin ordering, so it is internally consistent
with the bootstrap distribution rather than re-used from
`hstar_summary.csv`/`metrics_all_models.csv` (though it agrees with them by
construction, verified in the test suite).

## DM-HLN p-values at h in {1, 6, 12, 24}

Read verbatim from the pre-existing
`stats/dm_lags_meteo_vs_lags_only.csv` files (already computed at exactly
these four horizons per `dm_horizons` in
`code/e2_met_madrid_config.json` / `code/e2_met_ireland_config.json`, and
matching the manuscript's own stated horizons and DM-HLN methodology). Not
recomputed here, to avoid any risk of silently drifting from the frozen,
already-audited statistics.

## rho1 (lag-1 autocorrelation, training period)

`code/e2_autocorrelation_analysis.py` computes rho1 from
`data_processed/madrid_pm10_meteorology_experiment_base.csv` and
`data_processed/ireland_pm10_meteorology_hourly.csv`. Both files are
deliberately excluded from git tracking
(`reports/output_versioning_policy.md`) and were not present in the
environment this v1.2.1 audit pass ran in. `results_summary_v1.2.1.csv`
therefore sources rho1 from `results/rho1_reference_from_manuscript.csv`,
which is a verbatim transcription of the manuscript's own audited
`tab:rho1` (9 rows: Madrid + the 8 Irish stations, `source =
manuscript_tab_rho1`). Where the two raw processed CSVs are available
locally, re-run `code/e2_autocorrelation_analysis.py` (after removing its
hardcoded author-local absolute path) to regenerate rho1 directly from the
training-period series and treat that as the higher-provenance source.

## Reproducing this audit pass

```bash
python3 code/export_results_summary_v1_2_1.py --n-boot 1000
python3 -m pytest tests/test_hstar_metrics_v1_2_1.py -q
```

Outputs (none overwrite or delete any pre-existing artifact):

- `results/e2_met_madrid_pm10/metrics/loss_matrix_full.parquet`
- `results/e2_met_madrid_pm10/metrics/hstar_summary_v1_2_1.csv`
- `results/e2_met_madrid_pm10/stats/bootstrap_delta_hstar_v1_2_1.csv`
- `results/e2_met_ireland_pm10_regenerated/metrics/loss_matrix_full.parquet`
- `results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_v1_2_1.csv`
- `results/e2_met_ireland_pm10_regenerated/stats/bootstrap_delta_hstar_v1_2_1.csv`
- `results/results_summary_v1.2.1.csv` / `results/results_summary_v1.2.1.json`
