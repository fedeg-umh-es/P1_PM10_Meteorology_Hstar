---
tags:
  - investigacion
  - meteorologia
---

# P3 Identity Resolution Decision — Operational Meteorology

**Audit date:** 2026-08-01 (Europe/Madrid)  
**Mode:** local, bounded, read-only governance/provenance audit; no network and no scientific execution.

## Decision

```text
REMAINS_P2
```

Operational Meteorology is authoritatively **P2** and remains P2. No accepted source under `/Users/fede/repos` or `/Users/fede/Documents/Codex` records or authorizes a P2-to-P3 renumbering. A distinct real P3 is not authoritatively identified within scope and is therefore left **UNIDENTIFIED**, not inferred.

## Controlling authority

| Committed source | SHA-256 | Finding |
|---|---|---|
| `docs/PROG_P2_00_CANONICAL_FREEZE.md` | `a4d54916909c2be0f4c502adbcbd4ed17d2cb92bc5d57a43647285a69ddbd158` | Canonical repository for **P2 — Operational Meteorology**; P1 prefix is historical |
| `docs/PROG_P2_00_PROVENANCE_AUDIT.md` | `2c6369b32962c2d054019be00cb4e68be7c30fee713217d916962f1cf3940b21` | Authoritative computational repository for P2/E2-MET; repository authority settled |
| `docs/PROG_P2_01_METEOROLOGICAL_AVAILABILITY_CONTRACT.md` | `06087b97f5fd81019054c74ff2b830c9780f2fd8e70f79b4d3de63b4a64929eb` | Project explicitly named **P2 — Operational Meteorology** |

The later `docs/audit/P3_HSTAR_STRICT_REPO_PREPARATION.md` has SHA-256 `2767a36820af48cb366ddf15a4f8bfe723f6c9553314060e3941fd50ca7de15e`. It is a preparation record, not an approved renumbering decision, and does not supersede the P2 governance documents.

Additional unversioned audit artifacts call Operational Meteorology “P3,” or call the dependency-audit P3 and repository P2 the same project. They are recorded as contradictions. They are not an approved ADR, signed manifest, versioned roadmap/master registry, or committed programme crosswalk, and some cite alleged canon files outside the permitted roots. They therefore cannot supersede the committed P2 freeze.

Search result:

```text
NO_RENUMBERING_STATEMENT_FOUND
```

## Mapping

| Number | Identity within the authorized evidence | Status |
|---|---|---|
| P1 | Historical repository/manuscript prefix for this line | Legacy only |
| **P2** | **Operational Meteorology** / E2-MET | **Authoritative/current** |
| P3 | Not authoritatively identified | Unresolved; not inferred |
| P4 | Variance Retention / Ghost Skill / Dynamic Fidelity | Separate line |

## Canonical repository, ref, and SHA

- Remote: `https://github.com/fedeg-umh-es/P1_PM10_Meteorology_Hstar.git`
- Canonical branch: `main`
- Current local `main` = local `origin/main`: `370490a266fc2d3901b21340340e5047b33cf3a4`
- P3-labelled descendant: `aa00a1821786509b7028fb689478ced476aebc6a`, sole parent `370490a...`; it adds only the preparation note and does not change project identity.
- No canonical P3 repository/ref/SHA is emitted.

## Supersession

The provenance audit supersedes only the freeze's data-provenance completion status. It does not supersede the P2 identity. No identity document has been superseded, and no P3-labeled or unversioned artifact supersedes the P2 freeze.

## Contradictions retained

1. Committed governance says P2; directory, branch, commit subject, and preparation title say P3.
2. Remote and manuscript lineage retain historical P1 naming.
3. Unversioned P2-closeout/P3-release reports call Predictability Bound P2 and Operational Meteorology P3 without locally verifiable renumbering authority.
4. An untracked reconciliation decision says dependency-audit P3 and repository P2 are the same scientific project; scientific sameness is not an authorized programme renumbering.
5. The genuine P3 remains unidentified.
6. The Ireland validation scope says “No ... P1/P3 work,” while the later P3 preparation note inventories that evidence for P3 repair.
7. The preparation note's recorded local symlink was absent at audit time.

## Change and execution confirmations

No repository was modified. No prohibited Git command was used. Only the neutral canonical report and this delivery copy were written outside repositories.

No experiment, training, pipeline, prediction, metric, statistical test, table, figure, manuscript build, or PDF generation was executed. No dependencies or data were downloaded, and no network was used.

## Minimum next action

If P2 is intended, approve a governance-only cleanup of the non-authoritative P3 labels and stale P1 headers. If P3 is intended, create an immutable approved ADR, versioned roadmap/master-registry entry, or signed committed programme manifest containing the exact P2-to-P3 mapping, date, authority, repository, ref, full existing SHA, P1–P4 relationship, and explicit supersession list.

Until then, do not continue scientific recovery under a P3 label.

**Canonical report path:**
`/Users/fede/Documents/Codex/p3_identity_resolution_decision.md`
