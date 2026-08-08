---
tags:
  - investigacion
  - prompt
---

# SUPERPROMPT — Resolución mínima de identidad P2/P3 para Operational Meteorology

## Rol

Actúa como auditor sénior de gobernanza de proyectos y procedencia Git. Tu única misión es resolver la identidad programática de **Operational Meteorology**. No audites ni regeneres resultados científicos.

## Contexto verificado

Una recuperación forense local terminó con:

```text
P3_BLOCKED_IDENTITY_CONFLICT
```

El candidato `/Users/fede/repos/P3_Madrid_Ireland` contiene evidencia incompatible:

- `docs/PROG_P2_00_CANONICAL_FREEZE.md` identifica explícitamente el repositorio como **P2 — Operational Meteorology** y congela `main`;
- `docs/PROG_P2_01_METEOROLOGICAL_AVAILABILITY_CONTRACT.md` confirma **P2 — Operational Meteorology**;
- el commit `aa00a1821786509b7028fb689478ced476aebc6a` añade únicamente `docs/audit/P3_HSTAR_STRICT_REPO_PREPARATION.md`, cuyo título usa P3 y cuya base es `370490a266fc2d3901b21340340e5047b33cf3a4`;
- el remoto sigue llamándose `fedeg-umh-es/P1_PM10_Meteorology_Hstar`;
- el manuscrito conserva un encabezado P1;
- no se encontró una decisión inmutable que diga que P2 fue renumerado como P3.

No interpretes nombres de directorio o rama como autoridad programática.

## Objetivo único

Localizar o solicitar una fuente de autoridad que permita emitir exactamente una de estas decisiones:

1. **RENUMBERED_TO_P3** — P2 — Operational Meteorology fue renumerado oficialmente como P3 — Operational Meteorology.
2. **REMAINS_P2** — Operational Meteorology sigue siendo P2 y el P3 real es otro proyecto.
3. **IDENTITY_AUTHORITY_MISSING** — no existe evidencia autoritativa suficiente para decidir.

No realices ninguna acción científica posterior en esta sesión.

## Evidencia mínima aceptable

Una resolución positiva requiere una fuente programática explícita que incluya:

- nombre exacto del proyecto;
- número anterior y número vigente, si hubo renumeración;
- fecha y autor o autoridad responsable;
- repositorio canónico;
- rama o ref canónica;
- SHA completo existente localmente;
- relación con P1, P2, P3 y P4;
- declaración de qué documento anterior queda supersedido.

Fuentes aceptables:

- roadmap o registro maestro de proyectos versionado;
- ADR de renumeración aprobado;
- manifiesto de programa firmado o commiteado;
- instrucción expresa del propietario del programa que contenga el mapeo completo.

No son suficientes por sí solos:

- nombres de carpetas;
- nombres de ramas;
- asuntos de commit;
- un superprompt previo;
- títulos de notas de preparación;
- semejanza de la pregunta científica;
- fecha más reciente.

## Alcance de búsqueda

Busca solo bajo:

- `/Users/fede/repos`;
- `/Users/fede/Documents/Codex`.

Prioriza documentos de gobernanza, índices maestros, roadmaps, ADRs, manifiestos y reportes de cierre. No hagas una búsqueda de todo el sistema y no uses red.

## Restricciones absolutas

No ejecutes:

- `git pull`;
- `git fetch`;
- `git merge`;
- `git rebase`;
- `git reset`;
- `git checkout`;
- `git switch`;
- `git restore`;
- `git clean`;
- `git stash`;
- `git add`;
- `git commit`;
- `git push`;
- `git worktree add`;
- `git clone`.

No:

- modifiques ningún repositorio;
- entrenes modelos;
- ejecutes pipelines científicos;
- regeneres predicciones, métricas, tablas, figuras o PDFs;
- instales dependencias;
- descargues datos;
- uses red;
- cambies etiquetas P1/P2/P3/P4 dentro de archivos científicos;
- selecciones el candidato “más parecido”;
- conviertas inferencias en hechos.

## Procedimiento

### Fase A — Inventario de autoridad

Localiza documentos de gobernanza que mencionen simultáneamente al menos dos de estos términos:

- `Operational Meteorology`;
- `P2`;
- `P3`;
- `P1_PM10_Meteorology_Hstar`;
- `P3_Madrid_Ireland`.

Para cada documento registra ruta, commit si pertenece a Git, líneas pertinentes, tamaño y SHA-256.

### Fase B — Jerarquía y vigencia

Determina si cada fuente es:

- `AUTHORITATIVE`;
- `SUPERSEDED`;
- `PROPOSAL_ONLY`;
- `CONTRADICTORY`;
- `UNVERSIONED`.

Explica qué autoridad permite que una fuente posterior superseda la freeze P2. La mera posterioridad no basta.

### Fase C — Ref y SHA

Si la decisión es `RENUMBERED_TO_P3`, verifica localmente y en lectura:

- repositorio canónico exacto;
- ref exacta;
- SHA completo;
- existencia del objeto;
- relación de ancestros con `370490a266fc2d3901b21340340e5047b33cf3a4` y `aa00a1821786509b7028fb689478ced476aebc6a`;
- documento que autoriza el cambio de identidad.

Si cualquiera falta, usa `IDENTITY_AUTHORITY_MISSING`.

Si la decisión es `REMAINS_P2`, identifica el P3 real solo si una fuente autoritativa lo nombra expresamente. No lo infieras.

### Fase D — Decisión

Emite una sola decisión exacta:

- `RENUMBERED_TO_P3`
- `REMAINS_P2`
- `IDENTITY_AUTHORITY_MISSING`

Incluye una tabla de contradicciones sin suavizarlas.

## Entregable

No escribas dentro de ningún repositorio. Genera en una ubicación neutral bajo `/Users/fede/Documents/Codex`:

`p3_identity_resolution_decision.md`

Debe contener:

1. decisión exacta;
2. fuente de autoridad;
3. mapeo P1/P2/P3/P4;
4. repositorio canónico;
5. rama/ref canónica;
6. SHA canónico;
7. documentos supersedidos;
8. contradicciones restantes;
9. confirmación de que no se modificó ningún repositorio;
10. confirmación de que no se ejecutó ningún experimento;
11. siguiente acción mínima.

## Regla de parada

Si no existe una fuente explícita con autoridad para superseder o confirmar la freeze P2, detente con:

```text
IDENTITY_AUTHORITY_MISSING
```

No continúes con recuperación de predicciones, configuración, manifiestos, manuscrito o H*. No renombres ni reclasifiques ningún repositorio.

## Salida final

Entrega:

- decisión;
- fuente de autoridad y hash;
- repositorio/ref/SHA, solo si están resueltos;
- contradicciones;
- ruta absoluta del informe;
- confirmación de cero cambios en repositorios;
- confirmación de cero experimentos;
- siguiente paso mínimo.

No hagas commit, push ni PR.
