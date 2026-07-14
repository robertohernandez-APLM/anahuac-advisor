# anahuac-advisor

Skill de Claude Code que actúa como consejero vocacional para las **24 maestrías en línea de Universidad Anáhuac**, usando la metodología **diagnóstico de necesidades de formación**.

## Qué hace

Conduce una entrevista estructurada de 6 fases (apertura → perfil profesional → contexto organizacional → trayectoria deseada → restricciones → diagnóstico) y produce un JSON con:

- Diagnóstico de brechas tipificadas y priorizadas por severidad
- Mapeo a 4 pilares de impacto de negocio (rendimiento, recursos, adaptación, errores/costos)
- Hasta 3 maestrías recomendadas con score 0-100 y desglose
- Próximos pasos accionables

## Quick start

1. Instala la skill (copia este directorio a `~/.claude/skills/` o el path que use tu Claude Code).
2. Abre una sesión de Claude Code en cualquier directorio.
3. Dile algo como *"ayúdame a decidir qué maestría tomar en Anáhuac"* — la skill se activa sola.

## Probar los scripts manualmente

Los scripts viven en `scripts/` y todos usan flags (no stdin). Usa `assets/session_template.json` como punto de partida para tus sesiones de prueba.

```bash
# 1. Valida que la sesión tenga datos mínimos (3 por plano)
python3 scripts/validate_dnc.py --session assets/session_template.json

# 2. Calcula scores determinísticos y devuelve top 3
python3 scripts/compute_match.py \
  --session  assets/session_template.json \
  --programs assets/programs.json \
  --taxonomy assets/taxonomy.json \
  --rules    assets/matching_rules.json

# 3. Renderiza el reporte final markdown
python3 scripts/render_report.py \
  --session  assets/session_template.json \
  --template assets/report_template.md \
  --out      reporte.md
```

## Mapa rápido del repo

| Archivo | Para qué |
|---|---|
| `SKILL.md` | Protocolo del agente (qué hace, cómo conversa, cómo decide) |
| `CLAUDE.md` | Contexto general del proyecto para Claude Code |
| `references/methodology-dnc.md` | Modelo conceptual diagnóstico de necesidades de formación (3 planos, 4 pilares, 6 tipos de gap) |
| `references/conversation-flow.md` | Las 6 fases con bank de preguntas |
| `references/matching-algorithm.md` | Cómo se calcula el match_score (fórmula + ejemplo) |
| `references/special-cases.md` | Burnout, transición, sin licenciatura, comparativos |
| `assets/programs.json` | Catálogo de las 24 maestrías |
| `assets/taxonomy.json` | Vocabulario controlado |
| `assets/dnc_schema.json` | JSON Schema del input + output |
| `assets/matching_rules.json` | Pesos del scoring + diccionario de sinónimos |
| `assets/session_template.json` | Plantilla del estado de sesión |
| `assets/report_template.md` | Plantilla del reporte markdown final |
| `scripts/validate_dnc.py` | Valida que la sesión tenga datos mínimos antes del diagnóstico |
| `scripts/compute_match.py` | Calcula scores determinísticos y retorna top 3 (stdlib, sin deps) |
| `scripts/render_report.py` | Genera el reporte markdown final |

## Datos institucionales (no inventar)

- Email: info@onlineanahuac.mx
- Teléfono: (55) 5062-3403
- WhatsApp: 55 9414-7545
- Sitio oficial: https://online.anahuac.mx/maestrias-en-linea/

## Limitaciones que debes saber

- **Datos del catálogo modelados.** Solo 2 de las 24 maestrías tienen plan de estudios verificado contra el sitio oficial; las otras 22 se modelaron de fuentes secundarias y deben validarse con brochures oficiales antes de producción.
- **Sin tarifas.** El agente nunca da precios, fechas ni becas — siempre redirige.
- **Sólo master's en español.** No cubre especialidades, diplomados ni programas presenciales.

Para detalle técnico, ver `CLAUDE.md`.
