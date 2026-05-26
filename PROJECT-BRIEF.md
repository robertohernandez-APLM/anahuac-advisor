# CONSEJERO-DNC / AnáhuacAdvisor — Project Brief

**Engagement:** Skill de Claude Code · consejero vocacional automatizado para las **24 maestrías en línea de Universidad Anáhuac** · metodología **Detección de Necesidades de Capacitación (DNC)**
**Idioma operativo:** Español neutro (mexicano)
**Audiencia primaria:** profesionales mexicanos que trabajan en empresas y buscan posgrado para crecer
**Audiencia secundaria:** las propias empresas (el JSON de cierre se persiste para análisis agregado)
**Brief generated:** 2026-05-25

## Overview

CONSEJERO-DNC contiene el skill `anahuac-advisor`, un agente que conduce una **entrevista estructurada de 6 fases** (apertura → perfil profesional → contexto organizacional → trayectoria deseada → restricciones → diagnóstico) y produce un **JSON estructurado** con:

- Diagnóstico de brechas tipificadas y priorizadas por severidad
- Mapeo a los 4 pilares de impacto de negocio (rendimiento · recursos · adaptación · errores/costos)
- Hasta 3 maestrías recomendadas con score 0–100 y desglose
- Próximos pasos accionables

Es un cambio de marco deliberado: **del consumo educativo al diagnóstico estratégico**. En lugar de "¿qué maestría te gusta más?" la pregunta operativa es "¿qué brechas tienes que cerrar y cuál es el camino formativo más eficiente para cerrarlas?".

Todos los archivos viven en `/Users/macbookprodeaplatam/Desktop/CLAUDE/CONSEJERO-DNC/files/`.

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

Scripts en Python stdlib, sin dependencias externas. El skill empaquetado posiblemente reorganiza paths (referenciados como `assets/`, `references/`, `scripts/` desde el READ ME) — los archivos físicos en `files/` son la fuente.

## Metodología DNC

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

## Reglas duras (no negociables)

1. **Solo programas en `programs.json`** — si nada supera el umbral 50, decirlo abiertamente y sugerir formación complementaria fuera del catálogo
2. **Mínimo 3 datos por plano** (9 datos totales) antes de recomendar
3. **Nunca prometer resultados de carrera** ("con esta maestría serás CEO en 3 años") — hablar en probabilidad y capacidades
4. **No inventar precios, fechas, becas, docentes** — redirigir a admisiones
5. **No psicoanalizar** — sí señalar incongruencias entre datos del usuario
6. **No pedir datos personales sensibles** (RFC, teléfono, dirección) salvo que el usuario los ofrezca
7. **Si el gap es certificación profesional** (CFA, CPA, abogado postulante, médica) que ningún programa otorga, decirlo: el posgrado **complementa** pero no **sustituye** la certificación

## 12 casos especiales (`special-cases.md`)

| # | Escenario | Respuesta |
|---|---|---|
| 1 | Sin licenciatura concluida | Las maestrías Anáhuac requieren título y cédula. Decirlo claro, hacer el DNC igual para orientar formación previa |
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
| 2 | **Inconsistencia "5 vs 6 fases"** en `agent_system_prompt.md` — el header de la sección 3 dice "5 fases" pero el cuerpo lista Fase 1 → Fase 6 | Bug menor de redacción. Si el system prompt se procesa en otro contexto que solo lee el header, podría confundir |
| 3 | **Paths inconsistentes** — el README menciona `references/methodology.md`, `assets/programs.json`, etc., pero los archivos físicos en `files/` no usan esos prefijos | El skill empaquetado (`anahuac-advisor-skill.tar.gz`) posiblemente reorganiza paths. Verificar que las referencias internas del SKILL.md apunten a paths que existen |
| 4 | **Tensión "no inventar" vs "modelar"** — el anti-patrón #6 prohíbe inventar contenidos del plan de estudios, pero 22 programas tienen contenido modelado de fuentes secundarias | Zona gris que vale la pena explicitar en SKILL.md |
| 5 | **Sin tarifas, fechas, becas** — el agente nunca da estos datos | Es **regla deliberada**, no bug — siempre redirigir a admisiones |
| 6 | **Solo maestrías en español** | No cubre especialidades, diplomados, licenciaturas, doctorados ni programas presenciales |

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

## Comportamiento del proyecto (de `CLAUDE.md`)

Hay dos modos de operación:

- **Modo consejero:** si el usuario menciona selección de posgrado, maestrías, DNC, brechas de competencias, plan de carrera, formación ejecutiva → leer `SKILL.md` y actuar como AnáhuacAdvisor
- **Modo ingeniero de prompts:** si el usuario pide ayuda con mantener / modificar / probar el skill (editar catálogo, ajustar pesos, mejorar prompts) → actuar como mantenedor sobre los archivos del skill

**Cuándo NO usar el skill:**
- Pregunta por otras universidades sin mencionar Anáhuac
- Pide ayuda con doctorados, licenciaturas, cursos cortos o diplomados específicos
- Usuario en crisis personal o burnout severo (seguir `special-cases.md` §5; no forzar el flujo DNC)
