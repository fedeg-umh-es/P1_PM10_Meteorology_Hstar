import json
import hashlib
from pathlib import Path

REPO = Path("/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland")
OUT_DIR = REPO / "results" / "audit_canonical"

def sha256(p):
    path = REPO / p if not str(p).startswith("/") else Path(p)
    if not path.exists(): return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = {
    "repository": "P1_PM10_Meteorology_Hstar",
    "working_directory": str(REPO),
    "git_branch": "codex/p1-editorial-computational-audit",
    "git_head_commit": "5596c1c87f8c466813a87f1305a2bbf377d7a98a",
    "audit_timestamp": "2026-08-02T17:00:00Z",
    "environment": {
        "python_version": "3.9.6",
        "pandas_version": "2.3.3",
        "numpy_version": "2.0.2",
        "scipy_version": "1.13.1",
        "statsmodels_version": "0.14.6",
        "xgboost_version": "2.1.4",
        "scikit_learn_version": "1.6.1",
        "random_seed": 42
    },
    "canonical_datasets_and_predictions": {
        "madrid_predictions": {
            "path": "results/e2_met_madrid_pm10/predictions/predictions_all_models.csv",
            "sha256": sha256("results/e2_met_madrid_pm10/predictions/predictions_all_models.csv")
        },
        "ireland_predictions": {
            "path": "results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv",
            "sha256": sha256("results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv")
        },
        "ireland_inventory": {
            "path": "reports/ireland_dataset_inventory.csv",
            "sha256": sha256("reports/ireland_dataset_inventory.csv")
        }
    },
    "canonical_tables": {
        "table_1": {
            "csv": "results/audit_canonical/table_1_descriptive_statistics.csv",
            "sha256": sha256("results/audit_canonical/table_1_descriptive_statistics.csv")
        },
        "table_3": {
            "csv": "results/audit_canonical/table_3_madrid_dm.csv",
            "sha256": sha256("results/audit_canonical/table_3_madrid_dm.csv")
        },
        "table_4": {
            "csv": "results/audit_canonical/table_4_ireland_hstar.csv",
            "sha256": sha256("results/audit_canonical/table_4_ireland_hstar.csv")
        },
        "table_5": {
            "csv": "results/audit_canonical/table_5_ireland_dm.csv",
            "sha256": sha256("results/audit_canonical/table_5_ireland_dm.csv")
        },
        "table_6": {
            "csv": "results/audit_canonical/table_6_rho1_hstar.csv",
            "sha256": sha256("results/audit_canonical/table_6_rho1_hstar.csv")
        }
    },
    "canonical_audit_outputs": {
        "temporal_contract_audit": "results/audit_canonical/temporal_contract_audit.csv",
        "origin_accounting": "results/audit_canonical/origin_accounting.csv",
        "data_completeness": "results/audit_canonical/data_completeness_by_station.csv",
        "hstar_run_boundaries": "results/audit_canonical/hstar_run_boundaries.csv",
        "dm_hln_results": "results/audit_canonical/dm_hln_results.csv",
        "rho1_analysis": "results/audit_canonical/rho1_delta_hstar_analysis.csv",
        "overleaf_handoff_report": "results/audit_canonical/P1_OVERLEAF_HANDOFF.md"
    },
    "test_suite": {
        "test_file": "tests/test_audit_pipeline.py",
        "sha256": sha256("tests/test_audit_pipeline.py"),
        "result": "PASSED (3/3 unit tests)"
    },
    "verdict": "VERIFIED_WITH_DOCUMENTATION_ERRORS",
    "limits_and_rules_enforced": {
        "modified_latex_files": "NO",
        "modified_bib_files": "NO",
        "created_commit": "YES",
        "push_performed": "NO"
    }
}

with open(OUT_DIR / "P1_CANONICAL_RESULTS_MANIFEST.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("P1_CANONICAL_RESULTS_MANIFEST.json written successfully.")
