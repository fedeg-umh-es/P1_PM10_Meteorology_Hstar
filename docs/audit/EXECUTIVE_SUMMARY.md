# Resumen ejecutivo
**Verificado:** el motor que generó los resultados publicados
(`e2_met_madrid_shared.py`) está libre de fuga futura (GATE 1 VERDE,
probado por valor). Las 11 cifras Madrid del manuscrito (H*, ΔH*=+8h, DM
en 4 horizontes) coinciden con las predicciones trackeadas.
`rolling_origin.py` sí filtra futuro pero es código muerto de otro
proyecto, sin impacto en Madrid/Irlanda.

**Cambió respecto al borrador:** (1) la ventana declarada (ene-jul 2023)
no es la usada en las tablas (ene-dic, 362 orígenes); con la declarada,
ΔH*=+10h y el único DM significativo (h=12) deja de sobrevivir a
Bonferroni (p=0.045). (2) H*_strict en prosa ("desde h=1") no coincide con
lo tabulado ("racha más larga"); `lags_only` tiene skill negativo en h=1-2.
(3) bootstrap nuevo: IC95% de ΔH*=[-8,+13], cruza cero. (4) calibración
nula nueva: H*=9h ocurre por azar en 57% de permutaciones sin efecto real.
(5) se corrigió `run_metadata.json` de Madrid, desactualizado.

**Sigue sin cerrar:** sin datasets base en este entorno, nada alcanza
`VERIFIED_PRIMARY` (todo `REPRODUCED`). Reajuste SARIMA Irlanda (3a)
bloqueado: sin datos y sin anotación localizable. Un hash de Irlanda
(`merge_validation_report.md`) no reconstruible.
