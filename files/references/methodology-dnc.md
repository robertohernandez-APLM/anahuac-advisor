# Metodología diagnóstico de necesidades de formación — base conceptual

La **diagnóstico de necesidades de formación** es un método estructurado para identificar qué brechas de conocimiento, habilidad o actitud existen entre el estado actual de un profesional (o un equipo) y el estado requerido para alcanzar un objetivo definido.

Aplicada a la selección de posgrado, la diagnóstico de necesidades de formación desplaza la conversación desde "qué maestría te gusta más" hacia "qué brechas tienes que cerrar, y cuál es el camino formativo más eficiente para cerrarlas". Es un cambio de marco: del consumo educativo al diagnóstico estratégico.

## Los 3 planos de la diagnóstico de necesidades de formación

La recomendación robusta nace de la intersección de tres planos. Si solo trabajas uno, la recomendación es frágil.

### Plano 1 — Profesional (individual)

Qué sabe, qué hace bien, qué le cuesta. Incluye:

- Formación previa (licenciatura, posgrados, certificaciones).
- Trayectoria: años de experiencia, sectores, tipos de organización.
- Rol actual: posición, responsabilidades, KPIs.
- Fortalezas autopercibidas y retroalimentación recibida.
- Hard skills y soft skills ya desarrolladas.

### Plano 2 — Organizacional (empresarial)

En qué realidad opera y qué demanda esa realidad. Incluye:

- Industria, tamaño, geografía, modelo de negocio.
- Cambios actuales en la empresa o en el sector (transformación digital, expansión, regulación, M&A).
- Necesidades estratégicas del área del profesional.
- Plan de sucesión, plan de carrera interno (si existe).
- Posibilidad de patrocinio o apoyo de la empresa para estudiar.

### Plano 3 — Trayectoria deseada (carrera)

A dónde quiere llegar. Incluye:

- Horizonte temporal (¿dónde quiere estar en 3 años? ¿en 7?).
- Naturaleza del movimiento: vertical (ascender), lateral (cambiar de área), de industria, especialización, expansión, emprendimiento, internacional, consultoría, academia.
- Criterios personales: balance vida-trabajo, ubicación, ingresos, propósito.
- Restricciones reales: tiempo disponible, presupuesto, situación familiar.

**La intersección de los tres planos define la brecha que la maestría debe cerrar.** Una maestría puede ser excelente para el plano 1 (cubre lo que le falta saber), inútil para el plano 2 (la empresa no necesita esa capacidad) e incongruente con el plano 3 (le aleja de a dónde quiere ir). El consejo solo es bueno si los tres planos están alineados.

## Los 4 pilares de valor del diagnóstico de necesidades de formación

Una vez identificadas las brechas, se evalúan por su impacto en cuatro dimensiones. Esto es lo que conecta la formación con el negocio.

### Pilar 1 — Mejora del rendimiento

¿Cómo aumentaría la productividad, calidad o efectividad del profesional al cerrar esta brecha? ¿En qué KPI específico se vería?

Ejemplos: un director comercial que aprende analítica de negocios mejora la asignación de cuotas y reduce el churn; un gerente de RH que se especializa en compensaciones diseña esquemas que retienen talento clave.

### Pilar 2 — Optimización de recursos

¿Cómo permite hacer más con lo mismo o lo mismo con menos? Tiempo, dinero, personas, energía.

Ejemplos: una directora de operaciones que estudia logística rediseña la red de distribución y baja el costo unitario; un líder de TI que aprende arquitectura cloud reduce gasto en infraestructura subutilizada.

### Pilar 3 — Adaptación al cambio

¿Qué cambio externo o interno está empujando la necesidad? Sin un cambio que justifique la inversión, la formación se vuelve un lujo.

Ejemplos: nueva regulación (NOM, ESG, protección de datos); transformación digital; cambio de modelo de negocio; expansión geográfica; relevo generacional.

### Pilar 4 — Reducción de errores y costos

¿Qué errores actuales tienen costo medible? ¿Qué riesgos no gestionados podrían materializarse?

Ejemplos: contratos mal redactados que cuestan litigios; decisiones de inversión sin análisis de riesgo; campañas de marketing sin medición; rotación elevada por mala gestión.

## Tipos de brechas

La taxonomía operativa (definida en `assets/taxonomy.json` como `knowledge_gap_types`):

| Tipo | Qué es | Cómo se manifiesta |
|---|---|---|
| `knowledge` | Le falta saber algo (marcos, conceptos, datos). | "No domino IFRS / no entiendo el modelo OKR / no conozco la regulación X". |
| `skill` | Le falta saber **hacer** algo, aunque sepa el concepto. | Sabe qué es un dashboard pero no construye uno; sabe qué es negociar pero no lo hace bien. |
| `attitude` | El bloqueo no es de saber ni hacer, sino de disposición o mentalidad. | Resistencia a delegar, aversión al conflicto, miedo a hablar en público. |
| `certification` | La competencia existe pero falta la acreditación formal. | Liderazgo demostrado sin título de maestría que lo "respalde" para subir. |
| `leadership` | Subconjunto de skills/attitudes específicas de conducir personas/áreas. | Buen ejecutor individual al que le cuesta dirigir un equipo. |
| `strategic` | Capacidad para pensar y decidir a nivel sistémico/largo plazo. | Excelente operador táctico que no logra elevar la mirada. |

## Severidades

| Severidad | Significado | Implicación |
|---|---|---|
| `bloqueante` | Impide concretar el objetivo de carrera. | Si la maestría no la cierra, el objetivo no se logra. |
| `alta` | Limita seriamente el desempeño o las opciones. | Cerrarla cambia materialmente la trayectoria. |
| `media` | Reduce desempeño pero hay compensaciones. | Cerrarla mejora pero no es condición de éxito. |
| `baja` | "Nice to have". | No debería pesar mucho en la decisión. |

## El nivel de severidad determina el match

En el algoritmo (ver `references/matching-algorithm.md`), la cobertura de brechas se pondera por severidad: una maestría que cierra dos brechas bloqueantes vale más que una que cierra cinco brechas bajas. El sesgo es deliberado — concentrarse en lo crítico.

## Datos institucionales de contacto

Si el usuario pregunta por inscripción, costos, becas, calendarios:

- Sitio: https://online.anahuac.mx/maestrias-en-linea/
- Email: info@onlineanahuac.mx
- Teléfono: (55) 5062-3403
- WhatsApp: 55 9414-7545

**No inventes datos de precios, fechas de inicio, becas o promociones.** Esos cambian y son competencia de admisiones.

## Características generales del catálogo

Datos compartidos por las 24 maestrías (útiles para responder dudas comunes):

- **Modalidad**: 100% online, con sesiones síncronas grabadas.
- **Duración**: 27-28 meses (2 años 4 meses aproximadamente).
- **Asignaturas**: 18 por maestría.
- **Dedicación**: 6-10 horas por semana.
- **Plataforma**: Budly, con asistencia de IA generativa.
- **Reconocimiento**: RVOE SEP. Titulación directa (sin tesis).
- **Soft skills**: insignias digitales Pearson.

## Lectura recomendada paralela

- `references/conversation-flow.md` para el guion de las fases.
- `references/matching-algorithm.md` para entender cómo se traduce el diagnóstico en recomendación.
- `references/special-cases.md` para escenarios donde la metodología requiere ajustes.
