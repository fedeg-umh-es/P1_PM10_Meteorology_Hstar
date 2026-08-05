#!/usr/bin/env python3
import sys
import re
import pandas as pd
import numpy as np

def main():
    canonical_path = "results/ijer/bartlett_closure/dm_hln_bartlett_canonical.csv"
    table_render_path = "results/ijer/bartlett_closure/table_4_render_data.csv"
    fig_render_path = "results/ijer/bartlett_closure/figure_3_dm_heatmap_render_data.csv"
    tex_path = "manuscripts/tables/ijer/table_4_dm_summary.tex"
    
    df_canon = pd.read_csv(canonical_path)
    df_tbl = pd.read_csv(table_render_path)
    df_fig = pd.read_csv(fig_render_path)
    
    discrepancies = []
    
    # 1. Check Table Render Data against Canonical
    if len(df_tbl) != len(df_canon):
        discrepancies.append(f"Table render row count mismatch: {len(df_tbl)} vs canonical {len(df_canon)}")
    else:
        for i in range(len(df_canon)):
            c_row = df_canon.iloc[i]
            t_row = df_tbl.iloc[i]
            
            if c_row["station"] != t_row["station"] or int(c_row["horizon"]) != int(t_row["horizon"]):
                discrepancies.append(f"Row {i} key mismatch: ({t_row['station']}, {t_row['horizon']}) vs canonical ({c_row['station']}, {c_row['horizon']})")
                
            c_status = c_row["status"]
            t_status = t_row["status"]
            if c_status != t_status:
                discrepancies.append(f"Row {i} status mismatch: {t_status} vs canonical {c_status}")
                
            if c_status == "OK":
                c_dm = float(c_row["dm_hln_stat"])
                t_dm = float(t_row["dm_hln_stat"])
                if not np.isclose(c_dm, t_dm, atol=1e-3):
                    discrepancies.append(f"Row {i} ({c_row['station']} h={c_row['horizon']}) DM stat mismatch: render {t_dm} vs canonical {c_dm}")

    # 2. Check Figure Render Data against Canonical
    if len(df_fig) != len(df_canon):
        discrepancies.append(f"Figure render row count mismatch: {len(df_fig)} vs canonical {len(df_canon)}")
    else:
        for i in range(len(df_canon)):
            c_row = df_canon.iloc[i]
            f_row = df_fig.iloc[i]
            
            if c_row["station"] != f_row["station"] or int(c_row["horizon"]) != int(f_row["horizon"]):
                discrepancies.append(f"Fig Row {i} key mismatch: ({f_row['station']}, {f_row['horizon']}) vs canonical ({c_row['station']}, {c_row['horizon']})")
                
            c_status = c_row["status"]
            f_status = f_row["status"]
            if c_status != f_status:
                discrepancies.append(f"Fig Row {i} status mismatch: {f_status} vs canonical {c_status}")
                
            if c_status == "OK":
                c_dm = float(c_row["dm_hln_stat"])
                f_dm = float(f_row["dm_hln_stat"])
                if not np.isclose(c_dm, f_dm, atol=1e-3):
                    discrepancies.append(f"Fig Row {i} ({c_row['station']} h={c_row['horizon']}) DM stat mismatch: render {f_dm} vs canonical {c_dm}")

    # 3. Check TeX Table Content against Canonical
    with open(tex_path, "r") as f:
        tex_content = f.read()
        
    for i in range(len(df_canon)):
        c_row = df_canon.iloc[i]
        c_status = c_row["status"]
        if c_status == "OK":
            c_dm_str = f"{float(c_row['dm_hln_stat']):.2f}"
            if c_dm_str not in tex_content:
                discrepancies.append(f"TeX missing DM stat '{c_dm_str}' for {c_row['station']} h={c_row['horizon']}")

    if len(discrepancies) == 0:
        print("TABLE_FIGURE_CONSISTENT_WITH_CANONICAL_CSV")
        sys.exit(0)
    else:
        print("INCONSISTENCY_DETECTED:")
        for d in discrepancies:
            print(f"  - {d}")
        sys.exit(1)

if __name__ == "__main__":
    main()
