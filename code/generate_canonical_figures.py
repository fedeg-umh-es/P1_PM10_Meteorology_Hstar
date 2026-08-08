#!/usr/bin/env python3
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ── Style Setup ────────────────────────────────────────────────────────────────
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

REPO = Path(__file__).resolve().parents[1]
MANUSCRIPT_FIGS = REPO / "manuscripts/figures"
MANUSCRIPT_FIGS.mkdir(parents=True, exist_ok=True)

# ── Data Paths ────────────────────────────────────────────────────────────────
MADRID_METRICS = REPO / "results/regenerated_timestamp_safe/madrid/metrics_all_models.csv"
MADRID_HSTAR   = REPO / "results/regenerated_timestamp_safe/madrid/hstar_summary.csv"
GLOBAL_DM      = REPO / "results/manual_timestamp_safe_dm_global_bh.csv"

IRELAND_RMSE   = REPO / "results/regenerated_timestamp_safe/ireland/ireland_rmse_timestamp_safe.csv"
IRELAND_HSTAR  = REPO / "results/regenerated_timestamp_safe/ireland/ireland_hstar_timestamp_safe.csv"

STATION_ORDER = [
    "Birr co offlay",
    "Dublin Airport",
    "Dundalk Co Louth",
    "Pearse street dublin",
    "Ringsend dublin",
    "edenderry co offlay",
    "henry street Limerick",
    "porrlaoise co laois"
]

STATION_LABELS = {
    "Birr co offlay":       "Birr",
    "Dublin Airport":       "Dublin Airport",
    "Dundalk Co Louth":     "Dundalk",
    "Pearse street dublin": "Pearse St.",
    "Ringsend dublin":      "Ringsend",
    "edenderry co offlay":  "Edenderry",
    "henry street Limerick":"Limerick",
    "porrlaoise co laois":  "Portlaoise"
}

def save_fig(fig, name):
    for ext in ("png", "pdf"):
        p = MANUSCRIPT_FIGS / f"{name}.{ext}"
        fig.savefig(p, dpi=600 if ext == "png" else None, bbox_inches="tight")
        print(f"Saved: {p}")

# ── Figure 1: madrid_figure_skill_curves.png ─────────────────────────────────
def make_madrid_fig1():
    df = pd.read_csv(MADRID_METRICS)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    
    # Filter series
    lags_only = df[(df["condition"] == "lags_only") & (df["model"] == "xgboost_direct")].sort_values("horizon")
    lags_met = df[(df["condition"] == "lags_meteo") & (df["model"] == "xgboost_direct")].sort_values("horizon")
    sarima = df[(df["condition"] == "reference") & (df["model"] == "sarima")].sort_values("horizon")
    
    ax.plot(lags_only["horizon"], lags_only["skill_rmse_vs_persistence"], color=COLOR_LAGS, lw=LW, label="XGB lags only")
    ax.plot(lags_met["horizon"], lags_met["skill_rmse_vs_persistence"], color=COLOR_METEO, lw=LW, ls="--", label="XGB lags + met.")
    ax.plot(sarima["horizon"], sarima["skill_rmse_vs_persistence"], color=COLOR_SARIMA, lw=LW, ls=":", label="SARIMA")
    
    ax.axhline(0, color="#999999", lw=0.8, ls="--")
    ax.set_xlabel("Forecast horizon $h$ (hours)", fontsize=LABEL_FS)
    ax.set_ylabel("RMSE skill score $S(h)$", fontsize=LABEL_FS)
    ax.set_xlim(1, 24)
    ax.set_xticks([1, 6, 12, 18, 24])
    ax.set_ylim(-0.25, 0.35)
    ax.legend(loc="upper right", fontsize=LEG_FS)
    ax.set_title("Forecast skill comparison — Madrid Casa de Campo PM10", fontsize=LABEL_FS + 1, loc="left")
    save_fig(fig, "madrid_figure_skill_curves")
    plt.close(fig)

# ── Figure 2: madrid_figure_delta_skill.png ───────────────────────────────────
def make_madrid_fig2():
    df = pd.read_csv(MADRID_METRICS)
    lags_only = df[(df["condition"] == "lags_only") & (df["model"] == "xgboost_direct")].sort_values("horizon")
    lags_met = df[(df["condition"] == "lags_meteo") & (df["model"] == "xgboost_direct")].sort_values("horizon")
    
    h = lags_only["horizon"].values
    ds = lags_met["skill_rmse_vs_persistence"].values - lags_only["skill_rmse_vs_persistence"].values
    
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(h, ds, color="#333333", lw=LW)
    ax.axhline(0, color="#999999", lw=0.8, ls="--")
    
    # Fill areas
    ax.fill_between(h, ds, 0, where=(ds >= 0), color=COLOR_METEO, alpha=0.3, interpolate=True)
    ax.fill_between(h, ds, 0, where=(ds < 0), color=COLOR_LAGS, alpha=0.3, interpolate=True)
    
    ax.set_xlabel("Forecast horizon $h$ (hours)", fontsize=LABEL_FS)
    ax.set_ylabel("Pointwise skill difference $\Delta S(h)$", fontsize=LABEL_FS)
    ax.set_xlim(1, 24)
    ax.set_xticks([1, 6, 12, 18, 24])
    ax.set_ylim(-0.06, 0.16)
    ax.set_title("Pointwise meteorology benefit — Madrid Casa de Campo PM10", fontsize=LABEL_FS + 1, loc="left")
    save_fig(fig, "madrid_figure_delta_skill")
    plt.close(fig)

# ── Figure 3: madrid_figure_dm_significance.png ──────────────────────────────
def make_madrid_fig3():
    dm = pd.read_csv(GLOBAL_DM)
    dm = dm[dm["station"] == "Madrid"].sort_values("horizon")
    
    # Compute delta skill at those horizons for coloring direction
    df = pd.read_csv(MADRID_METRICS)
    delta_lk = {}
    for h in [1, 6, 12, 24]:
        lo = df[(df["condition"] == "lags_only") & (df["model"] == "xgboost_direct") & (df["horizon"] == h)].iloc[0]["skill_rmse_vs_persistence"]
        lm = df[(df["condition"] == "lags_meteo") & (df["model"] == "xgboost_direct") & (df["horizon"] == h)].iloc[0]["skill_rmse_vs_persistence"]
        delta_lk[h] = lm - lo

    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    horisons = [1, 6, 12, 24]
    
    for h in horisons:
        row = dm[dm["horizon"] == h]
        if row.empty:
            continue
        row = row.iloc[0]
        p = float(row["p_raw"]) if pd.notna(row["p_raw"]) else np.nan
        q = float(row["q_global_BH"]) if pd.notna(row["q_global_BH"]) else np.nan
        dsk = delta_lk[h]
        c = COLOR_POS if (row.get("favours") == "lags_meteo" or dsk >= 0) else COLOR_NEG
        
        # Filling MUST depend EXCLUSIVELY on q_global_BH < 0.05
        sig = (row.get("reject_global_BH") == True) or (pd.notna(q) and q < 0.05)
        
        if sig:
            ax.plot(h, 0, "o", color=c, ms=MS + 2, mew=0, zorder=3)
        else:
            ax.plot(h, 0, "o", color="white", ms=MS + 2, mew=1.6, mec=c, zorder=3)
            
        ax.annotate(f"p_raw={p:.3f}\nq_BH={q:.3f}", xy=(h, 0), xytext=(0, 14), textcoords="offset points", ha="center", fontsize=8, color="#444444")

    ax.set_xticks(horisons)
    ax.set_xticklabels([f"h={h}" for h in horisons], fontsize=TICK_FS)
    ax.set_yticks([])
    ax.set_xlabel("Forecast horizon", fontsize=LABEL_FS)
    ax.set_title("Diebold–Mariano test: lags+met vs lags only — Madrid PM10, 2023\n(Global BH across 33 valid tests)", fontsize=LABEL_FS + 1)
    ax.set_xlim(min(horisons) - 2, max(horisons) + 2)
    ax.set_ylim(-0.5, 0.5)
    ax.spines["left"].set_visible(False)
    
    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_POS, ms=MS, label="Global BH q < 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white", ms=MS, mew=1.4, mec=COLOR_POS, label="Valid, global BH q ≥ 0.05 (favours lags+met)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white", ms=MS, mew=1.4, mec=COLOR_NEG, label="Valid, global BH q ≥ 0.05 (favours lags only)"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=LEG_FS - 1)
    fig.tight_layout()
    save_fig(fig, "madrid_figure_dm_significance")
    plt.close(fig)

# ── Figure 4: madrid_figure_hstar_summary.png ─────────────────────────────────
def make_madrid_fig4():
    hstar = pd.read_csv(MADRID_HSTAR)
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
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4.0), constrained_layout=True)
    
    for ax, metric, title in [
        (ax1, "H_star_strict", "H* strict (max-run)"),
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
    fig.suptitle("H* summary — Madrid Casa de Campo PM10, 2023", fontsize=LABEL_FS + 1)
    save_fig(fig, "madrid_figure_hstar_summary")
    plt.close(fig)

# ── Figure 5: ireland_figure_skill_by_station.png ─────────────────────────────
def make_ireland_fig5():
    df = pd.read_csv(IRELAND_RMSE)
    
    fig, axes = plt.subplots(2, 4, figsize=(14, 7.5), sharex=True, sharey=True)
    axes = axes.flatten()
    
    for idx, stn in enumerate(STATION_ORDER):
        ax = axes[idx]
        stn_df = df[df["station"] == stn]
        
        lags_only = stn_df[(stn_df["condition"] == "lags_only") & (stn_df["model"] == "xgboost_direct")].sort_values("horizon")
        lags_met = stn_df[(stn_df["condition"] == "lags_meteo") & (stn_df["model"] == "xgboost_direct")].sort_values("horizon")
        
        ax.plot(lags_only["horizon"], lags_only["skill_rmse_vs_persistence"], color=COLOR_LAGS, lw=1.5, label="Lags only")
        ax.plot(lags_met["horizon"], lags_met["skill_rmse_vs_persistence"], color=COLOR_METEO, lw=1.5, ls="--", label="Lags + met.")
        
        ax.axhline(0, color="#999999", lw=0.8, ls="--")
        ax.set_xlim(1, 24)
        ax.set_xticks([1, 6, 12, 18, 24])
        ax.set_ylim(-0.25, 0.45)
        ax.yaxis.grid(True, lw=0.5, color="#eeeeee", zorder=0)
        ax.set_title(STATION_LABELS[stn], fontsize=LABEL_FS)
        
        if idx >= 4:
            ax.set_xlabel("Forecast horizon $h$ (hours)", fontsize=TICK_FS)
        if idx % 4 == 0:
            ax.set_ylabel("RMSE skill score $S(h)$", fontsize=TICK_FS)
            
    # Add a single legend for the panel
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize=LEG_FS)
    fig.suptitle("Forecast skill comparison — Ireland PM10 stations, 2023", fontsize=LABEL_FS + 2, y=0.98)
    fig.tight_layout()
    save_fig(fig, "ireland_figure_skill_by_station")
    plt.close(fig)

# ── Figure 6: ireland_figure_delta_skill.png ──────────────────────────────────
def make_ireland_fig6():
    df = pd.read_csv(IRELAND_RMSE)
    
    fig, ax = plt.subplots(figsize=(9, 5.0))
    cmap = plt.cm.tab10.colors
    
    for idx, stn in enumerate(STATION_ORDER):
        stn_df = df[df["station"] == stn]
        lags_only = stn_df[(stn_df["condition"] == "lags_only") & (stn_df["model"] == "xgboost_direct")].sort_values("horizon")
        lags_met = stn_df[(stn_df["condition"] == "lags_meteo") & (stn_df["model"] == "xgboost_direct")].sort_values("horizon")
        
        h = lags_only["horizon"].values
        ds = lags_met["skill_rmse_vs_persistence"].values - lags_only["skill_rmse_vs_persistence"].values
        
        ax.plot(h, ds, color=cmap[idx % 10], lw=LW, label=STATION_LABELS[stn])
        
    ax.axhline(0, color="#666666", lw=1.0, ls="--")
    ax.set_xlim(1, 24)
    ax.set_xticks([1, 6, 12, 18, 24])
    ax.set_xlabel("Forecast horizon $h$ (hours)", fontsize=LABEL_FS)
    ax.set_ylabel("Pointwise skill difference $\Delta S(h)$", fontsize=LABEL_FS)
    ax.set_title("Pointwise meteorology benefit across Irish network", fontsize=LABEL_FS + 1, loc="left")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=LEG_FS)
    fig.tight_layout()
    save_fig(fig, "ireland_figure_delta_skill")
    plt.close(fig)

# ── Figure 7: ireland_figure_dm_significance.png ──────────────────────────────
def make_ireland_fig7():
    dm = pd.read_csv(GLOBAL_DM)
    # Filter to only Irish stations
    dm = dm[dm["station"] != "Madrid"]
    
    # Build delta skill lookup for Ireland
    rmse_df = pd.read_csv(IRELAND_RMSE)
    delta_lk = {}
    for stn in STATION_ORDER:
        stn_df = rmse_df[rmse_df["station"] == stn]
        for h in [1, 6, 12, 24]:
            lo_rows = stn_df[(stn_df["condition"] == "lags_only") & (stn_df["model"] == "xgboost_direct") & (stn_df["horizon"] == h)]
            lm_rows = stn_df[(stn_df["condition"] == "lags_meteo") & (stn_df["model"] == "xgboost_direct") & (stn_df["horizon"] == h)]
            if not lo_rows.empty and not lm_rows.empty:
                delta_lk[(stn, h)] = lm_rows.iloc[0]["skill_rmse_vs_persistence"] - lo_rows.iloc[0]["skill_rmse_vs_persistence"]
            else:
                delta_lk[(stn, h)] = 0.0

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    horizons = [1, 6, 12, 24]
    
    for ri, stn in enumerate(STATION_ORDER):
        for h in horizons:
            # Map station name for match
            row = dm[(dm["station"].str.lower() == stn.lower()) & (dm["horizon"] == h)]
            
            # Check if test is invalid / DM undefined
            if row.empty or pd.isna(row.iloc[0]["DM"]) or pd.isna(row.iloc[0]["q_global_BH"]) or str(row.iloc[0]["favours"]) == "undetermined":
                ax.plot(h, ri, "x", color="#888888", ms=MS + 1, mew=1.8, zorder=3)
                continue
                
            row = row.iloc[0]
            q = float(row["q_global_BH"])
            reject = (row.get("reject_global_BH") == True) or (pd.notna(q) and q < 0.05)
            fav = str(row["favours"])
            
            dsk = delta_lk.get((stn, h), 0.0)
            c = COLOR_POS if (fav == "lags_meteo" or dsk >= 0) else COLOR_NEG
            
            if reject:
                ax.plot(h, ri, "o", color=c, ms=MS + 2, mew=0, zorder=4)
            else:
                ax.plot(h, ri, "o", color="white", ms=MS + 2, mew=1.6, mec=c, zorder=3)
                
    # grid lines between stations
    for r in range(len(STATION_ORDER) - 1):
        ax.axhline(r + 0.5, color="#e0e0e0", lw=0.7)
    ax.grid(axis="x", color="#e0e0e0", lw=0.7)
    
    ax.set_yticks(range(len(STATION_ORDER)))
    ax.set_yticklabels([STATION_LABELS[s] for s in STATION_ORDER], fontsize=TICK_FS)
    ax.set_xticks(horizons)
    ax.set_xticklabels([f"h={h}" for h in horizons], fontsize=TICK_FS)
    ax.set_xlabel("Forecast horizon", fontsize=LABEL_FS)
    ax.tick_params(axis="y", length=0)
    ax.set_title("Diebold–Mariano test: lags+met vs lags only — Ireland PM10, 2023\n(Global BH across 33 valid tests)", fontsize=LABEL_FS + 1)
    ax.set_xlim(min(horizons) - 2, max(horizons) + 2)
    ax.set_ylim(-0.5, len(STATION_ORDER) - 0.5)
    
    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_POS, ms=MS, label="Global BH q < 0.05"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white", ms=MS, mew=1.4, mec=COLOR_POS, label="Valid, global BH q ≥ 0.05 (favours lags+met)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white", ms=MS, mew=1.4, mec=COLOR_NEG, label="Valid, global BH q ≥ 0.05 (favours lags only)"),
        Line2D([0], [0], marker="x", color="#888888", ls="None", ms=MS, mew=1.8, label="DM undefined"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=LEG_FS - 1)
    fig.tight_layout()
    save_fig(fig, "ireland_figure_dm_significance")
    plt.close(fig)

# ── Figure 8: ireland_figure_hstar_summary.png ────────────────────────────────
def make_ireland_fig8():
    hstar = pd.read_csv(IRELAND_HSTAR)
    
    def _get_hstar(stn: str, cond: str, metric: str) -> int:
        row = hstar[(hstar["station"].str.lower() == stn.lower()) & (hstar["condition"] == cond)]
        if row.empty:
            return 0
        return int(row.iloc[0][metric])

    labels = [STATION_LABELS[s] for s in STATION_ORDER]
    x = np.arange(len(STATION_ORDER))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.0), sharey=True, gridspec_kw={"wspace": 0.06}, constrained_layout=True)
    
    for ax, metric, title in [
        (ax1, "H_strict_max_run", "H* strict (max-run)"),
        (ax2, "H_relax",          "H* relax"),
    ]:
        vals_lags  = [_get_hstar(s, "lags_only",  metric) for s in STATION_ORDER]
        vals_meteo = [_get_hstar(s, "lags_meteo", metric) for s in STATION_ORDER]
        
        b1 = ax.bar(x - width / 2, vals_lags,  width, color=COLOR_LAGS, alpha=0.85, label="Lags only",  zorder=3)
        b2 = ax.bar(x + width / 2, vals_meteo, width, color=COLOR_METEO, alpha=0.85, label="Lags + met.", zorder=3)
        
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
    save_fig(fig, "ireland_figure_hstar_summary")
    plt.close(fig)

if __name__ == "__main__":
    # ONLY regenerate the two target DM figures to leave the other six untouched
    print("Generating Figure 3 (Madrid DM)...")
    make_madrid_fig3()
    print("Generating Figure 7 (Ireland DM)...")
    make_ireland_fig7()
    print("\nDM figures corrected and saved successfully!")
