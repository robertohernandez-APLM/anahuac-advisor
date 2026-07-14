#!/usr/bin/env python3
"""save_brochure.py — recibe (name, url, texto crudo) y produce un .md estructurado."""
import argparse, re, sys, unicodedata
from pathlib import Path
from datetime import datetime

def slugify(name):
    """Convierte nombre a filename slug ASCII seguro."""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    s = re.sub(r"[-\s]+", "-", s)
    return s[:100]

def build_md(name, url, raw_text):
    """Estructura mínima: header con metadata + texto crudo limpio."""
    # Limpieza básica: normalizar saltos, eliminar líneas duplicadas contiguas
    lines = [ln.rstrip() for ln in raw_text.split("\n")]
    cleaned = []
    prev = None
    for ln in lines:
        if ln == prev:
            continue
        cleaned.append(ln)
        prev = ln
    body = "\n".join(cleaned).strip()

    header = f"""# {name}

**Fuente oficial:** [{url}]({url})
**Extraído:** {datetime.now().strftime('%Y-%m-%d')}
**Programa:** Anáhuac Online — Educación Continua

---

"""
    return header + body + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--text-file", required=True, help="ruta al archivo con el texto crudo")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    text = Path(args.text_file).read_text(encoding="utf-8")
    md = build_md(args.name, args.url, text)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(args.name)
    out_path = out_dir / f"{slug}.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"OK  {out_path}")

if __name__ == "__main__":
    main()
