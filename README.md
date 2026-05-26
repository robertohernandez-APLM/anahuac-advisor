# AnáhuacAdvisor — Consejero vocacional DNC

Wizard interactivo de **10 preguntas** que orienta a profesionales aspirantes a una maestría en línea de **Universidad Anáhuac** (Anáhuac Online). Aplica metodología **Detección de Necesidades de Capacitación (DNC)** sobre un catálogo de 24 maestrías y entrega un diagnóstico con hasta 3 recomendaciones ordenadas por match score.

## Demo en vivo

➡️ **[Abrir el demo en Render]()** _(URL pendiente de despliegue)_

## Qué es

Un single-page HTML autocontenido (~145 KB) sin backend ni dependencias externas en runtime. Toda la lógica de matching y los datos del catálogo viajan embebidos.

- **10 preguntas** estructuradas en 3 planos DNC (profesional, organizacional, trayectoria) + restricciones.
- **Algoritmo determinístico de matching** con 6 componentes ponderados (areas funcionales 25%, gap coverage 25%, career outcome 20%, industry/seniority/constraints 10% c/u).
- **Diagnóstico narrativo** con 5 secciones: resumen ejecutivo, cómo se usaron tus respuestas, top matches con racional, comparación head-to-head, preguntas para tu decisión.
- **Umbral mínimo de recomendación**: 50/100. Máximo 3 recomendaciones.

## Tecnología

- HTML + CSS + JavaScript vanilla.
- Catálogo (`programs.json`), taxonomy (`taxonomy.json`) y reglas (`matching_rules.json`) embebidos como constantes JS.
- Puerto JavaScript del algoritmo `compute_match.py` del skill `anahuac-advisor`.

## Despliegue en Render

Este repo es un **Static Site** — sin build, sin servidor.

1. Conecta este repo en [render.com](https://render.com) → New → Static Site.
2. **Build command**: deja vacío.
3. **Publish directory**: `.` (la raíz).
4. Render servirá `index.html` automáticamente.

## Limitaciones conocidas

- De las 24 maestrías del catálogo, **solo 2 están verificadas** oficialmente con plan de estudios textual (Capital Humano y Analítica de Negocios). Las otras 22 están **modeladas** a partir de fuentes públicas y deben validarse con admisiones antes de tomar la decisión final.
- **No reemplaza** la asesoría oficial de admisiones. Datos de contacto: info@onlineanahuac.mx · (55) 5062-3403 · WhatsApp 55 9414-7545.
- **No inventa** precios, fechas ni docentes — esos datos los confirma admisiones.

## Documentación adicional

Ver [`PROJECT-BRIEF.md`](./PROJECT-BRIEF.md) para el brief completo del proyecto: metodología DNC, flujo conversacional original (skill de Claude Code), algoritmo de matching detallado, taxonomía y casos especiales.

---

Construido sobre el skill [`anahuac-advisor`](https://github.com/anthropics/claude-code) para Claude Code · Apply Digital × Universidad Anáhuac Online.
