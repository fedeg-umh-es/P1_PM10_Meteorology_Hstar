# P3 Final Source Reconciliation

## Repository
- Path: `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland`
- Branch: `codex/p3-hstar-strict-manuscript-repair`
- Starting HEAD: `e2d9d073530fac7ed2ef3e4c04f045d0116c3d7e`
- Initial worktree: Dirty (modified `manuscripts/manuscript_main.tex`, `manuscripts/cover_letter.tex`, `code/e2_autocorrelation_analysis.py`, `code/e2_met_ireland_figures.py` and untracked files)

## Evidence basis
- Canonical decision: 2026-08-01-hstar-strict-definition
- Evidence audit: `P3_HSTAR_STRICT_EVIDENCE_AUDIT.md`
- Madrid evidence: `lags_only` = 9 h, `lags_meteo` = 17 h, Delta = +8 h
- Ireland evidence: media `lags_only` = 21.9 h, media `lags_meteo` = 22.9 h, media Delta = +1.0 h. Henry Street: `lags_only` = 17 h, `lags_meteo` = 24 h, Delta = +7 h
- Ireland provenance: regenerated evidence from recovered source data

## Manuscript
| Section | Change | Evidence | Classification | Action |
|---|---|---|---|---|
| Results | Ireland mean: 14.3 h vs 22.0 h -> 14.3 h vs 21.9 h | Ireland mean `lags_only` = 21.9 h | SUPPORTED_BY_REGENERATED_EVIDENCE | Include |
| Results | Henry St: +6 h -> +7 h | Henry St $\Delta H^*$ = +7 h | SUPPORTED_BY_REGENERATED_EVIDENCE | Include |
| Discussion | "governs the regime transition" -> "interpretation is consistent with" | Absence of causality | SAFE_EDITORIAL_HEDGE | Include |
| Discussion | Added caveat on retrospective meteorology | Absence of generalization | SAFE_EDITORIAL_HEDGE | Include |
| Data Availability | Note on regenerated Ireland sources | Regenerated provenance | SUPPORTED_BY_CANON | Include |
| Results | OLS regression values updated | Based on regenerated data | SUPPORTED_BY_REGENERATED_EVIDENCE | Include |

## Cover letter
| Paragraph or claim | Classification | Evidence | Action |
|---|---|---|---|
| Madrid $\rho_1 \approx 0.96$ | CONSISTENT_WITH_MANUSCRIPT | $\rho_1 = 0.957$ | Include |
| Ireland mean $\Delta H^* = +1.0$ h, $\rho_1 \approx 0.85$ | CONSISTENT_WITH_MANUSCRIPT | 22.9 - 21.9 = 1.0 h, $\rho_1 = 0.850$ | Include |
| "interpret this contrast" / "is associated with" | SAFE_POSITIONING | Absence of causality | Include |
| Retrospective upper bound caveat | SAFE_POSITIONING | Absence of generalization | Include |

## Numerical consistency
- Madrid: Consistent (+8 h)
- Henry Street: Consistent (+7 h, 17 h to 24 h)
- Ireland mean: Consistent (+1.0 h, 21.9 h to 22.9 h)
- Metric definition: Consistent ($H^*_{\text{strict,max-run}}$)
- Result: Consistent

## Claim discipline
- Causal claims: Mitigated (hedged "governs" to "associated with")
- Generalisations: Mitigated (added operational caveat)
- Novelty: Not inflated
- Result: Consistent

## Untracked files
| Path | Classification | Required for compilation | Included |
|---|---|---|---|
| `docs/data_inventory.md` | LIKELY_AUDIT_OUTPUT | No | No |
| `docs/meteorology_experiment_audit.md` | LIKELY_AUDIT_OUTPUT | No | No |
| `docs/meteorology_vs_lags_protocol.md` | LIKELY_AUDIT_OUTPUT | No | No |
| `docs/path_issues.md` | LIKELY_AUDIT_OUTPUT | No | No |
| `docs/script_inventory.md` | LIKELY_AUDIT_OUTPUT | No | No |
| `imports/` | LIKELY_MANUSCRIPT_IMPORT | No | No |
| `outputs/` | LIKELY_GENERATED_RESULT | No | No |

## Protected artefacts
- Code changed: No (staged changes)
- Results changed: No (staged changes)
- Predictions changed: No (staged changes)
- Configuration changed: No (staged changes)

## Previous Overleaf compilation
- Pages: 24
- Errors: 0
- Hyperref warnings: 4
- Overfull boxes: 5
- Reproducible from committed SHA: no

## Verdict
- READY_FOR_FINAL_SOURCE_COMMIT
