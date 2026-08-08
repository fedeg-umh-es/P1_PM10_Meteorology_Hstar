# Findings

Exact timestamp primitives replace positional origins, lags, and targets. The
canonical provisional evaluation window is January--July 2023. Tests cover all
eight lags, all 24 target horizons, gaps, duplicates, clock origins, information
cutoff, paired support, and aware DST arithmetic.

Ireland was reconstructed from the supplied P1 ZIP: 187,857 rows and eight
stations. The timestamp audit now contains 1,696 clock-generated candidate
origins, 13,568 lag checks, and 40,704 horizon checks. Strict all-lag/all-target
valid-origin counts range from 143 (Dundalk) to 212 (Pearse and Portlaoise). A
one-origin end-to-end smoke run completed and the full automated suite passed.

The required historical Madrid aligned input is still absent. The available
Madrid downloads cover 2024--2026, not the frozen 2019--2023 experiment. A full
Ireland rolling refit would also require roughly 1,536 strict origins and tens
of thousands of frozen 300-tree direct models; only a smoke run was completed
in this session. Consequently Madrid and the complete cross-station numerical
bundle (H*, DM/BH/Bonferroni, bootstrap, tables and figures) cannot be honestly
declared regenerated. Bootstrap remains `BOOTSTRAP_UNVERIFIABLE` for the repaired
complete run.

UNVERIFIABLE
