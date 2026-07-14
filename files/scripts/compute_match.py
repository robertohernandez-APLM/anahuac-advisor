#!/usr/bin/env python3
"""
compute_match.py — motor de scoring determinístico para el agente diagnóstico de necesidades de formación.

Aplica las reglas definidas en matching_rules.json contra el DNCInput del usuario
y el catálogo en programs.json para producir las top 3 recomendaciones.

Uso:
    python compute_match.py \
        --session <ruta-json-sesion> \
        --programs <ruta-programs.json> \
        --taxonomy <ruta-taxonomy.json> \
        --rules <ruta-matching_rules.json>

Salida: JSON con las top 3 recomendaciones (o menos si no superan el umbral).
"""

import argparse
import json
import sys
from pathlib import Path


# Default fallback — se sobreescribe en main() con rules["scoring_logic"]["gap_coverage"]["severity_weights"] si está presente
SEVERITY_WEIGHTS = {"bloqueante": 4, "alta": 3, "media": 2, "baja": 1}

SENIORITY_ORDER = ["junior", "analista", "lider_o_coordinacion", "gerencia", "direccion"]


def normalize_term(term, synonym_dict):
    """Aplica sinónimos para normalizar términos del usuario."""
    if not isinstance(term, str):
        return term
    t = term.strip().lower().replace(" ", "_")
    return synonym_dict.get(t, t)


def normalize_list(lst, synonym_dict):
    if not lst:
        return []
    return [normalize_term(x, synonym_dict) for x in lst]


def functional_areas_score(user_areas, program_areas, synonym_dict):
    """Componente 1: 25%."""
    user_norm = set(normalize_list(user_areas, synonym_dict))
    prog_norm = set(normalize_list(program_areas, synonym_dict))
    if not user_norm:
        return 0.0
    covered = user_norm & prog_norm
    return (len(covered) / len(user_norm)) * 100.0


def gap_coverage_score(gaps, program, synonym_dict):
    """Componente 2: 25%. Pondera brechas por severidad."""
    if not gaps:
        return 0.0

    prog_areas = set(normalize_list(program.get("functional_areas_covered") or [], synonym_dict))
    prog_hard = set(normalize_list(program.get("hard_skills") or [], synonym_dict))
    prog_soft = set(normalize_list(program.get("soft_skills") or [], synonym_dict))
    prog_capabilities = set(normalize_list(program.get("graduate_capabilities") or [], synonym_dict))
    # Los diplomados exponen su currículum en skills_outputs + modules (no en hard/soft_skills)
    prog_outputs = set(normalize_list(program.get("skills_outputs") or [], synonym_dict))
    prog_modules = set(normalize_list(program.get("modules") or [], synonym_dict))
    prog_total = prog_areas | prog_hard | prog_soft | prog_capabilities | prog_outputs | prog_modules

    total_weight = 0
    covered_weight = 0
    closed_gap_ids = []

    for gap in gaps:
        sev = gap.get("severity", "media")
        weight = SEVERITY_WEIGHTS.get(sev, 1)
        total_weight += weight

        competency = normalize_term(gap.get("competency") or "", synonym_dict)
        # Una brecha se cierra si su competency aparece en alguno de los conjuntos del programa
        # o si hay match parcial por substring en cualquiera de los conjuntos.
        closed = False
        if competency:
            if competency in prog_total:
                closed = True
            else:
                # match laxo por substring para tolerar variaciones de redacción
                for item in prog_total:
                    if competency in item or item in competency:
                        closed = True
                        break

        if closed:
            covered_weight += weight
            closed_gap_ids.append(gap.get("id"))

    if total_weight == 0:
        return 0.0
    score = (covered_weight / total_weight) * 100.0
    return score, closed_gap_ids


def career_outcome_score(primary_objective, target_role, program, synonym_dict):
    """Componente 3: 20%."""
    if not primary_objective and not target_role:
        return 50.0  # neutro si no hay objetivo claro

    outcomes = program.get("career_outcomes") or []
    outcomes_norm = [normalize_term(o, synonym_dict) for o in outcomes]
    target_norm = normalize_term(target_role or "", synonym_dict)

    # Match directo por rol objetivo
    if target_norm:
        for o in outcomes_norm:
            if target_norm in o or o in target_norm:
                return 100.0

    # Match parcial por objetivo
    objective_to_outcomes = {
        "promotion_vertical": ["director", "gerente", "lider"],
        "lateral_move": ["coordinador", "gerente", "lider"],
        "industry_switch": ["consultor", "analista"],
        "specialization": ["especialista", "consultor", "experto"],
        "broadening": ["gerente", "director"],
        "entrepreneurship": ["emprendedor", "fundador", "ceo", "director_general"],
        "international_career": ["director_internacional", "gerente_regional"],
        "consulting": ["consultor", "advisor"],
        "academia": ["docente", "investigador"],
    }

    keywords = objective_to_outcomes.get(primary_objective, [])
    for kw in keywords:
        for o in outcomes_norm:
            if kw in o:
                return 60.0

    return 20.0


def industry_fit_score(user_industry, program, synonym_dict):
    """Componente 4: 10%."""
    if not user_industry:
        return 50.0
    user_norm = normalize_term(user_industry, synonym_dict)
    industries = program.get("industries_fit") or []
    industries_norm = [normalize_term(i, synonym_dict) for i in industries]

    # Match exacto con la industria del usuario es el ideal
    if user_norm in industries_norm:
        return 100.0
    # Si el programa es marcado como universal, calza bien pero no perfecto
    if any(tag in industries_norm for tag in ("transversal", "todas", "todos")):
        return 80.0
    # match parcial por substring
    for i in industries_norm:
        if user_norm in i or i in user_norm:
            return 60.0
    return 20.0


def seniority_fit_score(current_seniority, target_seniority, program_seniority):
    """Componente 5: 10%."""
    if not program_seniority:
        return 50.0

    # program_seniority puede ser string (con comas opcionales) o lista
    if isinstance(program_seniority, list):
        prog_levels = [str(s).strip().lower() for s in program_seniority]
    else:
        prog_norm = str(program_seniority).strip().lower()
        prog_levels = [s.strip() for s in prog_norm.split(",")] if "," in prog_norm else [prog_norm]

    if target_seniority and target_seniority in prog_levels:
        return 100.0
    if current_seniority and current_seniority in prog_levels:
        return 50.0

    # Overshooting o undershooting por orden
    try:
        target_idx = SENIORITY_ORDER.index(target_seniority) if target_seniority else None
        prog_idx_max = max(SENIORITY_ORDER.index(p) for p in prog_levels if p in SENIORITY_ORDER)

        if target_idx is not None:
            if prog_idx_max > target_idx:
                return 70.0  # overshooting
            elif prog_idx_max < target_idx:
                return 20.0  # undershooting
    except (ValueError, KeyError):
        pass

    return 50.0


def constraints_fit_score(constraints, program):
    """Componente 6: 10%."""
    scores = []

    # Tiempo semanal
    hours = constraints.get("weekly_hours_available")
    if hours is not None:
        if hours >= 6:
            scores.append(100.0)
        else:
            scores.append(60.0)
    else:
        scores.append(80.0)  # desconocido, no penalizo demasiado

    # Modalidad
    modality_pref = (constraints.get("modality_preference") or "online").lower()
    prog_modality = (program.get("modality") or "online").lower()
    if "online" in modality_pref and "online" in prog_modality:
        scores.append(100.0)
    elif "presencial" in modality_pref and "presencial" in prog_modality:
        scores.append(100.0)
    elif "presencial" in modality_pref and "online" in prog_modality:
        scores.append(0.0)  # descarte de facto
    else:
        scores.append(80.0)

    # Idioma — asumimos español; si el usuario lo especifica distinto, ajustar
    scores.append(100.0)

    return sum(scores) / len(scores) if scores else 50.0


def score_program(program, dnc_input, rules, synonym_dict):
    """Calcula el match_score completo de un programa."""
    weights = rules["score_weights"]

    profile = dnc_input.get("professional_profile") or {}
    org = dnc_input.get("organizational_context") or {}
    career = dnc_input.get("career_path") or {}
    constraints = dnc_input.get("constraints") or {}

    # Áreas funcionales del usuario.
    # Preferencia: campos explícitos functional_areas_current + functional_areas_target.
    # Fallback: hard_skills_strong + hard_skills_weak (menos preciso).
    user_areas = []
    user_areas.extend(profile.get("functional_areas_current") or [])
    user_areas.extend(career.get("functional_areas_target") or [])
    if not user_areas:
        user_areas = (profile.get("hard_skills_strong") or []) + (profile.get("hard_skills_weak") or [])
    user_areas = list({normalize_term(a, synonym_dict) for a in user_areas if a})

    gaps = (dnc_input.get("diagnosis") or {}).get("gaps", [])
    # Si no se pasaron gaps en dnc_input, podrían venir en session.diagnosis
    if not gaps:
        gaps = dnc_input.get("_gaps", [])

    fa_score = functional_areas_score(user_areas, program.get("functional_areas_covered") or [], synonym_dict)
    gap_result = gap_coverage_score(gaps, program, synonym_dict)
    if isinstance(gap_result, tuple):
        gc_score, closed_gaps = gap_result
    else:
        gc_score, closed_gaps = gap_result, []

    co_score = career_outcome_score(
        career.get("primary_objective"),
        career.get("target_role"),
        program,
        synonym_dict,
    )
    ind_score = industry_fit_score(org.get("industry") or career.get("target_industry"), program, synonym_dict)
    sen_score = seniority_fit_score(
        normalize_term(profile.get("current_seniority") or "", synonym_dict) or None,
        career.get("target_seniority"),
        program.get("seniority_target"),
    )
    con_score = constraints_fit_score(constraints, program)

    total = (
        weights["functional_areas_match"] * fa_score
        + weights["gap_coverage"] * gc_score
        + weights["career_outcome_match"] * co_score
        + weights["industry_fit"] * ind_score
        + weights["seniority_fit"] * sen_score
        + weights["constraints_fit"] * con_score
    )

    return {
        "program_id": program.get("id"),
        "program_name": program.get("name"),
        "program_url": program.get("url"),
        "program_type": "maestria",
        "duration_months": program.get("duration_months"),
        "match_score": round(total, 1),
        "match_breakdown": {
            "functional_areas_match": round(fa_score, 1),
            "gap_coverage": round(gc_score, 1),
            "career_outcome_match": round(co_score, 1),
            "industry_fit": round(ind_score, 1),
            "seniority_fit": round(sen_score, 1),
            "constraints_fit": round(con_score, 1),
        },
        "gaps_addressed": closed_gaps,
        "_n_blocking_closed": sum(
            1 for g in gaps if g.get("id") in closed_gaps and g.get("severity") == "bloqueante"
        ),
    }


def time_fit_score(constraints, diplomado):
    """Factibilidad de tiempo para diplomados (reemplaza seniority/career en el track diplomado)."""
    avail = constraints.get("weekly_hours_available")
    need = diplomado.get("weekly_hours_estimate")
    if need is None or avail is None:
        return 90.0  # desconocido: no penalizar
    if need <= avail:
        return 100.0
    if need - avail <= 2:
        return 70.0
    return 40.0


def score_diplomado(dip, dnc_input, rules, synonym_dict):
    """Scoring del track diplomado: functional_areas + gap_coverage + time_fit + industry."""
    weights = rules.get("diplomado_score_weights") or {
        "functional_areas_match": 0.35, "gap_coverage": 0.35, "time_fit": 0.2, "industry_fit": 0.1
    }
    profile = dnc_input.get("professional_profile") or {}
    org = dnc_input.get("organizational_context") or {}
    career = dnc_input.get("career_path") or {}
    constraints = dnc_input.get("constraints") or {}

    user_areas = []
    user_areas.extend(profile.get("functional_areas_current") or [])
    user_areas.extend(career.get("functional_areas_target") or [])
    if not user_areas:
        user_areas = (profile.get("hard_skills_strong") or []) + (profile.get("hard_skills_weak") or [])
    user_areas = list({normalize_term(a, synonym_dict) for a in user_areas if a})

    gaps = (dnc_input.get("diagnosis") or {}).get("gaps", []) or dnc_input.get("_gaps", [])

    fa = functional_areas_score(user_areas, dip.get("functional_areas_covered") or [], synonym_dict)
    gap_result = gap_coverage_score(gaps, dip, synonym_dict)
    gc, closed = gap_result if isinstance(gap_result, tuple) else (gap_result, [])
    tf = time_fit_score(constraints, dip)
    ind = industry_fit_score(org.get("industry") or career.get("target_industry"), dip, synonym_dict) \
        if dip.get("industries_fit") else 70.0

    total = (
        weights["functional_areas_match"] * fa
        + weights["gap_coverage"] * gc
        + weights["time_fit"] * tf
        + weights["industry_fit"] * ind
    )
    return {
        "program_id": dip.get("id"),
        "program_name": dip.get("name"),
        "program_url": dip.get("url"),
        "program_type": "diplomado",
        "duration_months": dip.get("duration_months"),
        "weekly_hours_estimate": dip.get("weekly_hours_estimate"),
        "match_score": round(total, 1),
        "match_breakdown": {
            "functional_areas_match": round(fa, 1),
            "gap_coverage": round(gc, 1),
            "time_fit": round(tf, 1),
            "industry_fit": round(ind, 1),
        },
        "gaps_addressed": closed,
        "_n_blocking_closed": sum(
            1 for g in gaps if g.get("id") in closed and g.get("severity") == "bloqueante"
        ),
    }


def rank(scored, min_score, top):
    """Filtra por umbral y ordena con los tie-breakers estándar. Sirve para ambos pools."""
    q = [s for s in scored if s["match_score"] >= min_score]
    q.sort(key=lambda x: (
        -x["match_score"],
        -x.get("_n_blocking_closed", 0),
        -x["match_breakdown"].get("gap_coverage", 0),
        -x["match_breakdown"].get("career_outcome_match", x["match_breakdown"].get("time_fit", 0)),
        (x.get("duration_months") or 999),  # a igualdad, primero el más corto (camino más rápido)
        x["program_name"] or "",
    ))
    result = q[:top]
    for t in result:
        t.pop("_n_blocking_closed", None)
    return result


def derive_track(session):
    """Deriva learning_track de las restricciones (Fase 5) si no viene explícito."""
    c = (session.get("dnc_input") or {}).get("constraints") or {}
    if c.get("learning_track") in ("maestria", "diplomado", "ambos"):
        return c["learning_track"]
    hours = c.get("weekly_hours_available")
    transf = c.get("transformational_goal")      # bool | None
    commit = c.get("willing_long_commitment")     # bool | None
    if hours is not None and hours < 6:
        return "diplomado"
    if transf is False:
        return "diplomado"
    if transf and commit and (hours is None or hours >= 6):
        return "maestria"
    return "ambos"


def main():
    parser = argparse.ArgumentParser(description="Motor de matching diagnóstico de necesidades de formación × Anáhuac (maestrías + diplomados).")
    parser.add_argument("--session", required=True, help="JSON de sesión (con dnc_input y diagnosis.gaps).")
    parser.add_argument("--programs", required=True, help="programs.json (maestrías)")
    parser.add_argument("--diplomados", default=None, help="diplomados.json (opcional; activa el track diplomado)")
    parser.add_argument("--taxonomy", required=True, help="taxonomy.json")
    parser.add_argument("--rules", required=True, help="matching_rules.json")
    parser.add_argument("--track", choices=["maestria", "diplomado", "ambos"], default=None,
                        help="Fuerza el track; si se omite se deriva de las restricciones de la sesión.")
    parser.add_argument("--top", type=int, default=3, help="Recomendaciones por pool (default 3).")
    args = parser.parse_args()

    session = json.loads(Path(args.session).read_text(encoding="utf-8"))
    programs_data = json.loads(Path(args.programs).read_text(encoding="utf-8"))
    rules = json.loads(Path(args.rules).read_text(encoding="utf-8"))

    global SEVERITY_WEIGHTS
    loaded_weights = rules.get("scoring_logic", {}).get("gap_coverage", {}).get("severity_weights")
    if loaded_weights:
        SEVERITY_WEIGHTS = loaded_weights

    programs = programs_data["programs"] if isinstance(programs_data, dict) and "programs" in programs_data else programs_data
    synonym_dict = (rules.get("synonym_dictionary") or {}).get("mappings") or {}

    dnc_input = session.get("dnc_input") or {}
    diagnosis = session.get("diagnosis") or {}
    if diagnosis.get("gaps"):
        dnc_input["_gaps"] = diagnosis["gaps"]

    track = args.track or derive_track(session)
    mae_min = rules.get("recommendation_rules", {}).get("minimum_score_to_recommend", 50)
    dip_min = rules.get("diplomado_scoring_logic", {}).get("minimum_score_to_recommend", 45)

    mae_scored = [score_program(p, dnc_input, rules, synonym_dict) for p in programs]
    mae_top = rank(mae_scored, mae_min, args.top)

    dip_scored = []
    if args.diplomados:
        dd = json.loads(Path(args.diplomados).read_text(encoding="utf-8"))
        catalog = dd["diplomados"] if isinstance(dd, dict) and "diplomados" in dd else dd
        catalog = [d for d in catalog if d.get("professional_relevance") != "interes_personal"]
        dip_scored = [score_diplomado(d, dnc_input, rules, synonym_dict) for d in catalog]
    dip_top = rank(dip_scored, dip_min, args.top)

    output = {
        "learning_track": track,
        "n_maestrias_evaluated": len(programs),
        "n_diplomados_evaluated": len(dip_scored),
    }

    if track == "ambos":
        output["recommendations_maestria"] = mae_top
        output["recommendations_diplomado"] = dip_top
        output["no_recommendation"] = not mae_top and not dip_top
    else:
        primary_top = mae_top if track == "maestria" else dip_top
        other_top = dip_top if track == "maestria" else mae_top
        output["recommendations"] = primary_top
        output["crossover_recommendation"] = other_top[0] if other_top else None
        output["no_recommendation"] = len(primary_top) == 0
        if not primary_top:
            pool = mae_scored if track == "maestria" else dip_scored
            pool_sorted = sorted(pool, key=lambda x: -x["match_score"])
            output["best_below_threshold"] = [
                {k: v for k, v in s.items() if k != "_n_blocking_closed"} for s in pool_sorted[:3]
            ]

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
