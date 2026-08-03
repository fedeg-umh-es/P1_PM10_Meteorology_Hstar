# Fase 7 — Búsqueda de los datasets primarios en repos y fuentes externas

A petición explícita: "los datasets están en mis repos, sino en local,
estarán online, busca y si necesitas clonar, lo haces". Resultado:
**no se encontró ninguna copia versionada de
`madrid_pm10_meteorology_experiment_base.csv` ni de
`ireland_pm10_meteorology_hourly.csv` en ningún repositorio de la cuenta,
y la descarga desde la fuente oficial identificada está bloqueada por la
política de red de este entorno.** Detalle abajo.

## 1. Repos de GitHub inspeccionados

Búsqueda por dos vías: `search_code`/`search_repositories` a nivel de
organización (`fedeg-umh-es`, `EduIntellect`) por los nombres exactos de
fichero, por el contenido distintivo de las columnas meteorológicas de
Irlanda (`wetb`,`dewpt`,`vappr`) y por los nombres de las 8 estaciones
irlandesas; e inspección directa (clon o API `get_file_contents`) de los
repos con nombre más prometedor.

Repos añadidos y revisados: `e2-met-validation`,
`Hstar_PM10_PM25_Madrid_Valencia`, `pm10-research-audits`,
`PM10-Horizons-Diagnostic`, `pm10-predictability-bound`,
`madrid-pm10-rank-reversal`, `varret-pm10-paper`.

`pm10-research-audits/README.md` confirma el mapa oficial del programa de
investigación: P1_PM10_Meteorology_Hstar es el repo canónico de
"P2 — Operational Meteorology Strategy" — no hay, por diseño, otro repo
"hermano" que debiera contener estos datos.

Ningún repo inspeccionado contiene los ficheros exactos. Hallazgos
relacionados pero no equivalentes:

- `madrid-pm10-rank-reversal/data_raw/madrid/pm10_raw_casa_de_campo.csv`:
  serie **diaria** (no horaria) de PM10 Casa de Campo 2017-2024, con
  columnas `temp,hr,ws,wd` no usadas por ese proyecto. Esquema distinto,
  granularidad distinta; no reutilizable directamente.
- `varret-pm10-paper` (proyecto P3, "Ghost Skill"): contiene su propia
  auditoría de reproducibilidad previa
  (`docs/empirical_reproducibility_audit.md`, fechada antes de esta
  sesión) que **buscó independientemente en 34 repositorios** de la
  cuenta y llegó a la misma conclusión: la tabla 2019-2023 horaria de
  Madrid con meteorología no está commiteada en ninguna rama de ningún
  repo inspeccionado. Corrobora, desde un ángulo distinto, el hallazgo de
  la Fase 0 de esta auditoría.

## 2. Fuente oficial localizada (Madrid, solo PM10, sin meteorología)

`varret-pm10-paper/data/raw/madrid_air_hourly_2023.zip` (5.07 MB,
commiteado en ese repo) resultó ser una descarga real, sin modificar, del
portal de datos abiertos del Ayuntamiento de Madrid:

- Dataset: `https://datos.madrid.es/dataset/201200-0-calidad-aire-horario`
- Recurso: `201200-3-calidad-aire-horario-zip`
- SHA-256 del ZIP: `b3ee481e0a787239dd07b33e93b2da97e31e6b5123d3c659f49e14549fb62b2e`
- Estructura verificada (descarga y extracción de un mes): CSV ancho
  mensual (`PROVINCIA;MUNICIPIO;ESTACION;MAGNITUD;...;H01;V01;...;H24;V24`),
  un fichero por mes, todas las estaciones y magnitudes de Madrid.
- **Estación 24 (Casa de Campo) SÍ tiene magnitud 10 = PM10** — es la
  fuente correcta para el target.
- **Ninguna estación tiene magnitudes ≥80 en este recurso** (verificado
  por inspección directa de un mes completo) — el dataset de "calidad del
  aire" del Ayuntamiento de Madrid **no incluye variables meteorológicas**.
  Esas variables (temp_c, humidity_pct, pressure_hpa, wind_speed_ms,
  wind_dir_deg, solar_rad_wm2, precip_mm) tendrían que salir de un recurso
  distinto del mismo portal ("datos meteorológicos"), no identificado
  todavía.
- Este recurso sólo cubre el año 2023; el protocolo canónico de Madrid
  necesita entrenamiento desde 2019 (o 2020, según el documento), lo que
  implicaría descargar los ZIP anuales equivalentes de 2019-2022.

## 3. Bloqueo de red — no se pudo descargar desde este entorno

`datos.madrid.es` está bloqueado por la política de egress de este
entorno (confirmado: `curl` devuelve `CONNECT tunnel failed, response
403`; `/root/.ccr/README.md` es explícito: *"403/407 from the proxy... Do
not retry or route around it — report the blocked host"*). No se intentó
sortear el bloqueo. Se probó tanto acceso directo como al endpoint de
catálogo JSON del portal; ambos devuelven el mismo 403 de política.

**Consecuencia:** aunque ahora se conoce la fuente oficial exacta y
verificada para el PM10 de Madrid, este entorno no puede completar la
descarga. Sería posible desde una máquina o entorno con salida de red a
`datos.madrid.es` (y, para Irlanda, al portal de EPA correspondiente —
tampoco identificado con precisión en esta sesión).

## 4. Estado tras esta búsqueda

No cambia el veredicto de la Fase 0/2: los datasets base siguen ausentes
en este entorno, así que ninguna cifra pasa a `VERIFIED_PRIMARY`. Lo que
sí cambia es que ahora hay una ruta concreta y verificada para cerrarlo
(al menos para el target PM10 de Madrid), en vez de un bloqueo sin salida
conocida:

1. Confirmar si el usuario tiene, en local, la ZIP/CSV de meteorología de
   Madrid y el ZIP de Irlanda (`Finalised_merged_datasets-20260508T212701Z-3-001.zip`,
   hash ya conocido — Fase 0).
2. Si no, descargar desde una máquina con salida de red:
   - Madrid PM10: `datos.madrid.es`, recurso `201200-3-calidad-aire-horario-zip`,
     un ZIP anual por año 2019-2023.
   - Madrid meteorología: localizar el recurso equivalente de
     "meteorología" en `datos.madrid.es` (no identificado en esta sesión).
   - Irlanda: fuente EPA original del ZIP ya referenciado, o el propio
     ZIP si sigue disponible en el Drive/Downloads del usuario.
3. Subir los ficheros resultantes a `data_processed/` (o a
   `data_raw/` + rehacer el build), y sólo entonces reejecutar
   `code/e2_met_madrid_run.py` / `code/e2_met_ireland_run.py` para obtener
   evidencia `VERIFIED_PRIMARY` real.

No se han modificado datasets ni resultados existentes en esta fase; es
puramente de localización.
