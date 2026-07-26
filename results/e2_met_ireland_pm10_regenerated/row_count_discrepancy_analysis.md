# Row-count discrepancy analysis: 187,857 vs. 188,817

- Date: 2026-07-26
- Scope: reconcile the regenerated consolidated panel's row count
  (`data_processed/ireland_pm10_meteorology_hourly.csv`, 187,857 rows) against
  the figure of 188,817 rows referenced as "expected" in this regeneration
  task's own instructions.

## Result

**The regenerated total of 187,857 rows is fully explained and reproducible
from the recovered source CSVs. The figure of 188,817 rows is NOT reproducible
from any accounting of the recovered data tried below, and does not appear
anywhere in this repository's git history, code, or committed reports
(confirmed by `grep -rn "188" reports/ manuscripts/ notes/ docs/ results/`,
which returns no occurrence of 188,817 or 188817).** Per the task's own
instruction not to assume the prior figure was correct, this report treats
188,817 as an unverified number of unknown origin, not as a target the
regeneration failed to hit.

## How 187,857 is derived (fully reproducible)

`code/build_ireland_experiment_base.py`, run against the 9 recovered CSVs,
prints and writes (`reports/ireland_experiment_setup.md`) the following raw
row counts (`wc -l <file> - 1`, i.e. rows excluding the header):

| Station | Raw rows | Status | Rows after cleaning |
|---|---:|---|---:|
| Birr co offlay | 25,465 | included | 25,465 |
| Dublin Airport | 25,462 | included | 25,462 |
| Dundalk Co Louth | 25,675 | included | 25,675 |
| Pearse street dublin | 22,098 | included | 22,098 |
| Rathmines Dublin | 27,047 | **excluded** (PM10_min=-488, 121 negatives) | 0 |
| Ringsend dublin | 27,238 | included | 27,047 (see below) |
| edenderry co offlay | 16,784 | included | 16,784 |
| henry street Limerick | 18,279 | included | 18,279 |
| porrlaoise co laois | 27,047 | included | 27,047 |

- Sum of raw rows for the 8 **included** stations (excludes Rathmines):
  25,465 + 25,462 + 25,675 + 22,098 + 27,238 + 16,784 + 18,279 + 27,047 =
  **188,048**.
- Ringsend dublin's raw file contains 191 rows with unparseable timestamps
  (confirmed independently by `code/audit_ireland_datasets.py`'s
  `datetime_parse_failures` column = 191, and by the build script's own log
  line: `[Ringsend dublin] Dropped 191 rows with unparseable timestamps`).
  These are dropped by the build script's versioned rule ("eliminar
  timestamps inválidos").
- After dropping those 191 rows, zero further rows were removed for
  duplicate timestamps in this run (the build script's duplicate-resolution
  step logs nothing for Ringsend after the NaT drop, meaning the 190
  duplicate-timestamp pairs the audit had flagged were entirely among the
  191 unparseable rows and disappeared with them).
- **188,048 − 191 = 187,857**, exactly matching both the freshly regenerated
  panel and the row counts already committed in `reports/ireland_experiment_setup.md`
  before this regeneration began (byte-identical `git diff`, confirmed).

No PM10-value-based rule (negative→NaN, Dundalk >500→NaN) removes rows —
those rules only null out the `PM10` column value, they do not drop rows.
Only the excluded station (Rathmines) and Ringsend's timestamp-parse
failures change the row count.

## Accounting methods tried against 188,817 (none match)

| Method | Result | Matches 188,817? |
|---|---:|---|
| Sum of raw rows, 8 included stations (no cleaning) | 188,048 | No (Δ=769) |
| Sum of raw rows, 8 included stations, **including header line each** | 188,056 | No (Δ=761) |
| Sum of `expected_hourly_rows` (audit's date-range-implied hourly count), 8 included stations | 187,984 | No (Δ=833) |
| Regenerated/cleaned panel (this run) | 187,857 | No (Δ=960) |
| Manuscript's own implied train+eval totals (`tab:descriptive`, summed per station, claims IE-037..044) | 187,429 | No (Δ=1,388) |
| Sum of raw rows, **all 9 stations including excluded Rathmines** | 215,095 | No |

No combination of these six independent, code- or manuscript-derived totals
equals 188,817. The figure cannot be reconstructed from the recovered ZIP,
the repository's existing audit artifacts, or the manuscript's own descriptive
table.

## Conclusion

188,817 is treated as an **unverified, undocumented figure with no traceable
source in this repository or in the recovered ZIP's data**. It is not used as
a correctness target. The regenerated panel's row count (187,857) is instead
validated by full agreement with:

1. The already-committed `reports/ireland_experiment_setup.md` (byte-identical
   before/after this regeneration).
2. The already-committed `reports/ireland_dataset_inventory.{md,csv}`
   per-station raw row counts.
3. A fully traceable arithmetic derivation (188,048 raw − 191 dropped
   timestamps = 187,857) from the recovered source CSVs' own SHA-256-verified
   contents.

If 188,817 originates from some other source outside this repository (e.g. a
different snapshot of the raw data, or a transcription/memory error in the
regeneration task brief), that source has not been located and cannot be
reconciled without it.
