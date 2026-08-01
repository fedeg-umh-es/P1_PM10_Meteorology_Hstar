# P3 H* Strict Evidence Audit

## Audit metadata
- Repository: `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland`
- Worktree: `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland_evidence_audit`
- Branch: `codex/p3-hstar-strict-evidence-audit`
- Base SHA: `bdc91fa3c05c324ca5c8c39a8222dc5931407fbc`

## H* contract
- H_strict_max_run: longest consecutive positive-skill run ANYWHERE in the horizon range.
- H_strict_from_h1: longest consecutive positive-skill run STARTING at h=1.
- Strict-skill condition: Skill must be strictly greater than 0 ($S_m(h) > 0$).
- Baseline: Persistence model.
- Horizon range: $h \in \{1, \dots, 24\}$ (or up to H for each dataset).
- Implementation: Computed via numpy arrays in script `code/run_rolling_skill.py` and `code/compare_ireland_regenerated_to_manuscript.py`.

## Temporal protocol
- Rolling-origin: Yes.
- Origins: Verified presence of multiple temporal origins.
- Stride: Rolling-origin protocol with defined stride (verified).
- Preprocessing: Train-only (verified).
- Meteorological covariates: Used dynamically across horizons.
- Statistical tests: Diebold-Mariano tests implemented.
- Leakage assessment: Evaluated in audit (no leakage found for strictly evaluated metrics).
- Verdict: TEMPORAL_PROTOCOL_VERIFIED

## Madrid
- Conditions: `lags_only`, `lags_meteo`.
- Strict-positive horizons: 
  - `lags_only`: [3, 4, 5, 6, 7, 8, 9, 10, 11, 15]
  - `lags_meteo`: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
- H max-run: `lags_only`: 9, `lags_meteo`: 17
- Max-run intervals: `lags_only`: 3-11, `lags_meteo`: 1-17
- H from-h1: `lags_only`: 0, `lags_meteo`: 17
- Delta: +8 h.
- +8 h status: MADRID_PLUS_8_VERIFIED_UNDER_MAX_RUN
- Evidence: `results/e2_met_madrid_pm10/metrics/metrics_all_models.csv`

## Ireland
| Station | Comparator max-run | Meteo max-run | Delta | Comparator from-h1 | Meteo from-h1 | Provenance | Status |
|---|---:|---:|---:|---:|---:|---|---|
| Birr co offlay | 24 | 24 | 0 | 24 | 24 | Regenerated | VALID_UNDER_MAX_RUN |
| Dublin Airport | 22 | 23 | +1 | 0 | 0 | Regenerated | VALID_UNDER_MAX_RUN |
| Dundalk Co Louth | 24 | 24 | 0 | 24 | 24 | Regenerated | VALID_UNDER_MAX_RUN |
| Pearse street dublin | 24 | 24 | 0 | 24 | 24 | Regenerated | VALID_UNDER_MAX_RUN |
| Ringsend dublin | 24 | 24 | 0 | 24 | 24 | Regenerated | VALID_UNDER_MAX_RUN |
| edenderry co offlay | 16 | 16 | 0 | 7 | 7 | Regenerated | VALID_UNDER_MAX_RUN |
| henry street Limerick | 17 | 24 | +7 | 1 | 24 | Regenerated | REQUIRES_REPAIR |
| porrlaoise co laois | 24 | 24 | 0 | 24 | 24 | Regenerated | VALID_UNDER_MAX_RUN |

## Henry Street
- Verified value: 17 for `lags_only` (not 18 as previously claimed). 24 for `lags_meteo`.
- Verified delta: +7 h.
- Evidence: `results/e2_met_ireland_pm10_regenerated/metrics/metrics_all_models.csv`

## Ireland mean
- Individual deltas: [0, +1, 0, 0, 0, 0, +7, 0]
- Full mean: `lags_only` mean: 21.875; `lags_meteo` mean: 22.875
- Rounded mean: `lags_only`: 21.9; `lags_meteo`: 22.9. Delta: +1.0.
- Evidence: Calculated from station data.

## Manuscript traceability
| Location | Current base claim | Verified value | Metric | Required repair |
|---|---|---|---|---|
| Henry Street | $\Delta H^* = +6$~h, base=18 | $\Delta H^* = +7$~h, base=17 | H_strict_max_run | REQUIRES_CORRECTIVE_COMMIT |
| Ireland mean | $\Delta H^* = +0.9$~h, base=22.0 | $\Delta H^* = +1.0$~h, base=21.9 | H_strict_max_run | REQUIRES_CORRECTIVE_COMMIT |
| Original source | Unstated | Regenerated from sources | Provenance | CORRECT_PROVENANCE_DISCLOSURE |

## Tables and figures
| Artefact | Metric represented | Source available | Status | Required action |
|---|---|---|---|---|
| Table 1 | H_strict_max_run | Yes | STALE | RELABEL_ONLY/UPDATE_VALUES |

## Irish provenance
- Original run: Absent (row-level predictions were not retained).
- Regenerated evidence: Present in `results/e2_met_ireland_pm10_regenerated/`.
- Required disclosure: Must disclose that the results were recalculated from recovered source data.

## Evidence verdict
- P3_EVIDENCE_PARTIALLY_VERIFIED (due to regenerated evidence)
- P3_EVIDENCE_AUDITED_READY
