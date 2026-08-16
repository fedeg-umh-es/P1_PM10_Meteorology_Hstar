# P3 — Operational Meteorology

Version: 1.4
Last updated: 2026-08-16
Status: ACTIVE — F PROVENANCE GATE
Sequence gate: P3_SEQUENCE_GATE_CLEARED  
Canonical file: P3_PROJECT_CANON.md
P2 release decision: [[../P2_Predictability_Bound/P2_Closure_And_P3_Release_Decision]]

---

## 1. Source of truth

This file is the only persistent source of truth for P3.

Chat messages, temporary reports and local outputs are not canonical unless their decisions are incorporated here.

Any change to:

- experimental conditions;
- H* definition;
- information availability;
- station list;
- claims;
- numerical values;

requires an explicit decision and update to this file.

---

## 2. Canonical identity

### Name

P3 — Operational Meteorology

### Central research question

> Does meteorological information extend PM10 predictability when its temporal availability at forecast issue time is explicitly controlled?

### Scientific object

The object is the incremental predictive information provided by meteorology beyond lagged PM10.

The central comparison is informational, not merely algorithmic.

### Core thesis

Meteorological covariates constitute genuine predictive information only when their availability at forecast origin is defined.

Retrospective meteorology may estimate an upper bound.

Operational meteorology must be restricted to data or forecasts available at issuance time.

---

## 3. Canonical experimental conditions

The long-term design distinguishes:

### `lags_only`

Allowed:

- lagged PM10;
- calendar variables;
- information known at forecast origin.

### `lags_meteo_retrospective`

Allowed:

- lagged PM10;
- calendar variables;
- observed or reconstructed meteorology used retrospectively.

Interpretation:

```text
retrospective upper bound
```

Not operational evidence.

### `lags_meteo_operational`

Allowed:

- lagged PM10;
- calendar variables;
- meteorological forecasts issued no later than the PM10 forecast origin.

Must record:

- source;
- issue time;
- lead time;
- forecast cycle;
- version;
- spatial mapping;
- latency.

### `oracle`

Future observed meteorology.

Permitted only as an explicitly non-operational upper bound.

It must never be described as deployable or operational.

---

## 4. Mandatory availability contract

Every predictor must have machine-readable metadata:

```text
feature
source
observation_timestamp
available_at_origin
latency
maximum_available_horizon
information_condition
allowed_use
```

Canonical information labels:

```text
observed_at_origin
lagged_observed
forecast_available_at_origin
retrospective_reanalysis
future_observed_oracle
unknown
```

Unknown availability is not operational availability.

---

## 5. Mandatory protocol

- rolling-origin;
- identical origins between conditions;
- identical horizons;
- identical valid target pairs;
- train-only preprocessing;
- fixed or equivalently tuned model effort;
- persistence baseline;
- SARIMA secondary baseline;
- skill by horizon;
- H* relaxed;
- H* strict;
- DM-HLN when valid;
- results by station;
- prediction-level outputs;
- condition preserved in every artefact.

---

## 6. Madrid–Ireland paper

### Canonical manuscript identity

Working scientific title:

> Boundary-layer persistence shapes the meteorological contribution to urban PM10 forecastability across continental and maritime regimes

### Repository

```text
fedeg-umh-es/P1_PM10_Meteorology_Hstar
```

The repository name is historical and does not define the canonical project number.

### Scientific interpretation

Madrid represents a high-persistence continental regime.

Ireland represents a predominantly maritime and more ventilated regime.

The central finding is:

> Meteorological covariates extend the useful horizon clearly in Madrid, whereas their incremental contribution is generally small across the Irish stations because lagged PM10 already retains substantial predictive value.

This is an association with persistence regime, not proof of a universal causal law.

---

## 7. Regenerated Ireland evidence

Canonical validated evidence:

```text
Included stations: 8
Rolling origins: 1,569
Forecast horizons: 1..24
Prediction rows: 150,624
Processed panel rows: 187,857
Processed panel columns: 17
```

Stations:

- Birr;
- Dublin Airport;
- Dundalk;
- Pearse Street Dublin;
- Ringsend Dublin;
- Edenderry;
- Henry Street Limerick;
- Portlaoise.

Rathmines is excluded under the versioned data-quality rule.

The Ireland experiment is:

```text
REGENERATED FROM RECOVERED SOURCE DATA
```

It is not the recovered original execution.

---

## 8. Canonical H* values for Ireland

The main strict definition is:

```text
H_strict_max_run
```

Auxiliary:

```text
H_strict_from_h1
```

Henry Street Limerick, lags only:

```text
H_strict_from_h1 = 1 h
H_strict_max_run = 17 h
H_relax = 24 h
maximum run = h=3..19
```

Canonical changes:

```text
previous manuscript value: 18 h
validated value: 17 h

previous delta: +6 h
validated delta: +7 h
```

Ireland means:

```text
mean H_strict lags_only = 21.875 h = 21.9 h
mean H_strict lags_meteo = 22.875 h = 22.9 h
mean delta H_strict = 1.000 h = +1.0 h
```

---

## 9. Canonical DM-HLN summary

Directional balance across 32 station–horizon comparisons:

```text
24 favour lags + meteorology
7 favour lags only
1 invalid or unavailable comparison
```

Canonical summary:

```text
24/7/1
```

These are directional counts.

They are not counts of statistically significant differences.

---

## 10. rho1 association

Canonical nine-site association:

```text
n = 9
r = 0.554715
p = 0.121110
```

Rounded manuscript values:

```text
r = 0.555
p = 0.121
```

Interpretation:

> Positive but not statistically significant; consistent with, but not demonstrative of, the persistence-regime hypothesis.

Forbidden:

- causal language;
- “rho1 determines meteorological gain”;
- “boundary-layer persistence governs the gain” without qualification.

---

## 11. Edenderry

Canonical source rows:

```text
16,784
```

Valid descriptive observations in the current table:

```text
16,555
```

These are not necessarily inconsistent because source rows may contain missing or unusable PM10 observations.

Do not invent a new train/evaluation split to force the values to sum to the source-row total.

---

## 12. Current manuscript state

The manuscript must use:

- H* max-run definition;
- Henry Street = 17 h;
- Henry Street delta = +7 h;
- Ireland means 21.9 / 22.9 / +1.0 h;
- DM directional balance 24/7/1;
- rho1 association r=0.555, p=0.121, n=9;
- 187,857 panel rows;
- 1,569 origins;
- 150,624 predictions;
- regenerated-not-original wording;
- transparent AI-use declaration.

Figures must be generated from the validated regenerated outputs.

---

## 13. Aurora relationship

Aurora must be separated into:

- Aurora Air Pollution;
- Aurora 1.5 deterministic meteorology;
- Aurora 1.5 Ensemble.

For P3, the main future role is:

```text
lags_only
vs.
retrospective observed meteorology
vs.
Aurora 1.5 operational meteorology
```

Aurora 1.5 is a meteorological NWP source.

Aurora Air Pollution is not the same experimental arm.

Aurora 1.5 Ensemble is meteorological uncertainty, not a direct PM ensemble.

---

## 14. Novelty boundary

Weak framing:

> Adding weather improves PM10 forecasting.

Defensible framing:

> The incremental value of meteorology depends on temporal availability, forecast horizon and local persistence regime.

The current Madrid–Ireland paper is retrospective.

It must not claim operational deployment unless an origin-time NWP arm is added.

---

## 15. Boundaries with other lines

P3 may use P1 evaluation methods.

P3 may use P2 as an interpretative baseline for lag-memory.

P3 may use P4 diagnostics to test whether meteorological gains preserve variance.

P3 must not become:

- a universal H* methodology paper;
- a variance-retention paper;
- an Aurora benchmark paper;
- a foundation-model architecture paper.

---

## 16. Role allocation

### ChatGPT / Claude

- interpret findings;
- control causal claims;
- decide manuscript narrative;
- audit availability assumptions;
- prepare Overleaf instructions.

### Codex

- implement operational meteorology arms;
- execute models;
- generate outputs;
- create figures;
- verify H* and DM.

### Claude Code

- audit repository;
- verify regenerated evidence;
- inspect commits and PRs;
- detect mismatch between paper and code.

### Overleaf

- edit manuscript;
- insert figures;
- update numerical values;
- compile.

---

## 17. Current priority

P3 is currently in ACTIVE — F PROVENANCE GATE status.

P4 documentary closeout is validated and P2 has been explicitly released as a
sequencing blocker without being declared scientifically complete.

The separate P3 resume decision has now been issued through
docs/ADR_2026-08-16_P3_F_RESUME.md. Authorization is limited to the
single-origin Aurora 1.5 provenance and availability pilot. Manuscript editing,
full forecasting experiments, and atmospheric-mechanism experiments remain
unauthorized.

P3-A remains PARKED.

---

## 18. Next minimum action

Run a single-origin Aurora 1.5 operational-meteorology provenance and availability audit before any forecasting experiment.

This action belongs to a separate P3 resume task. It is not started by the P2
governance release.

---

## 19. Update log

### 2026-07-28 (Version 1.1)

- **Status changed to HOLD AND REPAIR**: The Madrid–Ireland paper is paused (no figures to be uploaded, Overleaf is on hold).
- **Core decisions and gaps identified**:
  1. *Operational separation*: Must strictly separate three information settings: `lags_only`, `lags_meteo_retrospective`, and `lags_meteo_operational` (operational must use forecasts with `issue_time`, latency, spatial mapping, cycle, etc. recorded).
  2. *Persistence regime interpretation*: Document that $r=0.555, p=0.121, n=9$ is positive but not statistically significant, avoiding causal claims.
- **Rejection risks explicitly audited**: Documented risks of presenting retrospective as operational, boundary layer mechanisms, protocol mismatch, generalization from 2 contexts, $H^*$ censorship at 24h, and small mean gains in Ireland.
- **Administrative numbering verification**: Confirmed Project Meteorology is **P3** and Ghost Skill is **P4** (the contradiction in TickTick must be corrected).
- **Work sequence**: P3 is paused until Paper A (P4) and Paper B (P2) are closed.

### 2026-08-01 (Version 1.2 — Decision 2026-08-01-hstar-strict-definition)
- **Decision log added**: Registered `[[P3_Hstar_Strict_Definition_Decision]]`.
- **H*strict Metric Convention**: Adopted `H_strict_max_run` as primary $H^*_{\mathrm{strict}}$ metric and `H_strict_from_h1` as auxiliary diagnostic.
- **Manuscript Repair Mandated**: Overleaf text, figures, tables, and claims must align with code (`H_strict_max_run`) rather than altering code to match legacy text.
- **Claim Suspension**: Suspended $\Delta H^* = +8$ h claim for Madrid pending primary artifact verification or formal missingness declaration.
- **Irlanda Transparency**: Formally mandated documenting Ireland evidence as regenerated from recovered source data.

### 2026-08-01 (Version 1.3 — Decision 2026-08-01-p2-closure-and-p3-release)

- **Sequence gate cleared**: `P3_SEQUENCE_GATE_CLEARED`.
- **P2 status**: P2 is not scientifically closed; it remains deferred and
  NO-GO, but is explicitly released as a sequencing blocker.
- **Dependency boundary**: P3 must not import unresolved P2 tables, forecasts,
  inference or claims as verified evidence. A future verified P2 linear-memory
  reference remains optional interpretative context only.
- **No automatic start**: P3 remains `HOLD AND REPAIR` until a separate resume
  task authorizes work under this canon.

### 2026-08-16 (Version 1.4 — Explicit P3-F Resume Decision)

- **Project identity**: Reconciled as **P3** on `main`.
- **P3-F status**: Resumed only for provenance and availability auditing.
- **Operational meteorology**: Aurora 1.5 remains the canonical first
  operational-meteorology candidate.
- **GFS**: Remains unauthorized.
- **Scope boundary**: Full forecasting experiments and manuscript changes remain
  unauthorized.
- **P3-A**: Remains **PARKED**.

---

## 20. P2 release and P3 sequence gate

Canonical decision:

```text
P2_NOT_CLOSED_BUT_EXPLICITLY_RELEASED_FOR_P3
```

P2 is not a producer or required dependency for P3 primary data, paired
predictions, configurations, availability contracts, folds, targets,
`H_strict_max_run` or `H_strict_from_h1`.

The separate P3 resume task has now been issued through
docs/ADR_2026-08-16_P3_F_RESUME.md. Current authorization is limited to the
single-origin Aurora 1.5 provenance and availability pilot and must use P3's
own primary evidence. No unresolved P2 result may be described as verified.
