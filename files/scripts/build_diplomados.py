"""Construye assets/diplomados.json a partir de las brochures en
diplomados/archivos-diplomados/*.md (fuente oficial Anáhuac Educación Continua).

Determinístico y auditable: extrae campos por regex, auto-taggea functional_areas
del taxonomy por palabras clave, estima horas/semana y marca el `track_fit`.
Los programas de interés personal (sin área profesional) quedan con
functional_areas_covered=[] → nunca superan el umbral en un diagnóstico de necesidades de formación de avance profesional.

Uso:
    python3 scripts/build_diplomados.py \
        --brochures ../diplomados/archivos-diplomados \
        --taxonomy assets/taxonomy.json \
        --out assets/diplomados.json
"""
from __future__ import annotations
import argparse, json, os, re, unicodedata, glob, datetime

WEEKS_PER_MONTH = 4.33


def deaccent(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


# palabra_clave (sin acentos) -> lista de functional_areas del taxonomy
KEYWORD_AREAS = {
    # data / tech / IA
    "inteligencia artificial": ["transformacion_digital", "analitica_de_datos"],
    "machine learning": ["analitica_de_datos"],
    "big data": ["analitica_de_datos", "business_intelligence"],
    "business intelligence": ["business_intelligence", "analitica_de_datos"],
    "business analytics": ["business_intelligence", "analitica_de_datos"],
    "ciencia de datos": ["analitica_de_datos"],
    "analitica": ["analitica_de_datos"],
    "estadistica": ["analitica_de_datos"],
    "matematicas para ciencia": ["analitica_de_datos"],
    "excel": ["analitica_de_datos", "business_intelligence"],
    "blockchain": ["transformacion_digital", "fintech"],
    "cloud": ["transformacion_digital"],
    "finops": ["transformacion_digital", "finanzas_corporativas"],
    "transformacion digital": ["transformacion_digital"],
    "salesforce": ["transformacion_digital", "customer_experience"],
    "teletrabajo": ["transformacion_digital", "desarrollo_organizacional"],
    "design thinking": ["innovacion"],
    "ux": ["transformacion_digital", "innovacion"],
    "diseno ux": ["transformacion_digital", "innovacion"],
    "ciberseg": ["compliance", "transformacion_digital"],
    "riesgos ciberneticos": ["gestion_riesgo", "transformacion_digital"],
    "proteccion de datos": ["cumplimiento_normativo", "compliance"],
    "fintech": ["fintech", "finanzas_corporativas"],
    # negocios / estrategia
    "planeacion estrategica": ["estrategia_corporativa"],
    "direccion estrategica": ["estrategia_corporativa", "direccion_general"],
    "administracion de empresas": ["estrategia_corporativa", "direccion_general"],
    "empresas familiares": ["direccion_general", "estrategia_corporativa"],
    "emprendimiento": ["innovacion", "estrategia_corporativa"],
    "desarrollo de negocios": ["estrategia_corporativa", "innovacion"],
    "geopolitica": ["estrategia_corporativa"],
    "innovacion": ["innovacion"],
    "competencias directivas": ["direccion_general", "gestion_talento"],
    "habilidades gerenciales": ["gestion_talento", "direccion_general"],
    "habilidades blandas": ["desarrollo_humano", "capacitacion_y_desarrollo"],
    # proyectos / operaciones
    "gestion de proyectos": ["operaciones", "innovacion"],
    "scrum": ["operaciones", "innovacion"],
    "agil": ["operaciones", "innovacion"],
    "planeacion": ["operaciones"],
    "calidad": ["calidad", "mejora_continua"],
    "lean": ["mejora_continua", "calidad"],
    "logistica": ["logistica", "supply_chain"],
    "cadena de suministro": ["supply_chain", "logistica"],
    "comercio internacional": ["comercio_exterior"],
    "comercio exterior": ["comercio_exterior"],
    # marketing / comercial
    "marketing": ["marketing", "marketing_digital"],
    "neuromarketing": ["marketing", "investigacion_mercados"],
    "publicidad": ["marketing", "marketing_digital"],
    "estrategia comercial": ["marketing", "customer_experience"],
    "customer success": ["customer_experience", "marketing"],
    "fidelizacion": ["customer_experience"],
    "analitica web": ["marketing_digital", "analitica_de_datos"],
    "organizacion de eventos": ["marketing", "comunicacion_corporativa"],
    "marketing politico": ["marketing", "comunicacion_corporativa"],
    # finanzas
    "administracion financiera": ["finanzas_corporativas"],
    "finanzas": ["finanzas_corporativas"],
    "costos y presupuestos": ["finanzas_corporativas", "contabilidad"],
    "riesgos financieros": ["gestion_riesgo", "auditoria"],
    "administracion de riesgos": ["gestion_riesgo"],
    "auditoria": ["auditoria", "compliance"],
    "anticorrupcion": ["compliance", "cumplimiento_normativo"],
    "inversion": ["inversiones", "finanzas_corporativas"],
    "bienes raices": ["inversiones", "finanzas_corporativas"],
    "seguros": ["gestion_riesgo", "finanzas_corporativas"],
    "nominas": ["compensaciones", "contabilidad"],
    "impuestos": ["fiscal_tributario", "contabilidad"],
    # RH / capital humano
    "capital humano": ["recursos_humanos", "gestion_talento"],
    "recursos humanos": ["recursos_humanos", "gestion_talento"],
    "gestion de talento": ["gestion_talento", "recursos_humanos"],
    "gestion del talento": ["gestion_talento", "recursos_humanos"],
    "desarrollo del talento": ["gestion_talento", "capacitacion_y_desarrollo"],
    "efectividad del capital": ["recursos_humanos", "desarrollo_organizacional"],
    "inclusion laboral": ["dei_corporativo", "recursos_humanos"],
    # compliance / legal / gobierno
    "compliance": ["compliance", "cumplimiento_normativo"],
    "esg": ["cumplimiento_normativo", "gobierno_corporativo"],
    "gobierno corporativo": ["gobierno_corporativo", "compliance"],
    "ciberjusticia": ["juridico", "compliance"],
    "derecho sanitario": ["juridico", "administracion_hospitalaria"],
    "ingles legal": ["juridico"],
    "politicas publicas": ["salud_publica", "gobierno_corporativo"],
    "relaciones internacionales": ["estrategia_corporativa"],
    # salud
    "administracion hospitalaria": ["administracion_hospitalaria", "gestion_clinica"],
    "salud ocupacional": ["seguridad_y_salud_ocupacional"],
    "salud mental para profesionales": ["salud_mental_laboral", "gestion_clinica"],
    "salud comunitaria": ["salud_publica"],
    "geriatria": ["gestion_clinica"],
    "cuidados paliativos": ["gestion_clinica"],
    "educacion en diabetes": ["educacion_medica", "gestion_clinica"],
    "enfermeria internacional": ["capacitacion_clinica", "gestion_clinica"],
    "negocios y emprendimiento en salud": ["administracion_hospitalaria", "innovacion"],
    # educación
    "coaching educativo": ["gestion_educativa", "capacitacion_y_desarrollo"],
    "psicopedagogia": ["gestion_educativa", "diseno_instruccional"],
    "didactica": ["diseno_instruccional", "gestion_educativa"],
    "inclusion educativa": ["inclusion_y_diversidad", "gestion_educativa"],
    "desarrollo del capital humano": ["capacitacion_y_desarrollo", "recursos_humanos"],
    # sostenibilidad / ambiental
    "sostenibilidad": ["cumplimiento_normativo", "gestion_riesgo"],
    "ambientales": ["cumplimiento_normativo"],
    "gestion de residuos": ["cumplimiento_normativo", "operaciones"],
    "arquitectura sustentable": ["cumplimiento_normativo"],
    "compliance corporativo": ["compliance", "gobierno_corporativo"],
    # --- ampliación de cobertura (catálogo extendido desde AOL_Diplomados_Links) ---
    "derecho": ["juridico"],
    "precios de transferencia": ["fiscal_tributario"],
    "fiscal": ["fiscal_tributario"],
    "tributacion": ["fiscal_tributario"],
    "comunicacion": ["comunicacion_corporativa"],
    "desarrollo organizacional": ["desarrollo_organizacional", "recursos_humanos"],
    "psicologia organizacional": ["recursos_humanos", "desarrollo_organizacional"],
    "gestion estrategica de capital humano": ["recursos_humanos", "gestion_talento"],
    "people analytics": ["recursos_humanos", "analitica_de_datos"],
    "ventas": ["marketing", "customer_experience"],
    "mercadotecnia": ["marketing"],
    "investigacion de mercados": ["investigacion_mercados", "marketing"],
    "inteligencia comercial": ["marketing", "business_intelligence"],
    "commerce": ["marketing_digital", "transformacion_digital"],
    "marca personal": ["branding", "comunicacion_corporativa"],
    "storytelling": ["marketing_digital", "comunicacion_corporativa"],
    "contenido": ["marketing_digital"],
    "videojuego": ["transformacion_digital"],
    "programacion de apps": ["transformacion_digital"],
    "apps": ["transformacion_digital"],
    "diseno instruccional": ["diseno_instruccional", "e_learning"],
    "e-learning": ["e_learning", "diseno_instruccional"],
    "educaci": ["gestion_educativa"],
    "docente": ["gestion_educativa", "capacitacion_y_desarrollo"],
    "instituciones educativas": ["gestion_educativa", "gestion_academica"],
    "gestion escolar": ["administracion_escolar", "gestion_educativa"],
    "salud publica": ["salud_publica"],
    "epidemiolog": ["epidemiologia", "salud_publica"],
    "administracion en salud": ["administracion_hospitalaria"],
    "atencion primaria": ["salud_publica", "gestion_clinica"],
    "bienestar corporativo": ["bienestar_organizacional", "recursos_humanos"],
    "hospitalidad": ["operaciones_hoteleras", "guest_experience"],
    "logistica de la cadena": ["logistica", "supply_chain"],
    "abastecimiento": ["supply_chain", "operaciones"],
    "industria 5": ["produccion", "transformacion_digital"],
    "industria quimica": ["produccion", "calidad"],
    "quimica analitica": ["calidad", "produccion"],
}


def parse_index_categories(brochures_dir: str) -> dict:
    """Mapea slug -> categoría según los headers '## ...' del INDEX.md."""
    idx = os.path.join(brochures_dir, "INDEX.md")
    cat = {}
    if not os.path.exists(idx):
        return cat
    current = "general"
    for line in open(idx, encoding="utf-8"):
        h = re.match(r"^##\s+(.+?)(?:\s*\(|\s*$)", line)
        if h and not line.startswith("###"):
            current = deaccent(h.group(1)).split("/")[0].strip().replace(" ", "_")
            continue
        m = re.search(r"\]\(\./([a-z0-9-]+)\.md\)", line)
        if m:
            cat[m.group(1)] = current
    return cat


def first(pattern, text, group=1, default=None, flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(group) if m else default


def extract(path: str, cats: dict) -> dict:
    slug = os.path.splitext(os.path.basename(path))[0]
    text = open(path, encoding="utf-8").read()
    name = (first(r"^#\s+(.+)$", text, flags=re.I | re.M) or slug).strip()
    url = first(r"\*\*Fuente oficial:\*\*\s*\[([^\]]+)\]", text) or first(r"\((https://online\.anahuac\.mx[^)]+)\)", text)
    months = first(r"(\d+)\s*meses", text)
    modules = first(r"M[oó]dulos?:\s*(\d+)", text) or first(r"(\d+)\s*m[oó]dulos", text)
    hours = first(r"(\d+)\s*horas", text) or first(r"Horas(?:\s*estimadas)?:\s*(\d+)", text)
    months = int(months) if months else None
    modules = int(modules) if modules else None
    hours = int(hours) if hours else None

    # descripción (primer párrafo bajo ## Descripción, o primeras líneas de prosa)
    desc = ""
    m = re.search(r"^##\s*Descripci[oó]n\s*\n+(.+?)(?:\n##|\n\Z)", text, re.I | re.S | re.M)
    if m:
        desc = " ".join(m.group(1).split())[:400]

    # módulos del plan de estudios (### N. Título)
    mods = re.findall(r"^###\s+\d+[\.\)]?\s+(.+)$", text, re.M)
    mods = [x.strip() for x in mods][:12]

    mod_count = modules or (len(mods) or None)
    hours_estimated = False
    if hours is None and mod_count:
        hours = mod_count * 25  # ~25 h por módulo (Anáhuac Educación Continua)
        hours_estimated = True
    weekly = round(hours / (months * WEEKS_PER_MONTH), 1) if (hours and months) else None

    # competencias (viñetas bajo ## Competencias)
    comps = []
    mc = re.search(r"^##\s*Competencias\s*\n+(.+?)(?:\n##|\n\Z)", text, re.I | re.S | re.M)
    if mc:
        comps = [re.sub(r"^[-*]\s*", "", l).strip() for l in mc.group(1).splitlines() if l.strip().startswith(("-", "*"))][:12]

    # auto-tag functional_areas: PRIMERO por título (preciso); si no hay señal, por módulos+competencias
    title_blob = deaccent(name)
    areas = []
    for kw, ars in KEYWORD_AREAS.items():
        if kw in title_blob:
            areas.extend(ars)
    if not areas:
        body_blob = deaccent(name + " " + " ".join(mods) + " " + " ".join(comps))
        for kw, ars in KEYWORD_AREAS.items():
            if kw in body_blob:
                areas.extend(ars)
    areas = sorted(set(areas))

    return {
        "id": None,  # se asigna después
        "slug": slug,
        "name": name,
        "type": "certificado" if slug.startswith("certificado") else "diplomado",
        "category": cats.get(slug, "general"),
        "url": url or "",
        "modality": "100% en línea",
        "duration_months": months,
        "modules_count": mod_count,
        "total_hours": hours,
        "hours_estimated": hours_estimated,
        "weekly_hours_estimate": weekly,
        "summary": desc,
        "modules": mods,
        "skills_outputs": comps,
        "functional_areas_covered": areas,
        "professional_relevance": "alta" if areas else "interes_personal",
    }


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--brochures", default=os.path.join(here, "..", "..", "diplomados", "archivos-diplomados"))
    ap.add_argument("--taxonomy", default=os.path.join(here, "..", "assets", "taxonomy.json"))
    ap.add_argument("--out", default=os.path.join(here, "..", "assets", "diplomados.json"))
    a = ap.parse_args()

    cats = parse_index_categories(a.brochures)
    files = sorted(glob.glob(os.path.join(a.brochures, "diplomado-*.md"))
                   + glob.glob(os.path.join(a.brochures, "certificado-*.md")))
    valid_areas = set(json.load(open(a.taxonomy, encoding="utf-8"))["functional_areas"].keys())

    items = []
    bad_areas = set()
    for i, f in enumerate(files, 1):
        d = extract(f, cats)
        d["id"] = f"DIP-{i:03d}"
        for ar in d["functional_areas_covered"]:
            if ar not in valid_areas:
                bad_areas.add(ar)
        items.append(d)

    out = {
        "schema_version": "1.0.0",
        "type": "diplomados",
        "generated_from": "diplomados/archivos-diplomados/*.md (Anáhuac Educación Continua)",
        "count": len(items),
        "diplomados": items,
    }
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    tagged = sum(1 for d in items if d["functional_areas_covered"])
    with_hours = sum(1 for d in items if d["weekly_hours_estimate"])
    print(f"Diplomados: {len(items)}  |  con área profesional: {tagged}  |  interés personal: {len(items)-tagged}")
    print(f"Con horas/semana estimadas: {with_hours}")
    if bad_areas:
        print("⚠️  áreas fuera del taxonomy:", sorted(bad_areas))
    else:
        print("Todas las functional_areas usadas existen en taxonomy ✓")
    # muestra
    print("\nMuestra (5):")
    for d in items[:5]:
        print(f"  {d['id']} {d['name'][:48]:<48} {str(d['duration_months'])+'m':>4} "
              f"{str(d['weekly_hours_estimate'] or '?')+'h/sem':>8}  {d['functional_areas_covered'][:3]}")
    print(f"\nEscrito: {a.out}")


if __name__ == "__main__":
    main()
