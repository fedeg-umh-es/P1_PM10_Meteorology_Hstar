# SERRA — PM10 forecast-horizon evidence

This repository contains the versioned analysis code and documentary evidence
associated with the SERRA manuscript below.  The repository name and historical
P2 programme labels are retained for provenance; they do not define a separate
manuscript.

## Associated manuscript

**When descriptive forecast-horizon gains do not imply global evidence of
incremental meteorological predictability: a multi-site PM10 study**

- **Target journal:** *Stochastic Environmental Research and Risk Assessment*
- **Manuscript author:** Federico García Crespí
- **Manuscript source:** `manuscripts/serra_manuscript.tex`
- **Manuscript PDF:** `manuscripts/serra_manuscript.pdf`

Historical manuscript and cover-letter files under `manuscripts/` are retained
for repository provenance and are not the current SERRA submission materials.

## Study design

The study evaluates hourly PM10 forecasting at Madrid Casa de Campo and eight
Irish stations over January--July 2023.  It uses an expanding-window,
rolling-origin evaluation with forecast origins spaced by 24 h and physical
horizons $h=1,\ldots,24$.

The comparison includes persistence and SARIMA reference models, plus direct
multi-horizon XGBoost models using either pollutant lags alone or pollutant lags
augmented with meteorological observations available at the forecast origin.
The meteorological covariates are an observational information set, not future
numerical-weather-prediction forecasts.  Irish meteorological covariates use the
nearest mapped EPA synoptic station documented for each monitoring site.

## Frozen results

- **Madrid:** $H^*_{\mathrm{strict}}$ increases from 9 to 17 h (+8 h); the
  relaxed descriptor increases from 15 to 17 h (+2 h).
- **Ireland:** mean strict $H^*$ increases from 21.875 to 22.875 h
  (+1.000 h); five of eight lags-only stations reach the 24-h boundary; eleven
  station/condition cases reach $H^*_{\mathrm{strict}}=24$; Henry Street
  Limerick changes from 17 to 24 h (+7 h).
- **Inference:** 36 planned site--horizon comparisons are assessed.  Under
  $q_{\mathrm{overlap}}=0$, global Bonferroni yields 0/36 significant tests.
  The fixed automatic Newey--West sensitivity also yields 0/36.  Limited
  station-wise Benjamini--Hochberg signals remain local sensitivity evidence,
  not the primary multi-site conclusion.

The manuscript treats $H^*$ as descriptive, treats values at 24 h as
right-censored by $H_{\max}=24$ where appropriate, and distinguishes failure to
reject from equivalence.  Descriptive horizon extension is therefore kept
separate from family-wise global attribution of incremental meteorological
predictability.

## Repository evidence

The final SERRA evidence mirrored here includes:

- `outputs/tables/serra_table_t2_dm_q0.tex` — primary overlap-based DM-HLN table;
- `outputs/tables/serra_table_t3_dm_auto_nw.tex` — fixed automatic Newey--West
  sensitivity table;
- `outputs/figures/serra_fig1_madrid_skill_curves.png`;
- `outputs/figures/serra_fig2_ireland_skill_by_station.png`;
- `manuscripts/serra_manuscript.tex` and `manuscripts/serra_manuscript.pdf`.

The repository also retains versioned analysis code, processed/generated study
artifacts, figure-generation support, and run metadata.  The Irish station
evaluations were regenerated from recovered source datasets using the versioned
analysis pipeline.  The row-level predictions from the originally executed
Irish computational run were not retained; therefore, the reported Irish
results correspond to the documented regeneration rather than recovery of the
original prediction files.

## Data and reproducibility

Raw source observations are not tracked in this repository.  Madrid air-quality
and meteorological observations are available from the Madrid City Council open
data portal; Irish air-quality and meteorological observations are available
from the Irish Environmental Protection Agency.  Processed and regenerated
study artifacts are versioned only where indicated by the repository manifests
and result directories.

The final inferential tables and manuscript materials listed above are the
documentary evidence associated with the current SERRA paper.  No claim is made
that the original Irish row-level prediction files are available.

## Historical materials

Earlier P2/E2-MET manuscripts, figures, and reports remain in their historical
locations for provenance.  They are not the current SERRA manuscript and should
not be used to infer the frozen results above.

## License

See `LICENSE`.
