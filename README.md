# AnáhuacAdvisor — Consejero vocacional DNC

Wizard interactivo de **10 preguntas** que orienta a profesionales aspirantes a una maestría en línea de **Universidad Anáhuac** (Anáhuac Online). Aplica metodología **Detección de Necesidades de Capacitación (DNC)** sobre un catálogo de 24 maestrías y entrega un diagnóstico con hasta 3 recomendaciones ordenadas por match score.

## Demo en vivo

Servido en paralelo desde dos hosts (el mismo `main` branch alimenta ambos; cualquier `git push` redespliega los dos en paralelo):

- ➡️ **[anahuac-advisor.onrender.com](https://anahuac-advisor.onrender.com)** — Render Static Site (CDN Cloudflare)
- ➡️ **[robertohernandez-aplm.github.io/anahuac-advisor](https://robertohernandez-aplm.github.io/anahuac-advisor/)** — GitHub Pages (CDN Fastly)

## Qué es

Un single-page HTML autocontenido (~148 KB) **sin backend ni dependencias externas en runtime** (0 llamadas a CDNs, fuentes ni APIs durante la sesión del usuario). Toda la lógica de matching, los datos del catálogo y la tipografía viajan embebidos o nativos del sistema.

- **10 preguntas** estructuradas en 3 planos DNC (profesional, organizacional, trayectoria) + restricciones.
- **Algoritmo determinístico de matching** con 6 componentes ponderados (áreas funcionales 25%, gap coverage 25%, career outcome 20%, industry/seniority/constraints 10% c/u).
- **Diagnóstico narrativo** con 5 secciones: resumen ejecutivo, cómo se usaron tus respuestas, top matches con racional, comparación head-to-head, preguntas para tu decisión.
- **Umbral mínimo de recomendación**: 50/100. Máximo 3 recomendaciones.

## Survey calibrado con conversaciones reales

Las opciones del survey se enriquecieron a partir del análisis de speech logs de asesores educativos (`speech-hallazgos.docx`), que detectó perfiles arquetípicos no capturados en la taxonomía original:

**5 industrias nuevas** detectadas como segmentos visibles en operación comercial:

- Despachos jurídicos / Legal corporativo
- Laboratorios clínicos / Diagnóstico
- Salud ocupacional / Bienestar corporativo
- Plantas productivas / Industria pesada
- Postventa / Distribución comercial

**2 motivadores nuevos** que dominaron las conversaciones reales:

- **`technical_to_management`** — el profesional técnico (ingeniería, sistemas, clínico) que quiere saltar a liderazgo o gestión.
- **`career_acceleration`** — egresado reciente o trayectoria corta que busca diferenciación curricular y ruta de crecimiento.

El catálogo `programs.json` también se enriqueció: **10 programas** ahora declaran explícitamente cuáles de las 5 industrias nuevas son su mejor encaje (ej. MAE-DE-001 y MAE-DE-002 → despachos jurídicos; MAE-IN-001 → plantas productivas; etc.). Esto eleva el `industry_fit` de 80 (transversal) a 100 (match específico) cuando aplica.

## Tecnología

- **HTML + CSS + JavaScript vanilla.** Sin framework, sin bundler, sin npm.
- **Tipografía Helvetica family** (`'Helvetica Neue', Helvetica, Arial, sans-serif`) — nativa de macOS/iOS, con Arial como fallback bit-perfect en Windows/Android. 0 llamadas a Google Fonts u otros CDNs de fuentes.
- Catálogo (`programs.json`), taxonomy (`taxonomy.json`) y reglas (`matching_rules.json`) embebidos como constantes JS al cargar.
- Puerto JavaScript del algoritmo `compute_match.py` del skill original `anahuac-advisor` (Claude Code).

## Despliegue

Este repo es un **Static Site** puro — sin build, sin servidor. Cualquier host estático funciona; los dos activos actualmente:

### Render Static Site

1. Conecta el repo en [render.com](https://render.com) → New → Static Site.
2. **Build command**: deja vacío.
3. **Publish directory**: `.` (la raíz).
4. Render servirá `index.html` automáticamente.

### GitHub Pages

Habilitado en `Settings → Pages → Source: Deploy from a branch → main / (root)`. La URL es `https://<user>.github.io/anahuac-advisor/`. Cada push a `main` dispara un build (~45s).

## Contacto

Para preguntas sobre admisión, becas, fechas, o detalles de algún programa específico:

- 📧 **ilce.gutierrez@aplatam.com**
- 📞 **55 3210 8483** (mismo número para llamada y WhatsApp)

## Limitaciones conocidas

- De las 24 maestrías del catálogo, **solo 2 están verificadas oficialmente** con plan de estudios textual del sitio Anáhuac (Capital Humano y Analítica de Negocios). Las otras 22 están **modeladas** a partir de fuentes públicas y deben validarse con admisiones antes de tomar la decisión final.
- **No reemplaza** la asesoría oficial de admisiones — es un primer mapeo, no una decisión.
- **No inventa** precios, fechas ni docentes; esos datos siempre los confirma admisiones.
- **No psicoanaliza** al usuario ni hace juicios sobre sus elecciones personales.

## Documentación adicional

Ver [`PROJECT-BRIEF.md`](./PROJECT-BRIEF.md) para el brief completo del proyecto: metodología DNC en profundidad, flujo conversacional original del skill, algoritmo de matching detallado, taxonomía completa y casos especiales del consejero.

---

Construido sobre el skill [`anahuac-advisor`](https://github.com/anthropics/claude-code) para Claude Code · Apply Digital × Universidad Anáhuac Online.
