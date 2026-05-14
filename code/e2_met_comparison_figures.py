#!/usr/bin/env python3
"""
e2_met_comparison_figures.py

Cross-city comparison figures: Madrid (single station) vs Ireland (8 stations).

Figure 1  figure_comparison_skill      — Skill(h) vs persistence: Madrid | Ireland mean±SD
Figure 2  figure_comparison_delta      — ΔSkill(h): Madrid line + Ireland station lines + mean
Figure 3  figure_comparison_hstar      — H*_strict bar chart: Madrid vs Ireland stations

Outputs: results/comparison_madrid_ireland/figures/

Usage:
  python3 code/e2_met_comparison_figures.py
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

# ── paths ──────────────────────────────────────────────────────────────────────

REPO = Path(__file__).resolve().parents[1]

MADRID_TABLES  = REPO / "results" / "e2_met_madrid_pm10"  / "manuscript_tables"
IRELAND_TABLES = REPO / "results" / "e2_met_ireland_pm10" / "manuscript_tables"
FIG_DIR        = REPO / "results" / "comparison_madrid_ireland" / "figures"

# ── style ──────────────────────────────────────────────────────────────────────

COLOR_LAGS  = "#2166ac"
COLOR_METEO = "#d6604d"
COLOR_MAD   = "#333333"    # Madrid reference line
ALPHA_BAND  = 0.18
LW_BOLD     = 2.2
LW_THIN     = 1.1
LW_MEAN     = 1.8
TICK_FS     = 9
LABEL_FS    = 10
TITLE_FS    = 10
LEG_FS      = 9

STATION_SHORT = {
    "Birr co offlay":       "Birr",
    "Dublin Airport":       "Dublin Airport",
    "Dundalk Co Louth":     "Dundalk",
    "Pearse street dublin": "Pearse St.",
    "Ringsend dublin":      "Ringsend",
    "edenderry co offlay":  "Edenderry",
    "henry street Limerick":"Limerick",
    "porrlaoise co laois":  "Portlaoise",
}

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


def _save(fig: plt.Figure, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        p = FIG_DIR / f"{name}.{ext}"
        fig.savefig(p, dpi=600 if ext == "png" else None, bbox_inches="tight")
        print(f"  saved: {p}")


# ── data loaders ───────────────────────────────────────────────────────────────

def load_madrid() -> dict[str, pd.DataFrame]:
    return {
        "metrics": pd.read_csv(MADRID_TABLES / "table_metrics_long.csv"),
        "hstar":   pd.read_csv(MADRID_TABLES / "table_hstar_summary.csv"),
        "delta":   pd.read_csv(MADRID_TABLES / "table_delta_lags_meteo_vs_lags_only.csv"),
        "dm":      pd.read_csv(MADRID_TABLES / "table_dm_lags_meteo_vs_lags_only.csv"),
    }


def load_ireland() -> dict[str, pd.DataFrame]:
    return {
        "metrics": pd.read_csv(IRELAND_TABLES / "table_metrics_long.csv"),
        "hstar":   pd.read_csv(IRELAND_TABLES / "table_station_hstar_summary.csv"),
        "delta":   pd.read_csv(IRELAND_TABLES / "table_delta_skill_meteo_vs_lags.csv"),
        "dm":      pd.read_csv(IRELAND_TABLES / "table_dm_lags_meteo_vs_lags_only.csv"),
    }


def _ireland_skill_stats(metrics: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Per-horizon mean and std of skill across Ireland stations, by condition."""
    xgb = metrics[metrics["model"] == "xgboost_direct"].copy()
    out = {}
    for cond in ("lags_only", "lags_meteo"):
        sub = xgb[xgb["condition"] == cond]
        agg = sub.groupby("horizon")["skill_rmse_vs_persistence"].agg(["mean", "std"]).reset_index()
        agg.columns = ["horizon", "mean", "std"]
        out[cond] = agg
    return out


# ── Figure 1: Skill(h) — Madrid | Ireland mean±SD ─────────────────────────────

def make_fig1(madrid: dict, ireland: dict) -> None:
    mad_xgb = madrid["metrics"][madrid["metrics"]["model"] == "xgboost_direct"]
    ire_stats = _ireland_skill_stats(ireland["metrics"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True,
                                    constrained_layout=True)

    # ── left: Madrid ──────────────────────────────────────────────────────────
    for cond, color, label, ls in [
        ("lags_only",  COLOR_LAGS,  "Lags only",  "-"),
        ("lags_meteo", COLOR_METEO, "Lags + met.", "--"),
    ]:
        sub = mad_xgb[mad_xgb["condition"] == cond].sort_values("horizon")
        ax1.plot(sub["horizon"], sub["skill_rmse_vs_persistence"],
                 color=color, lw=LW_BOLD, ls=ls, label=label)

    ax1.axhline(0, color="black", lw=0.7, ls=":", zorder=0)
    ax1.set_xlim(1, 24)
    ax1.set_xticks([1, 6, 12, 18, 24])
    ax1.set_xlabel("h (hours)", fontsize=LABEL_FS)
    ax1.set_ylabel("Skill vs persistence (RMSE)", fontsize=LABEL_FS)
    ax1.set_title("A — Madrid (Casa de Campo)", fontsize=TITLE_FS, loc="left")
    ax1.legend(fontsize=LEG_FS)

    # ── right: Ireland mean ± SD ───────────────────────────────────────────────
    for cond, color, label, ls in [
        ("lags_only",  COLOR_LAGS,  "Lags only (mean±SD)",  "-"),
        ("lags_meteo", COLOR_METEO, "Lags + met. (mean±SD)", "--"),
    ]:
        agg = ire_stats[cond].sort_values("horizon")
        h   = agg["horizon"].values
        mu  = agg["mean"].values
        sd  = agg["std"].values
        ax2.plot(h, mu, color=color, lw=LW_BOLD, ls=ls, label=label)
        ax2.fill_between(h, mu - sd, mu + sd, color=color, alpha=ALPHA_BAND)

    ax2.axhline(0, color="black", lw=0.7, ls=":", zorder=0)
    ax2.set_xlim(1, 24)
    ax2.set_xticks([1, 6, 12, 18, 24])
    ax2.set_xlabel("h (hours)", fontsize=LABEL_FS)
    ax2.set_title("B — Ireland (8 stations, mean ± 1 SD)", fontsize=TITLE_FS, loc="left")
    ax2.legend(fontsize=LEG_FS)

    fig.suptitle("Skill score vs persistence — Madrid and Ireland PM10, 2023",
                 fontsize=LABEL_FS + 1)
    _save(fig, "figure_comparison_skill")
    plt.close(fig)


# ── Figure 2: ΔSkill(h) — Madrid + Ireland stations + Ireland mean ────────────

def make_fig2(madrid: dict, ireland: dict) -> None:
    mad_delta = madrid["delta"].copy()
    ire_delta = ireland["delta"].copy()

    stations = sorted(ire_delta["station"].unique())

    fig, ax = plt.subplots(figsize=(8.0, 4.5))

    # Ireland stations — thin lines
    for i, stn in enumerate(stations):
        sub = ire_delta[ire_delta["station"] == stn].sort_values("horizon")
        ax.plot(sub["horizon"], sub["delta_skill_rmse_meteo_minus_lags"],
                color=TAB10[i % len(TAB10)], lw=LW_THIN, alpha=0.55,
                label=STATION_SHORT.get(stn, stn))

    # Ireland mean — bold dashed
    ire_mean = (
        ire_delta.groupby("horizon")["delta_skill_rmse_meteo_minus_lags"]
        .mean().reset_index()
    )
    ax.plot(ire_mean["horizon"], ire_mean["delta_skill_rmse_meteo_minus_lags"],
            color="#555555", lw=LW_MEAN, ls="--", label="Ireland mean", zorder=4)

    # Madrid — bold solid black
    ax.plot(mad_delta["horizon"], mad_delta["delta_skill_rmse_meteo_minus_lags"],
            color=COLOR_MAD, lw=LW_BOLD, ls="-", label="Madrid", zorder=5)

    ax.axhline(0, color="black", lw=0.8, ls=":", zorder=0)
    ax.set_xlim(1, 24)
    ax.set_xticks([1, 6, 12, 18, 24])
    ax.set_xlabel("Forecast horizon h (hours)", fontsize=LABEL_FS)
    ax.set_ylabel("ΔSkill_RMSE (lags+met − lags only)", fontsize=LABEL_FS)
    ax.set_title("Meteorology benefit — Madrid vs Ireland PM10, 2023",
                 fontsize=LABEL_FS + 1)

    # split legend: Ireland stations in 2 cols + summary lines
    handles, labels = ax.get_legend_handles_labels()
    # last two handles are Ireland mean + Madrid
    station_h, station_l = handles[:-2], labels[:-2]
    extra_h, extra_l = handles[-2:], labels[-2:]
    leg1 = ax.legend(station_h, station_l, loc="upper right",
                     ncol=2, fontsize=LEG_FS - 1, title="Ireland stations",
                     title_fontsize=LEG_FS - 1)
    ax.add_artist(leg1)
    ax.legend(extra_h, extra_l, loc="lower right", fontsize=LEG_FS)

    fig.tight_layout()
    _save(fig, "figure_comparison_delta")
    plt.close(fig)


# ── Figure 3: H*_strict — Madrid vs Ireland stations ─────────────────────────

def make_fig3(madrid: dict, ireland: dict) -> None:
    mad_hstar = madrid["hstar"]
    ire_hstar = ireland["hstar"]

    stations = sorted(ire_hstar["station"].unique())
    n_ire = len(stations)

    # Build value arrays
    def _mad(cond: str, metric: str) -> int:
        row = mad_hstar[
            (mad_hstar["model"] == "xgboost_direct") &
            (mad_hstar["condition"] == cond)
        ]
        return int(row.iloc[0][metric]) if not row.empty else 0

    def _ire(stn: str, cond: str, metric: str) -> int:
        row = ire_hstar[
            (ire_hstar["station"] == stn) &
            (ire_hstar["model"] == "xgboost_direct") &
            (ire_hstar["condition"] == cond)
        ]
        return int(row.iloc[0][metric]) if not row.empty else 0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2), constrained_layout=True)

    for ax, metric, panel_title in [
        (ax1, "H_star_strict", "A — H* strict"),
        (ax2, "H_star_relax",  "B — H* relax"),
    ]:
        # x positions: Madrid | gap | Ireland stations
        gap = 0.8
        x_mad = np.array([0.0, 0.5])                              # Madrid 2 bars
        x_ire = np.arange(n_ire) * 0.9 + x_mad[-1] + gap + 0.45  # Ireland bars (pairs)
        width = 0.35

        # Madrid bars
        v_mad_lo = _mad("lags_only",  metric)
        v_mad_me = _mad("lags_meteo", metric)
        b1 = ax.bar(x_mad[0], v_mad_lo, width, color=COLOR_LAGS,  alpha=0.9, zorder=3)
        b2 = ax.bar(x_mad[1], v_mad_me, width, color=COLOR_METEO, alpha=0.9, zorder=3)

        # Ireland bars (pairs per station)
        for i, stn in enumerate(stations):
            xi = x_ire[i]
            v_lo = _ire(stn, "lags_only",  metric)
            v_me = _ire(stn, "lags_meteo", metric)
            ax.bar(xi - width / 2, v_lo, width, color=COLOR_LAGS,  alpha=0.75, zorder=3)
            ax.bar(xi + width / 2, v_me, width, color=COLOR_METEO, alpha=0.75, zorder=3)

        # value labels
        for bar in ax.patches:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.2,
                        str(int(h)), ha="center", va="bottom",
                        fontsize=6.5, color="#333333")

        # separator line between Madrid and Ireland
        sep_x = (x_mad[-1] + x_ire[0] - width / 2) / 2 + 0.15
        ax.axvline(sep_x, color="#cccccc", lw=1.0, ls="--")

        # x-ticks
        x_all = np.concatenate([[np.mean(x_mad)], x_ire])
        labels_all = ["Madrid"] + [STATION_SHORT.get(s, s) for s in stations]
        ax.set_xticks(x_all)
        ax.set_xticklabels(labels_all, rotation=30, ha="right", fontsize=TICK_FS)
        ax.set_ylim(0, 27)
        ax.set_yticks([0, 6, 12, 18, 24])
        ax.yaxis.grid(True, lw=0.5, color="#eeeeee", zorder=0)
        ax.set_axisbelow(True)
        ax.set_title(panel_title, fontsize=LABEL_FS, loc="left")

    ax1.set_ylabel("H* (hours)", fontsize=LABEL_FS)

    legend_handles = [
        Line2D([0], [0], color=COLOR_LAGS,  lw=6, alpha=0.85, label="Lags only"),
        Line2D([0], [0], color=COLOR_METEO, lw=6, alpha=0.85, label="Lags + met."),
    ]
    ax1.legend(handles=legend_handles, fontsize=LEG_FS, loc="lower left")
    fig.suptitle("H* comparison — Madrid and Ireland PM10, 2023", fontsize=LABEL_FS + 1)
    _save(fig, "figure_comparison_hstar")
    plt.close(fig)


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    for path, name in [(MADRID_TABLES, "Madrid"), (IRELAND_TABLES, "Ireland")]:
        if not path.exists():
            raise FileNotFoundError(
                f"{name} tables not found at {path}\n"
                "Run e2_met_madrid_run.py and e2_met_ireland_run.py first."
            )

    print("Loading Madrid results...")
    madrid = load_madrid()
    print("Loading Ireland results...")
    ireland = load_ireland()

    mad_origins = madrid["metrics"]["n_eval"].max()
    print(f"  Madrid n_eval max: {mad_origins}")

    print("\nFigure 1: skill curves comparison...")
    make_fig1(madrid, ireland)

    print("Figure 2: delta skill comparison...")
    make_fig2(madrid, ireland)

    print("Figure 3: H* comparison...")
    make_fig3(madrid, ireland)

    print(f"\nDone. Figures in: {FIG_DIR}")


if __name__ == "__main__":
    main()
