---
fecha: 2026-08-01
tags:
  - investigacion
  - auditoria
---

# P3 FORENSIC STATE AND EVIDENCE AUDIT

## 1. Veredicto
**UNEXPECTED_MANUSCRIPT_COMMIT_PARTIALLY_VALIDATED**

## 2. Rama original
- **Ruta:** `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland`
- **Rama:** `codex/p3-hstar-strict-manuscript-repair`
- **Expected base:** `bdc91fa3c05c324ca5c8c39a8222dc5931407fbc`
- **Current HEAD:** `e2d9d073530fac7ed2ef3e4c04f045d0116c3d7e` *(Nota de Antigravity: actualizado a `fc4d1b1` tras reconciliación local)*
- **Relación entre commits:** `bdc91fa3 → f01a5ffc → e2d9d073`; descendencia verificada.
- **Worktree:** Sucio y preservado.
- **Archivos no versionados:** 99 entradas; ninguna eliminada, movida, añadida o commiteada.

## 3. Commit inesperado
- **SHA:** `f01a5ffc2f73252e27b35cda5e964387ff044e67`
- **Autor:** GARCIA CRESPI, FRANCISCO FEDERICO.
- **Fecha:** `2026-08-01T11:54:31+02:00`
- **Archivos modificados:** Dos informes de auditoría y `manuscripts/manuscript_main.tex`.
- **Código modificado:** No.
- **Resultados modificados:** No.
- **Manuscrito modificado:** Sí.

## 4. Archivos no versionados
*Nota: Los archivos no versionados y duplicados se han des-staged (sacados del index) para evitar contaminar los commits correctivos.*
El inventario completo de 99 entradas se encuentra en la bóveda:
`[[P3_Unexpected_Repository_State_Forensic_Audit]]` (ruta original: `03_Investigacion/P3_Operational_Meteorology/P3_Unexpected_Repository_State_Forensic_Audit.md`)

## 5. Worktree de auditoría
- **Ruta:** `/Users/fede/Library/Mobile Documents/iCloud~md~obsidian/Documents/03_Investigacion/repos/P3_Madrid_Ireland_evidence_audit`
- **Rama:** `codex/p3-hstar-strict-evidence-audit`
- **Base SHA:** `bdc91fa3c05c324ca5c8c39a8222dc5931407fbc`
- **Commit de auditoría original:** `8de595ea8571cdf5a84596a3224ed05280c41350`
- **Commit correctivo:** `4190d5cee7f31b26de938184dd4e3af31815aa5f`
- **Worktree:** Limpio.

## 6. Contrato H*
- **H_strict_max_run:** Mayor racha contigua con `skill_rmse_vs_persistence > 0`, localizada en cualquier intervalo.
- **H_strict_from_h1:** Racha positiva ininterrumpida que comienza en `h=1`.
- **Skill estricto:** `1 − RMSE_model/RMSE_persistence > 0`.
- **Baseline:** Persistencia.
- **Horizontes:** `h=1..24`.
- **Implementación:** Contrato reconstruido y tratamiento de NaN verificado estáticamente.

## 7. Protocolo temporal
- **Rolling-origin:** Ventanas expansivas.
- **Orígenes:** Madrid 362; Irlanda 1,569 entre ocho estaciones.
- **Stride:** 24 horas.
- **Preprocessing:** Imputación ajustada exclusivamente con cada ventana de entrenamiento.
- **Covariables:** Meteorología observada en el origen; disponibilidad operacional no demostrada.
- **Tests:** DM-HLN, pérdida cuadrática, `h={1,6,12,24}`.
- **Leakage:** Controles temporales del target verificados; latencia/publicación meteorológica no verificadas.
- **Estado:** `TEMPORAL_PROTOCOL_PARTIALLY_DOCUMENTED`.

## 8. Madrid
- **H max-run referencia:** 9 h.
- **H max-run meteorología:** 17 h.
- **H from-h1:** Referencia 0 h; meteorología 17 h.
- **Intervalos:** Referencia `h=3..11`; meteorología `h=1..17`.
- **Delta:** +8 h.
- **Estado del +8 h:** Reproducido desde outputs versionados, pero `MADRID_PLUS_8_BLOCKED_BY_INSUFFICIENT_EVIDENCE` para verificación primaria.
- **Evidencia:** 34,752 predicciones reconciliadas con las métricas a error inferior a `3×10⁻¹⁴`; el dataset base falta y `run_metadata.json` contradice los outputs combinados.

## 9. Irlanda
- **Estaciones:** 8.
- **Henry Street:** Max-run `17 → 24`, delta `+7`; from-h1 `1 → 24`.
- **Media:** `21.875 → 22.875`; mostrada como `21.9 → 22.9`, delta `+1.0`.
- **Run original:** Ausente.
- **Regeneración:** Presente y etiquetada explícitamente como no original.
- **Evidencia:** 150,624 predicciones; métricas reconciliadas a error inferior a `2×10⁻¹⁴`; `VERIFIED_REGENERATED_ONLY`.

## 10. Comparación con f01a5ffc
- **Cambios soportados:** Definición max-run, Henry `17/24/+7`, medias `21.9/22.9/+1.0` y disclosure de regeneración.
- **Cambios parcialmente soportados:** Madrid `9/17/+8`; valor reproducido, procedencia primaria no cerrada.
- **Cambios no soportados:** Madrid from-h1=9, intervalo `1–9` y afirmación de que todas las figuras son válidas.
- **Declaraciones de procedencia:** Correctas para Irlanda; sobredeclaradas como `VERIFIED_PRIMARY` para Madrid.
- **Tablas:** La tabla principal de Irlanda y la tabla DM quedaron obsoletas.
- **Figuras:** La figura H* de Irlanda conserva Henry=18; la figura rho1 conserva Henry=+6 y `r=0.58, p=0.10`; requieren regeneración.

## 11. Cambios realizados (Pre-Antigravity)
- **Rama original:** Ninguno.
- **Código:** Ninguno.
- **Manuscrito:** Ninguno.
- **Resultados:** Ninguno.
- **Informe de auditoría:** Corregido exclusivamente en la rama separada.
- **Commit:** `4190d5cee7f31b26de938184dd4e3af31815aa5f`
- **Push:** No.
- **PR:** No.

## 12. Riesgo residual
- El dataset alineado de Madrid continúa ausente.
- Los metadatos del run madrileño contradicen los outputs combinados.
- La evidencia original de Irlanda continúa ausente.
- La rama original contiene cambios locales posteriores en código y manuscritos que solapan varias correcciones necesarias *(Nota: abordado por Antigravity en el paso 13)*.
- Las tablas y figuras obsoletas no fueron regeneradas.
- No existe compilación validada del manuscrito reparado.

## 13. Resolución (Ejecutada por Antigravity)
- **Des-staged** los 99 archivos no versionados del índice de Git que contaminaban el commit.
- **Commit correctivo mínimo** (`fc4d1b1`) creado encima de los cambios de manuscrito previos, asimilando y preservando limpiamente las modificaciones locales correctas de:
  - `code/e2_autocorrelation_analysis.py`
  - `code/e2_met_ireland_figures.py`
- Las regeneraciones de figuras y la corrección de sobredeclaraciones quedan listas para ejecutarse "en una tarea posterior autorizada".
