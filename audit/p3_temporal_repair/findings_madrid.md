# Madrid timestamp-safe full regeneration

- Dataset SHA-256: `a2f1cb25cfd5c4bb698a8ddd8a88bdd3dba6e851df96998e6711d52485230718`.
- Candidate/valid/evaluated origins: 212 / 185 / 185.
- Prediction rows: 17,760; all target leads equal nominal clock hours.
- Both XGBoost conditions share all 4,440 origin-horizon keys and identical y_true.
- No duplicate prediction keys; horizons 1--24 and frozen models are complete.
- H_strict_max_run: lags-only 10 (h=15--24); lags+meteo 21 (h=4--24); Delta=+11.
- H_strict_from_h1: 0 / 0. H_relax: 24 / 24.
- Bootstrap historical contract reproduced: origins, block=7, B=2000, seed=20260802, paired dependence, percentile CI.

The temporal pipeline passes, but the headline +8 h and dependent numerical claims change materially.

TEMPORAL_REPAIR_PASS_RESULTS_CHANGED
