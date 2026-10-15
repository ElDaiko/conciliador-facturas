# ADR 0004: Interpretación de las reglas ambiguas del enunciado

- **Estado:** aceptada
- **Fecha:** 2026-10-15

## Contexto

Las 5 reglas del enunciado dejan decisiones abiertas y no hubo canal para aclararlas. La empresa tampoco entregó un resultado esperado.

## Decisiones

1. **Total con valores esperados.** La regla 2 (`base + IVA − retención`) se evalúa con el IVA y la retención *calculados*. Así cada error aparece con su causa raíz: en FAC-0006 y FAC-0018 solo el IVA está alterado y el total es coherente con el IVA correcto.
2. **Duplicado = mismo `id_factura`, se marcan todas las ocurrencias.** Es la única llave común entre los dos archivos (contabilidad no tiene NIT). No es posible saber cuál ocurrencia es la válida.
3. **Campos obligatorios = los 10 campos mínimos del enunciado.** Un campo vacío es inconsistencia; solo se omiten los cálculos que dependen de él.
4. **Estado contable distinto a `Contabilizada` es inconsistencia** (regla derivada del caso, que menciona *"estados de contabilización"*): una factura con registro pendiente no está conciliada.
5. **Reglas derivadas y adicionales** (retención, valor contabilizado, partida descuadrada, registro incompleto, valor inválido) se incluyen y se marcan como tales en el README. Con la muestra, ninguna cambia el conteo salvo la del punto 4.
6. **Advertencias** (línea contable en 0, periodo posterior, fecha contable anterior) se informan sin cambiar la clasificación: no son errores contables por sí mismas.

## Efecto en el resultado de la muestra

| Interpretación | Correctas | Con inconsistencia |
|---|---|---|
| Implementada | 32 | 18 |
| Solo reglas explícitas (sin el punto 4) | 35 | 15 |
| Duplicado solo en la segunda ocurrencia | 34 | 16 |

## Consecuencias

- El README separa reglas del enunciado, derivadas y adicionales, y muestra estas alternativas.
- Cambiar cualquiera de estas decisiones afecta una sola función en `domain/reglas.py` o `domain/conciliador.py`, y la prueba `test_muestra_real.py` indica el nuevo resultado.
