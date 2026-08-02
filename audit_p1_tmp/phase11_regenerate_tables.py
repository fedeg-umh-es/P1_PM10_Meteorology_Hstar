"""P1 audit — Phase 11: regenerate canonical tables as CSV + Markdown
(no LaTeX). Sources are the already-audited/verified predictions and
metrics under results/. Read-only w.r.t. those inputs; writes to
audit_p1_tmp/tables_out/.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "code"))

from unittest.mock import MagicMock

try:
    import xgboost  # noqa: F401
except Exception:
    sys.modules["xgboost"] = MagicMock()

from e2_met_madrid_shared import (  # noqa: E402
    compute_ceiling_flag,
    diebold_mariano_test,
)

OUT = Path(__file__).resolve().parent / "tables_out"
OUT.mkdir(exist_ok=True)

HEAD_SHA = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO).decode().strip()
NOW = datetime.now(timezone.utc).isoformat()


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _to_markdown_table(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in row.tolist()) + " |")
    return "\n".join(lines)


def write_csv_and_md(df: pd.DataFrame, name: str, caption: str, source_files: list[Path]) -> dict:
    csv_path = OUT / f"{name}.csv"
    md_path = OUT / f"{name}.md"
    df.to_csv(csv_path, index=False)
    with md_path.open("w") as f:
        f.write(f"# {caption}\n\n")
        f.write(_to_markdown_table(df))
        f.write("\n\n---\n")
        f.write(f"- producer: `audit_p1_tmp/phase11_regenerate_tables.py`\n")
        f.write(f"- HEAD SHA: `{HEAD_SHA}`\n")
        f.write(f"- generated: {NOW}\n")
        for sf in source_files:
            f.write(f"- source: `{sf.relative_to(REPO)}` sha256=`{sha256_of(sf)}`\n")
    return {
        "output_csv": str(csv_path.relative_to(REPO)),
        "output_csv_sha256": sha256_of(csv_path),
        "output_md": str(md_path.relative_to(REPO)),
        "sources": [
            {"path": str(sf.relative_to(REPO)), "sha256": sha256_of(sf)} for sf in source_files
        ],
        "head_sha": HEAD_SHA,
        "generated_at": NOW,
    }


manifest_entries: list[dict] = []

# ── Table 3 — Madrid DM-HLN (recomputed from row-level predictions) ─────
madrid_pred_path = REPO / "results/e2_met_madrid_pm10/predictions/predictions_all_models.csv"
madrid_pred = pd.read_csv(madrid_pred_path, parse_dates=["origin", "forecast_timestamp"])
lags_only = madrid_pred[(madrid_pred["condition"] == "lags_only") & (madrid_pred["model"] == "xgboost_direct")]
lags_meteo = madrid_pred[(madrid_pred["condition"] == "lags_meteo") & (madrid_pred["model"] == "xgboost_direct")]

rows = []
n_tests = 4
for h in [1, 6, 12, 24]:
    r = diebold_mariano_test(lags_only, lags_meteo, horizon=h, loss="squared_error")
    rows.append(
        {
            "horizon": h,
            "n": r["n"],
            "dm_statistic": round(r["dm_stat"], 4),
            "p_value": round(r["p_value"], 4),
            "p_value_bonferroni_adjusted": round(min(1.0, r["p_value"] * n_tests), 4),
            "favours": r["favours"],
        }
    )
table3 = pd.DataFrame(rows)
manifest_entries.append(
    write_csv_and_md(
        table3,
        "table_3_madrid_dm",
        "Table 3 — DM-HLN test results for Madrid: lags + met. vs. lags only "
        "(recomputed from row-level predictions; note NOTE below on the "
        "evaluation-window discrepancy)",
        [madrid_pred_path],
    )
)

# ── Table 4 — Ireland H* by station, with a real (computed) ceiling flag ─
ireland_pred_path = REPO / "results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv"
ireland_pred = pd.read_csv(ireland_pred_path, parse_dates=["origin", "forecast_timestamp"])


def hstar_for(df: pd.DataFrame, condition: str, model: str) -> pd.Series:
    sub = df[(df["condition"] == condition) & (df["model"] == model)].copy()
    sub["sq_err"] = (sub["y_true"] - sub["y_pred"]) ** 2
    pers = df[(df["condition"] == "reference") & (df["model"] == "persistence")].copy()
    pers["sq_err"] = (pers["y_true"] - pers["y_pred"]) ** 2
    rmse_m = sub.groupby("horizon")["sq_err"].apply(lambda s: np.sqrt(s.mean()))
    rmse_p = pers.groupby("horizon")["sq_err"].apply(lambda s: np.sqrt(s.mean()))
    skill = (1 - rmse_m / rmse_p).reindex(range(1, 25)).to_numpy()
    pos = np.where(skill > 0)[0]
    h_relax = int(pos.max() + 1) if len(pos) else 0
    best = cur = 0
    for v in skill:
        if pd.notna(v) and v > 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return pd.Series({"H_star_strict": best, "H_star_relax": h_relax})


rows4 = []
for station, g in ireland_pred.groupby("station"):
    row = {"station": station}
    for cond in ["lags_only", "lags_meteo"]:
        hs = hstar_for(g, cond, "xgboost_direct")
        row[f"H_star_strict_{cond}"] = hs["H_star_strict"]
        row[f"H_star_relax_{cond}"] = hs["H_star_relax"]
    sar = hstar_for(g, "reference", "sarima")
    row["H_star_strict_sarima"] = sar["H_star_strict"]
    row["H_star_relax_sarima"] = sar["H_star_relax"]
    row["delta_H_star_strict"] = row["H_star_strict_lags_meteo"] - row["H_star_strict_lags_only"]
    rows4.append(row)
table4 = pd.DataFrame(rows4)
table4 = compute_ceiling_flag(table4, horizon_max=24)
manifest_entries.append(
    write_csv_and_md(
        table4,
        "table_4_ireland_hstar",
        "Table 4 — H* by station/model/criterion for Ireland, with a "
        "computationally-derived ceiling flag (previously hand-typed in the "
        "manuscript; ceiling='No (submaximal tie)' distinguishes Edenderry "
        "from a true ceiling effect, per compute_ceiling_flag)",
        [ireland_pred_path],
    )
)

# ── Table 5 — Ireland DM-HLN per station ─────────────────────────────────
rows5 = []
for station, g in ireland_pred.groupby("station"):
    lo = g[(g["condition"] == "lags_only") & (g["model"] == "xgboost_direct")]
    me = g[(g["condition"] == "lags_meteo") & (g["model"] == "xgboost_direct")]
    for h in [1, 6, 12, 24]:
        r = diebold_mariano_test(lo, me, horizon=h, loss="squared_error")
        rows5.append(
            {
                "station": station,
                "horizon": h,
                "n": r["n"],
                "dm_statistic": round(r["dm_stat"], 4) if pd.notna(r["dm_stat"]) else np.nan,
                "p_value": round(r["p_value"], 4) if pd.notna(r["p_value"]) else np.nan,
                "favours": r["favours"],
            }
        )
table5 = pd.DataFrame(rows5)
manifest_entries.append(
    write_csv_and_md(
        table5,
        "table_5_ireland_dm",
        "Table 5 — DM-HLN test results for Ireland: lags + met. vs. lags only, all stations",
        [ireland_pred_path],
    )
)

# ── Table 6 — rho1 (eval-period) + H* + from-h1 + ceiling ────────────────
rows6 = []
for station, g in ireland_pred.groupby("station"):
    pers = g[(g["condition"] == "reference") & (g["model"] == "persistence")].copy()
    series = pers.drop_duplicates(subset="forecast_timestamp").set_index("forecast_timestamp")["y_true"].sort_index()
    full_idx = pd.date_range(series.index.min(), series.index.max(), freq="h")
    rho1_eval = series.reindex(full_idx).autocorr(lag=1)
    row = {"station": station, "rho1_evaluation_period_2023": round(rho1_eval, 4)}
    rows6.append(row)
table6_rho = pd.DataFrame(rows6)
table6 = table4.merge(table6_rho, on="station", how="left")
manifest_entries.append(
    write_csv_and_md(
        table6,
        "table_6_rho1_hstar",
        "Table 6 — rho1 and H* (extends Table 4 with rho1). NOTE: "
        "rho1_evaluation_period_2023 is computed from the 2023 evaluation "
        "window reconstructed from saved predictions (training-period "
        "2020-2022 rho1, as reported in the manuscript, could not be "
        "recomputed locally: data_raw/ and data_processed/ are gitignored "
        "and empty on this machine -- see P1_OVERLEAF_HANDOFF.md).",
        [ireland_pred_path],
    )
)

with (OUT / "table_manifest.json").open("w") as f:
    json.dump(manifest_entries, f, indent=2, default=str)

print(f"Wrote {len(manifest_entries)} tables to {OUT}")
for e in manifest_entries:
    print(" -", e["output_csv"])
