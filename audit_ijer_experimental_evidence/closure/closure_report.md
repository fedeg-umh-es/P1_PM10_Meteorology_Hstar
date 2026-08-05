# Closure Report: P1 PM10 Meteorology Hstar Computational Closure

## HECHOS

### Context & Configuration
- **Repository**: `fedeg-umh-es/P1_PM10_Meteorology_Hstar`
- **Branch**: `codex/p1-editorial-computational-audit`
- **Base Commit**: `18d0f830b1b7bf92684d5443c7b544d571e2a3b5`
- **Remote**: `origin` (`https://github.com/fedeg-umh-es/P1_PM10_Meteorology_Hstar.git`)

### Canonical Inputs & Initial Hashes
1. `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv` — SHA256: `e4a7edd656385df4f160176f0952a410848dc456cd5842981f191124189ea85c`
2. `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv` — SHA256: `e8b262e0812da8c1243afcded5d621dcbed51d6dae56dc07a3fe9069c9484d8e`
3. `manuscripts/tables/ijer/table_4_dm_summary.tex`
4. `manuscripts/figures/ijer/figure_3_dm_heatmap.pdf`
5. `audit_ijer_experimental_evidence/computational_fixes/run_metadata_madrid_corrected.json` — SHA256: `a911e2fec49fbb11c1d09e5c54d3e4b47f078e63df85e5d36e2f1dbfc0305f88`
6. `audit_ijer_experimental_evidence/computational_fixes/artifact_hash_manifest.csv` — SHA256: `bf576d33ac6e1c8d76a74b39b56f8fbd6b185b31fa0eaed223b320d3f231e5f8`

### Detected Schema Mapping
- **Madrid**: `origin`, `forecast_timestamp`, `horizon`, `condition` (`reference`, `lags_only`, `lags_meteo`), `model` (`persistence`, `sarima`, `xgboost_direct`), `y_true`, `y_pred`.
- **Ireland**: `station`, `origin`, `forecast_timestamp`, `horizon`, `condition`, `model`, `y_true`, `y_pred`.

### Bloque 1 — Matriz DM-HLN Bartlett
- **Total planned comparisons**: 36
- **Status OK**: 36/36
- **Status UNDETERMINED**: 0
- **FDR Station survivors**: 3 (Birr h=1, Pearse Street h=6, Pearse Street h=12)
- **FDR Global survivors**: 0
- **Bonferroni Global survivors**: 0
- **Portlaoise h=24**: status=OK, `dm_hln_stat` = 0.9055, `p_raw` = 0.3662.

### Bloque 2 — Autocorrelación Lag-1 en Ventana Común
- **Nominal Window**: 2023-01-01 00:00:00 to 2023-07-31 23:00:00 (5088 nominal hours).
- **Minimum Coverage Threshold**: 0.90
- **Observed Coverages**:
  - Madrid: 0.9801 (4987/5088)
  - Birr (Co. Offaly): 0.9992 (5084/5088)
  - Dublin Airport: 0.6840 (3480/5088) — **BELOW THRESHOLD**
  - Dundalk (Co. Louth): 0.7148 (3637/5088) — **BELOW THRESHOLD**
  - Pearse Street (Dublin): 0.9998 (5087/5088)
  - Ringsend (Dublin): 0.9996 (5086/5088)
  - Edenderry (Co. Offaly): 0.9882 (5028/5088)
  - Henry Street (Limerick): 0.9927 (5051/5088)
  - Portlaoise (Co. Laois): 0.9998 (5087/5088)
- **Status**: `RHO1_BLOCKED_BY_INSUFFICIENT_RECONSTRUCTED_COVERAGE`
- **Output**: `results/ijer/bartlett_closure/rho1_common_window.csv` generated with coverages and empty `rho1` / `n_pairs`.

### Bloque 3 — Repositorio y Publicación
- Replaced `results/e2_met_madrid_pm10/run_metadata.json` with corrected version; saved original to `run_metadata.superseded.json`. Verified byte-for-byte identity.
- Created `results/ijer/artifact_hash_manifest.csv` with updated SHA-256 hashes.
- Ireland pipeline identified: `code/e2_met_ireland_run.py` & `code/merge_ireland_regenerated_shards.py` (commit `61cf2b6d1e883945049b8be135ed52fed432e465`).

### Tests Executed
- All 20 mandatory minimum tests executed and PASSED.

### Created & Modified Paths
- **Created**:
  - `results/ijer/bartlett_closure/dm_hln_bartlett_canonical.csv`
  - `results/ijer/bartlett_closure/rho1_common_window.csv`
  - `results/ijer/bartlett_closure/rho1_common_window_summary.md`
  - `results/ijer/bartlett_closure/multiplicity_contract.json`
  - `results/ijer/bartlett_closure/table_4_render_data.csv`
  - `results/ijer/bartlett_closure/figure_3_dm_heatmap_render_data.csv`
  - `results/ijer/bartlett_closure/superseded_rectangular/table_4_dm_summary_rectangular.tex`
  - `results/ijer/bartlett_closure/superseded_rectangular/figure_3_dm_heatmap_rectangular.pdf`
  - `results/ijer/artifact_hash_manifest.csv`
  - `audit_ijer_experimental_evidence/closure/input_schema_mapping.md`
  - `audit_ijer_experimental_evidence/closure/manuscript_numbers.md`
  - `audit_ijer_experimental_evidence/closure/closure_execution.log`
  - `audit_ijer_experimental_evidence/closure/closure_report.md`
  - `audit_ijer_experimental_evidence/closure/compute_dm_hln_bartlett_closure.py`
  - `audit_ijer_experimental_evidence/closure/compute_rho1_common_window.py`
  - `audit_ijer_experimental_evidence/closure/render_dm_table_figure.py`
  - `audit_ijer_experimental_evidence/closure/verify_dm_artifacts.py`
  - `audit_ijer_experimental_evidence/closure/update_artifact_hash_manifest.py`
  - `audit_ijer_experimental_evidence/closure/run_p1_computational_closure.py`
- **Modified**:
  - `manuscripts/tables/ijer/table_4_dm_summary.tex`
  - `manuscripts/figures/ijer/figure_3_dm_heatmap.pdf`
  - `results/e2_met_madrid_pm10/run_metadata.json`

## INFERENCIAS
1. Switch from rectangular to Bartlett kernel in DM-HLN tests increases long-run variance estimates for several station-horizon pairs, rendering previously significant comparisons non-significant under strict Bonferroni control.
2. In the reconstructed observed series from prediction files, Dublin Airport and Dundalk have valid observation coverages of 68.4% and 71.5% in the 2023-01 to 2023-07 window (due to missing origins/rows in raw evaluation files), preventing un-imputed lag-1 autocorrelation estimation under the 90% strict coverage contract.

## BLOQUEOS
- `RHO1_BLOCKED_BY_INSUFFICIENT_RECONSTRUCTED_COVERAGE`: Dublin Airport (68.4%) and Dundalk Co Louth (71.5%) have coverage < 0.90 in the reconstructed observed series. `rho1` computation for common window is blocked without external raw data imputations.
