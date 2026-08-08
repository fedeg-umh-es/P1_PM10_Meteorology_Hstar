---
tags:
  - investigacion
  - informe
---

# P3 evidence recovery report

**Audit date:** 2026-08-01 (Europe/Madrid)  
**Scope:** local, bounded, read-only Git and file inspection under `/Users/fede/repos` and `/Users/fede/Documents/Codex`  
**Verdict:** `P3_BLOCKED_IDENTITY_CONFLICT`

## 1. Executive result

No repository can be assigned unambiguously to **P3 — Operational Meteorology** from the immutable local evidence.

The only content-level candidate is `/Users/fede/repos/P3_Madrid_Ireland`, but its history contains incompatible project assignments:

- the committed canonical freeze identifies the repository as **P2 — Operational Meteorology**;
- the committed availability contract also identifies it as **P2 — Operational Meteorology**;
- the current branch adds one preparation note headed **P3 H* Strict Repository Preparation**, without an authoritative P2-to-P3 renumbering decision;
- the remote and manuscript retain historical P1 naming;
- a committed Ireland validation report expressly describes its scope as “No ... P1/P3 work”.

Directory names, branch names and a preparation-note title are not sufficient to override the earlier explicit canonical identity freeze. The mandatory stop rule therefore applies before choosing a P3 repository, ref, manuscript, predictions or H* outputs.

## 2. Repository candidate map

Nine non-bare or bare Git repositories were found in the two authorized roots. The documented symlink `/Users/fede/repos/p3-madrid-ireland-manuscript` was not present at audit time and is not counted separately.

| Repository or worktree | Form | Observed branch/ref and HEAD | Working state | Content identity | P3 decision |
|---|---|---|---|---|---|
| `/Users/fede/repos/Code2_AI` | worktree | `main`, `a66fd332f2c6a5a55a6f70bdc980b53c48798469` | dirty, extensive staged deletions and untracked replacements | Code2 AI software | Exclude; unrelated |
| `/Users/fede/repos/varret-pm10-paper` | worktree | `codex/p4-documentary-closeout`, `390685f1f1312954ee67513f3e0db11b2670e7f9` | clean | README explicitly says P4 — Variance Retention | Exclude by content and prompt |
| `/Users/fede/repos/pm10-predictability-bound` | worktree | `codex/prog-p1-02-temporal-inference`, `245b68388ab9cfa34f9c253611a5318aa3d344f5` | clean | standalone predictability-bound manuscript | Exclude by content and prompt |
| `/Users/fede/repos/P3_Madrid_Ireland` | worktree | `codex/p3-hstar-strict-manuscript-repair`, `aa00a1821786509b7028fb689478ced476aebc6a` | clean | conflicting P2/P3/P1 identifiers; Operational Meteorology content | **Conflicted candidate** |
| `/Users/fede/Documents/Codex/2026-08-01/esto-ya-cerr-correctamente-prog-p1/work/P1_PM10_Meteorology_Hstar-audit` | worktree | `codex/prog-p3-00-remote-evidence-reconciliation`, `370490a266fc2d3901b21340340e5047b33cf3a4` | dirty only through untracked `audit/` | committed canonical documents identify P2 — Operational Meteorology | Context only; not independently P3 |
| `/Users/fede/Documents/Codex/2026-08-01/esto-ya-cerr-correctamente-prog-p1/work/P1_PM10_Meteorology_Hstar.git` | bare mirror | `main`, `370490a266fc2d3901b21340340e5047b33cf3a4` | N/A | same P2 Operational Meteorology history | Context only; not independently P3 |
| `/Users/fede/Documents/Codex/2026-08-01/esto-ya-cerr-correctamente-prog-p1/work/Hstar_PM10_PM25_Madrid_Valencia.git` | bare | `main`, `9fb93bd58843c80c54371082b266e0c545e2b557` | N/A | daily PM10/PM2.5 Madrid–Valencia predictability study | Exclude; different question/data design |
| `/Users/fede/Documents/Codex/2026-08-01/esto-ya-cerr-correctamente-prog-p1/work/P32_IJF_GhostSkill_Hstar.git` | bare | `main`, `843d1ff68cc7302d2b2b31008b55eb590c8d4dfa` | N/A | P32 Ghost Skill / diagnostic line | Exclude; different project |
| `/Users/fede/Documents/Codex/2026-08-01/esto-ya-cerr-correctamente-prog-p1/work/varret-pm10-paper-provenance.git` | bare | `main`, `2398565652227dedf0e6eaf1e0765242dc37545d` | N/A | README says P33; committed audit material also labels the line P4 — Ghost Skill / Dynamic Fidelity | Exclude; different and internally renumbered line, not Operational Meteorology |

The non-bare candidate and the local bare mirror point to the configured remote `https://github.com/fedeg-umh-es/P1_PM10_Meteorology_Hstar.git`. No network operation was used to inspect or update that remote.

## 3. Identity evidence and conflict

All references below were inspected as Git objects at `aa00a1821786509b7028fb689478ced476aebc6a` unless stated otherwise.

| Label | Evidence | Classification |
|---|---|---|
| `VERIFIED_EVIDENCE` | `docs/PROG_P2_00_CANONICAL_FREEZE.md:3-14` states that repository identity is frozen, names `main` and freeze commit `1aad811dab0083396dc5c7eee5abebc34276514c`, and explicitly assigns the repository to **P2 — Operational Meteorology**. | Strong canonical P2 identity |
| `VERIFIED_EVIDENCE` | `docs/PROG_P2_01_METEOROLOGICAL_AVAILABILITY_CONTRACT.md:3-12` identifies the project as **P2 — Operational Meteorology** and the repository as `fedeg-umh-es/P1_PM10_Meteorology_Hstar`. | Independent P2 confirmation |
| `VERIFIED_EVIDENCE` | `docs/audit/P3_HSTAR_STRICT_REPO_PREPARATION.md:1-17` uses a P3 heading and P3 local branch/path, but still names the P1-prefixed remote and P2 base SHA `370490a...`. | P3-labelled preparation record, not a renumbering authority |
| `VERIFIED_EVIDENCE` | `results/e2_met_ireland_pm10/validation/evidence_validation_report.md:3-8` says its recovery scope included “No ... P1/P3 work”. | Conflicts with treating that recovered layer as established P3 work |
| `VERIFIED_EVIDENCE` | `manuscripts/manuscript_main.tex:2` identifies the manuscript comment header as “P1 — Meteorology value for PM10 multi-horizon forecasting”. | Historical P1 identity remains in the manuscript |
| `VERIFIED_EVIDENCE` | Current commit `aa00a182...` has sole parent `370490a266...`, subject `Document P3 H-star strict manuscript repair baseline`, and adds only `docs/audit/P3_HSTAR_STRICT_REPO_PREPARATION.md` (73 insertions). | A descendant label exists, but no canonical crosswalk or identity amendment exists |
| `CONTRADICTION` | The preparation record claims `/Users/fede/repos/p3-madrid-ireland-manuscript` is a symlink; that path was absent during the audit. | Local-path claim not reproducible at audit time |

Inference deliberately rejected: that the P3 directory/branch means P2 was silently renumbered P3. No inspected immutable document states that mapping.

## 4. Git audit of the conflicted candidate

- Repository: `/Users/fede/repos/P3_Madrid_Ireland`
- Configured remote: `origin = https://github.com/fedeg-umh-es/P1_PM10_Meteorology_Hstar.git`
- Observed branch: `codex/p3-hstar-strict-manuscript-repair`
- Observed HEAD: `aa00a1821786509b7028fb689478ced476aebc6a`
- HEAD subject: `Document P3 H-star strict manuscript repair baseline`
- Author/commit date: 2026-08-01 11:46:57 +0200
- Parent: `370490a266fc2d3901b21340340e5047b33cf3a4`
- Working tree: clean
- Local `main`: `370490a266fc2d3901b21340340e5047b33cf3a4`
- `origin/main`: `370490a266fc2d3901b21340340e5047b33cf3a4`
- Current-branch delta from `main`: one new audit document only

No P3 canonical branch/ref/SHA was selected. The observed branch and HEAD are evidence of a proposed repair context, not evidence of canonical P3 authority.

## 5. Canonical ref and SHA

**P3 canonical repository:** `MISSING`  
**P3 canonical branch/ref:** `MISSING`  
**P3 canonical SHA:** `MISSING`

`main` at `370490a266...` is documented as the P2 audit head. `aa00a182...` is a one-commit P3-labelled descendant whose sole change does not amend or supersede the P2 identity freeze. Choosing either as P3 would require an unsupported relabelling.

## 6. Manuscript identity

An editable manuscript exists in the conflicted repository:

- path: `manuscripts/manuscript_main.tex`;
- title: *Does meteorology extend the useful forecast horizon for urban PM10? A multi-city, multi-horizon skill analysis with XGBoost and SARIMA*;
- Git blob: `de7a77a7a6e57ede2ada439105028fc2f051d2b7`;
- size: 48,602 bytes;
- SHA-256: `1f440fab4cb292e0d77ef821c6271f597d93c4c433e549ac28d5d1e8d3a9f5c8`.

Its internal header calls it P1, while canonical repository documents call the operational line P2. No tracked PDF was found in the HEAD tree. Consequently this source is `DOCUMENTED_ONLY` with respect to P3 and is not accepted as a canonical P3 manuscript.

## 7. Primary evidence inventory and producer map

The candidate tree visibly contains configurations, scripts, Madrid predictions, regenerated Ireland predictions, horizon-wise metrics and H* tables. Those paths were not promoted into a P3 evidence inventory because project identity failed first.

The committed P2 provenance audit further records material limitations: absent canonical Madrid and Ireland aligned input datasets, absent original Ireland row-level outputs, regenerated Ireland evidence that must not be relabelled as original, and unresolved Madrid combined-output provenance. These are `DOCUMENTED_CLAIM` items here; they were not revalidated as P3 artifacts after the identity stop.

Therefore:

- P3 input → producer → artifact chain: `MISSING`;
- P3 primary paired predictions: `MISSING` as a demonstrated P3 link;
- P3 configuration: `MISSING` as a demonstrated P3 link;
- P3 producer logs/manifests: `MISSING` as a demonstrated P3 link.

This does not assert that every file is physically absent. It asserts that none may be attributed canonically to P3 until identity is resolved.

## 8. H* contract

The P3 preparation note documents that the repository contains references to both `H_strict_max_run` and `H_strict_from_h1`, and the tree includes a regenerated Ireland table named `hstar_summary_both_definitions.csv`. However, the same repository’s earlier canonical documents assign those materials to P2 and the original Ireland evidence layer is incomplete.

Accordingly:

- `H_strict_max_run` as the P3 primary metric: `DOCUMENTED_CLAIM`, not verified as P3;
- `H_strict_from_h1` as the P3 auxiliary metric: `DOCUMENTED_CLAIM`, not verified as P3;
- ambiguous manuscript uses of `H^*_{strict}`: not adjudicated;
- no H* values were recomputed;
- no table or figure was certified as the P3 principal result.

The two definitions were not merged or substituted.

## 9. Hashes verified

Hashes below verify only the bytes of existing identity/manuscript documents at the observed candidate HEAD. They do not verify scientific provenance.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `README.md` | 4,014 | `b1f23ee591f3fe65555e0e02cd64760f18d16e081856e6ebbff5f5780c623569` |
| `docs/PROG_P2_00_CANONICAL_FREEZE.md` | 5,597 | `a4d54916909c2be0f4c502adbcbd4ed17d2cb92bc5d57a43647285a69ddbd158` |
| `docs/PROG_P2_00_PROVENANCE_AUDIT.md` | 11,200 | `2c6369b32962c2d054019be00cb4e68be7c30fee713217d916962f1cf3940b21` |
| `docs/PROG_P2_01_METEOROLOGICAL_AVAILABILITY_CONTRACT.md` | 8,653 | `06087b97f5fd81019054c74ff2b830c9780f2fd8e70f79b4d3de63b4a64929eb` |
| `docs/audit/P3_HSTAR_STRICT_REPO_PREPARATION.md` | 3,724 | `2767a36820af48cb366ddf15a4f8bfe723f6c9553314060e3941fd50ca7de15e` |
| `manuscripts/manuscript_main.tex` | 48,602 | `1f440fab4cb292e0d77ef821c6271f597d93c4c433e549ac28d5d1e8d3a9f5c8` |
| `results/e2_met_ireland_pm10/validation/evidence_validation_report.md` | 23,459 | `e0a7d36ced81a5efbf80147c9f6f79c44b93703e4ab968fec8815c98543f40d8` |

## 10. Strict project separation

| Artifact/context | Declared project | Demonstrated P3 relationship | Use decision |
|---|---|---|---|
| `pm10-predictability-bound` HEAD | separate predictability-bound line; prompt identifies it as P1 context | none | negative context only |
| `P1_PM10_Meteorology_Hstar` at `370490a...` | P2 — Operational Meteorology | disputed by later P3 preparation note | identity evidence only; no scientific import |
| `varret-pm10-paper` at `390685f...` | P4 — Variance Retention | none | negative context only |
| `P32_IJF_GhostSkill_Hstar.git` at `843d1ff...` | P32 Ghost Skill / diagnostic line | none | negative context only |
| `Hstar_PM10_PM25_Madrid_Valencia.git` at `9fb93bd...` | Madrid–Valencia daily predictability study | none | negative context only |

No predictions, configurations, results or claims were imported across project lines.

## 11. Contradictions

1. **Project number:** authoritative freeze and contract say P2; descendant preparation note says P3.
2. **Historical naming:** remote/README/manuscript retain P1 naming, while the canonical freeze says the P1 prefix is historical and operational identity is P2.
3. **P3 scope:** the Ireland recovery validation report explicitly excludes P1/P3 work, yet a later note inventories that evidence for P3 manuscript repair.
4. **Local alias:** the P3 preparation note records a symlink that was not present at audit time.
5. **Canonical authority:** no immutable crosswalk says that P2 — Operational Meteorology was renumbered to P3, and no identity amendment supersedes the P2 freeze.

## 12. Limitations

- The audit was intentionally local and used no network.
- No fetch was allowed, so absence means absent from the local refs/files inspected.
- Scientific artifacts were not loaded, recomputed or regenerated after the identity stop.
- Untracked `audit/` content in the related audit worktree was not treated as immutable identity evidence.
- The report does not decide whether P2 should be renamed P3; it records that current evidence cannot prove such a decision.

## 13. Verdict

```text
P3_BLOCKED_IDENTITY_CONFLICT
```

- Repository: not canonically identified; conflicted candidate `/Users/fede/repos/P3_Madrid_Ireland`
- Branch/ref: not selected; observed candidate branch `codex/p3-hstar-strict-manuscript-repair`
- SHA: not selected; observed candidate HEAD `aa00a1821786509b7028fb689478ced476aebc6a`
- Evidence recovered: bounded repository map, Git/ref state, immutable P2/P3 identity conflict, candidate manuscript identity, identity-document hashes
- Evidence absent: authoritative P2↔P3 crosswalk, canonical P3 repository/ref/SHA, canonical P3 manuscript, and a P3-attributable input→producer→prediction→metric chain
- Repositories modified: **none**
- Experiments executed: **none**
- Scientific metrics recomputed: **none**
- Network operations: **none**

## 14. Minimum next step

Obtain or create, at the programme-governance level, one immutable identity decision that explicitly does one of the following:

1. maps **P2 — Operational Meteorology** to **P3 — Operational Meteorology** and names the canonical repository, ref and full SHA; or
2. confirms that Operational Meteorology remains P2 and identifies the actual P3 project/repository separately.

The decision must cite an authoritative source and must not rely on directory names, branch names or inferred numbering. Only after that decision exists should a fresh read-only artifact audit resume at the named canonical SHA.

The complete superprompt for that action is in `p3_identity_resolution_superprompt.md` beside this report.
