# P3 Unexpected Repository State Forensic Audit

## Repository
- Path: `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland`
- Branch: `codex/p3-hstar-strict-manuscript-repair`
- Expected base: `bdc91fa3c05c324ca5c8c39a8222dc5931407fbc`
- Current HEAD: `f01a5ffc2f73252e27b35cda5e964387ff044e67`
- Worktree: Dirty (Untracked files present)

## Commit relationship
- Expected base is ancestor: Yes (EXPECTED_BASE_IS_ANCESTOR)
- Commits between base and HEAD: 1 (the unexpected commit itself)

## Unexpected commit
- Commit: `f01a5ffc2f73252e27b35cda5e964387ff044e67`
- Author: GARCIA CRESPI, FRANCISCO FEDERICO
- Date: Sat Aug 1 11:54:31 2026 +0200
- Message: Align P3 manuscript with canonical strict H-star definition
- Files changed: `docs/audit/P3_HSTAR_STRICT_MANUSCRIPT_REPAIR_REPORT.md`, `docs/audit/P3_HSTAR_STRICT_VALUE_VERIFICATION.md`, `manuscripts/manuscript_main.tex`
- Manuscript changed: Yes (`manuscripts/manuscript_main.tex`)
- Code changed: No
- Results changed: No

## Numeric and claim changes
| Location | Before | After | Type | Requires evidence verification |
|---|---|---|---|---|
| `manuscripts/manuscript_main.tex` | $\Delta H^*_{\text{strict}} = +6$~h | $\Delta H^*_{\text{strict}} = +7$~h | Numeric (Henry St.) | Yes |
| `manuscripts/manuscript_main.tex` | $+0.9$~h | $+1.0$~h | Numeric (Ireland mean) | Yes |
| `manuscripts/manuscript_main.tex` | 18 | 17 | Numeric (Table 1: Henry St. lags-only) | Yes |
| `manuscripts/manuscript_main.tex` | 22.0 | 21.9 | Numeric (Table 1: Ireland mean lags-only) | Yes |
| `manuscripts/manuscript_main.tex` | Original dataset claim | Regenerated source datasets note | Declarative (Provenance) | Yes |

## Untracked files
| Path | Size | SHA-256 | Classification | Provenance |
|---|---:|---|---|---|
| `docs/data_inventory.md` | ... | ... | LIKELY_AUDIT_OUTPUT | PROVENANCE_UNRESOLVED |
| `docs/meteorology_experiment_audit.md` | ... | ... | LIKELY_AUDIT_OUTPUT | PROVENANCE_UNRESOLVED |
| `docs/meteorology_vs_lags_protocol.md` | ... | ... | LIKELY_AUDIT_OUTPUT | PROVENANCE_UNRESOLVED |
| `docs/path_issues.md` | ... | ... | LIKELY_AUDIT_OUTPUT | PROVENANCE_UNRESOLVED |
| `docs/script_inventory.md` | ... | ... | LIKELY_AUDIT_OUTPUT | PROVENANCE_UNRESOLVED |
| `imports/...` | ... | ... | LIKELY_MANUSCRIPT_IMPORT | PROVENANCE_UNRESOLVED |
| `outputs/master_meteorology_diagnostic_table.csv` | 73782 | 2aca1083f971834c7e7c0814350ec8598326c85769adb9349497c01f18e78710 | LIKELY_GENERATED_RESULT | PROVENANCE_UNRESOLVED |
| `outputs/predictions_meteorology_experiment.csv` | 11178203 | 1bca8bc85b69f8432182cfc58051154ba02d8f2596920021d36f4cccafaca49e | LIKELY_GENERATED_RESULT | PROVENANCE_UNRESOLVED |

## Initial risk assessment
The unexpected commit amends the manuscript with numeric corrections (e.g., Henry Street from 18 to 17, and delta from +6 to +7; mean from +0.9 to +1.0) and adds provenance disclosures (that Ireland results were evaluated from regenerated source datasets). The untracked files are likely the results and diagnostic outputs of an independent audit or regeneration run that informed these manuscript changes.

## Preservation decision
- No files deleted.
- No reset performed.
- No current-branch changes made.

## Reconciliation of f01a5ffc with verified evidence

| Manuscript change | Value in f01a5ffc | Verified evidence | Status | Required action |
|---|---|---|---|---|
| Henry Street $\Delta H^*$ | +7 h | +7 h | SUPPORTED_BY_REGENERATED_EVIDENCE | TEXTUALLY_VALID_BUT_UNCOMPILED |
| Henry Street $H^*_{\text{lags-only}}$ | 17 h | 17 h | SUPPORTED_BY_REGENERATED_EVIDENCE | TEXTUALLY_VALID_BUT_UNCOMPILED |
| Ireland mean $\Delta H^*$ | +1.0 h | +1.0 h | SUPPORTED_BY_REGENERATED_EVIDENCE | TEXTUALLY_VALID_BUT_UNCOMPILED |
| Ireland mean $H^*_{\text{lags-only}}$ | 21.9 h | 21.9 h | SUPPORTED_BY_REGENERATED_EVIDENCE | TEXTUALLY_VALID_BUT_UNCOMPILED |
| Regenerated source disclosure | Added note | Regenerated | CORRECT_PROVENANCE_DISCLOSURE | TEXTUALLY_VALID_BUT_UNCOMPILED |
