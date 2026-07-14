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
    """Valida plano profesional."""
    edu = profile.get("education") or {}
    exp = profile.get("experience") or {}

    indicators = {
        "undergraduate_degree": bool(edu.get("undergraduate_degree")),
        "years_total": exp.get("years_total") is not None,
        "current_role": bool(exp.get("current_role")),
        "current_responsibilities": bool(exp.get("current_responsibilities")),
        "industries": bool(exp.get("industries")),
        "hard_skills_strong": bool(profile.get("hard_skills_strong")),
        "soft_skills_strong": bool(profile.get("soft_skills_strong")),
        "weakness_signal": bool(profile.get("hard_skills_weak") or profile.get("soft_skills_weak")),
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
        "geography": bool(ctx.get("geography")),
        "business_model": bool(ctx.get("business_model")),
        "current_changes": bool(ctx.get("current_changes")),
        "area_strategic_needs": bool(ctx.get("area_strategic_needs")),
        "support_for_studies": bool(ctx.get("support_for_studies")
                                    and any((ctx.get("support_for_studies") or {}).values())),
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
        "core_motivation": bool(path.get("core_motivation")),
        "personal_non_negotiables": bool(path.get("personal_non_negotiables")),
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
        "modality_preference": bool(cons.get("modality_preference")),
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
        validate_professional(dnc.get("professional_profile") or {}),
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
