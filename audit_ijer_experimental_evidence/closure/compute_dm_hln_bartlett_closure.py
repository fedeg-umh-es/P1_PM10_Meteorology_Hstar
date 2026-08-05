#!/usr/bin/env python3
import sys
import json
import math
import pandas as pd
import numpy as np
from scipy.stats import t as student_t

def adjust_bh(p_values):
    """Benjamini-Hochberg adjusted p-values (step-up procedure)."""
    m = len(p_values)
    if m == 0:
        return []
    
    sorted_indices = sorted(range(m), key=lambda i: p_values[i])
    sorted_p = [p_values[i] for i in sorted_indices]
    
    adjusted = [0.0] * m
    cum_min = 1.0
    for i in range(m - 1, -1, -1):
        rank = i + 1
        adj = sorted_p[i] * m / rank
        cum_min = min(cum_min, adj)
        adjusted[sorted_indices[i]] = min(1.0, cum_min)
        
    return adjusted

def main():
    madrid_path = "results/e2_met_madrid_pm10/predictions/predictions_all_models.csv"
    ireland_path = "results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv"
    
    m_df = pd.read_csv(madrid_path)
    i_df = pd.read_csv(ireland_path)
    
    schema_doc = """# Canonical Input Schema Mapping

## Madrid Dataset
- Path: `results/e2_met_madrid_pm10/predictions/predictions_all_models.csv`
- Station Column: (Implicit) "Madrid"
- Origin Column: `origin`
- Forecast Timestamp Column: `forecast_timestamp`
- Horizon Column: `horizon`
- Condition Column: `condition` (values: `reference`, `lags_only`, `lags_meteo`)
- Model Column: `model` (values: `persistence`, `sarima`, `xgboost_direct`)
- Observed Column: `y_true`
- Predicted Column: `y_pred`

## Ireland Dataset
- Path: `results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv`
- Station Column: `station`
- Origin Column: `origin`
- Forecast Timestamp Column: `forecast_timestamp`
- Horizon Column: `horizon`
- Condition Column: `condition` (values: `reference`, `lags_meteo`, `lags_only`)
- Model Column: `model` (values: `persistence`, `sarima`, `xgboost_direct`)
- Observed Column: `y_true`
- Predicted Column: `y_pred`
"""
    with open("audit_ijer_experimental_evidence/closure/input_schema_mapping.md", "w") as f:
        f.write(schema_doc)
        
    stations_info = [("Madrid", m_df)]
    for st in i_df["station"].unique():
        stations_info.append((st, i_df[i_df["station"] == st]))
        
    horizons = [1, 6, 12, 24]
    raw_results = []
    
    for station_name, df in stations_info:
        sub = df[df["model"] == "xgboost_direct"].copy() if "model" in df.columns else df.copy()
        
        for h in horizons:
            lags_only = sub[(sub["condition"] == "lags_only") & (sub["horizon"] == h)]
            lags_meteo = sub[(sub["condition"] == "lags_meteo") & (sub["horizon"] == h)]
            
            merged = pd.merge(
                lags_only[["origin", "horizon", "y_true", "y_pred"]],
                lags_meteo[["origin", "horizon", "y_true", "y_pred"]],
                on=["origin", "horizon"],
                suffixes=("_lags_only", "_lags_meteo"),
                how="outer"
            )
            
            # Key exists in only one condition OR missing values in predictions/target
            # n_dropped = number of pairing keys present in only one condition
            keys_lo = set(zip(lags_only["origin"], lags_only["horizon"]))
            keys_lm = set(zip(lags_meteo["origin"], lags_meteo["horizon"]))
            all_keys = keys_lo.union(keys_lm)
            common_keys = keys_lo.intersection(keys_lm)
            n_dropped = len(all_keys) - len(common_keys)
            
            valid = merged.dropna(subset=["y_true_lags_only", "y_true_lags_meteo", "y_pred_lags_only", "y_pred_lags_meteo"]).copy()
            
            y_diff = (valid["y_true_lags_only"] - valid["y_true_lags_meteo"]).abs().max()
            if len(valid) > 0 and y_diff > 1e-10:
                print(f"BLOCKED_BY_INCONSISTENT_OBSERVED_VALUES: {station_name} h={h} max diff={y_diff}")
                sys.exit(1)
                
            n_pairs = int(len(valid))
            max_lag = h - 1
            
            if n_pairs <= 1:
                raw_results.append({
                    "station": station_name, "horizon": h, "n_pairs": n_pairs, "n_dropped": n_dropped,
                    "dbar": np.nan, "lrv": np.nan, "max_lag": max_lag, "dm_stat": np.nan, "hln_factor": np.nan,
                    "dm_hln_stat": np.nan, "p_raw": np.nan, "favours": "none", "status": "UNDETERMINED",
                    "status_reason": "n_pairs <= 1"
                })
                continue
                
            d_t = (valid["y_true_lags_only"] - valid["y_pred_lags_only"])**2 - (valid["y_true_lags_only"] - valid["y_pred_lags_meteo"])**2
            dbar = float(d_t.mean())
            n = n_pairs
            
            d_zero = d_t - dbar
            gamma_0 = float((d_zero**2).sum() / n)
            
            lrv_sum = gamma_0
            for k in range(1, max_lag + 1):
                gamma_k = float((d_zero.iloc[k:].values * d_zero.iloc[:-k].values).sum() / n)
                w_k = 1.0 - k / (max_lag + 1)
                lrv_sum += 2.0 * w_k * gamma_k
                
            lrv = lrv_sum
            hln_num = n + 1 - 2*h + (h*(h-1)/n)
            hln_factor = math.sqrt(hln_num / n) if hln_num > 0 else np.nan
            
            favours = "lags_meteo" if dbar > 0 else ("lags_only" if dbar < 0 else "none")
            
            if lrv <= 0 or not math.isfinite(lrv) or not math.isfinite(hln_factor):
                raw_results.append({
                    "station": station_name, "horizon": h, "n_pairs": n_pairs, "n_dropped": n_dropped,
                    "dbar": dbar, "lrv": lrv, "max_lag": max_lag, "dm_stat": np.nan, "hln_factor": hln_factor,
                    "dm_hln_stat": np.nan, "p_raw": np.nan, "favours": favours, "status": "UNDETERMINED",
                    "status_reason": "LRV <= 0 or non-finite variance/HLN factor"
                })
                continue
                
            dm_stat = dbar / math.sqrt(lrv / n)
            dm_hln_stat = dm_stat * hln_factor
            p_raw = float(2.0 * student_t.sf(abs(dm_hln_stat), df=n - 1))
            
            raw_results.append({
                "station": station_name, "horizon": h, "n_pairs": n_pairs, "n_dropped": n_dropped,
                "dbar": dbar, "lrv": lrv, "max_lag": max_lag, "dm_stat": dm_stat, "hln_factor": hln_factor,
                "dm_hln_stat": dm_hln_stat, "p_raw": p_raw, "favours": favours, "status": "OK",
                "status_reason": ""
            })

    # Multiplicity adjustments on OK rows
    ok_indices = [i for i, r in enumerate(raw_results) if r["status"] == "OK"]
    m_global_ok = len(ok_indices)
    
    global_p_raws = [raw_results[i]["p_raw"] for i in ok_indices]
    global_fdr = adjust_bh(global_p_raws)
    
    for idx_in_ok, orig_idx in enumerate(ok_indices):
        p_r = raw_results[orig_idx]["p_raw"]
        raw_results[orig_idx]["p_fdr_global"] = global_fdr[idx_in_ok]
        raw_results[orig_idx]["p_bonf_global"] = min(1.0, p_r * m_global_ok)
        
    m_by_station = {}
    for station_name, _ in stations_info:
        st_ok_indices = [i for i in ok_indices if raw_results[i]["station"] == station_name]
        m_by_station[station_name] = len(st_ok_indices)
        if len(st_ok_indices) > 0:
            st_p_raws = [raw_results[i]["p_raw"] for i in st_ok_indices]
            st_fdr = adjust_bh(st_p_raws)
            for idx_in_st, orig_idx in enumerate(st_ok_indices):
                raw_results[orig_idx]["p_fdr_station"] = st_fdr[idx_in_st]

    contract = {
        "planned_comparisons": 36,
        "m_global_ok": m_global_ok,
        "m_by_station": m_by_station
    }
    with open("results/ijer/bartlett_closure/multiplicity_contract.json", "w") as f:
        json.dump(contract, f, indent=2)
        
    final_rows = []
    for r in raw_results:
        row = {
            "station": r["station"],
            "horizon": r["horizon"],
            "n_pairs": r["n_pairs"],
            "n_dropped": r["n_dropped"],
            "dbar": "" if math.isnan(r["dbar"]) else r["dbar"],
            "lrv": "" if math.isnan(r["lrv"]) else r["lrv"],
            "max_lag": r["max_lag"],
            "dm_stat": "" if math.isnan(r["dm_stat"]) else r["dm_stat"],
            "hln_factor": "" if math.isnan(r["hln_factor"]) else r["hln_factor"],
            "dm_hln_stat": "" if math.isnan(r["dm_hln_stat"]) else r["dm_hln_stat"],
            "p_raw": "" if math.isnan(r["p_raw"]) else r["p_raw"],
            "p_fdr_station": "" if r["status"] != "OK" else r.get("p_fdr_station", ""),
            "p_fdr_global": "" if r["status"] != "OK" else r.get("p_fdr_global", ""),
            "p_bonf_global": "" if r["status"] != "OK" else r.get("p_bonf_global", ""),
            "favours": r["favours"],
            "status": r["status"],
            "status_reason": r["status_reason"]
        }
        final_rows.append(row)
        
    cols_order = [
        "station", "horizon", "n_pairs", "n_dropped", "dbar", "lrv", "max_lag",
        "dm_stat", "hln_factor", "dm_hln_stat", "p_raw", "p_fdr_station",
        "p_fdr_global", "p_bonf_global", "favours", "status", "status_reason"
    ]
    df_out = pd.DataFrame(final_rows)[cols_order]
    df_out.to_csv("results/ijer/bartlett_closure/dm_hln_bartlett_canonical.csv", index=False)
    print(f"DM Bartlett canonical CSV written ({len(df_out)} rows, {m_global_ok} OK).")

if __name__ == "__main__":
    main()
