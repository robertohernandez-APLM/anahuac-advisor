# TalentAdvisor — Skill de Claude Code

Consejero vocacional para maestrías en línea de Universidad Anáhuac, basado en la metodología **diagnóstico de necesidades de formación**.

## Qué hace

Convierte a Claude en un agente conversacional que:

1. Recolecta el perfil del profesional siguiendo un flujo estructurado de 6 fases.
2. Construye un diagnóstico de necesidades de formación con brechas tipificadas por severidad.
3. Aplica un algoritmo determinístico para encontrar los programas del catálogo que mejor calzan.
4. Entrega un reporte markdown con recomendaciones explicables.

## Instalación

### Opción 1: skill global

Copia la carpeta `anahuac-advisor/` a `~/.claude/skills/`:

```bash
cp -r anahuac-advisor ~/.claude/skills/
```

Luego en cualquier sesión de Claude Code, el skill se activa automáticamente cuando el usuario pide ayuda con selección de posgrado.

### Opción 2: skill del proyecto

Copia la carpeta a `.claude/skills/` dentro del directorio del proyecto:

```bash
mkdir -p .claude/skills
cp -r anahuac-advisor .claude/skills/
```

## Uso

Una vez instalado, abre Claude Code y escribe algo como:

```
Quiero que me ayudes a decidir si una maestría de Anáhuac Online me conviene.
Soy gerente de operaciones en retail y quiero ascender a dirección de logística.
```

Claude debería:

1. Detectar el contexto y leer `SKILL.md`.
2. Comenzar la conversación con la apertura de la fase 1.
3. Llevarte por las 6 fases.
4. Generar el reporte al final.

Si no se activa solo, fuerza el contexto:

```
Lee el skill `anahuac-advisor` y empieza el flujo conversacional como TalentAdvisor.
```

## Estructura del skill

```
anahuac-advisor/
├── SKILL.md                          # Punto de entrada (instrucciones)
├── README.md                         # Este archivo
├── references/
│   ├── methodology-dnc.md            # Los 3 planos, 4 pilares, base conceptual
│   ├── conversation-flow.md          # Las 6 fases con guiones y preguntas
│   ├── matching-algorithm.md         # Algoritmo de scoring paso a paso
│   └── special-cases.md              # Manejo de escenarios complicados
├── assets/
│   ├── programs.json                 # Catálogo de 24 maestrías
│   ├── taxonomy.json                 # Vocabulario controlado
│   ├── dnc_schema.json               # JSON Schema input/output de diagnóstico
│   ├── matching_rules.json           # Pesos y reglas de scoring
│   ├── session_template.json         # Plantilla del estado en memoria
│   └── report_template.md            # Plantilla del reporte final
└── scripts/
    ├── validate_dnc.py               # Valida completitud de sesión
    ├── compute_match.py              # Motor de matching determinístico
    └── render_report.py              # Genera reporte markdown
```

## Pruebas rápidas

### Validar una sesión

```bash
python scripts/validate_dnc.py --session ruta/a/session.json
```

Exit code 0 = lista para diagnóstico, 1 = faltan datos.

### Calcular matches

```bash
python scripts/compute_match.py \
    --session ruta/a/session.json \
    --programs assets/programs.json \
    --taxonomy assets/taxonomy.json \
    --rules assets/matching_rules.json
```

Devuelve top 3 con score ≥ 50 (configurable con `--min-score`).

### Generar reporte

```bash
python scripts/render_report.py \
    --session ruta/a/session.json \
    --template assets/report_template.md \
    --out reporte.md
```

## Limitaciones conocidas

- **Plan de estudios modelado para 22 maestrías**: solo *Dirección del Capital Humano* y *Analítica de Negocios* tienen plan de estudios confirmado del sitio oficial. Las otras 22 están modeladas a partir de fuentes públicas y deben validarse con brochures oficiales de admisiones antes de uso en producción.
- **Sin persistencia**: el estado vive en la memoria de la conversación. Si la sesión se interrumpe, hay que reiniciar.
- **Solo español**: todos los assets están en español. Adaptación a otros idiomas requeriría traducción de `taxonomy.json`, `matching_rules.json` (synonym_dictionary), y todos los `.md`.

## Contacto institucional

Para preguntas operativas sobre las maestrías (costos, becas, fechas):

- Email: info@onlineanahuac.mx
- Teléfono: (55) 5062-3403
- WhatsApp: 55 9414-7545
- Sitio: https://online.anahuac.mx/maestrias-en-linea/
