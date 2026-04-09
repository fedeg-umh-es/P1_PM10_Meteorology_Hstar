# Madrid E2-MET Manuscript Figures

## Generating script

`code/madrid_sarima_make_figures.py`

Run with:
```
python3 code/madrid_sarima_make_figures.py
```

## Input tables (all from `results/madrid_sarima/`)

| File | Contents |
|------|----------|
| `skill_ci_panel_A.csv` | Horizon-wise skill + 95% bootstrap CI vs persistence (C1, C2, C3) |
| `skill_ci_panel_B.csv` | Horizon-wise skill + 95% bootstrap CI vs SARIMA (C1, C2, C3) |
| `dm_results_panel_A.csv` | DM test statistics and p-values vs persistence (C1, C2, C3) |
| `dm_results_panel_B.csv` | DM test statistics and p-values vs SARIMA (C1, C2, C3) |
| `metrics_sarima.csv` | Horizon-wise RMSE/MAE/skill for SARIMA vs persistence |
| `hstar_summary_sarima.csv` | H* strict and H* relax summary for all model/baseline pairs |

## Figures produced

| File | Description |
|------|-------------|
| `figure_skill_vs_persistence.{png,pdf}` | Figure 1: Horizon-wise skill curves (C1, C2, C3, SARIMA) vs persistence with 95% bootstrap CI bands. |
| `figure_skill_vs_sarima.{png,pdf}` | Figure 2: Horizon-wise skill curves (C1, C2, C3) vs SARIMA with 95% bootstrap CI bands. |
| `figure_dm_vs_persistence.{png,pdf}` | Figure 3A: DM significance dot-plot vs persistence. Filled circles = DM p < 0.05; open circles = not significant. Green = positive skill, red = negative skill. |
| `figure_dm_vs_sarima.{png,pdf}` | Figure 3B: DM significance dot-plot vs SARIMA. Filled circles = DM p < 0.05; open circles = not significant. Green = positive skill, red = negative skill. |
| `figure_hstar_summary.{png,pdf}` | Figure 4: Grouped bar chart of H* strict and H* relax for all model/baseline combinations. |

PNG figures exported at 600 dpi. PDF figures exported as vector outputs.

## Limitations and assumptions

- SARIMA bootstrap CI bands are not available in the input tables (the rolling bootstrap was only run for C1-C3). SARIMA skill in Figure 1 is therefore plotted without a shaded CI band.
- SARIMA DM significance (panel A of Figure 3) is derived from `dm_results_panel_A.csv`. If no row with `condition == SARIMA` is present (which is the case in the current outputs), SARIMA DM significance is marked as unknown (open circles, grey).
- H* values used in Figure 4 are cross-checked against the canonical values specified in the experiment protocol. A warning is printed if any discrepancy is found.
- The h = 5–10 interval is highlighted in all skill and DM figures as a conservative marker of the inferential zone with skill > 0, DM p < 0.05, and bootstrap CI excluding 0 for C2.
- C3 is visually distinguishable from C2 via a dashed line style; no claim of superiority is implied by the figure layout.

## Scientific context

- Domain: Madrid PM10, station 24 (Casa de Campo)
- Rolling-origin test period: 2023
- Stride: 24 h
- Horizons: h = 1..24
- Conditions: C0 persistence, C1 lag-only, C2 lag + core met, C3 lag + extended met
- Baselines: persistence (primary), SARIMA (secondary)
