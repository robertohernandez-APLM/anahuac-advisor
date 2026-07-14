# Algoritmo de matching — cómo se calcula match_score

Este documento desglosa el algoritmo determinístico definido en `assets/matching_rules.json`. El objetivo es que el score sea **reproducible, explicable y auditable**.

## Fórmula general

```
match_score = (
  0.25 * functional_areas_match +
  0.25 * gap_coverage +
  0.20 * career_outcome_match +
  0.10 * industry_fit +
  0.10 * seniority_fit +
  0.10 * constraints_fit
)
```

Cada componente devuelve un valor de **0 a 100**. El resultado final también está en 0-100.

**Umbral mínimo**: 50. Programas con score < 50 no se recomiendan.

**Máximo de recomendaciones**: 3.

## Componente 1 — functional_areas_match (peso 25%)

Mide qué tanto de las áreas funcionales del rol actual o deseado del usuario están cubiertas por el programa.

```
functional_areas_match = (áreas del usuario cubiertas por el programa / total áreas del usuario) * 100
```

Si el usuario tiene 4 áreas funcionales asociadas a su rol+objetivo (ej. `analitica_de_datos`, `gestion_de_proyectos`, `liderazgo_de_equipos`, `presupuestos`) y el programa `MAE-NG-002` (Analítica de Negocios) cubre 2 de esas (`analitica_de_datos`, `gestion_de_proyectos`), entonces:

```
functional_areas_match = (2 / 4) * 100 = 50
```

**Resolución de sinónimos**: aplica el `synonym_dictionary` de `matching_rules.json` antes de comparar. Ejemplos: "rh"→"recursos_humanos", "datos"→"analitica_de_datos", "ceo"→"direccion_general".

## Componente 2 — gap_coverage (peso 25%)

Mide qué tanto de las brechas detectadas (ponderadas por severidad) cierra el programa.

**Pesos por severidad** (de `matching_rules.json`):

| Severidad | Peso |
|---|---|
| `bloqueante` | 4 |
| `alta` | 3 |
| `media` | 2 |
| `baja` | 1 |

```
gap_coverage = (Σ pesos de brechas cerradas por el programa / Σ pesos de todas las brechas) * 100
```

**Una brecha se considera "cerrada" por un programa si**:

- El programa cubre el área funcional asociada a la brecha, **o**
- El programa lista la hard_skill o soft_skill correspondiente como output.

Ejemplo: el usuario tiene tres brechas — analítica predictiva (bloqueante, peso 4), liderazgo de equipos (alta, peso 3), inglés ejecutivo (baja, peso 1). Total = 8.

El programa cierra las dos primeras: cobertura = (4 + 3) / 8 = 0.875.

```
gap_coverage = 0.875 * 100 = 87.5
```

## Componente 3 — career_outcome_match (peso 20%)

Mide qué tanto los `career_outcomes` del programa están alineados con el objetivo de carrera del usuario.

Lógica:

1. Toma el `primary_objective` del usuario (uno de los 9 definidos en `taxonomy.json`: `promotion_vertical`, `lateral_move`, `industry_switch`, `specialization`, `broadening`, `entrepreneurship`, `international_career`, `consulting`, `academia`).

2. Toma los `career_outcomes` del programa.

3. Aplica matrices de afinidad:
   - Si al menos un `career_outcome` del programa coincide directamente con el objetivo o con un rol asociado a ese objetivo: **100**.
   - Si hay coincidencia parcial (mismo ámbito, distinto rol específico): **60**.
   - Sin coincidencia: **20** (no es 0 porque cualquier maestría aporta algo).

Ejemplo: usuario con `primary_objective = promotion_vertical` hacia "dirección de capital humano". Programa MAE-CH-001 (Dirección del Capital Humano) lista entre sus career_outcomes "Director(a) de Capital Humano" → **100**.

## Componente 4 — industry_fit (peso 10%)

```
industry_fit = (industrias del usuario cubiertas / industrias del usuario) * 100
```

Si el programa lista la industria del usuario en su `industries_fit` (o si su `industries_fit` es "transversal"): **100**. Si no aparece pero hay industria adyacente: **50**. Si no hay ninguna afinidad: **20**.

## Componente 5 — seniority_fit (peso 10%)

Compara la `seniority_target` del programa con la seniority actual + objetivo del usuario.

| Comparación | Score |
|---|---|
| Programa apunta al nivel objetivo del usuario | 100 |
| Programa apunta al nivel actual del usuario (no avanza) | 50 |
| Programa apunta por encima del objetivo (overshooting) | 70 |
| Programa apunta por debajo del nivel actual | 20 |

Niveles: `junior` (0-2 años), `analista` (2-4), `lider_o_coordinacion` (4-7), `gerencia` (7-12), `direccion` (12+).

## Componente 6 — constraints_fit (peso 10%)

Verifica que el programa respeta las restricciones del usuario:

- **Tiempo semanal disponible**: si el usuario reporta <6 hrs/semana, todos los programas Anáhuac Online demandan 6-10 → score 60 (señalar el riesgo en el reporte). Si 6-10 hrs: 100. Si >10 hrs: 100.
- **Modalidad**: todas son 100% online → si el usuario quiere online, 100; si pide presencial, 0 y el programa se descarta.
- **Idioma**: si el usuario solo habla español y el programa lo es: 100.

Promedio simple de los tres.

## Tie-breakers

Si dos programas empatan en match_score:

1. Gana el que cierra más brechas **bloqueantes**.
2. Si sigue empate, el que tenga mayor `gap_coverage`.
3. Si sigue, el que tenga mayor `career_outcome_match`.
4. Si sigue, orden alfabético por `name` (estable y reproducible).

## Ejemplo completo

**Usuario**: gerente de operaciones, 8 años de experiencia, industria retail, quiere ascender a dirección de logística, brechas detectadas:

- Analítica de cadena de suministro (bloqueante, peso 4)
- Liderazgo de equipos cross-funcionales (alta, peso 3)
- Presupuestación estratégica (media, peso 2)

Total pesos de brechas = 9. Áreas funcionales del usuario = `cadena_de_suministro`, `operaciones`, `analitica_de_datos`, `liderazgo_de_equipos`. Industria = `retail`. Seniority target = `direccion`.

**Evaluamos MAE-IN-001 (hipotético: Dirección de Operaciones y Logística)**:

| Componente | Cálculo | Valor |
|---|---|---|
| functional_areas_match | 4/4 cubiertas | 100 |
| gap_coverage | cierra brechas 1 y 2 (4+3=7 de 9) | 77.8 |
| career_outcome_match | "Director(a) de Operaciones" listado | 100 |
| industry_fit | retail listado en industries_fit | 100 |
| seniority_fit | programa apunta a dirección | 100 |
| constraints_fit | usuario tiene 8 hrs/sem, online ok, español ok | 100 |

```
match_score = 0.25*100 + 0.25*77.8 + 0.20*100 + 0.10*100 + 0.10*100 + 0.10*100
           = 25 + 19.45 + 20 + 10 + 10 + 10
           = 94.45
```

Score: **94**. Recomendación fuerte.

## Cómo presentar el score al usuario

En el reporte, muestra el score global y el breakdown por componente. Acompáñalo de **una racional verbal** que explique qué hace el programa por el usuario en términos de las brechas concretas — no en abstracto.

Ejemplo de racional verbal: *"Este programa cierra dos de tus tres brechas críticas (analítica de cadena y liderazgo cross-funcional), apunta al nivel directivo que buscas, está alineado con tu industria y respeta tu disponibilidad. La brecha de presupuestación estratégica se aborda parcialmente en la asignatura de gestión financiera de operaciones."*

## Cuándo no recomendar

- Ningún programa supera 50.
- El mejor programa supera 50 pero **no cierra ninguna brecha bloqueante**. En este caso, lo dices explícitamente: "El programa con mejor score técnico es X, pero no cierra ninguna de las brechas críticas. Sugiero re-evaluar el plan o considerar formación complementaria fuera de este catálogo."
- Las restricciones (tiempo, idioma, modalidad) son incompatibles con cualquier programa del catálogo.

En esos casos, el reporte se entrega igual, pero con la sección de recomendaciones diciendo claramente "no procede recomendación", y con sugerencias alternativas (otras modalidades, complementar con cursos cortos, considerar otra institución).
