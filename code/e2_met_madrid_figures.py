#!/usr/bin/env python3
"""
e2_met_madrid_figures.py

Manuscript figures for the Madrid PM10 E2-MET experiment.

Figure 1  figure_skill_curves     — Skill(h) vs persistence: lags_only, lags_meteo, SARIMA
Figure 2  figure_delta_skill      — ΔSkill(h): lags_meteo − lags_only
Figure 3  figure_dm_significance  — DM-HLN dot chart at dm_horizons
Figure 4  figure_hstar_summary    — H* bar chart: all models and conditions

Usage:
  python3 code/e2_met_madrid_figures.py --config code/e2_met_madrid_config.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

from e2_met_madrid_shared import ensure_results_dirs, load_json_config

# ── style ──────────────────────────────────────────────────────────────────────

COLOR_LAGS   = "#2166ac"
COLOR_METEO  = "#d6604d"
COLOR_SARIMA = "#4dac26"
COLOR_POS    = "#2ca25f"
COLOR_NEG    = "#de2d26"

LW       = 1.8
TICK_FS  = 9
LABEL_FS = 10
TITLE_FS = 10
LEG_FS   = 9
MS       = 7

plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.size":         10,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.linewidth":    1.0,
    "axes.labelsize":    LABEL_FS,
    "axes.titlesize":    TITLE_FS,
    "xtick.labelsize":   TICK_FS,
    "ytick.labelsize":   TICK_FS,
    "xtick.major.size":  3,
    "ytick.major.size":  3,
    "legend.frameon":    False,
    "legend.fontsize":   LEG_FS,
})

HORIZONS = np.arange(1, 25)


def _save(fig: plt.Figure, fig_dir: Path, name: str) -> None:
    for ext in ("png", "pdf"):
        p = fig_dir / f"{name}.{ext}"
        fig.savefig(p, dpi=600 if ext == "png" else None, bbox_inches="tight")
        print(f"  saved: {p}")


# ── Figure 1: Skill(h) — lags_only, lags_meteo, SARIMA ───────────────────────

def make_fig1(metrics: pd.DataFrame, fig_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.2))

    series = [
        ("lags_only",  "xgboost_direct", COLOR_LAGS,   "-",  "XGB lags only"),
        ("lags_meteo", "xgboost_direct", COLOR_METEO,  "--", "XGB lags + met."),
        ("reference",  "sarima",         COLOR_SARIMA, ":",  "SARIMA"),
    ]

    for condition, model, color, ls, label in series:
        sub = metrics[(metrics["condition"] == condition) & (metrics["model"] == model)]
        if sub.empty:
            continue
        sub = sub.sort_values("horizon")
        ax.plot(sub["horizon"], sub["skill_rmse_vs_persistence"],
                color=color, lw=LW, ls=ls, label=label)

    ax.axhline(0, color="black", lw=0.8, ls=":", zorder=0)
    ax.set_xlim(1, 24)
    ax.set_xticks([1, 6, 12, 18, 24])
    ax.set_xlabel("Forecast horizon h (hours)", fontsize=LABEL_FS)
    ax.set_ylabel("Skill vs persistence (RMSE)", fontsize=LABEL_FS)
    ax.set_title("Skill score — Madrid Casa de Campo PM10, 2023",
                 fontsize=LABEL_FS + 1)
    ax.legend(fontsize=LEG_FS)
    fig.tight_layout()
    _save(fig, fig_dir, "figure_skill_curves")
    plt.close(fig)


# ── Figure 2: ΔSkill(h) — lags_meteo minus lags_only ─────────────────────────

def make_fig2(delta: pd.DataFrame, fig_dir: Path) -> None:
    delta = delta.sort_values("horizon")

    fig, ax = plt.subplots(figsize=(7.5, 4.0))

    ax.plot(delta["horizon"], delta["delta_skill_rmse_meteo_minus_lags"],
            color=COLOR_METEO, lw=LW, label="ΔSkill (lags+met − lags only)")
    ax.fill_between(delta["horizon"],
                    delta["delta_skill_rmse_meteo_minus_lags"],
                    0,
                    where=delta["delta_skill_rmse_meteo_minus_lags"] >= 0,
                    color=COLOR_METEO, alpha=0.15)
    ax.fill_between(delta["horizon"],
                    delta["delta_skill_rmse_meteo_minus_lags"],
                    0,
                    where=delta["delta_skill_rmse_meteo_minus_lags"] < 0,
                    color=COLOR_NEG, alpha=0.10)

    ax.axhline(0, color="black", lw=0.8, ls="--", zorder=0)
    ax.set_xlim(1, 24)
    ax.set_xticks([1, 6, 12, 18, 24])
    ax.set_xlabel("Forecast horizon h (hours)", fontsize=LABEL_FS)
    ax.set_ylabel("ΔSkill_RMSE (lags+met − lags only)", fontsize=LABEL_FS)
    ax.set_title("Meteorology benefit — Madrid Casa de Campo PM10, 2023",
                 fontsize=LABEL_FS + 1)
    ax.legend(fontsize=LEG_FS)
    fig.tight_layout()
    _save(fig, fig_dir, "figure_delta_skill")
    plt.close(fig)


# ── Figure 3: DM-HLN significance dot chart ───────────────────────────────────

def make_fig3(dm: pd.DataFrame, delta: pd.DataFrame, fig_dir: Path) -> None:
    dm_horizons = sorted(dm["horizon"].unique())
    delta_lk = {int(row["horizon"]): row["delta_skill_rmse_meteo_minus_lags"]
                for _, row in delta.iterrows()}

    fig, ax = plt.subplots(figsize=(6.5, 2.5))

    for h in dm_horizons:
        row = dm[dm["horizon"] == h]
        if row.empty:
            ax.plot(h, 0, "x", color="#aaaaaa", ms=5, mew=1.0)
            continue
        row = row.iloc[0]
        p = row["p_value"]
        dsk = delta_lk.get(int(h), 0.0)
        c = COLOR_POS if dsk >= 0 else COLOR_NEG
        sig = pd.notna(p) and float(p) < 0.05

        if sig:
            ax.plot(h, 0, "o", color=c, ms=MS + 2, mew=0, zorder=3)
        else:
            ax.plot(h, 0, "o", color="white", ms=MS + 2, mew=1.6,
                    mec=c, zorder=3)

        ax.annotate(f"p={float(p):.3f}", xy=(h, 0),
                    xytext=(0, 14), textcoords="offset points",
                    ha="center", fontsize=8, color="#444444")

    ax.set_xticks(dm_horizons)
    ax.set_xticklabels([f"h={h}" for h in dm_horizons], fontsize=TICK_FS)
    ax.set_yticks([])
    ax.set_xlabel("Forecast horizon", fontsize=LABEL_FS)
    ax.set_title("DM-HLN test: lags+met vs lags only — Madrid PM10, 2023",
                 fontsize=LABEL_FS + 1)
    ax.set_xlim(min(dm_horizons) - 2, max(dm_horizons) + 2)
    ax.set_ylim(-0.5, 0.5)
    ax.spines["left"].set_visible(False)

    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_POS,
               ms=MS, label="lags+met better, p < 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               ms=MS, mew=1.4, mec=COLOR_POS, label="lags+met better, p ≥ 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               ms=MS, mew=1.4, mec=COLOR_NEG, label="lags only better, p ≥ 0.05"),
    ]
    fig.legend(handles=legend_handles, loc="lower center",
               bbox_to_anchor=(0.5, -0.18), ncol=3, fontsize=LEG_FS - 1)
    fig.tight_layout()
    _save(fig, fig_dir, "figure_dm_significance")
    plt.close(fig)


# ── Figure 4: H* summary bar chart ────────────────────────────────────────────

def make_fig4(hstar: pd.DataFrame, fig_dir: Path) -> None:
    # Build display rows: persistence, sarima, lags_only, lags_meteo
    def _get(condition: str, model: str, metric: str) -> int:
        row = hstar[(hstar["condition"] == condition) & (hstar["model"] == model)]
        return int(row.iloc[0][metric]) if not row.empty else 0

    entries = [
        ("Persistence", "reference",  "persistence",     "#888888"),
        ("SARIMA",      "reference",  "sarima",           COLOR_SARIMA),
        ("Lags only",   "lags_only",  "xgboost_direct",  COLOR_LAGS),
        ("Lags + met.", "lags_meteo", "xgboost_direct",  COLOR_METEO),
    ]

    labels  = [e[0] for e in entries]
    x       = np.arange(len(entries))
    width   = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4.0),
                                    constrained_layout=True)

    for ax, metric, title in [
        (ax1, "H_star_strict", "H* strict"),
        (ax2, "H_star_relax",  "H* relax"),
    ]:
        vals = [_get(e[1], e[2], metric) for e in entries]
        colors = [e[3] for e in entries]
        bars = ax.bar(x, vals, width * 2.2, color=colors, alpha=0.88, zorder=3)

        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3,
                    str(int(h)), ha="center", va="bottom",
                    fontsize=9, color="#333333")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=TICK_FS)
        ax.set_title(title, fontsize=LABEL_FS, loc="left")
        ax.set_ylim(0, 27)
        ax.set_yticks([0, 6, 12, 18, 24])
        ax.yaxis.grid(True, lw=0.5, color="#eeeeee", zorder=0)
        ax.set_axisbelow(True)

    ax1.set_ylabel("H* (hours)", fontsize=LABEL_FS)
    fig.suptitle("H* summary — Madrid Casa de Campo PM10, 2023",
                 fontsize=LABEL_FS + 1)
    _save(fig, fig_dir, "figure_hstar_summary")
    plt.close(fig)


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate E2-MET Madrid manuscript figures.")
    parser.add_argument("--config", default="code/e2_met_madrid_config.json")
    args = parser.parse_args()

    config = load_json_config(args.config)
    paths = ensure_results_dirs(config["results_dir"])
    fig_dir = paths["base"] / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    tables = paths["manuscript_tables"]
    metrics = pd.read_csv(tables / "table_metrics_long.csv")
    delta   = pd.read_csv(tables / "table_delta_lags_meteo_vs_lags_only.csv")
    dm      = pd.read_csv(tables / "table_dm_lags_meteo_vs_lags_only.csv")
    hstar   = pd.read_csv(tables / "table_hstar_summary.csv")

    print("Figure 1: skill curves...")
    make_fig1(metrics, fig_dir)

    print("Figure 2: delta skill...")
    make_fig2(delta, fig_dir)

    print("Figure 3: DM significance...")
    make_fig3(dm, delta, fig_dir)

    print("Figure 4: H* summary...")
    make_fig4(hstar, fig_dir)

    print(f"\nDone. Figures in: {fig_dir}")


if __name__ == "__main__":
    main()
