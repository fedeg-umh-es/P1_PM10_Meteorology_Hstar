#!/usr/bin/env python3
"""
e2_autocorrelation_analysis.py

Three lightweight analyses to validate the autocorrelation-persistence
mechanism claimed in the manuscript:

  1. Compute ρ₁ (lag-1 autocorrelation) for Madrid and each Irish station
     using the full training period (2020-01-01 to 2022-12-31).
  2. Print station-level ρ₁ alongside ΔH*_strict to verify the predicted
     positive association.
  3. Generate a scatter plot ρ₁ vs ΔH*_strict across all 9 sites (Figure 9
     of the manuscript).

Usage:
  python3 code/e2_autocorrelation_analysis.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# ── paths ─────────────────────────────────────────────────────────────────────

ROOT       = Path("/Users/federicogarciacrespi/Public/P1_PM10_Meteorology_Hstar")
DATA_MAD   = ROOT / "data_processed/madrid_pm10_meteorology_experiment_base.csv"
DATA_IRE   = ROOT / "data_processed/ireland_pm10_meteorology_hourly.csv"
HSTAR_MAD  = ROOT / "results/e2_met_madrid_pm10/manuscript_tables/table_hstar_summary.csv"
HSTAR_IRE  = ROOT / "results/e2_met_ireland_pm10/manuscript_tables/table_station_hstar_summary.csv"
OUT_TABLES = ROOT / "results/e2_met_madrid_pm10/manuscript_tables"
OUT_FIGS   = ROOT / "results/e2_met_madrid_pm10/figures"  # reuse Madrid figures dir

# Training period shared with both experiments
TRAIN_START = "2020-01-01"
TRAIN_END   = "2022-12-31 23:00:00"

# ── helpers ───────────────────────────────────────────────────────────────────

def lag1_autocorr(series: pd.Series) -> float:
    """Pearson lag-1 autocorrelation on non-NaN values."""
    s = series.dropna()
    return float(s.autocorr(lag=1))


# ── 1. Compute ρ₁ ─────────────────────────────────────────────────────────────

print("=" * 60)
print("1. Computing ρ₁ (lag-1 autocorrelation)")
print("=" * 60)

# Madrid
mad = pd.read_csv(DATA_MAD, parse_dates=["timestamp"])
mad = mad[(mad["timestamp"] >= TRAIN_START) & (mad["timestamp"] <= TRAIN_END)]
rho1_madrid = lag1_autocorr(mad["PM10"])
print(f"  Madrid Casa de Campo : ρ₁ = {rho1_madrid:.4f}  (n={mad['PM10'].dropna().shape[0]})")

# Ireland — per station
ire = pd.read_csv(DATA_IRE, parse_dates=["timestamp"])
ire = ire[(ire["timestamp"] >= TRAIN_START) & (ire["timestamp"] <= TRAIN_END)]

station_rho1: dict[str, float] = {}
for stn, grp in ire.groupby("station"):
    rho = lag1_autocorr(grp["PM10"])
    station_rho1[stn] = rho
    print(f"  {stn:<30s}: ρ₁ = {rho:.4f}  (n={grp['PM10'].dropna().shape[0]})")

ireland_mean_rho1 = float(np.mean(list(station_rho1.values())))
print(f"\n  Ireland mean ρ₁       : {ireland_mean_rho1:.4f}")
print(f"  Madrid ρ₁             : {rho1_madrid:.4f}")

# ── 2. ρ₁ vs ΔH*_strict per station ──────────────────────────────────────────

print("\n" + "=" * 60)
print("2. ρ₁ vs ΔH*_strict per station")
print("=" * 60)

# Ireland H* (strict, lags_meteo minus lags_only)
ire_hstar = pd.read_csv(HSTAR_IRE)
ire_lags_meteo = ire_hstar[
    (ire_hstar["condition"] == "lags_meteo") &
    (ire_hstar["model"] == "xgboost_direct")
][["station", "H_star_strict"]].rename(columns={"H_star_strict": "hstar_meteo"})

ire_lags_only = ire_hstar[
    (ire_hstar["condition"] == "lags_only") &
    (ire_hstar["model"] == "xgboost_direct")
][["station", "H_star_strict"]].rename(columns={"H_star_strict": "hstar_only"})

ire_delta = ire_lags_meteo.merge(ire_lags_only, on="station")
ire_delta["delta_hstar"] = ire_delta["hstar_meteo"] - ire_delta["hstar_only"]
ire_delta["rho1"] = ire_delta["station"].map(station_rho1)

print(f"\n  {'Station':<30s} {'ρ₁':>6} {'H*(meteo)':>10} {'H*(only)':>9} {'ΔH*':>5}")
print("  " + "-" * 65)
for _, row in ire_delta.sort_values("rho1", ascending=False).iterrows():
    print(f"  {row['station']:<30s} {row['rho1']:>6.4f} {row['hstar_meteo']:>10.0f} "
          f"{row['hstar_only']:>9.0f} {row['delta_hstar']:>5.0f}")

# Madrid row
mad_hstar_df = pd.read_csv(HSTAR_MAD)
mad_meteo = int(mad_hstar_df[
    (mad_hstar_df["condition"] == "lags_meteo") &
    (mad_hstar_df["model"] == "xgboost_direct")
]["H_star_strict"].iloc[0])
mad_only = int(mad_hstar_df[
    (mad_hstar_df["condition"] == "lags_only") &
    (mad_hstar_df["model"] == "xgboost_direct")
]["H_star_strict"].iloc[0])
mad_delta = mad_meteo - mad_only
print(f"  {'Madrid Casa de Campo':<30s} {rho1_madrid:>6.4f} {mad_meteo:>10d} "
      f"{mad_only:>9d} {mad_delta:>5d}")

# ── 3. Save table ─────────────────────────────────────────────────────────────

rows_ireland = []
for _, row in ire_delta.iterrows():
    rows_ireland.append({
        "site": row["station"],
        "country": "Ireland",
        "rho1": round(row["rho1"], 4),
        "H_star_strict_lags_only": int(row["hstar_only"]),
        "H_star_strict_lags_meteo": int(row["hstar_meteo"]),
        "delta_H_star_strict": int(row["delta_hstar"]),
    })

rows_madrid = [{
    "site": "Madrid Casa de Campo",
    "country": "Spain",
    "rho1": round(rho1_madrid, 4),
    "H_star_strict_lags_only": mad_only,
    "H_star_strict_lags_meteo": mad_meteo,
    "delta_H_star_strict": mad_delta,
}]

df_out = pd.DataFrame(rows_ireland + rows_madrid).sort_values("rho1", ascending=False)
table_path = OUT_TABLES / "table_rho1_vs_delta_hstar.csv"
df_out.to_csv(table_path, index=False)
print(f"\n  Saved: {table_path}")

# ── 4. Scatter plot ρ₁ vs ΔH*_strict ─────────────────────────────────────────

print("\n" + "=" * 60)
print("3. Generating scatter plot ρ₁ vs ΔH*_strict")
print("=" * 60)

COLOR_IRE = "#2166ac"
COLOR_MAD = "#d6604d"
MS        = 9
LABEL_FS  = 10
TICK_FS   = 9
LEG_FS    = 9

plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.size":         10,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.linewidth":    1.0,
    "axes.labelsize":    LABEL_FS,
    "axes.titlesize":    LABEL_FS,
    "xtick.labelsize":   TICK_FS,
    "ytick.labelsize":   TICK_FS,
    "legend.frameon":    False,
    "legend.fontsize":   LEG_FS,
})

# Manual label offsets (x_pt, y_pt) to avoid overlaps.
# Key challenge: Birr/Dublin Airport share ρ₁≈0.815; Pearse/Ringsend ≈0.842-0.843;
# all with ΔH*=0 except Dublin Airport (ΔH*=1).
LABEL_OFFSETS = {
    # station_name          : (dx_points, dy_points, ha)
    "Edenderry":   (-48,  8,  "left"),
    "Birr":        (-10, -16, "center"),   # below
    "Dublin Airp.":( 6,   5,  "left"),    # above-right
    "Pearse St.":  (-48, -16, "left"),    # below-left
    "Ringsend":    (-48,  8,  "left"),    # above-left
    "Portlaoise":  (  6, -16, "left"),    # below-right
    "Henry St.":   (  6,   5, "left"),    # above-right
    "Dundalk":     (  6, -16, "left"),    # below-right
    "Madrid":      (  6,   5, "left"),    # above-right
}

STATION_SHORT = {
    "Birr co offlay":        "Birr",
    "Dublin Airport":        "Dublin Airp.",
    "Dundalk Co Louth":      "Dundalk",
    "Pearse street dublin":  "Pearse St.",
    "Ringsend dublin":       "Ringsend",
    "edenderry co offlay":   "Edenderry",
    "henry street Limerick": "Henry St.",
    "porrlaoise co laois":   "Portlaoise",
    "Madrid Casa de Campo":  "Madrid",
}

# OLS first (need r/p for legend)
all_rho   = list(ire_delta["rho1"]) + [rho1_madrid]
all_delta = list(ire_delta["delta_hstar"].astype(float)) + [float(mad_delta)]
slope, intercept, r_val, p_val, _ = stats.linregress(all_rho, all_delta)
print(f"  OLS: slope={slope:.2f}, intercept={intercept:.2f}, "
      f"r={r_val:.3f}, p={p_val:.4f}")

fig, ax = plt.subplots(figsize=(8.5, 5.5))

# OLS line
x_line = np.linspace(min(all_rho) - 0.008, max(all_rho) + 0.008, 200)
ax.plot(x_line, slope * x_line + intercept,
        color="#aaaaaa", lw=1.3, ls="--", zorder=2)

ax.axhline(0, color="black", lw=0.7, ls=":", zorder=1)

def _annotate(ax, label, x, y, color):
    dx, dy, ha = LABEL_OFFSETS.get(label, (6, 5, "left"))
    ax.annotate(
        label,
        xy=(x, y),
        xytext=(dx, dy),
        textcoords="offset points",
        fontsize=8,
        color=color,
        ha=ha,
        va="center",
        arrowprops=dict(arrowstyle="-", color="#bbbbbb", lw=0.7)
        if abs(dx) > 10 or abs(dy) > 10 else None,
    )

# Ireland points
for _, row in ire_delta.iterrows():
    ax.plot(row["rho1"], row["delta_hstar"],
            "o", color=COLOR_IRE, ms=MS, mew=0, alpha=0.85, zorder=3)
    label = STATION_SHORT.get(row["station"], row["station"])
    _annotate(ax, label, row["rho1"], row["delta_hstar"], "#333333")

# Madrid point
ax.plot(rho1_madrid, mad_delta,
        "s", color=COLOR_MAD, ms=MS + 2, mew=0, alpha=0.90, zorder=4)
_annotate(ax, "Madrid", rho1_madrid, mad_delta, "#8b1a00")

from matplotlib.lines import Line2D
legend_handles = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_IRE,
           ms=MS, label="Ireland stations"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor=COLOR_MAD,
           ms=MS + 1, label="Madrid"),
    Line2D([0], [0], color="#aaaaaa", lw=1.3, ls="--",
           label=f"OLS  ($r = {r_val:.2f}$,  $p = {p_val:.2f}$, $n = 9$)"),
]
ax.legend(handles=legend_handles, fontsize=LEG_FS, loc="upper left")

ax.set_xlabel("Lag-1 autocorrelation $\\rho_1$ of hourly PM$_{10}$ (training period)",
              fontsize=LABEL_FS)
ax.set_ylabel("$\\Delta H^*_{\\mathrm{strict}}$ (h)  [lags+met $-$ lags only]",
              fontsize=LABEL_FS)
ax.set_title("Boundary-layer persistence regime and PM$_{10}$ forecast horizon gain",
             fontsize=LABEL_FS)
ax.set_ylim(-2.5, max(all_delta) + 3)
ax.set_xlim(min(all_rho) - 0.015, max(all_rho) + 0.015)

fig.tight_layout()

fig_path_png = OUT_FIGS / "figure_rho1_vs_delta_hstar.png"
fig_path_pdf = OUT_FIGS / "figure_rho1_vs_delta_hstar.pdf"
fig.savefig(fig_path_png, dpi=600, bbox_inches="tight")
fig.savefig(fig_path_pdf, bbox_inches="tight")
plt.close(fig)
print(f"  Saved: {fig_path_png}")
print(f"  Saved: {fig_path_pdf}")

print("\nDone.")
