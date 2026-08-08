# Auditoría Final: Regeneración Timestamp-Safe P3

## 1. Commit Real de Ejecución
`788218d22e83d9b6c031ca767996eccb7c07572b` (HEAD actual).

## 2. Commit / Tag Previamente Congelado
El tag `p3-ijer-submission-ready` apunta exactamente al commit `788218d22e83d9b6c031ca767996eccb7c07572b`. El hash documentado previamente (`788218d6e3f4df9cdbb9cebdad6c8d76eec4e1f7`) no existe en el repositorio (`fatal: bad object`), lo que indica que se trata de un error tipográfico o un hash huérfano de una versión anterior. El commit real contiene el refactor de `test_timestamp_contract.py` a unittest. 

## 3. Divergencia
No existe divergencia científica ni de código entre el HEAD de ejecución y el tag de envío (`p3-ijer-submission-ready`). Ambos son idénticos.

## 4. Madrid H* Antiguo vs Timestamp-Safe
- **Antiguo:** 9 (lags-only) -> 17 (lags+met), ΔH* = +8
- **Timestamp-safe:** 10 (lags-only) -> 21 (lags+met), ΔH* = +11

## 5. Resumen Ireland H*
La regeneración timestamp-safe mantiene intactas la mayoría de deltas, pero corrige los techos (ceilings) y modelos SARIMA al imponer ventanas de evaluación y orígenes estrictos:
- **Birr, Dublin Airport, Dundalk, Ringsend, Portlaoise:** ΔH* idénticos al manuscrito original.
- **Pearse Street:** SARIMA bajó de 17 a 15.
- **Edenderry:** Lags-only y lags+met subieron a 24 (empate sub-máximo). SARIMA subió de 9 a 15.
- **Henry Street Limerick:** Lags-only subió de 17 a 24. El ΔH* pasó de +7 a +0 al colisionar ambos contra el techo. SARIMA subió de 4 a 17.

## 6. C4 (Limerick / Henry Street)
- **Antiguo:** ΔH* = +7.
- **Timestamp-safe:** ΔH* = 0 (Ambos modelos alcanzan H* = 24).
- **Impacto:** El claim sobre la gran ganancia en Limerick se pierde al evaluar bajo estricto timestamp-safe (choca con el techo de horizonte 24).

## 7. C5 (Ceiling Ireland)
- **Antiguo:** 5 de 8 estaciones chocaban con H* = 24 (lags-only).
- **Timestamp-safe:** 7 de 8 estaciones (todas excepto Dublin Airport) chocan con H* = 24 (lags-only).

## 8. C6 (Madrid DM)
Se ha recuperado la implementación original exacta de `diebold_mariano_test` (utilizando la varianza de Bartlett, $q = h-1$, y corrección Harvey-Leybourne-Newbold) para recalcular las p-values sobre las predicciones de Madrid (especialmente $h=12$).

## 9. C7 (Ireland DM)
Se recalculó el contraste DM-HLN con Bartlett $q = h-1$ exacto para toda la familia de Irlanda (incluyendo los hitos clave de Dublin Airport $h=24$ y Pearse Street $h=12$), revirtiendo la versión asintótica normal $q=7$.

## 10. Estado C1-C9
- **C1 (Madrid H*):** SUPPORTED_WITH_NEW_VALUE
- **C2 (Madrid Bootstrap):** SUPPORTED_UNCHANGED
- **C3 (Madrid SARIMA):** SUPPORTED_UNCHANGED
- **C4 (Henry Street ΔH*):** NO_LONGER_SUPPORTED (Ahora ΔH*=0)
- **C5 (Ceiling Ireland):** SUPPORTED_WITH_NEW_VALUE (7 de 8)
- **C6 (Madrid DM):** SUPPORTED_RAW_ONLY (Recalculado vía HLN, p_raw=0.0123, no significativo tras BH)
- **C7 (Ireland DM):** SUPPORTED_WITH_NEW_VALUE (Recalculado vía HLN, Dublin Airport h=24 y Pearse St h=6,12 significativos tras BH)
- **C8 (Rho1 Cross-site):** SUPPORTED_UNCHANGED (Tratado puramente como descriptivo, n=9, r=0.678)
- **C9 (Global Multiplicity):** SUPPORTED_WITH_NEW_VALUE (Nueva familia BH sobre 36 tests)

## 11. Veredicto Final
**P3_TIMESTAMP_SAFE_CANONICALIZATION_COMPLETE**

## 12. Acción Permitida
OVERLEAF AUTORIZADO (Proceder a actualizar el manuscrito e integrar los cambios verificados).
