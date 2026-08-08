---
title: "test_meteorology_experiment_outputs.py"
categoria: "PERSONAL"
sub_area: "Personal"
tags:
  - personal
  - recurso
---

# 📌 test_meteorology_experiment_outputs.py

## 🧠 Síntesis y Puntos Clave (TDAH-friendly)
- **from pathlib** import Path
- **import pandas** as pd
- ROOT = Path(__file__).resolve().parents[1]
- **MASTER_TABLE =** ROOT / "outputs" / "tables" / "master_meteorology_diagnostic_table.csv"
- **PREDICTIONS =** ROOT / "outputs" / "metrics" / "predictions_meteorology_experiment.csv"
- **ADDED_CODE =** [ROOT / "code" / "run_meteorology_dynamic_experiment.py", Path(__file__)]
- **def test_master_table_expected_columns()** -> None:
- df = pd.read_csv(MASTER_TABLE)

## 📄 Contenido Detallado / Referencia
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MASTER_TABLE = ROOT / "outputs" / "tables" / "master_meteorology_diagnostic_table.csv"
PREDICTIONS = ROOT / "outputs" / "metrics" / "predictions_meteorology_experiment.csv"
ADDED_CODE = [ROOT / "code" / "run_meteorology_dynamic_experiment.py", Path(__file__)]


def test_master_table_expected_columns() -> None:
    df = pd.read_csv(MASTER_TABLE)
    expected = {
        "station",
        "station_type",
        "model",
        "condition",
        "horizon",
        "skill_h",
        "phi_h",
        "r_h",
        "beta_h",
        "kge_h",
    }
    assert expected.issubset(df.columns)


def test_no_nulls_in_essential_identifiers() -> None:
    master = pd.read_csv(MASTER_TABLE)
    predictions = pd.read_csv(PREDICTIONS)
    assert not master[["station", "model", "condition", "horizon"]].isna().any().any()
    assert not predictions[["station", "origin", "forecast_timestamp", "horizon", "condition", "model"]].isna().any().any()


def test_expected_horizons_and_conditions() -> None:
    df = pd.read_csv(MASTER_TABLE)
    assert sorted(df["horizon"].unique().tolist()) == list(range(1, 25))
    assert set(df["condition"].unique()) == {"lag_only", "lag_plus_met"}


def test_no_new_absolute_paths_in_added_code() -> None:
    forbidden = ["/" + "Users" + "/", "/" + "home" + "/", "C:" + "\\", "~" + "/"]
    for path in ADDED_CODE:
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden)


---
*Procesado automáticamente por Antigravity (Smart Router)*
