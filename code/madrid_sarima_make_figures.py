"""
madrid_sarima_make_figures.py
------------------------------
Generate canonical manuscript figures for the Madrid E2-MET paper.

Input tables (results/madrid_sarima/):
  - skill_ci_panel_A.csv   : skill + 95% bootstrap CI vs persistence (C1,C2,C3)
  - skill_ci_panel_B.csv   : skill + 95% bootstrap CI vs SARIMA (C1,C2,C3)
  - dm_results_panel_A.csv : DM test results vs persistence (all conditions incl. SARIMA)
  - dm_results_panel_B.csv : DM test results vs SARIMA (C1,C2,C3)
  - metrics_sarima.csv     : horizon-wise SARIMA vs persistence skill
  - hstar_summary_sarima.csv : H* strict/relax summary table

Outputs (results/madrid_sarima/figures/):
  - figure_skill_vs_persistence.{png,pdf}
  - figure_skill_vs_sarima.{png,pdf}
  - figure_dm_vs_persistence.{png,pdf}
  - figure_dm_vs_sarima.{png,pdf}
  - figure_hstar_summary.{png,pdf}
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# ── paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR   = os.path.join(REPO_ROOT, "results", "madrid_sarima")
FIG_DIR   = os.path.join(RES_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ── load data ─────────────────────────────────────────────────────────────────
ci_A  = pd.read_csv(os.path.join(RES_DIR, "skill_ci_panel_A.csv"))   # vs persistence
ci_B  = pd.read_csv(os.path.join(RES_DIR, "skill_ci_panel_B.csv"))   # vs SARIMA
dm_A  = pd.read_csv(os.path.join(RES_DIR, "dm_results_panel_A.csv")) # vs persistence
dm_B  = pd.read_csv(os.path.join(RES_DIR, "dm_results_panel_B.csv")) # vs SARIMA
met   = pd.read_csv(os.path.join(RES_DIR, "metrics_sarima.csv"))
hstar = pd.read_csv(os.path.join(RES_DIR, "hstar_summary_sarima.csv"))

# ── style constants ────────────────────────────────────────────────────────────
COLORS = {
    "C1":     "#2166ac",
    "C2":     "#d6604d",
    "C3":     "#4dac26",
    "SARIMA": "#756bb1",
}
LINESTYLES = {"C1": "-", "C2": "-", "C3": "--", "SARIMA": ":"}
ALPHA_CI   = 0.15
LW         = 2.0
TICK_FS    = 11
LABEL_FS   = 12
LEGEND_FS  = 11
TITLE_FS   = 14
MARKER_MS  = 8

plt.rcParams.update({
    "font.family":      "sans-serif",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.size":        12,
    "axes.titlesize":   TITLE_FS,
    "axes.labelsize":   LABEL_FS,
    "axes.linewidth":   1.2,
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "xtick.major.width":1.0,
    "ytick.major.width":1.0,
    "xtick.labelsize":  TICK_FS,
    "ytick.labelsize":  TICK_FS,
    "legend.frameon":   False,
    "legend.fontsize":  LEGEND_FS,
    "text.color":       "#000000",
    "axes.labelcolor":  "#000000",
    "axes.edgecolor":   "#000000",
    "xtick.color":      "#000000",
    "ytick.color":      "#000000",
})

HORIZONS = np.arange(1, 25)

def _save(fig, name):
    for ext in ("png", "pdf"):
        path = os.path.join(FIG_DIR, f"{name}.{ext}")
        if ext == "png":
            fig.savefig(path, dpi=600, bbox_inches="tight")
        else:
            fig.savefig(path, bbox_inches="tight")
        print(f"  saved: {path}")

# ──────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — Skill(h) vs persistence
# ──────────────────────────────────────────────────────────────────────────────
def make_fig1():
    fig, ax = plt.subplots(figsize=(6.5, 4.0))

    # SARIMA from metrics table
    sarima_skill = met.set_index("horizon")["skill_sarima_vs_persist"]

    # plot SARIMA reference (no CI available from bootstrap for SARIMA, use DM table)
    ax.plot(sarima_skill.index, sarima_skill.values,
            color=COLORS["SARIMA"], lw=LW, ls=LINESTYLES["SARIMA"],
            zorder=2, label="SARIMA")

    for cond in ["C1", "C2", "C3"]:
        sub = ci_A[ci_A["condition"] == cond].sort_values("horizon")
        h   = sub["horizon"].values
        sk  = sub["skill_mean"].values
        lo  = sub["ci_lower"].values
        hi  = sub["ci_upper"].values
        ax.plot(h, sk, color=COLORS[cond], lw=LW, ls=LINESTYLES[cond],
                zorder=3, label=cond)
        ax.fill_between(h, lo, hi, color=COLORS[cond], alpha=ALPHA_CI, zorder=1)

    # h=5–10 shading (conservative annotation)
    ax.axvspan(5, 10, color="gold", alpha=0.10, zorder=0, label="h = 5–10")

    ax.axhline(0, color="black", lw=0.8, ls="--", zorder=2)
    ax.set_xlim(1, 24)
    ax.set_xlabel("Forecast horizon h (hours)", fontsize=LABEL_FS)
    ax.set_ylabel("Skill score (vs persistence)", fontsize=LABEL_FS)
    ax.set_title("Skill vs persistence — Madrid station 24, 2023", fontsize=LABEL_FS)
    ax.legend(loc="lower left", ncol=2)
    ax.set_xticks([1, 5, 10, 15, 20, 24])

    fig.tight_layout()
    _save(fig, "figure_skill_vs_persistence")
    plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Skill(h) vs SARIMA
# ──────────────────────────────────────────────────────────────────────────────
def make_fig2():
    fig, ax = plt.subplots(figsize=(6.5, 4.0))

    for cond in ["C1", "C2", "C3"]:
        sub = ci_B[ci_B["condition"] == cond].sort_values("horizon")
        h   = sub["horizon"].values
        sk  = sub["skill_mean"].values
        lo  = sub["ci_lower"].values
        hi  = sub["ci_upper"].values
        ax.plot(h, sk, color=COLORS[cond], lw=LW, ls=LINESTYLES[cond],
                zorder=3, label=cond)
        ax.fill_between(h, lo, hi, color=COLORS[cond], alpha=ALPHA_CI, zorder=1)

    ax.axvspan(5, 10, color="gold", alpha=0.10, zorder=0, label="h = 5–10")
    ax.axhline(0, color="black", lw=0.8, ls="--", zorder=2)
    ax.set_xlim(1, 24)
    ax.set_xlabel("Forecast horizon h (hours)", fontsize=LABEL_FS)
    ax.set_ylabel("Skill score (vs SARIMA)", fontsize=LABEL_FS)
    ax.set_title("Skill vs SARIMA — Madrid station 24, 2023", fontsize=LABEL_FS)
    ax.legend(loc="lower left", ncol=2)
    ax.set_xticks([1, 5, 10, 15, 20, 24])

    fig.tight_layout()
    _save(fig, "figure_skill_vs_sarima")
    plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# FIGURE 3A / 3B — DM significance figures (split for manuscript legibility)
# ──────────────────────────────────────────────────────────────────────────────
def _build_dm_lookups():
    rows_A = ["SARIMA", "C1", "C2", "C3"]
    rows_B = ["C1", "C2", "C3"]

    lk_A = {}
    for _, row in dm_A.iterrows():
        cond = row["condition"] if "condition" in dm_A.columns else None
        h = int(row["horizon"])
        lk_A[(cond, h)] = (
            row["skill"],
            str(row["significant_0.05"]).lower() == "true",
        )

    for _, row in met.iterrows():
        h = int(row["horizon"])
        lk_A[("SARIMA", h)] = (row["skill_sarima_vs_persist"], None)

    sarima_in_dm_A = dm_A[dm_A["condition"].str.upper() == "SARIMA"] if "condition" in dm_A.columns else pd.DataFrame()
    if not sarima_in_dm_A.empty:
        for _, row in sarima_in_dm_A.iterrows():
            h = int(row["horizon"])
            lk_A[("SARIMA", h)] = (
                row["skill"],
                str(row["significant_0.05"]).lower() == "true",
            )

    lk_B = {}
    for _, row in dm_B.iterrows():
        cond = row["condition"]
        h = int(row["horizon"])
        lk_B[(cond, h)] = (
            row["skill"],
            str(row["significant_0.05"]).lower() == "true",
        )

    return rows_A, rows_B, lk_A, lk_B


def _skill_color(sk):
    if sk is None:
        return "#aaaaaa"
    if sk > 0.02:
        return "#2ca25f"
    if sk < -0.02:
        return "#de2d26"
    return "#aaaaaa"


def _dm_legend_elements():
    return [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#2ca25f",
               markersize=9, label="positive skill, DM p < 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               markersize=9, markeredgecolor="#2ca25f", markeredgewidth=1.4,
               label="positive skill, DM p ≥ 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               markersize=9, markeredgecolor="#de2d26", markeredgewidth=1.4,
               label="negative skill, DM p ≥ 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#de2d26",
               markersize=9, label="negative skill, DM p < 0.05"),
        Line2D([0], [0], marker="x", color="#bdbdbd", linestyle="None",
               markersize=8, markeredgewidth=1.2, label="no data"),
        mpatches.Patch(facecolor="#f6e27a", alpha=0.55, label="highlighted interval h = 5–10"),
    ]


def _make_dm_single_figure(rows, lk, title, output_name):
    fig, ax = plt.subplots(figsize=(7.2, 5.2))

    for ri, row_label in enumerate(rows):
        for h in HORIZONS:
            val = lk.get((row_label, h), None)
            if val is None:
                ax.plot(h, ri, "x", color="#bdbdbd", ms=6, mew=1.2, zorder=2)
                continue
            sk, sig = val
            c = _skill_color(sk)
            if sig:
                ax.plot(h, ri, "o", color=c, ms=MARKER_MS, zorder=3, mew=0)
            else:
                ax.plot(h, ri, "o", color="white", ms=MARKER_MS, zorder=3, mew=1.4, mec=c)

    ax.axvspan(4.5, 10.5, color="#f6e27a", alpha=0.20, zorder=0)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=TICK_FS)
    ax.set_xlim(0.5, 24.5)
    ax.set_xticks([1, 5, 10, 15, 20, 24])
    ax.set_xlabel("Forecast horizon h (hours)", fontsize=LABEL_FS)
    ax.axhline(-0.5, color="#d9d9d9", lw=0.8)
    for r in range(len(rows) - 1):
        ax.axhline(r + 0.5, color="#d9d9d9", lw=0.8)
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.8)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", pad=4)

    fig.legend(
        handles=_dm_legend_elements(),
        loc="lower center",
        bbox_to_anchor=(0.5, 0.02),
        fontsize=LEGEND_FS,
        ncol=2,
        frameon=False,
        columnspacing=1.6,
        handletextpad=0.6,
    )
    fig.suptitle(
        f"{title} — Madrid station 24, 2023\n"
        r"$\bf{shaded:}$" + " h = 5–10 (strong-claim window)",
        fontsize=TITLE_FS - 1, y=0.97,
    )
    fig.subplots_adjust(left=0.12, right=0.98, top=0.82, bottom=0.28)
    _save(fig, output_name)
    plt.close(fig)


def make_fig3():
    rows_A, rows_B, lk_A, lk_B = _build_dm_lookups()
    _make_dm_single_figure(rows_A, lk_A, "DM significance vs persistence", "figure_dm_vs_persistence")
    _make_dm_single_figure(rows_B, lk_B, "DM significance vs SARIMA", "figure_dm_vs_sarima")

# ──────────────────────────────────────────────────────────────────────────────
# FIGURE 4 — H* summary bar chart
# ──────────────────────────────────────────────────────────────────────────────
def make_fig4():
    """
    Compact grouped bar chart comparing H*_strict and H*_relax.
    Two sub-groups: vs persistence, vs SARIMA.
    """
    # canonical values from task spec (match hstar_summary_sarima.csv + SARIMA vs SARIMA from spec)
    # hstar_summary_sarima.csv has vs-persistence rows; for vs-SARIMA we read from the spec
    hstar_spec = {
        # (model, baseline): (strict, relax)
        ("SARIMA", "persistence"): (10, 21),
        ("C1",     "persistence"): (9, 15),
        ("C2",     "persistence"): (17, 23),
        ("C3",     "persistence"): (16, 16),
        ("C1",     "SARIMA"):      (9, 15),
        ("C2",     "SARIMA"):      (14, 23),
        ("C3",     "SARIMA"):      (14, 16),
    }

    # read from file and cross-check
    for _, row in hstar.iterrows():
        key = (row["model"], row["baseline"])
        if key in hstar_spec:
            file_strict = int(row["hstar_strict"])
            file_relax  = int(row["hstar_relax"])
            spec_strict, spec_relax = hstar_spec[key]
            if file_strict != spec_strict or file_relax != spec_relax:
                print(f"  WARNING: mismatch for {key}: file=({file_strict},{file_relax}), "
                      f"spec=({spec_strict},{spec_relax}) — using spec values")

    models_A = ["SARIMA", "C1", "C2", "C3"]
    models_B = ["C1", "C2", "C3"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.8),
                                    sharey=True, gridspec_kw={"wspace": 0.08})

    bar_width = 0.35
    x_A = np.arange(len(models_A))
    x_B = np.arange(len(models_B))

    for ax, models, xs, baseline, title in [
        (ax1, models_A, x_A, "persistence", "A — vs persistence"),
        (ax2, models_B, x_B, "SARIMA",      "B — vs SARIMA"),
    ]:
        strict_vals = [hstar_spec[(m, baseline)][0] for m in models]
        relax_vals  = [hstar_spec[(m, baseline)][1] for m in models]

        b1 = ax.bar(xs - bar_width/2, strict_vals, bar_width,
                    label="H* strict", color="#2166ac", alpha=0.85, zorder=3)
        b2 = ax.bar(xs + bar_width/2, relax_vals, bar_width,
                    label="H* relax",  color="#d6604d", alpha=0.85, zorder=3)

        for bars in [b1, b2]:
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.3,
                        str(int(h)), ha="center", va="bottom",
                        fontsize=8, color="#333333")

        ax.set_xticks(xs)
        ax.set_xticklabels(models, fontsize=TICK_FS)
        ax.set_title(title, fontsize=LABEL_FS, loc="left")
        ax.axhline(0, color="#999999", lw=0.6)
        ax.set_ylim(0, 26)
        ax.set_yticks([0, 5, 10, 15, 20, 24])
        ax.yaxis.grid(True, lw=0.5, color="#eeeeee", zorder=0)
        ax.set_axisbelow(True)

    ax1.set_ylabel("H* (horizon)", fontsize=LABEL_FS)
    ax1.legend(fontsize=LEGEND_FS, loc="upper left")
    fig.suptitle("H* summary — Madrid station 24, 2023", fontsize=LABEL_FS, y=1.01)
    fig.tight_layout()
    _save(fig, "figure_hstar_summary")
    plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating manuscript figures...")
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    print("Done.")
