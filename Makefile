# Makefile -- P1 audit (rama claude/audit-p1-meteorology-0ehg5v)
#
# Reproduce, con un solo comando, todo lo que esta auditoria es capaz de
# recomputar en un entorno donde los datasets base de Madrid e Irlanda NO
# estan presentes (ver docs/audit/00_inventory.md Sec.5). Todo lo que
# sigue trabaja exclusivamente desde predicciones row-level ya trackeadas
# en git (results/e2_met_madrid_pm10/, results/e2_met_ireland_pm10_regenerated/);
# nada se reentrena desde cero.
#
# Objetivos NO cubiertos por este Makefile porque requieren datos ausentes
# en este entorno (documentado, no fabricado):
#   - Regenerar data_processed/madrid_pm10_meteorology_experiment_base.csv
#     o data_processed/ireland_pm10_meteorology_hourly.csv desde fuentes crudas.
#   - Reentrenar XGBoost/SARIMA desde cero (code/e2_met_madrid_run.py,
#     code/e2_met_ireland_run.py) -- solo posible si se restauran esos datasets.
#   - Fase 3a (reajuste de SARIMA h=24, Irlanda): bloqueada, ver
#     docs/audit/03_recompute.md.
#
# Uso:
#   make venv        # crea .venv_audit/ con el stack declarado
#   make test        # Fase 1: GATE de fuga (bloqueante)
#   make audit       # Fases 2, 4, 5: recomputo completo desde row-level
#   make figures      # figuras de diagnostico
#   make all          # todo lo anterior, en orden, con el mismo interprete

PYTHON := .venv_audit/bin/python3
PIP := .venv_audit/bin/pip

.PHONY: venv test phase2 phase4 phase5 audit figures all clean-venv

venv:
	python3 -m venv .venv_audit
	$(PIP) install -q --upgrade pip
	$(PIP) install -q pandas numpy scikit-learn statsmodels xgboost pyarrow scipy matplotlib

test: venv
	$(PYTHON) tests/test_no_leakage.py

phase2: venv
	$(PYTHON) code/audit_phase2_madrid_recompute.py

phase4: venv
	$(PYTHON) code/audit_phase4_madrid_window.py

phase5: venv
	$(PYTHON) code/audit_phase5_calibration.py

audit: test phase2 phase4 phase5

figures: audit
	$(PYTHON) code/audit_build_figures.py

all: figures
	@echo "Listo. Ver results/RESULTS_CANONICAL.md y results/NUMBERS_FOR_MANUSCRIPT.json"

clean-venv:
	rm -rf .venv_audit
