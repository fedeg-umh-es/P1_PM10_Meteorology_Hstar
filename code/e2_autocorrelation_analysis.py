#!/usr/bin/env python3
"""
e2_autocorrelation_analysis.py

Render the manuscript scatter of lag-1 autocorrelation (rho_1) against the
meteorology benefit Delta H*_strict (max-run definition) across the nine sites
(Madrid + eight Irish stations), producing:

    manuscripts/figures/figure_rho1_vs_delta_hstar.png  (+ .pdf)

CANONICAL DATA SOURCE (P3 canon v1.3; decision 2026-08-01-hstar-strict-definition)
----------------------------------------------------------------------------------
This script reads the versioned canonical nine-site table

    results/derived/nine_site_rho1_delta_hstar.csv

with columns:
    site, country, rho1,
    H_strict_max_run_lags_only, H_strict_max_run_lags_meteo,
    delta_H_strict_max_run, provenance

Provenance of that table:
  * H_strict_max_run values: Ireland from the regenerated bundle
    (results/e2_met_ireland_pm10_regenerated, regenerated-not-original);
    Madrid from results/e2_met_madrid_pm10 tracked outputs.
  * rho1 values: the canonical nine-site table. The raw hourly PM10 series
    (processed panels) are NOT present in this clone, so rho1 is NOT recomputed
    here from time series. The correlation coefficient r is recomputed from the
    canonical table; the two-sided p-value is INHERITED from the canon/validated
    prior analysis (raw-series recomputation unavailable in this clone).

Canonical statistics (do not overwrite with a recomputed p):
    n = 9,  r = 0.554715 (-> 0.555),  p = 0.121110 (-> 0.121)

This script does NOT read absent processed datasets and does NOT read the
obsolete original Ireland results tree. It performs no model run.

Usage:
    python3 code/e2_autocorrelation_analysis.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

# ── repo-relative paths (script lives in <repo>/code) ─────────────────────────
REPO      = Path(__file__).resolve().parents[1]
TABLE     = REPO / "results/derived/nine_site_rho1_delta_hstar.csv"
OUT_FIGS  = REPO / "manuscripts/figures"

# Canonical statistics. r is recomputed below and cross-checked against R_CANON;
# p is inherited (the raw series required to recompute it are absent here).
R_CANON = 0.554715
P_CANON = 0.121110
N_CANON = 9

# ── load canonical nine-site table ────────────────────────────────────────────
rows = list(csv.DictReader(open(TABLE, newline="")))
if len(rows) != N_CANON:
    raise SystemExit(f"Expected {N_CANON} sites, found {len(rows)} in {TABLE}")

site      = [r["site"] for r in rows]
country   = [r["country"] for r in rows]
rho1      = np.array([float(r["rho1"]) for r in rows])
delta     = np.array([float(r["delta_H_strict_max_run"]) for r in rows])

# ── recompute r from the table; inherit p ─────────────────────────────────────
r_recomputed = float(np.corrcoef(rho1, delta)[0, 1])
if abs(r_recomputed - R_CANON) > 1e-4:
    raise SystemExit(
        f"Recomputed r={r_recomputed:.6f} disagrees with canon {R_CANON:.6f}; "
        "aborting rather than publishing an inconsistent figure."
    )
# OLS line coefficients (numpy polyfit; no scipy dependency)
slope, intercept = np.polyfit(rho1, delta, 1)
r_val, p_val = R_CANON, P_CANON
print(f"n={N_CANON}  r={r_val:.6f} (recomputed {r_recomputed:.6f})  "
      f"p={p_val:.6f} (inherited from canon; raw-series recomputation unavailable)")

# ── plot ──────────────────────────────────────────────────────────────────────
COLOR_IRE = "#2166ac"
COLOR_MAD = "#d6604d"
MS = 9
LABEL_FS, TICK_FS, LEG_FS = 10, 9, 9

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 1.0, "axes.labelsize": LABEL_FS, "axes.titlesize": LABEL_FS,
    "xtick.labelsize": TICK_FS, "ytick.labelsize": TICK_FS,
    "legend.frameon": False, "legend.fontsize": LEG_FS,
})

SHORT = {
    "Madrid Casa de Campo": "Madrid",
    "Dundalk (Co. Louth)": "Dundalk",
    "Henry St. Limerick": "Henry St.",
    "Portlaoise (Co. Laois)": "Portlaoise",
    "Ringsend Dublin": "Ringsend",
    "Pearse St. Dublin": "Pearse St.",
    "Dublin Airport": "Dublin Airp.",
    "Birr (Co. Offaly)": "Birr",
    "Edenderry (Co. Offaly)": "Edenderry",
}
LABEL_OFFSETS = {
    "Edenderry": (6, 8, "left"), "Birr": (-10, -16, "center"),
    "Dublin Airp.": (6, 5, "left"), "Pearse St.": (-48, -16, "left"),
    "Ringsend": (-48, 8, "left"), "Portlaoise": (6, -16, "left"),
    "Henry St.": (6, 5, "left"), "Dundalk": (6, -16, "left"), "Madrid": (6, 5, "left"),
}

def _annotate(ax, label, x, y, color):
    dx, dy, ha = LABEL_OFFSETS.get(label, (6, 5, "left"))
    ax.annotate(label, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
                fontsize=8, color=color, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color="#bbbbbb", lw=0.7)
                if abs(dx) > 10 or abs(dy) > 10 else None)

fig, ax = plt.subplots(figsize=(8.5, 5.5))
x_line = np.linspace(rho1.min() - 0.008, rho1.max() + 0.008, 200)
ax.plot(x_line, slope * x_line + intercept, color="#aaaaaa", lw=1.3, ls="--", zorder=2)
ax.axhline(0, color="black", lw=0.7, ls=":", zorder=1)

for s, c, d in zip(site, country, delta):
    x, y = rho1[site.index(s)], d
    if country[site.index(s)] == "Spain":
        ax.plot(x, y, "s", color=COLOR_MAD, ms=MS + 2, mew=0, alpha=0.90, zorder=4)
        _annotate(ax, "Madrid", x, y, "#8b1a00")
    else:
        ax.plot(x, y, "o", color=COLOR_IRE, ms=MS, mew=0, alpha=0.85, zorder=3)
        _annotate(ax, SHORT.get(s, s), x, y, "#333333")

legend_handles = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_IRE, ms=MS, label="Ireland stations"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor=COLOR_MAD, ms=MS + 1, label="Madrid"),
    Line2D([0], [0], color="#aaaaaa", lw=1.3, ls="--",
           label=f"OLS  ($r = {r_val:.3f}$,  $p = {p_val:.3f}$, $n = {N_CANON}$)"),
]
ax.legend(handles=legend_handles, fontsize=LEG_FS, loc="upper left")
ax.set_xlabel("Lag-1 autocorrelation $\\rho_1$ of hourly PM$_{10}$ (training period)", fontsize=LABEL_FS)
ax.set_ylabel("$\\Delta H^*_{\\mathrm{strict,max\\text{-}run}}$ (h)  [lags+met $-$ lags only]", fontsize=LABEL_FS)
ax.set_title("Boundary-layer persistence regime and PM$_{10}$ forecast horizon gain", fontsize=LABEL_FS)
ax.set_ylim(-2.5, float(delta.max()) + 3)
ax.set_xlim(rho1.min() - 0.015, rho1.max() + 0.015)
fig.tight_layout()

OUT_FIGS.mkdir(parents=True, exist_ok=True)
png = OUT_FIGS / "figure_rho1_vs_delta_hstar.png"
pdf = OUT_FIGS / "figure_rho1_vs_delta_hstar.pdf"
fig.savefig(png, dpi=600, bbox_inches="tight")
fig.savefig(pdf, bbox_inches="tight")
plt.close(fig)
print(f"  saved: {png}")
print(f"  saved: {pdf}")
print("Done.")
