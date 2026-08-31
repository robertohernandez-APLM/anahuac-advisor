#!/usr/bin/env python3
"""
gap_program_value_report.py — Reporte consolidado Brecha → Programa → Valor dual.

Toma un conjunto de sesiones DNC (varios aspirantes) y produce, de forma AGREGADA y
ANÓNIMA, el puente que conecta:

    Brecha detectada  →  Programa (diplomado/maestría) que la cierra
                      →  valor para el ASPIRANTE (competencia que desarrolla)
                      +  valor para la EMPRESA (4 pilares de negocio)

Audiencia: empresas / RH (caso de negocio de la inversión en formación).
Privacidad: agregado y anónimo; no reporta grupos con < MIN_GROUP aspirantes.

Uso:
    python gap_program_value_report.py --sessions <carpeta_o_glob> [--company "<nombre>"]
                                       [--taxonomy assets/taxonomy.json] [--out reporte.md]
"""

import argparse
import glob
import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

MIN_GROUP = 5
SEVERITY_WEIGHT = {"bloqueante": 4, "alta": 3, "media": 2, "baja": 1}

# Normalización de pilares → label (acepta enum del schema y claves del dict de la plantilla)
PILLAR_LABEL = {
    "mejora_rendimiento": "Mejora del rendimiento", "rendimiento": "Mejora del rendimiento",
    "optimizacion_recursos": "Optimización de recursos", "recursos": "Optimización de recursos",
    "adaptacion_cambios": "Adaptación al cambio", "adaptacion": "Adaptación al cambio",
    "reduccion_errores_costos": "Reducción de errores y costos", "errores_costos": "Reducción de errores y costos",
}

# Cómo enmarcar el valor para el ASPIRANTE según el tipo de brecha que cierra el programa
APPLICANT_VALUE = {
    "knowledge": "Adquiere conocimiento en {c}",
    "skill": "Desarrolla la habilidad de {c}",
    "attitude": "Fortalece mindset/actitud en {c}",
    "certification": "Avanza hacia credencial en {c}",
    "leadership": "Desarrolla competencia directiva en {c}",
    "strategic": "Gana visión estratégica en {c}",
}


def applicant_value(gtype, competency):
    tmpl = APPLICANT_VALUE.get(gtype, "Cierra su brecha en {c}")
    return tmpl.format(c=competency)


def load_sessions(pattern):
    paths = glob.glob(os.path.join(pattern, "*.json")) if os.path.isdir(pattern) else glob.glob(pattern)
    out = []
    for p in paths:
        try:
            out.append(json.loads(Path(p).read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def _dnc(s):
    return s.get("dnc_input") or s


def _diagnosis(s):
    return s.get("diagnosis") or (s.get("dnc_output") or {}).get("diagnosis") or {}


def _recommendations(s):
    return s.get("recommendations") or (s.get("dnc_output") or {}).get("recommendations") or []


def _pillars_for_gap(bim, gap_id, competency):
    """Devuelve el conjunto de labels de pilar asociados a un gap. Normaliza las dos formas
    posibles de business_impact_mapping (array del schema · dict de la plantilla)."""
    pillars = set()
    if isinstance(bim, list):                       # forma schema: [{gap_id, impact_areas, ...}]
        for item in bim:
            if not isinstance(item, dict):
                continue
            if item.get("gap_id") == gap_id:
                for a in item.get("impact_areas", []):
                    if a in PILLAR_LABEL:
                        pillars.add(PILLAR_LABEL[a])
    elif isinstance(bim, dict):                      # forma plantilla: {pilar: [gap_id|competency, ...]}
        for key, lst in bim.items():
            if key in PILLAR_LABEL and isinstance(lst, list):
                if gap_id in lst or (competency and competency in lst):
                    pillars.add(PILLAR_LABEL[key])
    return pillars


def aggregate(sessions):
    n = len(sessions)
    affected = Counter()                 # competency → nº aspirantes
    priority = Counter()                 # competency → peso severidad acumulado
    gtype = {}                           # competency → tipo de gap (último visto)
    prog_by_comp = defaultdict(Counter)  # competency → Counter(program_name)
    prog_type = {}                       # program_name → 'maestria'|'diplomado'
    pillars_by_comp = defaultdict(Counter)  # competency → Counter(pilar_label)
    tracks = Counter()

    for s in sessions:
        diag = _diagnosis(s)
        gaps = diag.get("gaps") or []
        bim = diag.get("business_impact_mapping")
        id2comp = {g.get("id"): g.get("competency") for g in gaps if g.get("competency")}

        seen = set()
        for g in gaps:
            comp = g.get("competency")
            if not comp:
                continue
            priority[comp] += SEVERITY_WEIGHT.get(g.get("severity", "media"), 2)
            if g.get("type"):
                gtype[comp] = g["type"]
            if comp not in seen:
                affected[comp] += 1
                seen.add(comp)
            for pl in _pillars_for_gap(bim, g.get("id"), comp):
                pillars_by_comp[comp][pl] += 1

        # brecha → programa (vía gaps_addressed)
        for r in _recommendations(s):
            name = r.get("program_name")
            if not name:
                continue
            prog_type[name] = r.get("program_type") or prog_type.get(name, "—")
            for gid in (r.get("gaps_addressed") or []):
                comp = id2comp.get(gid)
                if comp:
                    prog_by_comp[comp][name] += 1

        lt = ((_dnc(s).get("constraints") or {}).get("learning_track")
              or (s.get("dnc_output") or {}).get("learning_track"))
        if lt:
            tracks[lt] += 1

    return {
        "n": n, "affected": affected, "priority": priority, "gtype": gtype,
        "prog_by_comp": prog_by_comp, "prog_type": prog_type,
        "pillars_by_comp": pillars_by_comp, "tracks": tracks,
    }


def render(agg, company):
    n = agg["n"]
    if n < MIN_GROUP:
        return (f"# Reporte de brechas y valor formativo — {company or 'empresa'}\n\n"
                f"⚠️ Sólo {n} aspirante(s) (mínimo {MIN_GROUP} para reportar de forma anónima). "
                f"Amplía la muestra.")

    # Puente: una fila por brecha, ordenada por prioridad (severidad × frecuencia)
    rows = []
    for comp, w in agg["priority"].most_common():
        progs = agg["prog_by_comp"].get(comp)
        if progs:
            pname, _ = progs.most_common(1)[0]
            ptype = agg["prog_type"].get(pname, "—")
            prog_cell = f"{pname} ({ptype})"
        else:
            prog_cell = "_sin programa vinculado en los datos_"
        pill = agg["pillars_by_comp"].get(comp)
        pill_cell = ", ".join(k for k, _ in pill.most_common()) if pill else "—"
        gt = agg["gtype"].get(comp, "—")
        rows.append((comp, gt, agg["affected"][comp], w, prog_cell, pill_cell))

    bridge = ["| Brecha (competencia) | Aspirantes | Prioridad | Programa que la cierra | Valor para el ASPIRANTE | Valor para la EMPRESA (pilar) |",
              "|---|--:|--:|---|---|---|"]
    for comp, gt, aff, w, prog, pill in rows[:15]:
        bridge.append(f"| **{comp}** ({gt}) | {aff} | {w} | {prog} | {applicant_value(gt, comp)} | {pill} |")
    bridge_block = "\n".join(bridge)

    # Programas por track: cuántas brechas distintas cierra cada uno
    prog_gapcount = Counter()
    for comp, progs in agg["prog_by_comp"].items():
        for pname in progs:
            prog_gapcount[pname] += 1
    prog_lines = ["| Programa | Tipo | Brechas que cierra |", "|---|---|--:|"]
    for pname, c in prog_gapcount.most_common(10):
        prog_lines.append(f"| {pname} | {agg['prog_type'].get(pname,'—')} | {c} |")
    prog_block = "\n".join(prog_lines) if len(prog_lines) > 2 else "_Sin vínculo brecha→programa en los datos (requiere `gaps_addressed` en las recomendaciones)._"

    # Impacto de negocio agregado por pilar
    pillar_total = Counter()
    for comp, pill in agg["pillars_by_comp"].items():
        for k, c in pill.items():
            pillar_total[k] += c
    pil_lines = ["| Pilar de negocio | Brechas que lo impactan |", "|---|--:|"]
    for k in ["Mejora del rendimiento", "Optimización de recursos", "Adaptación al cambio", "Reducción de errores y costos"]:
        pil_lines.append(f"| **{k}** | {pillar_total.get(k, 0)} |")
    pil_block = "\n".join(pil_lines)

    return f"""# Reporte de brechas y valor formativo
### {company or 'Empresa (agregado anónimo)'}  ·  del dato del aspirante al valor de negocio

**Aspirantes analizados**: {n}  ·  **Brechas distintas**: {len(agg['affected'])}  ·  **Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Ruta formativa derivada**: {', '.join(f'{k} {v}' for k, v in agg['tracks'].most_common()) or '—'}
**Fuente**: diagnósticos TalentAdvisor (agregado y anónimo · sin datos individuales)

Este reporte conecta, en una sola vista, **la brecha detectada → el programa (diplomado o maestría) que la cierra → el valor para el aspirante (competencia que desarrolla) y para la empresa (pilar de negocio)**.

---

## 1. Puente: Brecha → Programa → Valor dual

> Ordenado por **prioridad** (severidad × nº de aspirantes). El **valor para el aspirante** es desarrollar la competencia de la brecha; el **valor para la empresa** es el pilar de negocio que mejora al cerrarla.

{bridge_block}

---

## 2. Programas y cuántas brechas cierra cada uno

Concentra la inversión de formación en los programas de mayor cobertura:

{prog_block}

---

## 3. Impacto de negocio agregado (4 pilares)

Al cerrar estas brechas con formación, así se distribuye el impacto en el negocio:

{pil_block}

---

## 4. Notas

- **Anónimo y agregado**: sin datos individuales; no se reportan grupos con < {MIN_GROUP} aspirantes.
- **Brecha → programa**: se toma de `gaps_addressed` de cada recomendación del diagnóstico; una brecha sin programa vinculado aparece marcada.
- **Valor empresa**: los 4 pilares provienen del `business_impact_mapping` del diagnóstico (metodología DNC).
- Para 22 de 24 maestrías el plan de estudios es modelado — validar con brochure oficial antes de decidir la inversión.

*Reporte generado por TalentAdvisor · gap_program_value_report.py*
"""


def main():
    ap = argparse.ArgumentParser(description="Reporte consolidado Brecha → Programa → Valor dual (empresa).")
    ap.add_argument("--sessions", required=True, help="Carpeta o glob de JSONs de sesión.")
    ap.add_argument("--company", default=None, help="Nombre de la empresa (filtra por company_name y etiqueta).")
    ap.add_argument("--taxonomy", default=None, help="taxonomy.json (opcional).")
    ap.add_argument("--out", default=None, help="Ruta .md de salida (si se omite, imprime a stdout).")
    args = ap.parse_args()

    sessions = load_sessions(args.sessions)
    if args.company:
        sessions = [s for s in sessions
                    if ((_dnc(s).get("organizational_context") or {}).get("company_name") == args.company)]

    report = render(aggregate(sessions), args.company)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Reporte generado: {args.out} ({len(sessions)} aspirantes)")
    else:
        print(report)


if __name__ == "__main__":
    main()
