#!/usr/bin/env python3
"""
company_skills_report.py — Reporte AGREGADO y ANÓNIMO de skills por empresa.

Audiencia secundaria del proyecto: las empresas. Toma un conjunto de sesiones de diagnóstico
(JSONs ya diagnosticados) y produce un mapa de plantilla — fortalezas comunes,
brechas recurrentes y oportunidades de formación — SIN exponer individuos.

Privacidad: el reporte es agregado y anónimo. Se descartan nombres y cualquier PII;
sólo se reporta un grupo cuando tiene >= MIN_GROUP perfiles (evita reidentificación).
Las fortalezas son AUTOEVALUACIÓN direccional, no un assessment formal.

Uso:
    python company_skills_report.py --sessions <carpeta_o_glob> [--company "<nombre>"]
                                    [--taxonomy assets/taxonomy.json] [--out reporte.md]
"""

import argparse
import glob
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

MIN_GROUP = 5           # no reportar grupos con menos de N perfiles (anti-reidentificación)
SEVERITY_WEIGHT = {"bloqueante": 4, "alta": 3, "media": 2, "baja": 1}


def load_sessions(pattern):
    paths = []
    if os.path.isdir(pattern):
        paths = glob.glob(os.path.join(pattern, "*.json"))
    else:
        paths = glob.glob(pattern)
    out = []
    for p in paths:
        try:
            out.append(json.loads(Path(p).read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def _dnc(session):
    # tolera sesiones con dnc_input anidado o plano
    return session.get("dnc_input") or session


def _label_map(taxonomy):
    """id/término → label legible, para hard_skills_catalog (dict) y soft (lista)."""
    m = {}
    hc = (taxonomy or {}).get("hard_skills_catalog") or {}
    for k, v in hc.items():
        if k.startswith("_"):
            continue
        m[k] = v.get("label", k) if isinstance(v, dict) else k
    for s in (taxonomy or {}).get("soft_skills_catalog") or []:
        m[s] = s
    return m


def aggregate(sessions, taxonomy):
    labels = _label_map(taxonomy)
    n = len(sessions)
    seniority = Counter()
    strengths = Counter()
    gaps_weighted = Counter()   # competency → peso acumulado por severidad
    gaps_people = Counter()     # competency → nº de perfiles que la tienen
    programs = Counter()        # programa recomendado → nº de veces
    tracks = Counter()

    for s in sessions:
        dnc = _dnc(s)
        prof = dnc.get("profile") or {}
        sl = prof.get("seniority_level")
        if sl:
            seniority[sl] += 1
        for st in (prof.get("self_assessed_strengths") or []):
            strengths[labels.get(st, st)] += 1
        # gaps del diagnóstico
        diag = s.get("diagnosis") or (s.get("dnc_output") or {}).get("diagnosis") or {}
        seen = set()
        for g in (diag.get("gaps") or []):
            comp = g.get("competency")
            if not comp:
                continue
            gaps_weighted[comp] += SEVERITY_WEIGHT.get(g.get("severity", "media"), 2)
            if comp not in seen:
                gaps_people[comp] += 1
                seen.add(comp)
        # recomendaciones (oportunidad de formación concreta)
        recs = s.get("recommendations") or (s.get("dnc_output") or {}).get("recommendations") or []
        for r in recs[:3]:
            nm = r.get("program_name")
            if nm:
                programs[nm] += 1
        lt = ((dnc.get("constraints") or {}).get("learning_track")
              or (s.get("dnc_output") or {}).get("learning_track"))
        if lt:
            tracks[lt] += 1

    return {
        "n": n, "seniority": seniority, "strengths": strengths,
        "gaps_weighted": gaps_weighted, "gaps_people": gaps_people,
        "programs": programs, "tracks": tracks,
    }


def _table(counter, n, top=8, pct=True, col="Competencia", countcol="Perfiles"):
    rows = counter.most_common(top)
    if not rows:
        return "_Sin datos suficientes._"
    header = f"| {col} | {countcol} | % |" if pct else f"| {col} | {countcol} |"
    sep = "|---|--:|--:|" if pct else "|---|--:|"
    lines = [header, sep]
    for k, v in rows:
        if pct:
            lines.append(f"| {k} | {v} | {v / n * 100:.0f}% |" if n else f"| {k} | {v} | — |")
        else:
            lines.append(f"| {k} | {v} |")
    return "\n".join(lines)


def render(agg, company, taxonomy):
    n = agg["n"]
    if n < MIN_GROUP:
        return (f"# Reporte de plantilla — {company or 'empresa'}\n\n"
                f"⚠️ Sólo {n} perfil(es) en el grupo (mínimo {MIN_GROUP} para reportar de forma "
                f"anónima sin riesgo de reidentificación). Amplía la muestra antes de generar el reporte.")

    # balance hard/soft esperado por nivel (de la matriz)
    prop = (taxonomy or {}).get("hard_soft_proportion_by_level") or {}
    sen_lines = []
    for lvl, c in agg["seniority"].most_common():
        pr = prop.get(lvl)
        exp = f" · balance esperado hard {pr['hard']}% / soft {pr['soft']}%" if isinstance(pr, dict) else ""
        sen_lines.append(f"- **{lvl}**: {c} perfil(es){exp}")
    sen_block = "\n".join(sen_lines) or "_Sin datos de seniority._"

    # brechas: ponderadas por severidad = prioridad de formación
    gap_rows = agg["gaps_weighted"].most_common(8)
    gap_lines = ["| Brecha (competencia) | Perfiles afectados | Prioridad (peso severidad) |", "|---|--:|--:|"]
    for comp, w in gap_rows:
        gap_lines.append(f"| {comp} | {agg['gaps_people'][comp]} | {w} |")
    gap_block = "\n".join(gap_lines) if gap_rows else "_Sin brechas registradas._"

    return f"""# Mapa de plantilla — oportunidades de formación
### {company or 'Empresa (agregado anónimo)'}

**Perfiles analizados**: {n}  ·  **Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Fuente**: diagnósticos TalentAdvisor (agregado y anónimo · sin datos individuales)

---

## 1. Composición de la plantilla (por nivel)

{sen_block}

**Ruta formativa derivada del diagnóstico**: {', '.join(f'{k} {v}' for k, v in agg['tracks'].most_common()) or '—'}

---

## 2. Fortalezas más comunes (autoevaluación del equipo)

> Autoevaluación direccional (no assessment formal). Útil para identificar apalancamientos internos.

{_table(agg['strengths'], n)}

---

## 3. Brechas recurrentes — prioridades de formación

Ordenadas por **prioridad** (frecuencia × severidad). Éstas son las oportunidades de mayor impacto para la plantilla:

{gap_block}

---

## 4. Oportunidad de formación concreta (programas más pertinentes)

Programas recomendados con mayor recurrencia en los diagnósticos del grupo:

{_table(agg['programs'], n, pct=False, col="Programa", countcol="Menciones")}

---

## 5. Notas

- **Anónimo y agregado**: sin nombres ni datos individuales; grupos con < {MIN_GROUP} perfiles no se reportan.
- Las **fortalezas** son autoevaluación (dirección, no medición rigurosa — para eso, aplicar la matriz BARS/BEI de `Matriz_Hard_y_Soft_Skills_Cuestionario.pdf`).
- Las **brechas** provienen del diagnóstico de necesidades de formación (tipificadas y ponderadas por severidad).
- Para 22 de 24 maestrías el plan de estudios es modelado — validar con brochure oficial antes de decidir inversión de capacitación.

*Reporte generado por TalentAdvisor · company_skills_report.py*
"""


def main():
    ap = argparse.ArgumentParser(description="Reporte agregado y anónimo de skills por empresa.")
    ap.add_argument("--sessions", required=True, help="Carpeta o glob de JSONs de sesión.")
    ap.add_argument("--company", default=None, help="Nombre de la empresa (etiqueta del reporte).")
    ap.add_argument("--taxonomy", default=None, help="taxonomy.json (para labels y balance por nivel).")
    ap.add_argument("--out", default=None, help="Ruta de salida .md (si se omite, imprime a stdout).")
    args = ap.parse_args()

    sessions = load_sessions(args.sessions)
    taxonomy = json.loads(Path(args.taxonomy).read_text(encoding="utf-8")) if args.taxonomy else {}

    # Si se pide una empresa concreta, filtra por organizational_context.company_name
    if args.company:
        sessions = [s for s in sessions
                    if ((_dnc(s).get("organizational_context") or {}).get("company_name") == args.company)]

    agg = aggregate(sessions, taxonomy)
    report = render(agg, args.company, taxonomy)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Reporte generado: {args.out} ({agg['n']} perfiles)")
    else:
        print(report)


if __name__ == "__main__":
    main()
