# ADR — P2 Operational Meteorology identity normalization

**Status:** approved and versioned locally; pending review/publication
**Decision date:** 2026-08-01
**Project:** P2 — Operational Meteorology (historically E2-MET)
**Approval basis:** explicit user instruction in the Codex task after acceptance
of the read-only identity-resolution audit
**Decision:** `REMAINS_P2`

## Context

The committed governance layer identifies this repository as **P2 —
Operational Meteorology**. Active local labels later used P3 in a directory,
branch, commit subject, and preparation-note title, while the configured remote
and manuscript header retained historical P1 labels. No authoritative source
records a P2-to-P3 renumbering.

The controlling identity evidence is:

- `docs/PROG_P2_00_CANONICAL_FREEZE.md`;
- `docs/PROG_P2_00_PROVENANCE_AUDIT.md`;
- `docs/PROG_P2_01_METEOROLOGICAL_AVAILABILITY_CONTRACT.md`.

## Decision

1. The current programme identity is **P2 — Operational Meteorology**.
2. No P2-to-P3 renumbering is recognized.
3. The canonical repository remains the historically named remote
   `fedeg-umh-es/P1_PM10_Meteorology_Hstar`.
4. The canonical branch remains `main`.
5. The locally verified canonical `main` SHA at the identity audit is
   `370490a266fc2d3901b21340340e5047b33cf3a4`.
6. The P3-labelled descendant
   `aa00a1821786509b7028fb689478ced476aebc6a` is retained in Git history as
   provenance but has no renumbering authority.
7. The current local working directory is normalized to
   `/Users/fede/repos/P2_Operational_Meteorology`.
8. The current local work branch is normalized to
   `codex/p2-identity-normalization`.

## Programme mapping

| Number | Decision for this normalization |
|---|---|
| P1 | Historical repository/manuscript prefix for this line; not its current assignment |
| P2 | Operational Meteorology / E2-MET; current and authoritative identity |
| P3 | Not identified by an authoritative source in the bounded audit; not inferred |
| P4 | Separate Variance Retention / Ghost Skill / Dynamic Fidelity line; not this repository |

## Supersession and preservation

This ADR does not rewrite the historical P2 freeze. It confirms and implements
that freeze's identity decision.

This ADR is now a versioned repository decision. Publication or push requires
separate authorization.

It supersedes the following labels as *active identity labels*:

- local directory `P3_Madrid_Ireland`;
- local branch `codex/p3-hstar-strict-manuscript-repair`;
- title/path `docs/audit/P3_HSTAR_STRICT_REPO_PREPARATION.md`;
- P1 programme headers in the active README and manuscript source.

Historical Git objects, commit subjects, remote names, and quoted historical
paths remain preserved as provenance. The remote is not renamed by this ADR.

## Change boundary

This is a governance/documentation normalization only. It does not alter code,
data, configurations, predictions, metrics, statistical results, tables,
figures, or manuscript scientific claims. It does not authorize a scientific
rerun or a P3 classification.

## Next gate

After documentary consistency is verified, the next scientific governance task
is **PROG-P2-02 — audit leakage and rolling-origin protocol**. That task must be
separately authorized and must begin read-only.
