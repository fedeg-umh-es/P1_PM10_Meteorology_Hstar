#!/usr/bin/env python3
import os
import shutil
import hashlib
import pandas as pd

def get_file_info(filepath):
    if not os.path.exists(filepath):
        return False, 0, ""
    size = os.path.getsize(filepath)
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return True, size, h.hexdigest()

def main():
    # 1. Madrid run metadata replacement
    orig_meta = "results/e2_met_madrid_pm10/run_metadata.json"
    superseded_meta = "results/e2_met_madrid_pm10/run_metadata.superseded.json"
    corrected_meta = "audit_ijer_experimental_evidence/computational_fixes/run_metadata_madrid_corrected.json"
    
    if os.path.exists(orig_meta) and not os.path.exists(superseded_meta):
        shutil.copy2(orig_meta, superseded_meta)
        print(f"Copied original {orig_meta} to {superseded_meta}")
        
    shutil.copy2(corrected_meta, orig_meta)
    print(f"Replaced {orig_meta} with {corrected_meta}")
    
    # Verify byte identity
    with open(orig_meta, "rb") as f1, open(corrected_meta, "rb") as f2:
        if f1.read() != f2.read():
            raise RuntimeError("Madrid run_metadata.json replacement verification failed!")
    print("Verified run_metadata.json byte-for-byte identity to corrected metadata.")
    
    # 2. Manifest copy and update
    src_manifest = "audit_ijer_experimental_evidence/computational_fixes/artifact_hash_manifest.csv"
    dst_manifest = "results/ijer/artifact_hash_manifest.csv"
    
    shutil.copy2(src_manifest, dst_manifest)
    df_manifest = pd.read_csv(dst_manifest)
    
    # Files to track
    tracked_files = [
        ("madrid_metadata", "results/e2_met_madrid_pm10/run_metadata.json"),
        ("madrid_metadata", "results/e2_met_madrid_pm10/run_metadata.superseded.json"),
        ("closure_results", "results/ijer/bartlett_closure/dm_hln_bartlett_canonical.csv"),
        ("closure_results", "results/ijer/bartlett_closure/rho1_common_window.csv"),
        ("closure_results", "results/ijer/bartlett_closure/multiplicity_contract.json"),
        ("closure_results", "results/ijer/bartlett_closure/table_4_render_data.csv"),
        ("closure_results", "results/ijer/bartlett_closure/figure_3_dm_heatmap_render_data.csv"),
        ("manuscript_table", "manuscripts/tables/ijer/table_4_dm_summary.tex"),
        ("manuscript_figure", "manuscripts/figures/ijer/figure_3_dm_heatmap.pdf"),
        ("closure_artifact", "audit_ijer_experimental_evidence/closure/manuscript_numbers.md"),
        ("closure_artifact", "audit_ijer_experimental_evidence/closure/input_schema_mapping.md"),
        ("closure_artifact", "audit_ijer_experimental_evidence/closure/rho1_common_window_summary.md"),
        ("closure_script", "audit_ijer_experimental_evidence/closure/compute_dm_hln_bartlett_closure.py"),
        ("closure_script", "audit_ijer_experimental_evidence/closure/compute_rho1_common_window.py"),
        ("closure_script", "audit_ijer_experimental_evidence/closure/render_dm_table_figure.py"),
        ("closure_script", "audit_ijer_experimental_evidence/closure/verify_dm_artifacts.py"),
        ("closure_script", "audit_ijer_experimental_evidence/closure/update_artifact_hash_manifest.py"),
        ("closure_script", "audit_ijer_experimental_evidence/closure/run_p1_computational_closure.py")
    ]
    
    manifest_dict = {}
    for idx, r in df_manifest.iterrows():
        manifest_dict[r["path"]] = {
            "category": r["category"],
            "path": r["path"],
            "exists": r["exists"],
            "size_bytes": r["size_bytes"],
            "sha256": r["sha256"]
        }
        
    for cat, p in tracked_files:
        exists, size, sha = get_file_info(p)
        manifest_dict[p] = {
            "category": cat,
            "path": p,
            "exists": exists,
            "size_bytes": size,
            "sha256": sha
        }
        
    # Recalculate SHA-256 for all existing files in manifest
    updated_rows = []
    for p, entry in manifest_dict.items():
        exists, size, sha = get_file_info(p)
        entry["exists"] = exists
        entry["size_bytes"] = size
        entry["sha256"] = sha
        updated_rows.append(entry)
        
    df_updated = pd.DataFrame(updated_rows)[["category", "path", "exists", "size_bytes", "sha256"]]
    df_updated.to_csv(dst_manifest, index=False)
    print(f"Updated hash manifest written to {dst_manifest} ({len(df_updated)} total entries).")

if __name__ == "__main__":
    main()
