# TalentAdvisor — Project Brief

**Engagement:** Skill de Claude Code · consejero vocacional automatizado para las **24 maestrías en línea de Universidad Anáhuac** · metodología **diagnóstico de necesidades de formación**
**Idioma operativo:** Español neutro (mexicano)
**Audiencia primaria:** profesionales mexicanos que trabajan en empresas y buscan posgrado para crecer
**Audiencia secundaria:** las propias empresas (el JSON de cierre se persiste para análisis agregado)
**Brief generated:** 2026-05-25

## Overview

TalentAdvisor contiene el skill `anahuac-advisor`, un agente que conduce una **entrevista estructurada de 6 fases** (apertura → perfil profesional → contexto organizacional → trayectoria deseada → restricciones → diagnóstico) y produce un **JSON estructurado** con:

- Diagnóstico de brechas tipificadas y priorizadas por severidad
- Mapeo a los 4 pilares de impacto de negocio (rendimiento · recursos · adaptación · errores/costos)
- Hasta 3 maestrías recomendadas con score 0–100 y desglose
- Próximos pasos accionables

Es un cambio de marco deliberado: **del consumo educativo al diagnóstico estratégico**. En lugar de "¿qué maestría te gusta más?" la pregunta operativa es "¿qué brechas tienes que cerrar y cuál es el camino formativo más eficiente para cerrarlas?".

Todos los archivos viven en ``files/` (raíz del skill en este repo)`.

## Stack & architecture

| Capa | Archivos |
|---|---|
| **Protocolo del agente** | `SKILL.md` · `agent_system_prompt.md` |
| **Contexto del proyecto** | `CLAUDE.md` · `README.md` · `anahuac-advisor-README.md` |
| **Modelo conceptual** | `methodology-dnc.md` (3 planos · 4 pilares · 6 tipos de gap) |
| **Flujo conversacional** | `conversation-flow.md` (6 fases con bank de preguntas) |
| **Manejo de excepciones** | `special-cases.md` (12 escenarios — burnout, transición, sin licenciatura, etc.) |
| **Lógica de matching** | `matching-algorithm.md` + `compute_match.py` (determinístico, auditable) |
| **Renderizado** | `render_report.py` + `report_template.md` |
| **Validación** | `validate_dnc.py` |
| **Plantillas** | `session_template.json` |
| **Skill empaquetado** | `anahuac-advisor-skill.tar.gz` |

Scripts en Python stdlib, sin dependencias externas. **La fuente en `files/` usa el layout estructurado del skill** (actualizado 2026-07-13): `references/` para los docs `.md`, `scripts/` para los `.py`, `assets/` para JSON/plantillas, con `SKILL.md` en la raíz — igual que el paquete `anahuac-advisor-skill.tar.gz`. Todas las referencias internas resuelven contra ese layout.

**Dos copias del skill (sincronizadas 2026-08-30):** la **fuente canónica** vive en `~/Desktop/CLAUDE/CONSEJERO-DNC/files/`; el repo público `anahuac-advisor` (`~/Desktop/anahuac-advisor/`) mantiene un **espejo publicado** en su `files/`. Antes de esa fecha el espejo estaba congelado en el commit del 2026-07-14 (vocabulario viejo `professional_profile`/`functional_areas_current` + pesos de diplomado 0.35/0.35/0.20/0.10) y el `.tar.gz` era anterior al rebrand. Al sincronizar se **excluyen del repo público**, por ser material interno o con datos personales: `references/won-buyer-profile.md`, `assets/won_buyer_profile.json`, `assets/skills_matrix_analysis.json` (análisis de llamadas de venta WON), `perfil-buyerPersona-diplomados.md`, `PROPUESTA-cuestionario-diplomados.md`, `AnahuacAdvisor-Leads.xlsx` y los `.bak`. Están en el `.gitignore` del repo, y las referencias cruzadas a `won-buyer-profile.md` van marcadas como *documento interno · no versionado en el repo público*. **Al cambiar el skill hay que replicar en el espejo** (y regenerar el `.tar.gz`, que se arma desde `files/` con `CLAUDE.md` en la raíz + `anahuac-advisor/{SKILL.md, README.md ← anahuac-advisor-README.md, assets/, references/, scripts/}`).

## Metodología diagnóstico de necesidades de formación

### 3 planos (intersección obligatoria)

| Plano | Pregunta clave |
|---|---|
| **Profesional** | ¿Qué sabe y qué sabe hacer hoy? |
| **Empresarial** | ¿Qué objetivos persigue la empresa y qué necesita su área? |
| **Trayectoria** | ¿Hacia qué rol/horizonte quiere moverse? |

**Regla central:** una capacitación es útil sólo si cierra gaps en **al menos dos de los tres planos**.

### 4 pilares de valor de negocio (mapeo obligatorio en el output)

1. **Mejora del rendimiento** — productividad, calidad, KPIs
2. **Optimización de recursos** — más con lo mismo / lo mismo con menos
3. **Adaptación al cambio** — sin un cambio que la justifique, la formación es un lujo
4. **Reducción de errores y costos** — errores con costo medible, riesgos sin gestionar

### 6 tipos de gap

`knowledge` · `skill` · `attitude` · `certification` · `leadership` · `strategic`

### 4 severidades (con pesos para el matching)

| Severidad | Peso |
|---|---|
| `bloqueante` | 4 |
| `alta` | 3 |
| `media` | 2 |
| `baja` | 1 |

## Flujo conversacional (6 fases)

| Fase | Objetivo | Turnos | Datos mínimos |
|---|---|---|---|
| 1. Apertura | Encuadre + consentimiento | 1–2 | — |
| 2. Perfil profesional | Plano individual | 3–5 | 3/6 |
| 3. Contexto organizacional | Plano empresarial — **el más saltado por chatbots** | 2–4 | 3/6 |
| 4. Trayectoria deseada | Plano carrera | 2–3 | 3/5 |
| 5. Restricciones | Tiempo, modalidad, idioma, presupuesto | 1 | — |
| 6. Diagnóstico + recomendación | JSON + reporte markdown | 1 | — |

**Reglas transversales del flujo:**
- Una pregunta por turno (dos máx si están muy ligadas)
- **Sin viñetas en fases 2–5** — conversación en prosa
- Reformula antes de avanzar (protege contra malinterpretación)
- Captura citas literales del usuario → las usarás como `evidence` de cada gap
- Si el usuario divaga, redirige: *"Anoto eso. Antes de seguir, necesito entender [X]."*
- Si quiere ir más rápido, comprimir las fases 2–4 a 2 preguntas cada una — pero **nunca eliminar** una fase

## Algoritmo de matching (determinístico)

```
match_score = 0.25·functional_areas_match
            + 0.25·gap_coverage
            + 0.20·career_outcome_match
            + 0.10·industry_fit
            + 0.10·seniority_fit
            + 0.10·constraints_fit
```

- **Umbral mínimo: 50** — programas debajo no se recomiendan
- **Máximo 3 recomendaciones**
- Cada componente devuelve 0–100; el resultado final también en 0–100

**Tie-breakers (orden estable y reproducible):**
1. Más brechas **bloqueantes** cerradas
2. Mayor `gap_coverage`
3. Mayor `career_outcome_match`
4. Alfabético por `name`

**Una brecha se considera "cerrada"** si el programa cubre el área funcional asociada **o** lista la hard/soft skill correspondiente como output.

**Cuándo NO recomendar (incluso si el score técnico es alto):**
- Ningún programa supera 50, **o**
- El mejor programa supera 50 pero **no cierra ninguna brecha bloqueante** — decirlo explícitamente
- Las restricciones (tiempo, idioma, modalidad) son incompatibles con cualquier programa del catálogo

## Diplomados — track corto (educación continua) · añadido 2026-07-14 · ruteo y pesos actualizados 2026-07-28

El modelo ahora rutea entre **dos catálogos** según tiempo disponible y ambición:

| Track | Catálogo | Perfil | Duración | Dedicación |
|---|---|---|---|---|
| **Maestría** | `assets/programs.json` (24) | Cambio profesional **transformacional** | ~27-28 meses · 18 asignaturas | 6-10 h/sem |
| **Diplomado** | `assets/diplomados.json` (203: 201 diplomados + 2 certificados) | Cerrar una **brecha puntual** de skills | ~7 meses · 5-6 módulos | ~4-6 h/sem |

- **Fuente diplomados:** `diplomados/archivos-diplomados/*.md` (brochures **oficiales** Anáhuac Educación Continua). El catálogo se amplió de 89 → **203** (201 diplomados + 2 certificados) descargando los brochures faltantes con `scripts/fetch_brochures.py` a partir de `AOL_Diplomados_Links.pdf` (incluye operaciones/logística: Logística de la Cadena de Suministro, Lean Manufacturing, Compras Estratégicas, Comercio Exterior, Industria 5.0, etc.). Parseadas por `scripts/build_diplomados.py` (determinístico; auto-tag de `functional_areas` por título contra el taxonomy). **157/203 con área profesional; 46 marcados `interes_personal`** (arte, astronomía, nutrición-fitness, religión…) → nunca se recomiendan en un diagnóstico de necesidades de formación profesional. A diferencia de las 22 maestrías con datos modelados (limitación #1), los diplomados provienen de **fuente oficial verificada**.
- **Ruteo (track primario + cruce):** la Fase 5 captura las señales de restricción/preferencia y `derive_track` deriva `learning_track` ∈ `maestria` | `diplomado` | `ambos` por **puntuación multi-señal** (espejo exacto de `deriveTrack` del sitio — paridad verificada). Modelo actual (ya **no** usa los booleanos `transformational_goal` / `willing_long_commitment`):
  - **Horas:** `<6` → diplomado (+2) · `>10` → maestría (+1) · **6-10 neutral** ("tener horas ya no basta").
  - **Ambición (desde `career_path.primary_objective`):** objetivo puntual (`specialization`, `career_acceleration`) → diplomado (+2) · transformacional (`promotion_vertical`, `industry_switch`, `entrepreneurship`, `international_career`, `technical_to_management`, `broadening`) → maestría (+2).
  - **Señales diplomado (+1 c/u):** `flexibility_need=alta` · `application_horizon=inmediata_practica` · `payment_preference∈{por_modulo,parcialidades}` · `life_load` ≥ 2 cargas.
  - **Señales maestría (+1 c/u):** `application_horizon=transformacional` · `company_sponsored=true`.
  - **Señal maestría fuerte (+2):** `compara_universidades=true` — el aspirante compara universidades/modalidad/costo-valor/titulación antes de decidir. Del **perfil del comprador WON** (matriz hard/soft skills, 2026-08-06): el comprador de maestría es deliberativo/comparador; el de diplomado es transaccional y no compara. Ver `references/won-buyer-profile.md`. Captura: Fase 5 (o espontánea) en el skill · pregunta P13 en el wizard. **Paridad sitio↔skill verificada.**
  - **Decisión:** `diplomado` si dip≥2 y dip>mae · `maestria` si mae≥3 y mae>dip · en otro caso `ambos`.
- `compute_match.py --diplomados …` puntúa ambos pools (**pesos diplomado actuales: functional_areas 0.45 · gap_coverage 0.20 · time_fit 0.25 · industry 0.10** — el fit de área domina y `gap_coverage` pesa menos por ser señal ruidosa derivada del dolor; umbral **45**) y devuelve el pool primario + un `crossover_recommendation` del otro (p.ej. maestría + diplomado puente).
- **Reglas** en `assets/matching_rules.json#/learning_track` y `#/diplomado_score_weights`. Cuestionario actualizado en `references/conversation-flow.md` (Fase 5 + 5.5 de objeciones/viabilidad + Fase 6).

## Reglas duras (no negociables)

1. **Solo programas en `programs.json`** — si nada supera el umbral 50, decirlo abiertamente y sugerir formación complementaria fuera del catálogo
2. **Mínimo 3 datos por plano** (9 datos totales) antes de recomendar
3. **Nunca prometer resultados de carrera** ("con esta maestría serás CEO en 3 años") — hablar en probabilidad y capacidades
4. **No inventar precios, fechas, becas, docentes** — redirigir a admisiones
5. **No psicoanalizar** — sí señalar incongruencias entre datos del usuario
6. **No pedir datos personales sensibles** (RFC, teléfono, dirección) salvo que el usuario los ofrezca
7. **Si el gap es certificación profesional** (CFA, CPA, abogado postulante, médica) que ningún programa otorga, decirlo: el posgrado **complementa** pero no **sustituye** la certificación
8. **Elegibilidad de maestría (título)** — al **inicio del cuestionario (Fase 1)** se pregunta "¿cuentas con título de licenciatura vigente?" (`profile.has_university_degree`). Si es **`false`** (sin título / en trámite), el diagnóstico se **limita a diplomados**: el motor fuerza `learning_track = diplomado` y **NO ofrece ninguna maestría** (tampoco como `crossover_recommendation`), porque las maestrías Anáhuac requieren título + cédula. Implementado igual en el skill (`compute_match.py`) y en el sitio (`deriveTrack` + pantalla de elegibilidad antes del wizard) — paridad verificada.

## 12 casos especiales (`special-cases.md`)

| # | Escenario | Respuesta |
|---|---|---|
| 1 | Sin licenciatura concluida | Las maestrías Anáhuac requieren título y cédula. Decirlo claro, hacer el diagnóstico de necesidades de formación igual para orientar formación previa |
| 2 | Senior C-level (>15 años) | Diagnóstico estratégico, no técnico. Preguntar: certificación, reskilling o estructura |
| 3 | Transición radical de carrera | La maestría es palanca, no garantía — proponer acciones complementarias |
| 4 | Indeciso / "no sé qué quiero" | Reducir abstracción; si no logra concreción tras 3–4 intentos, sugerir coaching antes |
| 5 | Burnout o crisis personal | No psicoanalizar. Ofrecer pausar. Nunca recomendar un programa como "solución" |
| 6 | Comparativos con otras universidades | No descalificar. Mantener foco en Anáhuac, dar criterios objetivos para comparar |
| 7 | La empresa lo está empujando | Preguntar si **él** lo quiere también — riesgo de abandono |
| 8 | Pregunta por costos/becas/fechas | **No inventar**. Redirigir a admisiones |
| 9 | Pregunta por contenido específico de asignatura | Solo para los 2 programas verificados hay detalle textual; para los otros, redirigir |
| 10 | Solo quiere validación, no diagnóstico | Hacer el matching igual y decirlo con argumentos — esa es la lealtad real |
| 11 | Más de un objetivo competidor | Forzar jerarquía: *"¿cuál te dolería menos abandonar?"*; si insiste, dos diagnósticos |
| 12 | Recomendación con datos modelados | Incluir nota al final del reporte sobre validación con brochure oficial |

## Datos institucionales (no inventar)

- **Sitio:** https://online.anahuac.mx/maestrias-en-linea/
- **Email:** info@onlineanahuac.mx
- **Teléfono:** (55) 5062-3403
- **WhatsApp:** 55 9414-7545

Datos compartidos del catálogo (sí citables):
- 100% online · sesiones síncronas grabadas
- Duración: 27–28 meses (≈2 años 4 meses)
- 18 asignaturas por maestría
- Dedicación: 6–10 horas/semana
- Plataforma: Budly con IA generativa (reconocida por QS Reimagine Education)
- RVOE SEP · titulación directa (sin tesis)
- Insignias Pearson Soft Skills (únicos en Latinoamérica)
- Universidad Anáhuac: más de 60 años de trayectoria, presencia en 18 países

## Limitaciones conocidas + bugs flageados

| # | Item | Impacto |
|---|---|---|
| 1 | **22 de 24 maestrías con datos modelados** (no verificados oficialmente). Solo Dirección del Capital Humano y Analítica de Negocios tienen plan verificado contra el sitio oficial | Para los 22, el reporte **debe incluir** nota de validación con brochure oficial (`special-cases.md` §12). Riesgo: usuario no lee la nota |
| 2 | **✅ RESUELTO (2026-07-13)** — Inconsistencia "5 vs 6 fases". La fuente real estaba en `SKILL.md` (Bloque 1 rotulado "fases 1-5" mientras el cuerpo decía "6 fases conversacionales" sin reconciliar; peor aún en el `.tar.gz`, que había perdido la frase reconciliadora). `agent_system_prompt.md` ya decía "6 fases" | Corregido en `SKILL.md` (fuente) y en el `.tar.gz` reempaquetado (backup `.bak`). Todas las menciones ahora dicen **6 fases** (1-5 conversacionales de recolección + fase 6 diagnóstico) |
| 3 | **✅ RESUELTO (2026-07-13)** — Paths inconsistentes. `files/` estaba plano pero `SKILL.md`/`README` referenciaban `references/`, `scripts/`, `assets/` | Reorganizado: los `.md` movidos a `references/`, los `.py` a `scripts/` (`assets/` ya existía). Verificado: **0 referencias rotas**, scripts compilan, y el layout de la fuente ahora es idéntico al del paquete |
| 4 | **Tensión "no inventar" vs "modelar"** — el anti-patrón #6 prohíbe inventar contenidos del plan de estudios, pero 22 programas tienen contenido modelado de fuentes secundarias | Zona gris que vale la pena explicitar en SKILL.md |
| 5 | **Sin tarifas, fechas, becas** — el agente nunca da estos datos | Es **regla deliberada**, no bug — siempre redirigir a admisiones |
| 6 | **Solo maestrías en español** | No cubre especialidades, diplomados, licenciaturas, doctorados ni programas presenciales |
| 7 | **✅ RESUELTO (2026-08-30)** — `session_template.json` con vocabulario viejo | La plantilla de sesión seguía en `professional_profile` / `current_seniority` / `functional_areas_current` / `hard_skills_strong` mientras `dnc_schema.json` y los tres scripts ya usaban `profile` / `seniority_level` / `current_functional_areas` / `current_hard_skills` (reconciliados 2026-07-24): si el agente armaba la sesión desde la plantilla, el motor no encontraba las áreas y `fa_score` caía a 0. **Reescrita** conforme a `dnc_schema.json` (verificado: 0 claves fuera del schema, 0 faltantes en los 5 bloques), incluyendo `readiness_objections` y las señales de ruteo (`flexibility_need`, `application_horizon`, `payment_preference`, `life_load`, `compara_universidades`), con enums en `$comment` y el gate `has_university_degree`. También se alineó el bloque de sesión de `SKILL.md`. **Medido:** mismo perfil, `fa` 0 → 50 y match 52.0 → 74.5 |
| 8 | **Leads históricos sin los campos nuevos** | Los ~205 leads previos no tienen `key_gap`, `planned_time`, `rango_edad` ni `industry` (este último se enviaba pero no se guardaba, **no recuperable**). Las tablas y filtros que dependen de ellos dirán «0 de N» hasta que entren leads nuevos |

## Output canónico

Al cierre de la conversación (Fase 6), además del mensaje conversacional, el agente emite un objeto JSON conforme a `dnc_schema.json#/$defs/DNCOutput`:

```json
{
  "session_id": "uuid",
  "dnc_input": { /* todo lo recolectado */ },
  "dnc_output": {
    "diagnosis": {
      "executive_summary": "...",
      "alignment_score": 0,
      "gaps": [
        { "id": "GAP-001", "type": "...", "competency": "...",
          "severity": "...", "evidence": "..." }
      ],
      "business_impact_mapping": [ /* mapeo a 4 pilares */ ]
    },
    "recommendations": [
      {
        "program_id": "MAE-XX-000",
        "rank": 1,
        "match_score": 0,
        "match_breakdown": { /* desglose por componente */ },
        "gaps_addressed": ["GAP-001"],
        "rationale": "..."
      }
    ],
    "next_steps": ["..."]
  }
}
```

El JSON se persiste para la empresa y para análisis agregado.

### Reporte agregado de skills por empresa (audiencia secundaria · añadido 2026-08-06)

Dos reportes agregados y anónimos para la empresa (ambos con guard anti-reidentificación: no reportan grupos con < 5 aspirantes):

- **`scripts/company_skills_report.py`** — **mapa de plantilla**: composición por nivel, **fortalezas más comunes** (de `self_assessed_strengths`, capturadas en Fase 2 y mapeadas a `taxonomy.json#/hard_skills_catalog` + `soft_skills_catalog`), **brechas recurrentes** (de `diagnosis.gaps`, ponderadas por severidad) y **programas más pertinentes**. Las fortalezas son autoevaluación direccional (no assessment formal). Uso: `python company_skills_report.py --sessions <carpeta> --company "<nombre>" --taxonomy assets/taxonomy.json`.
- **`scripts/gap_program_value_report.py`** (añadido 2026-08-06) — **puente Brecha → Programa → Valor dual**: por cada brecha detectada, el **programa (diplomado/maestría) que la cierra** (vía `recommendations[].gaps_addressed`), el **valor para el aspirante** (competencia que desarrolla, según el tipo de brecha) y el **valor para la empresa** (los **4 pilares de negocio**, de `business_impact_mapping` — normaliza sus dos formas: array del schema y dict de la plantilla). Es el caso de negocio de la inversión en formación. Uso: `python gap_program_value_report.py --sessions <carpeta> --company "<nombre>"`.

Ambos son **skill-side, sin impacto en el matching ni en el sitio** (las fortalezas no entran al scoring). Para 22 de 24 maestrías el plan es modelado → validar con brochure oficial antes de decidir inversión.

### Captura de leads en el sitio (funnel · dashboard)

El sitio (lead-gen) captura datos de contacto + un campo demográfico en **ambos** formularios de registro: el **gate pre-wizard** (`gateEdad`) y el **formulario post-wizard anónimo** (`leadEdad`). Campos: `nombre`, `telefono`, `email`, `consentimiento`, `self_assessed_strengths` (fortalezas), y **`rango_edad`** (añadido 2026-08-07).

- **`self_assessed_strengths` (fortalezas)** — se captura en el wizard con la **pregunta P12 de hard/soft skills**, que **reemplazó** a la antigua pregunta de esquema de pago (2026-08-06). Autoevaluación direccional (≥1 obligatoria, no assessment formal); **no entra al scoring**. Requiere columna `Fortalezas` en el Sheet + `data.self_assessed_strengths` en el `appendRow`.
- **`rango_edad`** — obligatorio, 4 cohortes: `18-29` · `30-45` · `46-61` · `62-80`. Es **demográfico para segmentación de leads, NO entra al scoring ni al ruteo** (a diferencia de las señales de `derive_track`). Se envía en el payload del POST a Apps Script → requiere columna `rango_edad` en el Sheet + `data.rango_edad` en el `appendRow`. Surge como **columna «Edad» + filtro por cohorte + campo en el modal** del dashboard de leads. Los ~133 leads históricos quedan sin valor (capturados antes del campo).
- **`industry`** — industria de la organización (pregunta P4 del wizard, `answers.industry`). **Sí entra al scoring** (`industry_fit`, peso 0.10 en `derive_track`/`compute_match`), a diferencia de edad/fortalezas. **No confundir con `functional_area`** (área funcional del puesto) ni con `area-necesita` — son campos distintos. **Bug detectado y resuelto (2026-08-07):** el sitio capturaba y enviaba `industry` en ambos payloads (`index.html:1234`/`2030`), pero **faltaba la columna en el Sheet**, así que el `appendRow` lo descartaba y llegaba vacío al dashboard (columna «Industria» y su filtro vacíos). Fix: (a) columna `industry` en el Sheet + `data.industry` en el `appendRow`; (b) **fallback tolerante** en el dashboard que normaliza `l.industry` desde variantes del header (`industry`/`industria`/`Industria`/`Industry`) al cargar, para columna, filtro, modal y orden. **Validado (2026-08-07)** con POST de prueba: `industry:"salud_bienestar"` aterrizó correctamente en la columna. Los ~133 leads históricos quedan sin industria (el dato se enviaba pero nunca se guardó — **no recuperable**).
- **`company_key`** (añadido 2026-08-29) — «Clave de compañía», campo abierto **numérico de 4 dígitos, obligatorio**, en ambos formularios (`#gateCompanyKey` y `#leadCompanyKey`): `inputmode=numeric` + `maxlength=4` + `oninput` que strippea no-dígitos + validación `/^\d{4}$/`. Demográfico/segmentación, **no entra al scoring**. La columna ya existía en el Sheet y el Apps Script.
- **`key_gap` y `planned_time`** (añadidos 2026-08-29) — dos valores que el wizard **ya capturaba pero no enviaba**: `key_gap` = `input.pain` (P5, el reto/brecha en texto libre) y `planned_time` = `input.timing_funding` (P10, cuándo planea comenzar: `soon_self` · `soon_sponsor` · `year_undefined` · `exploring`). Se leen de `window._lastDiagnosisInput` y van en **ambos** payloads. Validado con POST de prueba (leído de vuelta idéntico). El `doPost` mapea por nombre de campo→columna, así que basta con enviar la key correcta.
- Anti-spam del endpoint: honeypot (`website`) + token compartido en el payload (defensa por oscuridad, complementa el honeypot).

**Dashboard de leads** (`dashboard/index.html`, protegido por password) — 3 pestañas:

1. **Leads** — tabla + filtros (fecha, industria, **compañía**, **rango de edad**, **inicio planeado**, búsqueda), modal de detalle y KPIs. La columna y el filtro **«Origen»** se **eliminaron** el 2026-08-29 (el modal de detalle sí lo sigue mostrando); en su lugar entró **«Inicio planeado»** (`planned_time`, con etiquetas humanizadas vía `PLANNED_TIME_LABELS`).
2. **Radar de competencias** — radares hard (8) + soft (10) dibujados en Canvas, **en vivo** desde los leads: la demanda de cada eje se infiere del mix de seniority × competencias prioritarias por nivel de la matriz. Filtros de **Programa recomendado + Rango de edad** (2026-08-07) **+ Industria + Compañía** (2026-08-29) que recalculan el corte.
3. **Reporte de brechas** — mismos filtros (**Programa + Rango de edad + Industria + Compañía**) alimentan el panel **«Corte seleccionado»** con señales reales del funnel (nº de leads, `score-brechas` prom., match prom., distribución de `area-necesita`, mix de seniority). El 2026-08-29 la pestaña quedó **100% real**: la tabla demo «Brecha → Programa → Valor dual» (aspirantes ficticios) se reemplazó por **«Brechas reales del funnel»** — tabla por-lead poblada en `renderBrechas` con `key_gap` / `area-necesita` / `score-brechas` / fortalezas / `top_match_name`, filtrable, que solo lista leads con `key_gap`; y se eliminó la sección demo «Impacto 4 pilares». El puente Brecha→Programa→Valor dual **completo** (con brechas de competencia diagnosticadas) sigue viniendo de las sesiones del skill vía `gap_program_value_report.py`.

**Filtros de compañía e industria (2026-08-29):** `filterCompany` en Leads y `radarIndustry`/`radarCompany` + `brechasIndustry`/`brechasCompany` en las otras dos; `reportLeads()` se generalizó a `(programId, ageId, industryId, companyId)` y el poblado quedó en `populateIndustryFilter` (3 pestañas) + `populateCompanyFilters`. Verificado headless contra los 205 leads reales. Nota: 136 de esos 205 comparten `company_key` «1001».

**Verificación de los filtros de reporte (2026-08-07):** se ejecutó el JS **desplegado en vivo** (extraído del HTML publicado) contra los 133 leads reales + leads sintéticos con edad, en un stub de DOM. Todos los casos pasaron: `populateProgramFilters` puebla 45 opciones (1 «Todos» + **44 programas reales** distintos de `top_match_name`); `reportLeads` filtra correctamente por programa (17→19 con sintéticos), por edad (`30-45`→2) y por ambos combinados (intersección = 2); `drawRadars` recalcula el conteo del corte; `renderBrechas` genera el panel «Corte seleccionado» con las barras de área/seniority; y un corte sin match (`62-80` sobre históricos sin edad) muestra el aviso de vacío. **Confirmado**: el filtro de edad da 0 sobre los ~133 leads históricos (sin `rango_edad`) y segmenta bien en cuanto entran leads nuevos con edad; el filtro de programa ya opera plenamente con la base actual.

## Comportamiento del proyecto (de `CLAUDE.md`)

Hay dos modos de operación:

- **Modo consejero:** si el usuario menciona selección de posgrado, maestrías, diagnóstico de necesidades de formación, brechas de competencias, plan de carrera, formación ejecutiva → leer `SKILL.md` y actuar como TalentAdvisor
- **Modo ingeniero de prompts:** si el usuario pide ayuda con mantener / modificar / probar el skill (editar catálogo, ajustar pesos, mejorar prompts) → actuar como mantenedor sobre los archivos del skill

**Cuándo NO usar el skill:**
- Pregunta por otras universidades sin mencionar Anáhuac
- Pide ayuda con doctorados, licenciaturas, cursos cortos o diplomados específicos
- Usuario en crisis personal o burnout severo (seguir `special-cases.md` §5; no forzar el flujo diagnóstico de necesidades de formación)
