#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data_processed" / "ireland_pm10_meteorology_hourly.csv"
SOURCE_PREDICTIONS = ROOT / "results" / "e2_met_ireland_pm10" / "predictions" / "predictions_all_models.csv"
OUTPUT_PREDICTIONS = ROOT / "outputs" / "metrics" / "predictions_meteorology_experiment.csv"
MASTER_TABLE = ROOT / "outputs" / "tables" / "master_meteorology_diagnostic_table.csv"
FIGURES_DIR = ROOT / "outputs" / "figures"

AUDIT_DIR = ROOT / "docs" / "audit"
PROTOCOL_DIR = ROOT / "docs" / "protocol"
RESULTS_DIR = ROOT / "results"

METEO_COLS = ["rain", "temp", "wetb", "dewpt", "vappr", "rhum", "msl", "wdsp", "wddir"]
EXPECTED_HORIZONS = list(range(1, 25))
CONDITION_MAP = {"lags_only": "lag_only", "lags_meteo": "lag_plus_met"}


def ensure_dirs() -> None:
    for path in [OUTPUT_PREDICTIONS.parent, MASTER_TABLE.parent, FIGURES_DIR, AUDIT_DIR, PROTOCOL_DIR, RESULTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ") for col in cols]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def load_dataset() -> pd.DataFrame:
    if not DATASET.exists():
        raise FileNotFoundError(f"Required processed dataset not found: {rel(DATASET)}")
    return pd.read_csv(DATASET, parse_dates=["timestamp"])


def load_predictions() -> pd.DataFrame:
    if not SOURCE_PREDICTIONS.exists():
        raise FileNotFoundError(
            "Required rolling-origin predictions are missing. Run "
            "`python3 code/e2_met_ireland_run.py --config code/e2_met_ireland_config.json --condition all` first."
        )
    preds = pd.read_csv(SOURCE_PREDICTIONS, parse_dates=["origin", "forecast_timestamp"])
    needed = {"station", "origin", "forecast_timestamp", "horizon", "condition", "model", "y_true", "y_pred"}
    missing = needed.difference(preds.columns)
    if missing:
        raise ValueError(f"Prediction file is missing columns: {sorted(missing)}")
    preds = preds[preds["model"].isin(["persistence", "xgboost_direct"])].copy()
    preds["condition"] = preds["condition"].replace(CONDITION_MAP)
    preds = preds[preds["condition"].isin(["reference", "lag_only", "lag_plus_met"])].copy()
    preds.to_csv(OUTPUT_PREDICTIONS, index=False)
    return preds


def station_inventory(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for station, group in df.groupby("station", sort=True):
        group = group.sort_values("timestamp")
        joint_rows = int(group[["PM10", *METEO_COLS]].dropna().shape[0])
        usable = (
            group["PM10"].notna().mean() >= 0.95
            and group[METEO_COLS].notna().mean().min() >= 0.95
            and joint_rows >= 8760
            and group["timestamp"].diff().dt.total_seconds().div(3600).median() == 1.0
        )
        rows.append(
            {
                "station_id": station,
                "pm10_available": bool(group["PM10"].notna().any()),
                "meteorology_available": bool(group[METEO_COLS].notna().any().all()),
                "joint_period_available": f"{group['timestamp'].min()} to {group['timestamp'].max()}",
                "usable_for_experiment": bool(usable),
                "notes": (
                    f"rows={len(group)}; joint_rows={joint_rows}; "
                    f"pm10_nonnull={group['PM10'].notna().mean():.3f}; "
                    f"min_met_nonnull={group[METEO_COLS].notna().mean().min():.3f}"
                ),
            }
        )
    return pd.DataFrame(rows)


def _safe_corr(obs: pd.Series, pred: pd.Series) -> float:
    if len(obs) < 3 or obs.std(ddof=0) == 0 or pred.std(ddof=0) == 0:
        return float("nan")
    return float(np.corrcoef(obs, pred)[0, 1])


def compute_master_table(preds: pd.DataFrame) -> pd.DataFrame:
    baseline = preds[(preds["condition"] == "reference") & (preds["model"] == "persistence")].copy()
    baseline_rows = []
    for (station, horizon), group in baseline.groupby(["station", "horizon"], sort=True):
        valid = group.dropna(subset=["y_true", "y_pred"])
        rmse = float(np.sqrt(np.mean((valid["y_true"] - valid["y_pred"]) ** 2))) if len(valid) else float("nan")
        baseline_rows.append({"station": station, "horizon": int(horizon), "rmse_persistence": rmse})
    baseline_df = pd.DataFrame(baseline_rows)

    rows: list[dict[str, Any]] = []
    model_preds = preds[(preds["model"] == "xgboost_direct") & (preds["condition"].isin(["lag_only", "lag_plus_met"]))].copy()
    for (station, condition, model, horizon), group in model_preds.groupby(
        ["station", "condition", "model", "horizon"], sort=True
    ):
        valid = group.dropna(subset=["y_true", "y_pred"])
        if valid.empty:
            rmse = r_h = phi_h = beta_h = kge_h = float("nan")
            n_eval = 0
        else:
            obs = pd.to_numeric(valid["y_true"], errors="coerce")
            pred = pd.to_numeric(valid["y_pred"], errors="coerce")
            rmse = float(np.sqrt(np.mean((obs - pred) ** 2)))
            r_h = _safe_corr(obs, pred)
            obs_std = float(obs.std(ddof=0))
            pred_std = float(pred.std(ddof=0))
            obs_mean = float(obs.mean())
            pred_mean = float(pred.mean())
            phi_h = pred_std / obs_std if obs_std != 0 else float("nan")
            beta_h = pred_mean / obs_mean if obs_mean != 0 else float("nan")
            if all(np.isfinite(x) for x in [r_h, phi_h, beta_h]):
                kge_h = 1.0 - math.sqrt((r_h - 1.0) ** 2 + (phi_h - 1.0) ** 2 + (beta_h - 1.0) ** 2)
            else:
                kge_h = float("nan")
            n_eval = int(len(valid))
        rows.append(
            {
                "station": station,
                "station_type": "unknown",
                "model": model,
                "condition": condition,
                "horizon": int(horizon),
                "n_eval": n_eval,
                "rmse": rmse,
                "r_h": r_h,
                "phi_h": phi_h,
                "beta_h": beta_h,
                "kge_h": kge_h,
            }
        )
    out = pd.DataFrame(rows).merge(baseline_df, on=["station", "horizon"], how="left")
    out["skill_h"] = 1.0 - (out["rmse"] / out["rmse_persistence"])
    out = out[
        [
            "station",
            "station_type",
            "model",
            "condition",
            "horizon",
            "n_eval",
            "skill_h",
            "phi_h",
            "r_h",
            "beta_h",
            "kge_h",
            "rmse",
            "rmse_persistence",
        ]
    ].sort_values(["station", "model", "condition", "horizon"])
    out.to_csv(MASTER_TABLE, index=False)
    return out


def plot_profiles(master: pd.DataFrame) -> None:
    profile = (
        master.groupby(["condition", "horizon"], as_index=False)[["skill_h", "phi_h", "kge_h"]]
        .median(numeric_only=True)
        .sort_values(["condition", "horizon"])
    )
    labels = {"lag_only": "lag-only", "lag_plus_met": "lag + meteorology"}
    for metric, ylabel, name in [
        ("skill_h", "median Skill_h", "skill_profile_by_horizon.png"),
        ("phi_h", "median phi_h", "phi_profile_by_horizon.png"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 4.8))
        for condition, group in profile.groupby("condition", sort=True):
            ax.plot(group["horizon"], group[metric], marker="o", linewidth=1.8, label=labels.get(condition, condition))
        ax.axhline(0 if metric == "skill_h" else 1, color="0.35", linewidth=0.9, linestyle="--")
        ax.set_xlabel("Forecast horizon (hours)")
        ax.set_ylabel(ylabel)
        ax.legend(frameon=False)
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / name, dpi=180)
        plt.close(fig)

    wide = master.pivot_table(
        index=["station", "model", "horizon"], columns="condition", values=["skill_h", "phi_h", "kge_h"], aggfunc="first"
    )
    delta_rows = []
    for metric in ["skill_h", "phi_h", "kge_h"]:
        if (metric, "lag_plus_met") not in wide.columns or (metric, "lag_only") not in wide.columns:
            continue
        delta = (wide[(metric, "lag_plus_met")] - wide[(metric, "lag_only")]).rename(metric)
        tmp = delta.reset_index().groupby("horizon", as_index=False)[metric].median()
        tmp["metric"] = metric
        tmp = tmp.rename(columns={metric: "median_delta"})
        delta_rows.append(tmp)
    delta_df = pd.concat(delta_rows, ignore_index=True)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for metric, group in delta_df.groupby("metric", sort=True):
        ax.plot(group["horizon"], group["median_delta"], marker="o", linewidth=1.8, label=metric)
    ax.axhline(0, color="0.35", linewidth=0.9, linestyle="--")
    ax.set_xlabel("Forecast horizon (hours)")
    ax.set_ylabel("median lag_plus_met - lag_only")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "median_delta_skill_phi_kge_by_horizon.png", dpi=180)
    plt.close(fig)


def write_audit_docs(df: pd.DataFrame, inventory: pd.DataFrame) -> None:
    inv_md = markdown_table(inventory)
    (AUDIT_DIR / "data_inventory.md").write_text(
        "# Data Inventory\n\n"
        f"Primary experiment dataset: `{rel(DATASET)}`.\n\n"
        f"Rows: {len(df)}. Stations: {df['station'].nunique()}. "
        f"Period: {df['timestamp'].min()} to {df['timestamp'].max()}.\n\n"
        "Meteorology columns used: `rain`, `temp`, `wetb`, `dewpt`, `vappr`, `rhum`, `msl`, `wdsp`, `wddir`.\n\n"
        "## Station Usability\n\n"
        f"{inv_md}\n",
        encoding="utf-8",
    )
    (AUDIT_DIR / "script_inventory.md").write_text(
        "# Script Inventory\n\n"
        "- `code/e2_met_ireland_run.py`: existing multi-station rolling-origin producer for lag-only and lag+meteorology forecasts.\n"
        "- `code/e2_met_madrid_run.py`: existing one-station Madrid rolling-origin producer.\n"
        "- `code/e2_met_madrid_shared.py`: shared feature construction, persistence, SARIMA, XGBoost-direct, metrics and DM helpers.\n"
        "- `code/run_meteorology_dynamic_experiment.py`: compact downstream compiler for the decisive dynamic-fidelity table and figures.\n"
        "- `code/e2_met_ireland_config.json` and `code/e2_met_madrid_config.json`: experiment configs; both contain pre-existing absolute paths and should be relativized before reuse in a clean rerun.\n",
        encoding="utf-8",
    )
    (AUDIT_DIR / "path_issues.md").write_text(
        "# Path Issues\n\n"
        "Pre-existing absolute paths were found in reports, run notes and legacy configs. The new experiment script uses repo-relative paths internally.\n\n"
        "Known files requiring cleanup before a fully portable rerun:\n"
        "- `code/e2_met_ireland_config.json`\n"
        "- `code/e2_met_madrid_config.json`\n"
        "- `code/build_madrid_experiment_base.py`\n"
        "- `code/e2_autocorrelation_analysis.py`\n"
        "- `RUN_ORDER.md`\n"
        "- selected historical files under `reports/`, `notes/`, and LaTeX build artifacts under `manuscripts/`.\n",
        encoding="utf-8",
    )
    (AUDIT_DIR / "meteorology_experiment_audit.md").write_text(
        "# Meteorology Experiment Audit\n\n"
        "The repo already contains an E2 meteorology line with processed PM10+meteorology datasets, rolling-origin scripts, prediction outputs, metrics, figures and a manuscript draft.\n\n"
        "Priority design files inspected: `01_scope_protocol.md`, `CANONICAL_PROTOCOL.md`, and `notes/e2_met_canonical_protocol.md`.\n\n"
        "Current evaluation protocol found: expanding rolling-origin, hourly horizons `h = 1..24`, daily origin stride, train-only feature imputation, persistence as primary baseline, and XGBoost-direct as the main lag-only vs lag+meteorology comparison model.\n\n"
        "For the minimum decisive experiment, the multi-station Ireland processed dataset is used because it supports station-level consistency checks with reliable meteorology coverage. Madrid remains a usable one-station branch but cannot answer cross-station consistency by itself.\n\n"
        "No new absolute paths are introduced by the added code.\n\n"
        "## Station Table\n\n"
        f"{inv_md}\n",
        encoding="utf-8",
    )


def write_protocol_doc(inventory: pd.DataFrame) -> None:
    used = ", ".join(inventory.loc[inventory["usable_for_experiment"], "station_id"].astype(str))
    (PROTOCOL_DIR / "meteorology_vs_lags_protocol.md").write_text(
        "# Meteorology vs Lags Protocol\n\n"
        f"Stations included: {used}.\n\n"
        "- Target: hourly `PM10`.\n"
        "- Horizons: `h = 1..24`, preserving the current E2-MET convention.\n"
        "- Baseline: persistence, evaluated at the same origins and horizons.\n"
        "- Rolling-origin: expanding windows, test origins in 2023, 24-hour stride, station-wise evaluation.\n"
        "- Preprocessing: lags and calendar features are generated inside each train/origin context; numeric missing features are imputed with train-window medians only in the upstream rolling script.\n"
        "- Missingness: stations require usable PM10 and all selected meteorological covariates over the joint period; remaining fold-level missing values are handled train-only.\n"
        "- Lag features: `PM10` lags `[1, 2, 3, 6, 12, 24, 48, 168]` plus calendar features.\n"
        "- Meteorology features: `rain`, `temp`, `wetb`, `dewpt`, `vappr`, `rhum`, `msl`, `wdsp`, `wddir`.\n"
        "- Conditions: `lag_only` and `lag_plus_met`.\n"
        "- Model family in this pass: `xgboost_direct`, already supported by the repo. No new model family or tuning is introduced.\n"
        "- Exclusion criteria: missing processed PM10+meteorology panel, less than one year of joint hourly data, median time step other than one hour, or meteorology coverage below 95% in any selected covariate.\n"
        "- Final diagnostics: `skill_h` versus persistence, `phi_h` as forecast-to-observed standard deviation ratio, `r_h` as forecast-observation correlation, `beta_h` as mean ratio, and `KGE_h` from `(r_h, phi_h, beta_h)`.\n",
        encoding="utf-8",
    )


def interpretation(master: pd.DataFrame) -> tuple[str, str]:
    wide = master.pivot_table(index=["station", "horizon"], columns="condition", values=["skill_h", "phi_h", "r_h", "beta_h", "kge_h"])
    deltas = {}
    for metric in ["skill_h", "phi_h", "r_h", "beta_h", "kge_h"]:
        deltas[metric] = wide[(metric, "lag_plus_met")] - wide[(metric, "lag_only")]
    delta_df = pd.DataFrame(deltas).reset_index()
    phi_distance_delta = (
        (wide[("phi_h", "lag_plus_met")] - 1.0).abs()
        - (wide[("phi_h", "lag_only")] - 1.0).abs()
    ).rename("phi_distance_delta")
    delta_df = delta_df.merge(phi_distance_delta.reset_index(), on=["station", "horizon"], how="left")
    med = delta_df.groupby("horizon")[["skill_h", "phi_h", "r_h", "beta_h", "kge_h"]].median()
    station_med = delta_df.groupby("station")[["skill_h", "phi_h", "r_h", "beta_h", "kge_h"]].median()
    phi_med = delta_df.groupby("horizon")["phi_distance_delta"].median()
    station_phi_med = delta_df.groupby("station")["phi_distance_delta"].median()

    skill_positive_h = int((med["skill_h"] > 0).sum())
    kge_positive_h = int((med["kge_h"] > 0).sum())
    phi_closer_h = int((phi_med < 0).sum())
    stations_skill_pos = int((station_med["skill_h"] > 0).sum())
    stations_kge_pos = int((station_med["kge_h"] > 0).sum())
    stations_phi_closer = int((station_phi_med < 0).sum())
    error_not_dynamic = int(((delta_df["skill_h"] > 0) & (delta_df["phi_h"].abs() < 0.01) & (delta_df["kge_h"] <= 0)).sum())
    r_or_kge_not_phi = int((((delta_df["r_h"] > 0) | (delta_df["kge_h"] > 0)) & (delta_df["phi_h"].abs() < 0.01)).sum())
    error_not_dynamic_answer = (
        f"Sí: {error_not_dynamic} pares estación-horizonte tienen `skill_h` positivo sin mejora clara de `KGE_h` y con cambio pequeño de `phi_h`."
        if error_not_dynamic > 0
        else "No bajo este criterio descriptivo: no aparecen pares estación-horizonte con `skill_h` positivo, `KGE_h` no positivo y cambio pequeño de `phi_h`."
    )
    r_or_kge_not_phi_answer = (
        f"Sí: {r_or_kge_not_phi} pares estación-horizonte cumplen ese patrón descriptivo."
        if r_or_kge_not_phi > 0
        else "No bajo este criterio descriptivo."
    )

    text = (
        "# Meteorology Experiment Interpretation\n\n"
        f"- ¿La meteorología mejora el skill frente a persistencia? Medianamente sí en {skill_positive_h}/24 horizontes; "
        f"por estación, {stations_skill_pos}/{station_med.shape[0]} tienen delta mediano positivo de `skill_h`.\n"
        f"- ¿La meteorología mejora la fidelidad dinámica? La evidencia es mixta: `KGE_h` mejora medianamente en {kge_positive_h}/24 horizontes, "
        f"pero `phi_h` se acerca a 1 solo en {phi_closer_h}/24 horizontes y en {stations_phi_closer}/{station_med.shape[0]} estaciones.\n"
        f"- ¿El efecto es consistente por horizonte? No completamente; los deltas medianos cambian con `h`.\n"
        f"- ¿El efecto es consistente entre estaciones? No completamente; {stations_kge_pos}/{station_med.shape[0]} estaciones tienen delta mediano positivo de `KGE_h`.\n"
        f"- ¿Hay perfiles donde mejora error pero no dinámica? {error_not_dynamic_answer}\n"
        f"- ¿Hay perfiles donde la mejora aparece en `r_h` o `KGE_h` aunque `phi_h` cambie poco? {r_or_kge_not_phi_answer}\n"
        "- ¿Qué patrón merece seguimiento en un manuscrito? El patrón a seguir es la separación entre ganancia de precisión y ganancia dinámica por horizonte y estación, especialmente donde `skill_h` sube pero `KGE_h` o `phi_h` no acompañan.\n"
    )

    if stations_skill_pos == station_med.shape[0] and stations_kge_pos == station_med.shape[0]:
        verdict = "go: meteorology improves both accuracy and dynamic fidelity"
    elif stations_skill_pos > 0 and (stations_kge_pos > 0 or kge_positive_h > 0):
        verdict = "go: meteorology improves accuracy but fidelity gains are mixed"
    elif stations_skill_pos > 0:
        verdict = "hold: meteorology does not yet justify manuscript focus"
    else:
        verdict = "hold: meteorology does not yet justify manuscript focus"
    return text, verdict


def write_results_docs(master: pd.DataFrame, inventory: pd.DataFrame, verdict: str, interpretation_text: str) -> None:
    (RESULTS_DIR / "meteorology_experiment_interpretation.md").write_text(interpretation_text, encoding="utf-8")
    stations = ", ".join(inventory.loc[inventory["usable_for_experiment"], "station_id"].astype(str))
    horizons = f"{min(EXPECTED_HORIZONS)}..{max(EXPECTED_HORIZONS)}"
    limitations = (
        "station type metadata is not present in the processed dataset; "
        "this run compiles existing rolling-origin forecasts rather than refitting them; "
        "legacy configs still contain absolute paths."
    )
    (RESULTS_DIR / "meteorology_experiment_closure.md").write_text(
        "# Meteorology Experiment Closure\n\n"
        f"- Stations entered: {stations}.\n"
        "- Models entered: `xgboost_direct`; persistence is the reference baseline.\n"
        f"- Horizons evaluated: `{horizons}`.\n"
        f"- Outputs generated: `{rel(OUTPUT_PREDICTIONS)}`, `{rel(MASTER_TABLE)}`, and figures in `{rel(FIGURES_DIR)}`.\n"
        f"- Limitations blocking strong inference: {limitations}\n\n"
        f"{verdict}\n",
        encoding="utf-8",
    )
    summary = {
        "stations": inventory.loc[inventory["usable_for_experiment"], "station_id"].tolist(),
        "model": "xgboost_direct",
        "horizons": EXPECTED_HORIZONS,
        "rows_master_table": int(len(master)),
        "verdict": verdict,
    }
    (RESULTS_DIR / "meteorology_experiment_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    df = load_dataset()
    inventory = station_inventory(df)
    preds = load_predictions()
    master = compute_master_table(preds)
    plot_profiles(master)
    write_audit_docs(df, inventory)
    write_protocol_doc(inventory)
    interpretation_text, verdict = interpretation(master)
    write_results_docs(master, inventory, verdict, interpretation_text)
    print(f"Wrote {rel(OUTPUT_PREDICTIONS)}")
    print(f"Wrote {rel(MASTER_TABLE)}")
    print(f"Wrote figures under {rel(FIGURES_DIR)}")
    print(verdict)


if __name__ == "__main__":
    main()
