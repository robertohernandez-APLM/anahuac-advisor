#!/usr/bin/env python3
"""
validate_dnc.py — guardarraíl previo al diagnóstico.

Verifica que el objeto de sesión diagnóstico de necesidades de formación tenga los datos mínimos para emitir un diagnóstico válido.
Regla: al menos 3 datos no-nulos por plano (profesional, organizacional, carrera).

Uso:
    python validate_dnc.py --session <ruta-json>

Retorna:
    exit code 0 si está completo, 1 si falta información.
    Imprime JSON con detalle de qué falta.
"""

import argparse
import json
import sys
from pathlib import Path


MIN_DATA_POINTS_PER_PLANE = 3


def count_filled(obj, keys):
    """Cuenta cuántas de las claves dadas tienen valor no-nulo, no-vacío, no-lista-vacía."""
    count = 0
    for k in keys:
        v = obj.get(k)
        if v is None:
            continue
        if isinstance(v, (list, dict, str)) and len(v) == 0:
            continue
        count += 1
    return count


def validate_professional(profile):
    """Valida plano profesional (vocabulario de dnc_schema.json → ProfessionalProfile)."""
    indicators = {
        "undergraduate_degree": bool(profile.get("undergraduate_degree")),
        "years_experience": profile.get("years_experience") is not None,
        "current_role": bool(profile.get("current_role")),
        "current_functional_areas": bool(profile.get("current_functional_areas")),
        "current_hard_skills": bool(profile.get("current_hard_skills")),
        "current_soft_skills": bool(profile.get("current_soft_skills")),
        "weakness_signal": bool(profile.get("self_assessed_weaknesses")),
    }
    filled = sum(1 for v in indicators.values() if v)
    missing = [k for k, v in indicators.items() if not v]
    return {
        "plane": "professional",
        "filled": filled,
        "required": MIN_DATA_POINTS_PER_PLANE,
        "complete": filled >= MIN_DATA_POINTS_PER_PLANE,
        "missing_or_empty": missing,
    }


def validate_organizational(ctx):
    """Valida plano organizacional."""
    indicators = {
        "company_size": ctx.get("company_size") is not None,
        "industry": bool(ctx.get("industry")),
        "company_strategic_objectives": bool(ctx.get("company_strategic_objectives")),
        "key_business_challenges": bool(ctx.get("key_business_challenges")),
        "department_pain_points": bool(ctx.get("department_pain_points")),
        "expected_role_evolution": bool(ctx.get("expected_role_evolution")),
    }
    filled = sum(1 for v in indicators.values() if v)
    missing = [k for k, v in indicators.items() if not v]
    return {
        "plane": "organizational",
        "filled": filled,
        "required": MIN_DATA_POINTS_PER_PLANE,
        "complete": filled >= MIN_DATA_POINTS_PER_PLANE,
        "missing_or_empty": missing,
    }


def validate_career(path):
    """Valida plano de trayectoria/carrera."""
    indicators = {
        "primary_objective": bool(path.get("primary_objective")),
        "horizon_years": path.get("horizon_years") is not None,
        "target_role": bool(path.get("target_role")),
        "target_seniority": bool(path.get("target_seniority")),
        "target_functional_areas": bool(path.get("target_functional_areas")),
        "motivation": bool(path.get("motivation")),
    }
    filled = sum(1 for v in indicators.values() if v)
    missing = [k for k, v in indicators.items() if not v]
    return {
        "plane": "career",
        "filled": filled,
        "required": MIN_DATA_POINTS_PER_PLANE,
        "complete": filled >= MIN_DATA_POINTS_PER_PLANE,
        "missing_or_empty": missing,
    }


def validate_constraints(cons):
    """Valida restricciones (no es un plano, pero conviene completarlo)."""
    indicators = {
        "weekly_hours_available": cons.get("weekly_hours_available") is not None,
        "preferred_modality": bool(cons.get("preferred_modality")),
    }
    filled = sum(1 for v in indicators.values() if v)
    missing = [k for k, v in indicators.items() if not v]
    return {
        "plane": "constraints",
        "filled": filled,
        "required": 2,
        "complete": filled >= 2,
        "missing_or_empty": missing,
    }


def main():
    parser = argparse.ArgumentParser(description="Valida completitud de sesión diagnóstico de necesidades de formación.")
    parser.add_argument("--session", required=True, help="Ruta al JSON de sesión.")
    args = parser.parse_args()

    session_path = Path(args.session)
    if not session_path.exists():
        print(json.dumps({"status": "error", "message": f"Archivo no encontrado: {args.session}"},
                         ensure_ascii=False, indent=2))
        sys.exit(2)

    with session_path.open(encoding="utf-8") as f:
        session = json.load(f)

    dnc = session.get("dnc_input") or {}
    results = [
        validate_professional(dnc.get("profile") or {}),
        validate_organizational(dnc.get("organizational_context") or {}),
        validate_career(dnc.get("career_path") or {}),
        validate_constraints(dnc.get("constraints") or {}),
    ]

    all_complete = all(r["complete"] for r in results)
    summary = {
        "status": "ready" if all_complete else "incomplete",
        "ready_for_diagnosis": all_complete,
        "planes": results,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if all_complete else 1)


if __name__ == "__main__":
    main()
