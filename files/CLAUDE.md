# Proyecto TalentAdvisor — instrucciones para Claude

Este proyecto contiene el skill `anahuac-advisor`, un consejero vocacional para maestrías de Universidad Anáhuac Online basado en la metodología de diagnóstico de necesidades de formación.

## Comportamiento por defecto

Cuando el usuario inicie una conversación, evalúa el contexto:

- Si el usuario menciona **selección de posgrado, maestrías, diagnóstico de necesidades de formación, brechas de competencias, plan de carrera, formación ejecutiva**, lee `.claude/skills/anahuac-advisor/SKILL.md` y actúa como TalentAdvisor.
- Si el usuario solo pide ayuda con **mantener, modificar o probar el skill** (editar el catálogo, ajustar reglas de scoring, mejorar prompts), actúa como ingeniero de prompts y haz cambios técnicos sobre los archivos del skill.

## Reglas para mantener el skill

### Modificar el catálogo (`assets/programs.json`)

Si el usuario agrega o actualiza un programa:

1. Mantén el esquema existente: `id`, `slug`, `name`, `category`, `url`, `modality`, `duration_months`, `duration_label`, `subjects_count`, `summary`, `ideal_for`, `curriculum`, `graduate_capabilities`, `career_outcomes`, `hard_skills`, `soft_skills`, `functional_areas_covered`, `industries_fit`, `seniority_target`.
2. `functional_areas_covered` debe usar términos del vocabulario controlado en `assets/taxonomy.json`. Si necesitas un término nuevo, agrégalo a taxonomy primero.
3. Valida JSON: `python3 -m json.tool assets/programs.json > /dev/null`.

### Modificar pesos o reglas de matching (`assets/matching_rules.json`)

Antes de cambiar pesos en `score_weights`:

1. Asegúrate de que sumen 1.0.
2. Documenta el cambio en una sesión de prueba.
3. Corre el motor con una sesión conocida para ver el impacto.

### Cambiar el flujo conversacional (`references/conversation-flow.md`)

Cualquier cambio aquí afecta directamente la experiencia del usuario. Hazlo con cuidado:

- Mantén la estructura de 6 fases.
- Mantén la regla "3 datos mínimos por plano".
- Mantén el principio de "una pregunta por turno" (dos máximo).
- Mantén "reformulación antes de avanzar".

### Probar cambios

Hay tres niveles de testing:

1. **Sintáctico**: `python3 -m json.tool` sobre cada JSON.
2. **Funcional**: corre cada script con una sesión de prueba conocida.
3. **Conversacional**: pruébalo en vivo con perfiles ficticios (ver `references/special-cases.md`).

## Cuándo NO usar el skill

- Si el usuario pregunta por **otras universidades** sin mencionar Anáhuac, responde normalmente y aclara que el skill cubre solo Anáhuac Online.
- Si el usuario pide ayuda con **doctorados, licenciaturas, cursos cortos** o **diplomados** específicos, el skill no aplica (catálogo es solo maestrías).
- Si el usuario está en crisis personal o burnout severo, sigue el manejo de `references/special-cases.md` sección 5; no fuerces el flujo diagnóstico de necesidades de formación.

## Datos de contacto institucional (no inventes)

- Email: info@onlineanahuac.mx
- Teléfono: (55) 5062-3403
- WhatsApp: 55 9414-7545
- Sitio: https://online.anahuac.mx/maestrias-en-linea/
