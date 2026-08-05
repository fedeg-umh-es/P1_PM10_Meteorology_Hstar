#!/usr/bin/env python3
import sys
import shutil
import hashlib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def calc_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def get_star(p_st, p_gl, p_bf):
    if pd.isna(p_bf) or p_bf == "":
        return ""
    p_bf = float(p_bf)
    p_gl = float(p_gl)
    p_st = float(p_st)
    if p_bf < 0.05:
        return "***"
    elif p_gl < 0.05:
        return "**"
    elif p_st < 0.05:
        return "*"
    return ""

def main():
    table_src = "manuscripts/tables/ijer/table_4_dm_summary.tex"
    fig_src = "manuscripts/figures/ijer/figure_3_dm_heatmap.pdf"
    
    table_dst = "results/ijer/bartlett_closure/superseded_rectangular/table_4_dm_summary_rectangular.tex"
    fig_dst = "results/ijer/bartlett_closure/superseded_rectangular/figure_3_dm_heatmap_rectangular.pdf"
    
    shutil.copy2(table_src, table_dst)
    shutil.copy2(fig_src, fig_dst)
    
    table_sha_old = calc_sha256(table_dst)
    fig_sha_old = calc_sha256(fig_dst)
    print(f"Saved superseded table (SHA256: {table_sha_old})")
    print(f"Saved superseded figure (SHA256: {fig_sha_old})")
    
    df = pd.read_csv("results/ijer/bartlett_closure/dm_hln_bartlett_canonical.csv")
    
    display_names = {
        "Madrid": "Madrid",
        "Birr co offlay": "Birr (Co. Offaly)",
        "Dublin Airport": "Dublin Airport",
        "Dundalk Co Louth": "Dundalk (Co. Louth)",
        "Pearse street dublin": "Pearse Street (Dublin)",
        "Ringsend dublin": "Ringsend (Dublin)",
        "edenderry co offlay": "Edenderry (Co. Offaly)",
        "henry street Limerick": "Henry Street (Limerick)",
        "porrlaoise co laois": "Portlaoise (Co. Laois)"
    }
    
    table_render_rows = []
    for idx, r in df.iterrows():
        st = r["station"]
        h = int(r["horizon"])
        dm_raw = float(r["dm_hln_stat"]) if pd.notna(r["dm_hln_stat"]) and r["dm_hln_stat"] != "" else np.nan
        p_raw = float(r["p_raw"]) if pd.notna(r["p_raw"]) and r["p_raw"] != "" else np.nan
        p_st = float(r["p_fdr_station"]) if pd.notna(r["p_fdr_station"]) and r["p_fdr_station"] != "" else np.nan
        p_gl = float(r["p_fdr_global"]) if pd.notna(r["p_fdr_global"]) and r["p_fdr_global"] != "" else np.nan
        p_bf = float(r["p_bonf_global"]) if pd.notna(r["p_bonf_global"]) and r["p_bonf_global"] != "" else np.nan
        status = r["status"]
        star = get_star(p_st, p_gl, p_bf) if status == "OK" else ""
        
        table_render_rows.append({
            "station": st,
            "horizon": h,
            "dm_hln_stat": "" if np.isnan(dm_raw) else f"{dm_raw:.6f}",
            "p_raw": "" if np.isnan(p_raw) else f"{p_raw:.4f}",
            "p_fdr_station": "" if np.isnan(p_st) else f"{p_st:.4f}",
            "p_fdr_global": "" if np.isnan(p_gl) else f"{p_gl:.4f}",
            "p_bonf_global": "" if np.isnan(p_bf) else f"{p_bf:.4f}",
            "significance_marker": star,
            "status": status
        })
        
    df_table_render = pd.DataFrame(table_render_rows)
    df_table_render.to_csv("results/ijer/bartlett_closure/table_4_render_data.csv", index=False)
    
    ok_count = len(df[df["status"] == "OK"])
    undet_count = len(df[df["status"] != "OK"])
    m_global = ok_count
    
    undet_str = f", undetermined: {undet_count}" if undet_count > 0 else ""
    caption_text = r"\caption{Summary of Diebold--Mariano (DM-HLN) statistical significance tests across nine stations ($h \in \{1, 6, 12, 24\}$). Statistics employ a Bartlett/Newey--West kernel with $\text{max\_lag} = h - 1$, Harvey--Leybourne--Newbold (HLN) finite-sample correction, and two-tailed Student's $t$-distribution ($df = n-1$). $p$-values are reported unadjusted ($p_{\text{raw}}$), under station-level FDR ($p_{\text{fdr,station}}$), global FDR ($p_{\text{fdr,global}}$), and global Bonferroni correction ($p_{\text{bonf,global}}$ over $m=" + str(m_global) + r"$ valid tests). Asterisks indicate significance: $^*p_{\text{fdr,station}} < 0.05$, $^{**}p_{\text{fdr,global}} < 0.05$, $^{***}p_{\text{bonf,global}} < 0.05$. Total valid tests: " + str(ok_count) + r"/36" + undet_str + r".}"
    
    tex_lines = [
        r"\begin{table*}[t]",
        r"\centering",
        caption_text,
        r"\label{tab:dm_summary}",
        r"\small",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lrrllll}",
        r"\toprule",
        r"Station & $h$ & DM Stat & $p_{\text{raw}}$ & $p_{\text{fdr,station}}$ & $p_{\text{fdr,global}}$ & $p_{\text{bonf,global}}$ \\",
        r"\midrule"
    ]
    
    current_st = None
    for idx, r in df_table_render.iterrows():
        st = r["station"]
        disp_st = display_names.get(st, st)
        if current_st is not None and st != current_st:
            tex_lines.append(r"\midrule")
        current_st = st
        
        h = r["horizon"]
        dm = float(r["dm_hln_stat"]) if r["dm_hln_stat"] != "" else np.nan
        dm_str = f"{dm:.2f}" if not np.isnan(dm) else "N/A"
        p_raw = r["p_raw"]
        p_st = r["p_fdr_station"]
        p_gl = r["p_fdr_global"]
        p_bf = r["p_bonf_global"]
        star = r["significance_marker"]
        
        if r["status"] != "OK":
            tex_lines.append(rf"{disp_st} & {h} & \text{{N/A}} & \text{{N/A}} & \text{{N/A}} & \text{{N/A}} & \text{{N/A}} \\")
        else:
            p_bf_str = f"{p_bf}{star}" if star else p_bf
            tex_lines.append(rf"{disp_st} & {h} & {dm_str} & {p_raw} & {p_st} & {p_gl} & {p_bf_str} \\")
            
    tex_lines.extend([
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{table*}"
    ])
    
    with open("manuscripts/tables/ijer/table_4_dm_summary.tex", "w") as f:
        f.write("\n".join(tex_lines) + "\n")
        
    print("Regenerated manuscripts/tables/ijer/table_4_dm_summary.tex")
    
    # 3. Figure 3 Heatmap
    fig_render_rows = []
    stations_unique = list(df["station"].unique())
    horizons_unique = [1, 6, 12, 24]
    
    matrix = np.full((len(stations_unique), len(horizons_unique)), np.nan)
    markers = [["" for _ in range(len(horizons_unique))] for _ in range(len(stations_unique))]
    statuses = [["" for _ in range(len(horizons_unique))] for _ in range(len(stations_unique))]
    
    for i, st in enumerate(stations_unique):
        for j, h in enumerate(horizons_unique):
            match = df[(df["station"] == st) & (df["horizon"] == h)]
            if len(match) > 0:
                row = match.iloc[0]
                status = row["status"]
                statuses[i][j] = status
                if status == "OK":
                    dm_val = float(row["dm_hln_stat"])
                    matrix[i, j] = dm_val
                    p_st = float(row["p_fdr_station"])
                    p_gl = float(row["p_fdr_global"])
                    p_bf = float(row["p_bonf_global"])
                    star = get_star(p_st, p_gl, p_bf)
                    markers[i][j] = star
                else:
                    matrix[i, j] = np.nan
                    markers[i][j] = ""
            else:
                statuses[i][j] = "UNDETERMINED"
                
            fig_render_rows.append({
                "station": st,
                "horizon": h,
                "dm_hln_stat": "" if np.isnan(matrix[i, j]) else f"{matrix[i, j]:.6f}",
                "significance_marker": markers[i][j],
                "status": statuses[i][j]
            })
            
    df_fig_render = pd.DataFrame(fig_render_rows)
    df_fig_render.to_csv("results/ijer/bartlett_closure/figure_3_dm_heatmap_render_data.csv", index=False)
    
    plt.figure(figsize=(8, 6), dpi=300)
    cmap = plt.cm.coolwarm.copy()
    cmap.set_bad(color="lightgrey")
    
    masked_matrix = np.ma.masked_invalid(matrix)
    max_val = max(abs(np.nanmin(matrix)), abs(np.nanmax(matrix)))
    im = plt.imshow(masked_matrix, cmap=cmap, vmin=-max_val, vmax=max_val, aspect="auto")
    
    cbar = plt.colorbar(im)
    cbar.set_label("DM-HLN Statistic\n(> 0 favours lags_meteo, < 0 favours lags_only)", rotation=270, labelpad=25)
    
    plt.xticks(range(len(horizons_unique)), [f"h={h}" for h in horizons_unique])
    plt.yticks(range(len(stations_unique)), [display_names.get(st, st) for st in stations_unique])
    
    for i in range(len(stations_unique)):
        for j in range(len(horizons_unique)):
            status = statuses[i][j]
            if status == "OK":
                val = matrix[i, j]
                star = markers[i][j]
                text_str = f"{val:.2f}{star}"
                plt.text(j, i, text_str, ha="center", va="center", color="black", fontsize=9, fontweight="bold" if star else "normal")
            else:
                plt.text(j, i, "N/A", ha="center", va="center", color="gray", fontsize=9, linestyle="italic")
                
    plt.title("Diebold--Mariano DM-HLN Heatmap (Bartlett Kernel)")
    plt.tight_layout()
    plt.savefig("manuscripts/figures/ijer/figure_3_dm_heatmap.pdf", format="pdf")
    plt.close()
    
    print("Regenerated manuscripts/figures/ijer/figure_3_dm_heatmap.pdf")

if __name__ == "__main__":
    main()
