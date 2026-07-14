"""Descarga las brochures de diplomados faltantes (build/mantenimiento, NO runtime).

Lee AOL_Diplomados_Links.pdf (raíz del proyecto), parsea (nombre, URL), y para cada
diplomado que no exista ya en diplomados/archivos-diplomados/ descarga el PDF oficial,
extrae el texto y guarda un .md con el formato de brochure. Luego corre build_diplomados.py.

Requiere `pypdf` (solo para este paso de build):  python3 -m pip install --user pypdf
Uso:  python3 scripts/fetch_brochures.py
"""
import re, os, io, socket, unicodedata
from urllib.parse import urlsplit, urlunsplit, quote
import urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))          # raíz del proyecto
PDF = os.path.join(ROOT, "AOL_Diplomados_Links.pdf")
BRO = os.path.join(ROOT, "diplomados", "archivos-diplomados")
socket.setdefaulttimeout(25)


def slugify(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    return re.sub(r"[-\s]+", "-", s)[:100]


def enc(u):
    p = urlsplit(u.strip())
    # safe="/%" preserva '%' para no doble-codificar URLs ya percent-encoded, y codifica espacios/acentos
    return urlunsplit((p.scheme, p.netloc, quote(p.path, safe="/%"), quote(p.query, safe="=&%"), p.fragment))


def build_md(name, url, raw):
    out, prev = [], None
    for ln in (l.rstrip() for l in raw.split("\n")):
        if ln != prev:
            out.append(ln); prev = ln
    header = (f"# {name}\n\n**Fuente oficial:** [{url}]({url})\n"
              f"**Extraído:** {datetime.now().strftime('%Y-%m-%d')}\n"
              f"**Programa:** Anáhuac Online — Educación Continua\n\n---\n\n")
    return header + "\n".join(out).strip() + "\n"


def parse_pairs():
    import pypdf
    r = pypdf.PdfReader(PDF)
    text = "\n".join((p.extract_text() or "") for p in r.pages)
    seen, pairs = set(), []
    for chunk in re.split(r"(?=Diplomado en |Certificado )", text):
        m = re.search(r"https://.+?\.pdf", chunk)
        if not m:
            continue
        name = chunk[:m.start()].strip()
        if not name.lower().startswith(("diplomado", "certificado")) or len(name) < 9:
            continue
        s = slugify(name)
        if s and s not in seen:
            seen.add(s); pairs.append((name, m.group(0).strip(), s))
    return pairs


def main():
    pairs = parse_pairs()
    existing = {os.path.splitext(f)[0] for f in os.listdir(BRO) if f.endswith(".md")}
    missing = [p for p in pairs if p[2] not in existing]
    print(f"En el PDF: {len(pairs)} únicos | presentes: {len(existing)} | faltantes: {len(missing)}")
    ok = fail = 0
    for i, (name, url, slug) in enumerate(missing, 1):
        try:
            data = urllib.request.urlopen(urllib.request.Request(enc(url), headers={"User-Agent": "Mozilla/5.0"})).read()
            import pypdf
            raw = "\n".join((p.extract_text() or "") for p in pypdf.PdfReader(io.BytesIO(data)).pages)
            if len(raw) < 150:
                fail += 1; continue
            open(os.path.join(BRO, slug + ".md"), "w", encoding="utf-8").write(build_md(name, url, raw))
            ok += 1
        except Exception as e:
            fail += 1; print(f"  FAIL {name[:44]} -> {type(e).__name__}")
    print(f"Descargados: {ok} | fallidos: {fail}")
    print("Ahora corre:  python3 scripts/build_diplomados.py")


if __name__ == "__main__":
    main()
