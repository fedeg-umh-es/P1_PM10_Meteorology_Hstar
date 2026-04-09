# E2-MET Canonical Protocol — Madrid PM10

## Canonical protocol (frozen)

This file freezes the canonical execution protocol for the E2-MET experiment in this repository.

- Domain: Madrid PM10
- Site: station 24, Casa de Campo
- Dataset: `data_processed/madrid_pm10_meteorology_experiment_base.csv`
- Forecast horizon: `h = 1..24`
- Rolling-origin test period: calendar year 2023
- Rolling-origin stride: `24` hours
- Training regime: expanding rolling-origin windows from `2019-01-01 00:00:00` with minimum training rows `8760`
- Primary baseline: persistence
- Secondary baseline: SARIMA
- Main ML model: XGBoost-direct
- Current SARIMA execution specification in repo: `(1,0,1)(1,0,0,24)`
- Random seed: `42`

## Scientific interpretation rules

- The canonical manuscript-facing comparison is Madrid, not Elche.
- The canonical operational horizon for this experiment is `h=1..24`, not `h=1..7`.
- Persistence remains the primary baseline for the main H* framing.
- SARIMA is the required stronger secondary baseline for protocol completeness.
- DM-HLN outputs must be interpreted only from the full run, never from smoke-run validation outputs.
- Smoke-run outputs are pipeline-validation artifacts and must not be used as manuscript evidence.

## Purpose

This protocol freeze is intended to prevent drift between the repo scaffold, the manuscript framing, the reported baselines, the forecast horizon, and the inferential interpretation.
