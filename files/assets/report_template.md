# Diagnóstico diagnóstico de necesidades de formación y Recomendación de Posgrado

**Sesión**: {{session_id}}
**Fecha**: {{date}}
**Catálogo evaluado**: Universidad Anáhuac Online — Maestrías + Diplomados
**Track de aprendizaje**: {{learning_track}}

---

## 1. Resumen ejecutivo

{{executive_summary}}

**Nivel de alineación de tu plan (0-100)**: {{alignment_score}}

---

## 2. Tu perfil sintetizado

**Rol actual**: {{current_role}}
**Experiencia**: {{years_experience}} años en {{industries}}
**Industria actual**: {{current_industry}}
**Objetivo de carrera**: {{primary_objective}} — {{target_role}}
**Horizonte**: {{horizon_years}} años

---

## 3. Diagnóstico diagnóstico de necesidades de formación — Brechas detectadas

Las brechas están ordenadas por severidad. Cada una está mapeada a los 4 pilares de valor diagnóstico de necesidades de formación que impacta.

{{#each gaps}}
### Brecha {{index}}: {{competency}}

| Atributo | Detalle |
|---|---|
| Tipo | {{type}} |
| Severidad | **{{severity}}** |
| Nivel actual | {{current_proficiency}} |
| Nivel requerido | {{required_proficiency}} |
| Pilares impactados | {{pillars_affected}} |

**Evidencia**: {{evidence}}

{{/each}}

### Mapeo a los 4 pilares de valor

| Pilar | Brechas asociadas |
|---|---|
| **Mejora del rendimiento** | {{pillar_rendimiento}} |
| **Optimización de recursos** | {{pillar_recursos}} |
| **Adaptación al cambio** | {{pillar_adaptacion}} |
| **Reducción de errores y costos** | {{pillar_errores_costos}} |

---

## 4. Programas recomendados

{{#if recommendations_exist}}
Estos son los programas del catálogo Anáhuac Online que mejor calzan con tu diagnóstico. Cada uno se evaluó en seis dimensiones; el score final es ponderado.

{{#each recommendations}}
### {{rank}}. {{program_name}}

**Match score**: **{{match_score}}/100**

**Desglose**:

| Componente | Score | Peso |
|---|---|---|
| Áreas funcionales que cubre | {{functional_areas_match}} | 25% |
| Cobertura de brechas | {{gap_coverage}} | 25% |
| Alineación con objetivo de carrera | {{career_outcome_match}} | 20% |
| Fit con industria | {{industry_fit}} | 10% |
| Fit con seniority objetivo | {{seniority_fit}} | 10% |
| Fit con restricciones | {{constraints_fit}} | 10% |

**Brechas que este programa cierra**:
{{gaps_addressed_list}}

**Por qué te conviene**:
{{rationale}}

**Riesgos o consideraciones**:
{{risks_list}}

**URL del programa**: {{program_url}}

---
{{/each}}
{{else}}
**No procede recomendación con el umbral mínimo de match (50).**

Ningún programa del catálogo Anáhuac Online supera el umbral mínimo para tu perfil y objetivo. Esto puede deberse a:

- Tu objetivo apunta a un dominio o seniority no cubierto por el catálogo.
- Las restricciones de tiempo, formato o idioma son incompatibles con la oferta.
- Tu diagnóstico necesita más información antes de poder emitir recomendación.

**Sugerencias**:
- {{alternative_suggestions}}

{{/if}}

---

## 5. Siguientes pasos

**Esta semana**:
- {{next_step_1}}
- {{next_step_2}}

**Próximas 2 semanas**:
- {{next_step_3}}

**Para inscripción y dudas operativas** (costos, becas, fechas de inicio):

- Email: **info@onlineanahuac.mx**
- Teléfono: **(55) 5062-3403**
- WhatsApp: **55 9414-7545**
- Sitio: **https://online.anahuac.mx/maestrias-en-linea/**

---

## 6. Notas metodológicas

Este diagnóstico aplica la metodología **diagnóstico de necesidades de formación** desde la intersección de tres planos: profesional, organizacional y trayectoria deseada. Las brechas detectadas se ponderan por severidad antes de calcular el match con los programas.

{{#if has_modeled_programs}}
**Sobre el catálogo**: las asignaturas y capacidades detalladas para programas distintos a *Dirección del Capital Humano* y *Analítica de Negocios* están modeladas a partir de fuentes públicas y deben validarse con el brochure oficial que entrega admisiones antes de la decisión final.
{{/if}}

---

*Reporte generado por TalentAdvisor. Este documento es de orientación; la decisión final es del usuario.*
