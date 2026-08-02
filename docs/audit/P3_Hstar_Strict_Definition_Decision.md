---
tags: [#investigacion, #hstar]
fecha: 2026-08-01
decision_id: 2026-08-01-hstar-strict-definition
proyecto: [[P3_PROJECT_CANON|P3 — Operational Meteorology]]
estado: CONGELADO_REGISTRO_CANONICO
---

# 📜 Decision Log: Definición Canónica de $H^*_{\mathrm{strict}}$ (Madrid–Irlanda)

## 📌 Identificador
`2026-08-01-hstar-strict-definition`

---

## ❓ Pregunta Canónica
¿Qué definición de $H^*_{\mathrm{strict}}$ debe utilizarse como resultado principal en el manuscrito Madrid–Irlanda, dado que el texto del manuscrito y la implementación en código utilizan criterios divergentes?

---

## 🔍 Evidencia Disponible

- **Auditoría de Repositorio**: Repositorio `fedeg-umh-es/P1_PM10_Meteorology_Hstar` (commit `370490a266fc2d3901b21340340e5047b33cf3a4`).
- **Discrepancia Texto vs. Código**:
  - El **manuscrito** define $H^*_{\mathrm{strict}}$ como una racha positiva contigua de skill iniciada obligatoriamente en $h=1$.
  - El **código** calcula la mayor racha positiva de skill localizada en cualquier intervalo de horizontes (`H_strict_max_run`).
- **Sensibilidad del Resultado**: El claim $\Delta H^* = +8$ h de Madrid depende de la definición basada en la mayor racha (`H_strict_max_run`).
- **Ausencia de Artefactos Primarios**: Los resultados originales completos, las bases fuente primarias y las predicciones row-level originales no están disponibles.
- **Regeneración de Irlanda**: La ejecución disponible para Irlanda fue regenerada desde datos fuente recuperados y no corresponde al run original.
- **Canon Vigente de P3**: `H_strict_max_run` actúa como definición principal y `H_strict_from_h1` como diagnóstico auxiliar.

---

## 🎯 Decisión Canónica

1. **Adoptar `H_strict_max_run`** como la definición principal de $H^*_{\mathrm{strict}}$ en el manuscrito.
2. **Mantener `H_strict_from_h1`** como diagnóstico auxiliar explícitamente diferenciado.
3. **Reparar el Manuscrito**: Modificar definición, notación, tablas, figuras y claims del texto para alinearlos con estas dos métricas. **No modificar el código** para forzar la definición incorrecta del texto.
4. **Congelación de Reruns**: No ejecutar nuevamente los modelos hasta recuperar o descartar formalmente los artefactos primarios ausentes.

---

## ✅ Claims Permitidos

- El análisis utiliza la mayor racha contigua de skill estricto positivo como definición principal de `H_strict_max_run`.
- `H_strict_from_h1` describe separadamente la continuidad del skill desde el primer horizonte ($h=1$).
- Las dos definiciones pueden producir resultados distintos cuando existen interrupciones tempranas del skill.
- Los resultados de Irlanda proceden de una regeneración basada en datos fuente recuperados.
- El estudio actual utiliza meteorología retrospectiva y no demuestra despliegue operacional.

---

## 🚫 Claims Prohibidos

- Presentar `H_strict_max_run` como si exigiera skill positivo continuo desde $h=1$.
- Usar el término genérico $H^*_{\mathrm{strict}}$ sin especificar cuál de las dos definiciones se aplica.
- Mantener el claim $\Delta H^* = +8$ h como resultado verificado primariamente antes de recuperar o verificar sus artefactos fuente.
- Afirmar que el run original de Irlanda fue recuperado.
- Presentar meteorología observada o reconstruida retrospectivamente como información disponible operacionalmente.
- Afirmar que los resultados han sido reproducidos mediante un rerun nuevo.

---

## 🔬 Evidencia Requerida para Desbloqueo

1. **Tabla de Trazabilidad**: Relacionar cada valor de $H^*$ de Madrid e Irlanda con:
   - Definición aplicada (`H_strict_max_run` vs `H_strict_from_h1`).
   - Fichero fuente.
   - Condición informacional (`lags_only`, `lags_meteo_retrospective`, `lags_meteo_operational`).
   - Estación meteorológica/calidad de aire.
   - Modelo.
   - Horizontes que componen la racha.
   - Estado: `VERIFIED_PRIMARY` o `VERIFIED_REGENERATED_ONLY`.
2. **Recuperación o Declaración Formal de Ausencia**:
   - Bases originales.
   - Predicciones row-level originales.
   - Configuración exacta del run original.
   - Tablas fuente utilizadas por el manuscrito.
3. **Verificación de Madrid**: Comprobación específica del valor $\Delta H^* = +8$ h de Madrid bajo `H_strict_max_run`.

---

## 📄 Efecto Directo en el Manuscrito (Overleaf)

- **Methods**: Corregir la definición matemática y textual de $H^*_{\mathrm{strict}}$.
- **Notación**: Introducir nombres inequívocos: `H_strict_max_run` y `H_strict_from_h1`.
- **Tablas y Figuras**: Revisar todos los elementos visuales que utilicen $H^*_{\mathrm{strict}}$.
- **Claims de Madrid**: Suspender temporalmente el claim $\Delta H^* = +8$ h hasta verificación primaria.
- **Transparencia en Irlanda**: Declarar explícitamente que los datos de Irlanda proceden de una regeneración con fuentes recuperadas.
- **Framing Retrospectivo**: Mantener el encuadre estrictamente retrospectivo y eliminar cualquier afirmación de despliegue operacional.
- **Suspensión**: Posponer la compilación final y la auditoría claim–evidence hasta completar las reparaciones de trazabilidad.
