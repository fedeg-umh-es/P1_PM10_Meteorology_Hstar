#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np

def main():
    madrid_path = "results/e2_met_madrid_pm10/predictions/predictions_all_models.csv"
    ireland_path = "results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv"
    
    m_df = pd.read_csv(madrid_path)
    i_df = pd.read_csv(ireland_path)
    
    m_df["station"] = "Madrid"
    all_df = pd.concat([m_df, i_df], ignore_index=True)
    all_df["target_dt"] = pd.to_datetime(all_df["forecast_timestamp"], format="ISO8601")
    
    # Check consistency per station + target_dt
    grouped = all_df.groupby(["station", "target_dt"])["y_true"].agg(["min", "max", "count"])
    inconsistent = grouped[(grouped["max"] - grouped["min"]) > 1e-10]
    if len(inconsistent) > 0:
        print("RHO1_BLOCKED_BY_INCONSISTENT_RECONSTRUCTED_OBSERVATIONS:")
        print(inconsistent)
        sys.exit(1)
        
    dedup = all_df[["station", "target_dt", "y_true"]].dropna(subset=["y_true"]).drop_duplicates(subset=["station", "target_dt"])
    
    window_start_str = "2023-01-01 00:00:00"
    window_end_str = "2023-07-31 23:00:00"
    window_start = pd.Timestamp(window_start_str)
    window_end = pd.Timestamp(window_end_str)
    
    win_df = dedup[(dedup["target_dt"] >= window_start) & (dedup["target_dt"] <= window_end)].copy()
    expected_hours = 5088
    
    station_order = ["Madrid"] + list(i_df["station"].unique())
    
    rows = []
    coverages = {}
    blocked = False
    
    for st in station_order:
        st_df = win_df[win_df["station"] == st].sort_values("target_dt")
        n_valid = len(st_df)
        cov = n_valid / expected_hours
        coverages[st] = cov
        if cov < 0.90:
            blocked = True
            
    for st in station_order:
        st_df = win_df[win_df["station"] == st].sort_values("target_dt")
        n_valid = len(st_df)
        cov = coverages[st]
        
        if blocked:
            rows.append({
                "station": st,
                "window_start": window_start_str,
                "window_end": window_end_str,
                "n_hours_nominal": expected_hours,
                "n_valid_observations": n_valid,
                "coverage": cov,
                "n_pairs": "",
                "rho1": ""
            })
        else:
            st_df["next_dt"] = st_df["target_dt"].shift(-1)
            st_df["next_y"] = st_df["y_true"].shift(-1)
            consec = st_df[(st_df["next_dt"] - st_df["target_dt"]) == pd.Timedelta(hours=1)]
            n_pairs = len(consec)
            rho1 = float(np.corrcoef(consec["y_true"], consec["next_y"])[0, 1]) if n_pairs > 1 else np.nan
            rows.append({
                "station": st,
                "window_start": window_start_str,
                "window_end": window_end_str,
                "n_hours_nominal": expected_hours,
                "n_valid_observations": n_valid,
                "coverage": cov,
                "n_pairs": n_pairs,
                "rho1": rho1
            })

    cols = ["station", "window_start", "window_end", "n_hours_nominal", "n_valid_observations", "coverage", "n_pairs", "rho1"]
    df_out = pd.DataFrame(rows)[cols]
    df_out.to_csv("results/ijer/bartlett_closure/rho1_common_window.csv", index=False)
    
    # Summary report
    summary_md = f"""# Rho-1 Common Window Summary

## Status
RHO1_BLOCKED_BY_INSUFFICIENT_RECONSTRUCTED_COVERAGE

## Station Coverages (Nominal hours = {expected_hours})
"""
    for st, cov in coverages.items():
        summary_md += f"- {st}: coverage = {cov:.4f} ({df_out[df_out['station']==st]['n_valid_observations'].values[0]}/{expected_hours})\n"
        
    summary_md += "\n## Verdict\n- veredicto: BLOCKED\n"
    
    with open("results/ijer/bartlett_closure/rho1_common_window_summary.md", "w") as f:
        f.write(summary_md)
        
    if blocked:
        print("RHO1_BLOCKED_BY_INSUFFICIENT_RECONSTRUCTED_COVERAGE")
        for st, cov in coverages.items():
            print(f"  {st}: {cov:.4f}")
    else:
        print("RHO1 computation completed successfully.")

if __name__ == "__main__":
    main()
