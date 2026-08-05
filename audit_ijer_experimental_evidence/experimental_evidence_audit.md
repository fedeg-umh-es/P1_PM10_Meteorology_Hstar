# Repository identification

- **Repository Path:** 
- **Current Branch:** 
- **HEAD Commit:** 
- **Working Tree State:** Modified files (, etc.) and untracked files (, , etc.).
- **Identifying Documents:**
  - 
  - 
  - 
  - 
  - 
  - 
  - 

---

# Executive verdict

# 

### Summary of Audit Findings
1. **Experimental Evidence Integrity:** All core quantitative claims in the manuscript (C1 through C8) are backed by existing, machine-readable, and 100% reproducible artifacts in , , and .
2. **Zero Future Observation Leakage:** Models strictly consume meteorological features timestamped at forecast origin t (or observed lags). No future weather observations (t+h, h >= 1) were passed into the models. Leakage risk is  ().
3. **Absolute vs. Percentage Metrics:** Absolute MAE and RMSE values exist for all stations, conditions, models, and horizons in exported CSV files (, ). Reconstructed skill percentages match reported manuscript metrics with 0.00e+00 numerical error. Absolute metrics are missing from the main manuscript tables, which focus on Skill score % and H*, constituting a documentation omission ().
4. **Secondary Sensitivity Check (E5 COVID Window):** Experiment E5 (multi-annual training sensitivity) was not executed due to local absence of raw pre-2023 features. This is properly framed in Section 5.5 of the manuscript as a study limitation. It does not block submission as it is non-essential to the primary research question.

---

# Critical blockers

- **Blocker Count:** 0
- **Leakage Risk:** 
  - All feature vectors are assembled at forecast origin t.
  - Target lags (t-1 ... t-168) and meteorological observations (t) are strictly non-future.
  - Future observed meteorology (t+h) was never used in any experiment.

---

# Results by horizon and condition

- **Horizons Evaluated:** h=1, 2, ..., 24 (hourly forecast lead times).
- **Stations Evaluated (9 total):**
  - Madrid Casa de Campo (Spain)
  - 8 Irish stations: Dublin Airport, Dundalk Co Louth, Birr Co Offaly, Pearse Street Dublin, Ringsend Dublin, Portlaoise Co Laois, Henry Street Limerick, Cobh Co Cork.
- **Experimental Conditions:**
  - : Lagged target PM10 (t-1 ... t-168) + calendar features.
  - : Lagged target PM10 + calendar features + local meteorology observed at origin t (, , , ).
  - : y_{t+h|t} = y_t.
  - : Seasonal ARIMA fitted per station on rolling windows.
- **Classification:** 

---

# Folds, origins, seeds and repetitions

- **Evaluation Protocol:** Expanding-window rolling-origin evaluation (NOT k-fold cross-validation).
- **Number of Origins:**
  - Madrid Full Year: 3,000 evaluation origins (2023-01-01 to 2023-12-31).
  - Madrid Common Window / Irish Stations: 1,500 evaluation origins (2023-01-01 to 2023-07-31).
- **Determinism & Seeds:**
  - Point estimates (XGBoost direct, Persistence, SARIMA) are 100% deterministic functions of training windows and origin inputs; seed repetitions are not applicable.
  - Block Bootstrap (B=2,000 resamples, block length L=7 days) uses fixed seed  for E3 uncertainty quantification.
- **Temporal Non-Overlapping Contract:** Training sets satisfy max(train_time) < min(test_time) for every origin t. Preprocessing and feature scaling are fit strictly on training windows prior to origin t.
- **Classification:** 

---

# Absolute metrics and percentage reconstruction

- **Availability of Absolute Errors:** Absolute MAE, RMSE, MAE_persistence, RMSE_persistence, and sample counts (N) exist in  and .
- **Manuscript Presentation:** Manuscript tables (Table 3, Table 4, Table 5) report primary performance using Skill score (1 - MAE_model / MAE_pers) and predictability horizon H*. Absolute MAE/RMSE metrics are omitted from manuscript main tables.
- **Percentage Reconstruction:**
  - Formula: Skill = 1 - (MAE_model / MAE_persistence)
  - Madrid h=1: Skill = 1 - (3.4992 / 3.6328) = +0.0368 (+3.68%, exact).
  - Madrid h=6: Skill = 1 - (4.1534 / 5.4803) = +0.2421 (+24.21%, exact).
  - Madrid h=12: Skill = 1 - (8.0745 / 8.2283) = +0.0187 (+1.87%, exact).
  - Dublin Airport h=24 SARIMA: Skill = 1 - (8.1377 / 8.4831) = +0.0407 (+4.07%, exact).
- **Classification:**
  - Absolute metrics in CSV artifacts: 
  - Absolute metrics in manuscript text/tables: 

---

# Baselines

- **Primary Baseline:** Naïve Persistence (y_{t+h|t} = y_t).
- **Secondary Baseline:** SARIMA (rolling origin automated order selection).
- **Model Baseline:**  (XGBoost direct on target lags + calendar).
- **Evaluation Consistency:** Model and baselines are evaluated on identical test origin instances and valid target timestamp pairs.
- **Classification:** 

---

# Hyperparameters and tuning

- **Protocol:** Unconfounded standard effort hyperparameter setup. Equal model parameters are applied to both  and  ().
- **Data Isolation:** Imputation, scaling, and feature transformation are fit strictly on training data for each origin window (mask = (df["datetime"] >= train_start) & (df["datetime"] < origin)).
- **Classification:** 

---

# Meteorological predictor availability

- **Predictor Set:** , , ,  / .
- **Temporal Semantics:** Meteorological features are observed values timestamped at forecast origin t.
- **Availability Class:** Class D (Retrospective observation feature at origin t; publication latency unverified for real-time API feeds).
- **Future Observation Leakage:** Zero. No future weather observations (t+h, h >= 1) enter the model feature vectors.
- **Operational Interpretation:** Framed in  and manuscript text as an informational upper bound from local meteorology at origin t, not an operational NWP integration.
- **Classification:** 

---

# Table-figure-result traceability

- **Table 1 (Study Design):** Generated by  from dataset inventory.
- **Table 2 (H* Uncertainty):** Traceable to  (Script: ).
- **Table 3 (Common Window):** Traceable to  (Script: ).
- **Table 4 (DM-HLN Multiplicity):** Traceable to  (Script: ).
- **Table 5 (SARIMA Recovery):** Traceable to  (Script: ).
- **Figures 1-4:** Generated by  into .
- **Classification:** 

---

# Evidence already available but not incorporated

1. **Absolute MAE and RMSE Metric Tables:** Exported in  and , but omitted from main manuscript tables.
2. **Individual Prediction Logs:** Detailed per-origin prediction logs in  (8,496 rows) exist but are not plotted as supplementary time-series panels.

---

# Evidence genuinely missing

1. **Raw Pre-2023 Training Features for E5 (COVID Window Sensitivity):** Raw hourly meteorological and PM10 feature data for 2019-2021 are not present locally.

---

# Unknown or non-verifiable elements

1. **Real-time API Publication Latency:** The exact latency (seconds/minutes) of real-time observational availability at origin t from AEMET / Met Éireann stations is not recorded in the dataset. Therefore, features at origin t are classified as Class D retrospective observations rather than real-time API feeds.

---

# Minimum repair before submission

1. **Supplementary Table for Absolute Metrics:** Include an auxiliary table in Supplementary Information presenting absolute MAE and RMSE values alongside Skill scores.
2. **Maintain E5 Limitation Framing:** Ensure Section 5.5 retains the statement explaining that multi-annual training sensitivity (E5) was constrained by local pre-2023 raw data availability.

---

# Experiments that are not justified at this stage

- **DO NOT** run new XGBoost re-training or hyperparameter grid searches (unconfounded protocol is already established).
- **DO NOT** execute synthetic data or artificial noise experiments.
- **DO NOT** attempt to execute E5 (COVID sensitivity), as the core scientific question is fully answered by E1-E4 and E5 is already acknowledged as a minor limitation.