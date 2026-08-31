> ⚠️ **REPORTE DE MUESTRA / DEMO.** "Grupo Industrial del Bajío" es una empresa ficticia y los 6 perfiles de aspirantes son construidos (no hay conversaciones reales). Lo **real** es el motor y el catálogo: los nombres de programa, el ruteo diplomado/maestría, los match scores y el vínculo brecha→programa (`gaps_addressed`) los calculó `compute_match.py` contra `programs.json`/`diplomados.json`/`taxonomy.json` reales. Con aspirantes reales el reporte es idéntico, con 100% de datos reales. Generado con `scripts/gap_program_value_report.py`.

# Reporte de brechas y valor formativo
### Grupo Industrial del Bajío  ·  del dato del aspirante al valor de negocio

**Aspirantes analizados**: 6  ·  **Brechas distintas**: 11  ·  **Generado**: 2026-08-06 14:09
**Ruta formativa derivada**: diplomado 4, ambos 1, maestria 1
**Fuente**: diagnósticos TalentAdvisor (agregado y anónimo · sin datos individuales)

Este reporte conecta, en una sola vista, **la brecha detectada → el programa (diplomado o maestría) que la cierra → el valor para el aspirante (competencia que desarrolla) y para la empresa (pilar de negocio)**.

---

## 1. Puente: Brecha → Programa → Valor dual

> Ordenado por **prioridad** (severidad × nº de aspirantes). El **valor para el aspirante** es desarrollar la competencia de la brecha; el **valor para la empresa** es el pilar de negocio que mejora al cerrarla.

| Brecha (competencia) | Aspirantes | Prioridad | Programa que la cierra | Valor para el ASPIRANTE | Valor para la EMPRESA (pilar) |
|---|--:|--:|---|---|---|
| **analitica_de_datos** (skill) | 2 | 5 | Diplomado en Big Data para la toma de Decisiones (diplomado) | Desarrolla la habilidad de analitica_de_datos | Mejora del rendimiento, Optimización de recursos |
| **gestion_del_cambio** (attitude) | 1 | 4 | Maestría en Dirección de Empresas (maestria) | Fortalece mindset/actitud en gestion_del_cambio | Adaptación al cambio |
| **liderazgo** (leadership) | 1 | 4 | Maestría en Dirección de Empresas (maestria) | Desarrolla competencia directiva en liderazgo | Adaptación al cambio |
| **mejora_continua** (skill) | 1 | 3 | Maestría en Ingeniería en Gestión de Operaciones (maestria) | Desarrolla la habilidad de mejora_continua | Mejora del rendimiento, Reducción de errores y costos |
| **finanzas_corporativas** (knowledge) | 1 | 3 | Diplomado en Costos y Presupuestos (diplomado) | Adquiere conocimiento en finanzas_corporativas | Reducción de errores y costos, Optimización de recursos |
| **gestion_talento** (skill) | 1 | 3 | Diplomado en Desarrollo del Capital Humano (diplomado) | Desarrolla la habilidad de gestion_talento | Mejora del rendimiento, Adaptación al cambio |
| **marketing_digital** (skill) | 1 | 3 | Diplomado en Marketing Digital (diplomado) | Desarrolla la habilidad de marketing_digital | Mejora del rendimiento |
| **estrategia_corporativa** (strategic) | 1 | 3 | Maestría en Dirección de Empresas (maestria) | Gana visión estratégica en estrategia_corporativa | Mejora del rendimiento, Adaptación al cambio |
| **business_intelligence** (knowledge) | 1 | 2 | Diplomado en Big Data para la toma de Decisiones (diplomado) | Adquiere conocimiento en business_intelligence | Mejora del rendimiento |
| **contabilidad** (skill) | 1 | 2 | Diplomado en Costos y Presupuestos (diplomado) | Desarrolla la habilidad de contabilidad | Reducción de errores y costos |
| **recursos_humanos** (knowledge) | 1 | 2 | Diplomado en Desarrollo del Capital Humano (diplomado) | Adquiere conocimiento en recursos_humanos | Optimización de recursos |

---

## 2. Programas y cuántas brechas cierra cada uno

Concentra la inversión de formación en los programas de mayor cobertura:

| Programa | Tipo | Brechas que cierra |
|---|---|--:|
| Maestría en Analítica de Negocios | maestria | 4 |
| Maestría en Dirección de Empresas | maestria | 3 |
| Maestría en Ingeniería en Gestión de Operaciones | maestria | 2 |
| Maestría en Dirección de Centros Educativos | maestria | 2 |
| Diplomado en Big Data para la toma de Decisiones | diplomado | 2 |
| Diplomado en Business Analytics | diplomado | 2 |
| Diplomado en Excel para la toma de decisiones | diplomado | 2 |
| Diplomado en Costos y Presupuestos | diplomado | 2 |
| Maestría en Contabilidad Internacional | maestria | 2 |
| Diplomado en Desarrollo del Capital Humano | diplomado | 2 |

---

## 3. Impacto de negocio agregado (4 pilares)

Al cerrar estas brechas con formación, así se distribuye el impacto en el negocio:

| Pilar de negocio | Brechas que lo impactan |
|---|--:|
| **Mejora del rendimiento** | 7 |
| **Optimización de recursos** | 4 |
| **Adaptación al cambio** | 4 |
| **Reducción de errores y costos** | 3 |

---

## 4. Notas

- **Anónimo y agregado**: sin datos individuales; no se reportan grupos con < 5 aspirantes.
- **Brecha → programa**: se toma de `gaps_addressed` de cada recomendación del diagnóstico; una brecha sin programa vinculado aparece marcada.
- **Valor empresa**: los 4 pilares provienen del `business_impact_mapping` del diagnóstico (metodología de diagnóstico de necesidades de formación).
- Para 22 de 24 maestrías el plan de estudios es modelado — validar con brochure oficial antes de decidir la inversión.

*Reporte generado por TalentAdvisor · gap_program_value_report.py*
