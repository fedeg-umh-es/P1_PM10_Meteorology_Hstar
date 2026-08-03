#!/usr/bin/env python3
"""Regenera las figuras de esta auditoria (Fases 2, 4 y 5) a partir de los
artefactos ya versionados en results/audit/. No reentrena ni toca los datos
de origen del manuscrito.

Uso:
    source .venv_audit/bin/activate
    python3 code/audit_build_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT_RESULTS = ROOT / "results" / "audit"
OUT_DIR = ROOT / "figures" / "audit"


def figure_skill_curves() -> None:
    s = pd.read_csv(AUDIT_RESULTS / "madrid_recompute" / "skill_curves_S_h.csv", index_col="horizon")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.axhline(0, color="black", linewidth=0.8)
    ax.plot(s.index, s["lags_only"], "o-", color="tab:blue", label="lags only")
    ax.plot(s.index, s["lags_meteo"], "s-", color="tab:red", label="lags + meteo")
    ax.plot(s.index, s["sarima"], "^--", color="tab:gray", label="SARIMA", alpha=0.7)
    # Highlight the true max-run window for lags_only (h=3-11) vs. the
    # manuscript prose's implied h=1-11.
    ax.axvspan(3, 11, color="tab:blue", alpha=0.08)
    ax.axvspan(1, 17, color="tab:red", alpha=0.06)
    ax.set_xlabel("Forecast horizon h (hours)")
    ax.set_ylabel("RMSE skill score S(h) vs. persistence")
    ax.set_title("Madrid: S(h) recomputado desde predictions_all_models.csv\n(sombreado = racha max-run real de cada condicion)")
    ax.legend()
    ax.set_xticks(range(1, 25, 2))
    fig.tight_layout()
    fig.savefig(OUT_DIR / "madrid_skill_curves_recomputed.png", dpi=150)
    plt.close(fig)


def figure_bootstrap_windows() -> None:
    published_window_replicates = pd.read_csv(AUDIT_RESULTS / "madrid_recompute" / "bootstrap_delta_hstar_replicates.csv")["delta_hstar_max_run"]
    window_json = json.loads((AUDIT_RESULTS / "madrid_window_sensitivity" / "window_comparison.json").read_text())

    # Full histogram for the published (sensitivity) window's bootstrap replicates.
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.hist(published_window_replicates, bins=range(int(published_window_replicates.min()) - 1, int(published_window_replicates.max()) + 2), color="tab:red", alpha=0.7, edgecolor="white")
    ax2.axvline(8, color="black", linestyle="--", label="punto estimado publicado = +8h")
    ax2.set_xlabel("ΔH*_strict,max-run (h), remuestra de bloques moviles")
    ax2.set_ylabel("Frecuencia (de 2000 remuestras)")
    ax2.set_title("Bootstrap de ΔH*_strict,max-run -- ventana publicada (ene-dic 2023)")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT_DIR / "madrid_bootstrap_delta_hstar_histogram.png", dpi=150)
    plt.close(fig2)

    # Point estimate + 95% CI comparison across the two windows (summary only;
    # per-window replicate arrays for PRIMARIA are not separately persisted,
    # see results/audit/madrid_window_sensitivity/window_comparison.json).
    labels = ["SENSIBILIDAD\n(ene-dic, 362 orig.,\n= publicado)", "PRIMARIA\n(ene-jul, 212 orig.,\nsimetrica c/ Irlanda)"]
    keys = ["SENSIBILIDAD_jan_dec_2023", "PRIMARIA_jan_jul_2023"]
    points = [window_json[k]["delta_hstar_max_run"] for k in keys]
    ci_low = [window_json[k]["bootstrap_ci95"][0] for k in keys]
    ci_high = [window_json[k]["bootstrap_ci95"][1] for k in keys]
    err_low = [p - lo for p, lo in zip(points, ci_low)]
    err_high = [hi - p for p, hi in zip(points, ci_high)]

    fig, ax = plt.subplots(figsize=(6, 4.2))
    x = range(len(labels))
    ax.axhline(0, color="black", linewidth=0.8)
    ax.errorbar(x, points, yerr=[err_low, err_high], fmt="o", color="tab:red", capsize=6, markersize=8)
    for xi, p in zip(x, points):
        ax.annotate(f"+{p}h", (xi, p), xytext=(8, 0), textcoords="offset points", va="center")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("ΔH*_strict,max-run (h) -- punto estimado e IC95% bootstrap")
    ax.set_title("Fase 4: sensibilidad de ΔH*_strict,max-run a la ventana de evaluacion")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "madrid_delta_hstar_window_sensitivity.png", dpi=150)
    plt.close(fig)


def figure_null_calibration() -> None:
    draws = pd.read_csv(AUDIT_RESULTS / "calibration" / "null_max_run_draws.csv")["null_max_run"]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.hist(draws, bins=range(0, 26), color="tab:purple", alpha=0.7, edgecolor="white")
    ax.axvline(9, color="black", linestyle="--", label="H*_strict,max-run observado (lags_only) = 9h")
    ax.set_xlabel("max-run bajo permutacion (S(h)=0 en todos los horizontes)")
    ax.set_ylabel("Frecuencia (de 5000 permutaciones)")
    ax.set_title("Fase 5a: calibracion nula de H*_strict,max-run")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "madrid_null_calibration_max_run.png", dpi=150)
    plt.close(fig)


def figure_rho1_tobit() -> None:
    df = pd.read_csv(AUDIT_RESULTS / "calibration" / "rho1_delta_hstar_table.csv")
    reg = json.loads((AUDIT_RESULTS / "calibration" / "rho1_delta_hstar_regression.json").read_text())

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for ceiling, marker, color, label in [
        (False, "o", "tab:blue", "no censurado"),
        (True, "x", "tab:gray", "censurado (techo 24h)"),
    ]:
        sub = df[df["ceiling"] == ceiling]
        ax.scatter(sub["rho1"], sub["delta_hstar"], marker=marker, color=color, s=70, label=label)

    xs = [df["rho1"].min(), df["rho1"].max()]
    ols = reg["ols"]
    ax.plot(xs, [ols["intercept"] + ols["slope"] * x for x in xs], "--", color="tab:orange", label=f"OLS (r={ols['r']:.2f}, p={ols['p_value']:.2f})")
    tobit = reg["tobit_right_censored_at_0"]
    ax.plot(xs, [tobit["beta0"] + tobit["beta1_slope"] * x for x in xs], "-", color="tab:red", label=f"Tobit censurado (β1={tobit['beta1_slope']:.1f})")

    for _, row in df.iterrows():
        ax.annotate(row["site"].split(" (")[0], (row["rho1"], row["delta_hstar"]), fontsize=6, xytext=(3, 3), textcoords="offset points")

    ax.set_xlabel(r"$\rho_1$ (autocorrelacion lag-1, periodo de entrenamiento)")
    ax.set_ylabel(r"$\Delta H^*_{strict}$ (h)")
    ax.set_title("Fase 5b: OLS vs. Tobit censurado (n=9)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "rho1_delta_hstar_ols_vs_tobit.png", dpi=150)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    figure_skill_curves()
    figure_bootstrap_windows()
    figure_null_calibration()
    figure_rho1_tobit()
    print(f"Figuras escritas en {OUT_DIR}")


if __name__ == "__main__":
    main()
