# DATA_MANIFEST.md — Data Provenance & Availability Manifest

**Repository:** `P3_Madrid_Ireland`  
**Date:** 2026-08-07 / 2026-08-08  
**Project:** Operational Meteorology ($H^*$ forecast horizon evaluation)  
**Status:** Audit & Editorial Package Closed  

---

## 1. Expected Pipeline Datasets

The computational pipeline defined in `RUN_ORDER.md` expects the following preprocessed time-series datasets:

1. `data_processed/madrid_pm10_meteorology_experiment_base.csv`
   - Hourly PM10 and 7 meteorological variables for Madrid (Casa de Campo station, 2019–2023).
2. `data_processed/ireland_pm10_meteorology_hourly.csv`
   - Hourly PM10 and 9 meteorological variables across 8 EPA stations in Ireland (2020–2023).

---

## 2. Local Dataset Availability

* **`data_processed/madrid_pm10_meteorology_experiment_base.csv`**: **ABSENT LOCALLY**
* **`data_processed/ireland_pm10_meteorology_hourly.csv`**: **ABSENT LOCALLY**

As explicitly documented in `README.md` and `RUN_ORDER.md`:
> *"Raw data and processed full datasets are not tracked in this repository."*

---

## 3. Preserved Frozen Prediction & Result Artifacts

Although raw feature matrices are not tracked to keep the repository lightweight, complete row-level predictions, metrics, and audit evidence are fully preserved and tracked:

* **Madrid (E2-MET) Results:**
  * `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`
  * `results/e2_met_madrid_pm10/metrics/hstar_summary.csv`
  * `results/e2_met_madrid_pm10/stats/dm_lags_meteo_vs_lags_only.csv`
  * `results/e2_met_madrid_pm10/manuscript_tables/`
* **Ireland (E2-MET) Results:**
  * `results/e2_met_ireland_pm10_regenerated/manuscript_tables/`
  * `results/e2_met_ireland_pm10_regenerated/output_hashes.csv`
  * `results/e2_met_ireland_pm10_regenerated/run_metadata.json`
* **Canonical Evidence & Closure Audit:**
  * `audit_ijer_experimental_evidence/claim_evidence_matrix.csv`
  * `audit_ijer_experimental_evidence/closure/` (Bartlett DM-HLN closure, common-window rho1)
  * `audit_ijer_experimental_evidence/final_send_decision/` (`absolute_metrics_final.csv`, `claim_evidence_final.csv`)
  * `outputs/metrics/predictions_meteorology_experiment.csv`
  * `outputs/tables/master_meteorology_diagnostic_table.csv`

---

## 4. Reproducibility & Regeneration Scope

### RESULT REPRODUCIBILITY (Fully Available)
The repository supports complete verification and re-computation of all manuscript claims, statistical tests, tables, figures, and confidence intervals from frozen predictions and metrics:
* Re-running Diebold-Mariano tests with Bartlett autocorrelation correction.
* Regenerating Tables 1–6 and Supplementary Tables.
* Rendering all manuscript figures (F1--F4).
* Bootstrapping H* confidence intervals.

### FULL PIPELINE REGENERATION (Requires External Datasets)
Re-running feature extraction and retraining XGBoost / SARIMA models from raw hourly timestamps requires acquiring the original public datasets.

---

## 5. Verified Data Acquisition Routes

* **Madrid Data:**
  * Source: Ayuntamiento de Madrid, Portal de Datos Abiertos (https://datos.madrid.es/portal/site/egob).
  * License: Creative Commons Attribution 4.0 (CC BY 4.0).
  * Coverage: Hourly PM10 (Station 24 Casa de Campo) & hourly meteorology (2019–2023).
* **Ireland Data:**
  * Source: Environmental Protection Agency Ireland (EPA Air Quality & Met Éireann) (https://www.epa.ie/our-services/monitoring--assessment/air/).
  * Coverage: Hourly PM10 and 9 meteorological parameters across 8 stations (2020–2023).
