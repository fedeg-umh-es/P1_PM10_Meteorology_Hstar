from pathlib import Path


# Project paths
ROOT_DIR = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT_DIR / "code"
DATA_RAW_DIR = ROOT_DIR / "data_raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data_processed"
RESULTS_DIR = ROOT_DIR / "results"
FIGURES_DIR = ROOT_DIR / "figures"
NOTES_DIR = ROOT_DIR / "notes"


# Temporal configuration
TRAIN_START = "2017-01-01"
TRAIN_END = "2022-12-31"
TEST_START = "2023-01-01"
TEST_END = "2023-12-31"
FREQ = "H"
HORIZON_MAX = None  # to be fixed in implementation


# Target and site
TARGET_VARIABLE = "PM10"
SITE_NAME = "Elche"
STATION_CATEGORY = "Cat. 4 urban background"
DATASET_SOURCE = "Red Valenciana de Vigilancia y Control de la Contaminacion Atmosferica"


# Experimental conditions
CONDITIONS = ["C0", "C1", "C2", "C3"]

CONDITION_DESCRIPTIONS = {
    "C0": "Persistence baseline.",
    "C1": "Lag-only benchmark with autoregressive inputs and calendar features where applicable.",
    "C2": "Lag plus meteorological core features.",
    "C3": "Lag plus meteorological extended features.",
}


# Feature groups
AUTOREGRESSIVE_FEATURES = []  # to be fixed in implementation

CALENDAR_FEATURES = [
    "hour_of_day",
    "day_of_week",
    "month",
    "julian_day",
]

METEO_CORE_FEATURES = [
    "temperature",
    "relative_humidity",
    "surface_pressure",
]

METEO_EXTENDED_FEATURES = [
    "temperature",
    "relative_humidity",
    "surface_pressure",
    "wind_speed",
    "wind_direction",
    "precipitation",
    "solar_radiation",
    "boundary_layer_height",
]


# Model groups
BASELINE_MODELS = [
    "persistence",
]

LAG_ONLY_MODELS = [
    "arima",
    "sarima",
    "xgboost_direct",
    "lstm_mimo",
]

METEO_MODELS = [
    "xgboost_direct",
    "lstm_mimo",
]


# Metrics
METRICS = ["rmse", "mae", "skill"]
HSTAR_VARIANTS = ["hstar_relax", "hstar_strict"]


# Reproducibility / environment
RANDOM_SEED = None  # to be fixed in implementation
OMP_NUM_THREADS = None  # to be fixed in implementation
MKL_NUM_THREADS = None  # to be fixed in implementation
PYTORCH_ENABLE_MPS_FALLBACK = None  # to be fixed in implementation


# Implementation placeholders
PM10_LAG_DEPTH = None  # to be fixed in implementation
SARIMA_ORDER = None  # to be fixed in implementation
ARIMA_ORDER = None  # to be fixed in implementation
METEO_DATA_SOURCE = None  # to be fixed in implementation
LOCAL_METEO_STATION = None  # to be fixed in implementation
ERA5_IS_RETROSPECTIVE_UPPER_BOUND = True
