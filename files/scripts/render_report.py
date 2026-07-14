#!/usr/bin/env python3
"""
render_report.py — genera el reporte markdown final del diagnóstico de necesidades de formación.

Toma el JSON de sesión (con diagnosis y recommendations ya llenados) y la plantilla
en markdown, hace la sustitución de placeholders y produce el archivo final.

Uso:
    python render_report.py \
        --session <ruta-json> \
        --template <ruta-template.md> \
        --out <ruta-salida.md>
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def fmt_list(items, prefix="- ", empty="(ninguna)"):
    if not items:
        return empty
    return "\n".join(f"{prefix}{x}" for x in items)


def fmt_inline_list(items, empty="—"):
    if not items:
        return empty
    return ", ".join(str(x) for x in items)


def render_gaps_section(gaps):
    """Renderiza la sección de brechas iterando."""
    if not gaps:
        return "_Sin brechas relevantes detectadas._"

    severity_order = {"bloqueante": 0, "alta": 1, "media": 2, "baja": 3}
    gaps_sorted = sorted(gaps, key=lambda g: severity_order.get(g.get("severity"), 9))

    blocks = []
    for i, gap in enumerate(gaps_sorted, 1):
        block = f"""### Brecha {i}: {gap.get('competency', '—')}

| Atributo | Detalle |
|---|---|
| Tipo | {gap.get('type', '—')} |
| Severidad | **{gap.get('severity', '—')}** |
| Nivel actual | {gap.get('current_proficiency', '—')} |
| Nivel requerido | {gap.get('required_proficiency', '—')} |
| Pilares impactados | {fmt_inline_list(gap.get('pillars_affected', []))} |

**Evidencia**: {gap.get('evidence', '—')}
"""
        blocks.append(block)
    return "\n".join(blocks)


def _badge(rec):
    """Etiqueta de tipo/duración/dedicación según el track del programa."""
    if rec.get("program_type") == "diplomado":
        dm = rec.get("duration_months") or "~7"
        wh = rec.get("weekly_hours_estimate") or "4-6"
        return f"Diplomado · {dm} meses · ~{wh} h/sem"
    dm = rec.get("duration_months") or "27-28"
    return f"Maestría · {dm} meses · 6-10 h/sem"


def _render_breakdown(rec):
    b = rec.get("match_breakdown", {})
    if rec.get("program_type") == "diplomado":
        rows = [
            ("Áreas funcionales que cubre", b.get("functional_areas_match", 0), "35%"),
            ("Cobertura de brechas", b.get("gap_coverage", 0), "35%"),
            ("Fit de tiempo (cabe en tus horas)", b.get("time_fit", 0), "20%"),
            ("Fit con industria", b.get("industry_fit", 0), "10%"),
        ]
    else:
        rows = [
            ("Áreas funcionales que cubre", b.get("functional_areas_match", 0), "25%"),
            ("Cobertura de brechas", b.get("gap_coverage", 0), "25%"),
            ("Alineación con objetivo de carrera", b.get("career_outcome_match", 0), "20%"),
            ("Fit con industria", b.get("industry_fit", 0), "10%"),
            ("Fit con seniority objetivo", b.get("seniority_fit", 0), "10%"),
            ("Fit con restricciones", b.get("constraints_fit", 0), "10%"),
        ]
    lines = ["| Componente | Score | Peso |", "|---|---|---|"]
    lines += [f"| {n} | {s} | {w} |" for n, s, w in rows]
    return "\n".join(lines)


def render_one_rec(rank, rec, gap_map):
    """Renderiza un programa (maestría o diplomado) adaptando el desglose a su track."""
    gaps_addressed_names = [gap_map.get(gid, gid) for gid in rec.get("gaps_addressed", [])]
    risks = rec.get("risks", [])
    return f"""### {rank}. {rec.get('program_name', '—')}

_{_badge(rec)}_ · **Match {rec.get('match_score', 0)}/100**

**Desglose**:

{_render_breakdown(rec)}

**Brechas que este programa cierra**:
{fmt_list(gaps_addressed_names)}

**Por qué te conviene**:
{rec.get('rationale', '—')}

**Riesgos o consideraciones**:
{fmt_list(risks)}

**URL del programa**: {rec.get('program_url', 'https://online.anahuac.mx/')}
"""


def render_recommendations_section(recommendations, gaps):
    """Renderiza la sección de programas recomendados (separados por regla)."""
    if not recommendations:
        return None
    gap_map = {g.get("id"): g.get("competency") for g in (gaps or [])}
    return "\n---\n\n".join(render_one_rec(rank, rec, gap_map) for rank, rec in enumerate(recommendations, 1))


def render_no_recommendation(scored_below):
    """Sección para cuando no hay recomendaciones que califiquen."""
    body = """**No procede recomendación con el umbral mínimo de match (50).**

Ningún programa del catálogo Anáhuac Online supera el umbral mínimo para tu perfil y objetivo. Esto puede deberse a:

- Tu objetivo apunta a un dominio o seniority no cubierto por el catálogo.
- Las restricciones de tiempo, formato o idioma son incompatibles con la oferta.
- Tu diagnóstico necesita más información antes de poder emitir recomendación.
"""
    if scored_below:
        body += "\n**Para tu información**, los tres programas con mayor afinidad (aún por debajo del umbral) fueron:\n\n"
        for s in scored_below[:3]:
            body += f"- {s.get('program_name')} — score {s.get('match_score')}/100\n"
    return body


def main():
    parser = argparse.ArgumentParser(description="Genera reporte markdown del diagnóstico de necesidades de formación.")
    parser.add_argument("--session", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--scored-below-threshold", default=None,
                        help="JSON opcional con programas que no calificaron (para diagnóstico).")
    args = parser.parse_args()

    session = json.loads(Path(args.session).read_text(encoding="utf-8"))

    dnc = session.get("dnc_input") or {}
    profile = dnc.get("professional_profile") or {}
    exp = profile.get("experience") or {}
    org = dnc.get("organizational_context") or {}
    career = dnc.get("career_path") or {}
    diagnosis = session.get("diagnosis") or {}
    gaps = diagnosis.get("gaps") or []
    gaps_section = render_gaps_section(gaps)
    gap_map = {g.get("id"): g.get("competency") for g in gaps}
    learning_track = (dnc.get("constraints") or {}).get("learning_track") or "—"

    rec_mae = session.get("recommendations_maestria")
    rec_dip = session.get("recommendations_diplomado")

    if rec_mae is not None or rec_dip is not None:
        # Track "ambos": dos pools completos, uno por sección
        rec_section = render_recommendations_section(rec_mae or [], gaps) or "_Ninguna maestría supera el umbral._"
        dip_section = render_recommendations_section(rec_dip or [], gaps) or "_Ningún diplomado supera el umbral._"
        section4_title = "4. Maestrías recomendadas — formato transformacional (~2 años, 6-10 h/sem)"
        crossover_section = "\n## 4b. Diplomados recomendados — formato corto (~7 meses, <6 h/sem)\n\n" + dip_section
    else:
        recommendations = session.get("recommendations") or []
        rec_section = render_recommendations_section(recommendations, gaps)
        if not rec_section:
            scored_below = []
            if args.scored_below_threshold:
                scored_below = json.loads(Path(args.scored_below_threshold).read_text(encoding="utf-8"))
            rec_section = render_no_recommendation(scored_below)
        section4_title = "4. Programas recomendados"
        crossover = session.get("crossover_recommendation")
        crossover_section = ""
        if crossover:
            otro = "diplomado" if crossover.get("program_type") == "diplomado" else "maestría"
            crossover_section = (
                "\n## 4b. Opción complementaria — track " + otro + "\n\n"
                "Del otro formato destaca esta opción. Una maestría puede complementarse con un "
                "diplomado puente; un diplomado puede ser el primer paso hacia una maestría futura.\n\n"
                + render_one_rec(1, crossover, gap_map)
            )

    # Mapeo a pilares
    bim = diagnosis.get("business_impact_mapping") or {}
    pillar_rendimiento = fmt_inline_list(bim.get("rendimiento", []))
    pillar_recursos = fmt_inline_list(bim.get("recursos", []))
    pillar_adaptacion = fmt_inline_list(bim.get("adaptacion", []))
    pillar_errores = fmt_inline_list(bim.get("errores_costos", []))

    # Datos del perfil sintetizado
    current_role = exp.get("current_role") or "—"
    years_exp = exp.get("years_total") or "—"
    industries = fmt_inline_list(exp.get("industries", []))
    current_industry = org.get("industry") or "—"
    primary_obj = career.get("primary_objective") or "—"
    target_role = career.get("target_role") or "—"
    horizon = career.get("horizon_years") or "—"

    # Construir el reporte sin depender del template (sustitución simple)
    # El template existe como referencia humana; aquí generamos directamente.
    report = f"""# Diagnóstico diagnóstico de necesidades de formación y Recomendación de Posgrado

**Sesión**: {session.get('session_id', '—')}
**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Catálogo evaluado**: Universidad Anáhuac Online — Maestrías + Diplomados
**Track de aprendizaje**: {learning_track}

---

## 1. Resumen ejecutivo

{diagnosis.get('executive_summary', '_Resumen no disponible._')}

**Nivel de alineación de tu plan (0-100)**: {diagnosis.get('alignment_score', '—')}

---

## 2. Tu perfil sintetizado

- **Rol actual**: {current_role}
- **Experiencia**: {years_exp} años en {industries}
- **Industria actual**: {current_industry}
- **Objetivo de carrera**: {primary_obj} — {target_role}
- **Horizonte**: {horizon} años

---

## 3. Diagnóstico diagnóstico de necesidades de formación — Brechas detectadas

Las brechas están ordenadas por severidad. Cada una está mapeada a los 4 pilares de valor diagnóstico de necesidades de formación que impacta.

{gaps_section}

### Mapeo a los 4 pilares de valor

| Pilar | Brechas asociadas |
|---|---|
| **Mejora del rendimiento** | {pillar_rendimiento} |
| **Optimización de recursos** | {pillar_recursos} |
| **Adaptación al cambio** | {pillar_adaptacion} |
| **Reducción de errores y costos** | {pillar_errores} |

---

## {section4_title}

{rec_section}
{crossover_section}

---

## 5. Siguientes pasos

**Esta semana**: revisar este reporte completo. Si hay programas recomendados, visitar sus páginas oficiales y comparar el detalle de las asignaturas con tu situación.

**Próximas 2 semanas**: contactar a admisiones para obtener brochure oficial actualizado, costos, becas y fechas de inicio del próximo grupo.

**Para inscripción y dudas operativas** (costos, becas, fechas de inicio):

- Email: **info@onlineanahuac.mx**
- Teléfono: **(55) 5062-3403**
- WhatsApp: **55 9414-7545**
- Sitio: **https://online.anahuac.mx/maestrias-en-linea/**

---

## 6. Notas metodológicas

Este diagnóstico aplica la metodología **diagnóstico de necesidades de formación** desde la intersección de tres planos: profesional, organizacional y trayectoria deseada. Las brechas detectadas se ponderan por severidad antes de calcular el match con los programas.

**Sobre el catálogo**: para las **maestrías**, las asignaturas de programas distintos a *Dirección del Capital Humano* y *Analítica de Negocios* están modeladas a partir de fuentes públicas y deben validarse con el brochure oficial. Los **diplomados** provienen de brochures oficiales de Anáhuac Educación Continua (fuente verificada); aun así, confirma horarios, costos y fechas con admisiones antes de decidir.

---

*Reporte generado por TalentAdvisor. Este documento es de orientación; la decisión final es del usuario.*
"""

    Path(args.out).write_text(report, encoding="utf-8")
    print(f"Reporte generado: {args.out}")


if __name__ == "__main__":
    main()
