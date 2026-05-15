# P1_PM10_Meteorology_Hstar

Experiments and results for the paper:

**"Meteorological predictors and the useful forecast horizon (H*) for PM10:
a comparative study under high and moderate autocorrelation regimes"**

Target journal: Atmospheric Environment (Elsevier, Q1)

---

## Experiments

### Madrid — Casa de Campo
- Period: train 2019–2022 / test 2023 (~354 rolling origins)
- Model: XGBoost-direct (one model per horizon h=1..24)
- Conditions: `lags_only` vs `lags_meteo`
- Meteorological variables: temperature, humidity, pressure, wind speed,
  wind direction, solar radiation, precipitation
- Validation: rolling-origin expanding window (origin spacing: 24 h)
- Benchmark: pure persistence
- Key result: H*_strict `lags_only`=9h → `lags_meteo`=17h (ΔH*=+8h)
- lag-1 autocorrelation: ρ₁ = 0.90

### Ireland — 8 stations
- Stations: Birr, Dublin Airport, Dundalk, Pearse St. (Dublin),
  Ringsend (Dublin), Edenderry, Limerick, Portlaoise
- Period: train 2020–2022 / test 2023-01 to 2023-08
  (145–212 origins per station depending on data coverage)
- Model: same protocol as Madrid
- Meteorological variables: rain, temperature, wetbulb temperature,
  dew point, vapour pressure, relative humidity, MSL pressure,
  wind speed, wind direction (no solar radiation available)
- Key result: H*_strict mean `lags_only`=21.5h → `lags_meteo`=22.4h (ΔH*=+0.9h)
- lag-1 autocorrelation: ρ₁ mean = 0.82 (range 0.66–0.89)

---

## Central finding

The value of adding meteorological variables depends on the lag-1
autocorrelation regime of the PM10 series.

- **High autocorrelation (Madrid, ρ₁=0.90):** meteorology breaks the
  persistence barrier at h=1–2 and extends H*_strict by 8 hours.
- **Moderate autocorrelation (Ireland, ρ₁≈0.82):** the lags-only model
  is already competitive across the full 24-hour horizon; meteorological
  gain is marginal (+0.9h on average).

---

## Repository structure

```
P1_PM10_Meteorology_Hstar/
├── code/                          # training and evaluation scripts
│   └── models/                    # XGBoost, ARIMA, persistence, LSTM
├── data_processed/                # curated input data (raw data not tracked)
├── data_raw/                      # not tracked — see Data Sources below
├── results/
│   ├── e2_met_madrid_pm10/        # metrics, predictions, tables, DM test
│   ├── e2_met_ireland_pm10/       # per-station and aggregate results
│   ├── comparison_madrid_ireland/ # comparative figures
│   └── madrid_sarima/             # SARIMA baseline results
├── figures/                       # final figures for the paper
├── manuscripts/                   # Overleaf link and final PDF when available
├── notes/                         # experimental design documents
└── reports/                       # audit and setup reports
```

---

## Data sources

Raw data is not tracked in this repository.

**Madrid — air quality:**
Ayuntamiento de Madrid, Portal de Datos Abiertos.
https://datos.madrid.es/portal/site/egob
Licence: Creative Commons Attribution 4.0 (CC BY 4.0)
Series: hourly PM10, station Casa de Campo, 2019–2023.

**Madrid — meteorology:**
Ayuntamiento de Madrid, Portal de Datos Abiertos.
https://datos.madrid.es/portal/site/egob
Series: hourly meteorological variables, 2019–2023.

**Ireland — air quality and meteorology:**
Environmental Protection Agency Ireland (EPA).
https://www.epa.ie/our-services/monitoring--assessment/air/
Series: hourly PM10 and meteorological variables,
8 stations, 2020–2023.

---

## Reproducibility

Full reproduction instructions will be added prior to journal submission.
A Zenodo DOI will be registered at that point and linked here.

See `RUN_ORDER.md` for the current execution sequence.

---

## Authors

- Federico García Crespi — UMH, Dep. Tecnología Informática y Computación
- Julio Ramos — j.ramos@umh.es, UMH

---

## License

To be defined prior to submission.
