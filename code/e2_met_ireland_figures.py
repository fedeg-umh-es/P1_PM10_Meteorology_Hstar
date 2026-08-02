#!/usr/bin/env python3
"""
e2_met_ireland_figures.py

Manuscript figures for the Ireland PM10 E2-MET experiment.

Figure 1  figure_skill_by_station      — 2×4 grid: Skill(h) vs persistence per station
Figure 2  figure_delta_skill           — ΔSkill(h) across all stations (one line per station)
Figure 3  figure_dm_significance       — DM-HLN dot chart: station × horizon
Figure 4  figure_hstar_summary         — H*_strict bar chart per station

Usage:
  python3 code/e2_met_ireland_figures.py --config code/e2_met_ireland_config.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

import sys
from unittest.mock import MagicMock
sys.modules['xgboost'] = MagicMock()
from e2_met_madrid_shared import ensure_results_dirs, load_json_config

# ── canonical paths (P3 canon v1.3) ───────────────────────────────────────────
# Script lives in <repo>/code. The H* summary figure must be built from the
# validated REGENERATED Ireland bundle (regenerated-not-original) using the
# primary strict metric H_strict_max_run, and written to the manuscript figure
# directory under the manuscript's expected filename.
REPO = Path(__file__).resolve().parents[1]
IRELAND_HSTAR_REGEN = REPO / "results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv"
MANUSCRIPT_FIGS = REPO / "manuscripts/figures"

# ── style ──────────────────────────────────────────────────────────────────────

COLOR_LAGS  = "#2166ac"   # lags_only
COLOR_METEO = "#d6604d"   # lags_meteo
COLOR_POS   = "#2ca25f"   # DM: favours lags_meteo (positive ΔSkill)
COLOR_NEG   = "#de2d26"   # DM: favours lags_only  (negative ΔSkill)

LW       = 1.8
ALPHA_CI = 0.15
TICK_FS  = 9
LABEL_FS = 10
TITLE_FS = 10
LEG_FS   = 9
MS       = 7

STATION_LABELS = {
    "Birr co offlay":       "Birr",
    "Dublin Airport":       "Dublin Airport",
    "Dundalk Co Louth":     "Dundalk",
    "Pearse street dublin": "Pearse St.",
    "Ringsend dublin":      "Ringsend",
    "edenderry co offlay":  "Edenderry",
    "henry street Limerick":"Limerick",
    "porrlaoise co laois":  "Portlaoise",
}

STATION_ORDER = list(STATION_LABELS.keys())

TAB10 = plt.cm.tab10.colors

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


# ── Figure 1: Skill(h) vs persistence — 2×4 station grid ─────────────────────

def make_fig1(metrics: pd.DataFrame, fig_dir: Path) -> None:
    xgb = metrics[metrics["model"] == "xgboost_direct"].copy()
    stations = [s for s in STATION_ORDER if s in xgb["station"].unique()]

    nrows, ncols = 2, 4
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 5.5), sharey=False)
    axes = axes.flatten()

    for i, stn in enumerate(stations):
        ax = axes[i]
        for cond, color, label, ls in [
            ("lags_only",  COLOR_LAGS,  "Lags only",  "-"),
            ("lags_meteo", COLOR_METEO, "Lags + met.", "--"),
        ]:
            sub = xgb[(xgb["station"] == stn) & (xgb["condition"] == cond)].sort_values("horizon")
            ax.plot(sub["horizon"], sub["skill_rmse_vs_persistence"],
                    color=color, lw=LW, ls=ls, label=label)

        ax.axhline(0, color="black", lw=0.7, ls=":", zorder=0)
        ax.set_xlim(1, 24)
        ax.set_xticks([1, 6, 12, 18, 24])
        ax.set_title(STATION_LABELS.get(stn, stn), fontsize=TITLE_FS, pad=3)
        ax.set_xlabel("h (hours)", fontsize=TICK_FS)
        if i % ncols == 0:
            ax.set_ylabel("Skill vs persistence", fontsize=TICK_FS)

    # shared legend below figure
    legend_handles = [
        Line2D([0], [0], color=COLOR_LAGS,  lw=LW, ls="-",  label="Lags only"),
        Line2D([0], [0], color=COLOR_METEO, lw=LW, ls="--", label="Lags + meteorology"),
    ]
    fig.legend(handles=legend_handles, loc="lower center",
               bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=LEG_FS)
    fig.suptitle("Skill score (RMSE vs persistence) — Ireland PM10, 2023",
                 fontsize=LABEL_FS + 1, y=1.01)
    fig.tight_layout()
    _save(fig, fig_dir, "figure_skill_by_station")
    plt.close(fig)


# ── Figure 2: ΔSkill(h) all stations ─────────────────────────────────────────

def make_fig2(delta: pd.DataFrame, fig_dir: Path) -> None:
    stations = [s for s in STATION_ORDER if s in delta["station"].unique()]

    fig, ax = plt.subplots(figsize=(7.5, 4.0))

    for i, stn in enumerate(stations):
        sub = delta[delta["station"] == stn].sort_values("horizon")
        ax.plot(sub["horizon"], sub["delta_skill_rmse_meteo_minus_lags"],
                color=TAB10[i % len(TAB10)], lw=LW, label=STATION_LABELS.get(stn, stn))

    ax.axhline(0, color="black", lw=0.8, ls="--", zorder=0)
    ax.set_xlim(1, 24)
    ax.set_xticks([1, 6, 12, 18, 24])
    ax.set_xlabel("Forecast horizon h (hours)", fontsize=LABEL_FS)
    ax.set_ylabel("ΔSkill_RMSE (lags+met − lags only)", fontsize=LABEL_FS)
    ax.set_title("Meteorology benefit per station — Ireland PM10, 2023",
                 fontsize=LABEL_FS + 1)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=LEG_FS - 1)

    fig.tight_layout()
    _save(fig, fig_dir, "figure_delta_skill")
    plt.close(fig)


# ── Figure 3: DM-HLN significance dot chart ───────────────────────────────────

def make_fig3(dm: pd.DataFrame, delta: pd.DataFrame, fig_dir: Path) -> None:
    stations = [s for s in STATION_ORDER if s in dm["station"].unique()]
    dm_horizons = sorted(dm["horizon"].unique())

    # build ΔSkill lookup to colour dots by direction
    delta_lk: dict[tuple, float] = {}
    for _, row in delta.iterrows():
        delta_lk[(row["station"], int(row["horizon"]))] = row["delta_skill_rmse_meteo_minus_lags"]

    fig, ax = plt.subplots(figsize=(7.0, 4.5))

    for ri, stn in enumerate(stations):
        for h in dm_horizons:
            row = dm[(dm["station"] == stn) & (dm["horizon"] == h)]
            if row.empty:
                ax.plot(h, ri, "x", color="#aaaaaa", ms=5, mew=1.0, zorder=2)
                continue
            row = row.iloc[0]
            p = row["p_value"]
            fav = row["favours"]
            dsk = delta_lk.get((stn, int(h)), 0.0)

            c = COLOR_POS if dsk >= 0 else COLOR_NEG
            sig = pd.notna(p) and p < 0.05

            if sig:
                ax.plot(h, ri, "o", color=c, ms=MS, mew=0, zorder=3)
            else:
                ax.plot(h, ri, "o", color="white", ms=MS, mew=1.4,
                        mec=c, zorder=3)

    # grid lines between stations
    for r in range(len(stations) - 1):
        ax.axhline(r + 0.5, color="#e0e0e0", lw=0.7)
    ax.grid(axis="x", color="#e0e0e0", lw=0.7)

    ax.set_yticks(range(len(stations)))
    ax.set_yticklabels([STATION_LABELS.get(s, s) for s in stations], fontsize=TICK_FS)
    ax.set_xticks(dm_horizons)
    ax.set_xticklabels([f"h={h}" for h in dm_horizons], fontsize=TICK_FS)
    ax.set_xlabel("Forecast horizon", fontsize=LABEL_FS)
    ax.tick_params(axis="y", length=0)
    ax.set_title("DM-HLN test: lags+met vs lags only — Ireland PM10, 2023",
                 fontsize=LABEL_FS + 1)

    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_POS,
               ms=MS, label="lags+met better, p < 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               ms=MS, mew=1.4, mec=COLOR_POS, label="lags+met better, p ≥ 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               ms=MS, mew=1.4, mec=COLOR_NEG, label="lags only better, p ≥ 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_NEG,
               ms=MS, label="lags only better, p < 0.05"),
    ]
    fig.legend(handles=legend_handles, loc="lower center",
               bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=LEG_FS)
    fig.tight_layout()
    _save(fig, fig_dir, "figure_dm_significance")
    plt.close(fig)


# ── Figure 4: H*_strict bar chart per station ─────────────────────────────────

def make_fig4(hstar: pd.DataFrame | None, fig_dir: Path) -> None:
    """Ireland H* summary bar chart.

    CANONICAL: reads the validated REGENERATED bundle
    (results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv)
    and uses the primary strict metric ``H_strict_max_run`` (auxiliary
    ``H_strict_from_h1`` is not plotted as the primary strict bar). The relax
    bars use ``H_relax``. The figure is written to the manuscript figures
    directory as ``ireland_figure_hstar_summary`` so the manuscript picks up the
    corrected values (Henry St. lags-only = 17, lags + met. = 24). The ``hstar``
    argument and ``fig_dir`` argument are ignored on purpose; the canonical
    source and destination are fixed. No model is rerun.
    """
    xgb = pd.read_csv(IRELAND_HSTAR_REGEN)
    xgb = xgb[xgb["model"] == "xgboost_direct"].copy()
    stations = [s for s in STATION_ORDER if s in xgb["station"].unique()]
    labels = [STATION_LABELS.get(s, s) for s in stations]

    x = np.arange(len(stations))
    width = 0.35

    def _get_hstar(stn: str, cond: str, metric: str) -> int:
        row = xgb[(xgb["station"] == stn) & (xgb["condition"] == cond)]
        if row.empty:
            return 0
        return int(row.iloc[0][metric])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.0), sharey=True,
                                    gridspec_kw={"wspace": 0.06},
                                    constrained_layout=True)

    for ax, metric, title in [
        (ax1, "H_strict_max_run", "H* strict (max-run)"),
        (ax2, "H_relax",          "H* relax"),
    ]:
        vals_lags  = [_get_hstar(s, "lags_only",  metric) for s in stations]
        vals_meteo = [_get_hstar(s, "lags_meteo", metric) for s in stations]

        b1 = ax.bar(x - width / 2, vals_lags,  width, color=COLOR_LAGS,
                    alpha=0.85, label="Lags only",  zorder=3)
        b2 = ax.bar(x + width / 2, vals_meteo, width, color=COLOR_METEO,
                    alpha=0.85, label="Lags + met.", zorder=3)

        for bars in (b1, b2):
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.2,
                        str(int(h)), ha="center", va="bottom",
                        fontsize=7, color="#333333")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=TICK_FS)
        ax.set_title(title, fontsize=LABEL_FS, loc="left")
        ax.set_ylim(0, 27)
        ax.set_yticks([0, 6, 12, 18, 24])
        ax.yaxis.grid(True, lw=0.5, color="#eeeeee", zorder=0)
        ax.set_axisbelow(True)
        ax.axhline(0, color="#999999", lw=0.6)

    ax1.set_ylabel("H* (hours)", fontsize=LABEL_FS)
    ax1.legend(fontsize=LEG_FS, loc="upper center", bbox_to_anchor=(1.0, -0.25), ncol=2)
    fig.suptitle("H* summary — Ireland PM10, 2023 (regenerated bundle)", fontsize=LABEL_FS + 1)
    MANUSCRIPT_FIGS.mkdir(parents=True, exist_ok=True)
    _save(fig, MANUSCRIPT_FIGS, "ireland_figure_hstar_summary")
    plt.close(fig)


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate E2-MET Ireland manuscript figures.")
    parser.add_argument("--config", default="code/e2_met_ireland_config.json")
    args = parser.parse_args()

    config = load_json_config(args.config)
    paths = ensure_results_dirs(config["results_dir"])
    fig_dir = paths["base"] / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    tables = paths["manuscript_tables"]

    # Figures 1-3 (skill, delta-skill, DM) are out of scope for the P3 controlled
    # repair and are only regenerated when the original-tree manuscript tables are
    # present. Figure 4 (H* summary) is the in-scope canonical repair: it reads
    # the regenerated bundle directly and writes to manuscripts/figures/.
    try:
        metrics = pd.read_csv(tables / "table_metrics_long.csv")
        delta   = pd.read_csv(tables / "table_delta_skill_meteo_vs_lags.csv")
        dm      = pd.read_csv(tables / "table_dm_lags_meteo_vs_lags_only.csv")
        print("Figure 1: skill by station...")
        make_fig1(metrics, fig_dir)
        print("Figure 2: delta skill...")
        make_fig2(delta, fig_dir)
        print("Figure 3: DM significance...")
        make_fig3(dm, delta, fig_dir)
    except FileNotFoundError as exc:
        print(f"Figures 1-3 skipped (source table absent, out of P3 repair scope): {exc}")

    print("Figure 4: H* summary (canonical, regenerated bundle -> manuscript)...")
    make_fig4(None, fig_dir)

    print(f"\nDone. Canonical H* figure written under: {MANUSCRIPT_FIGS}")


if __name__ == "__main__":
    main()
