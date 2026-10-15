# ADR 0003: Montos con Decimal, tolerancia de ±$1 y montos como texto en JSON

- **Estado:** aceptada
- **Fecha:** 2026-10-15

## Contexto

La conciliación compara valores en pesos. El tipo `float` no representa exactamente valores como 0,19, y la prueba evalúa el "cálculo correcto del IVA y del total".

## Decisión

- Todos los montos y tarifas se manejan con `decimal.Decimal`, creados desde texto.
- Una diferencia se considera inconsistencia si supera **±$1** (`TOLERANCIA` en `core/config.py`).
- La API envía los montos como **texto** (`"190000.00"`); el frontend los convierte a número solo para mostrarlos.

## Evidencia

- Con `float`, 11 de las 50 facturas de la muestra fallan una comparación exacta; con `Decimal`, solo fallan las 2 que de verdad tienen el IVA mal calculado.
- La menor diferencia real de la muestra es de $1.500 (FAC-0036). Una tolerancia porcentual (por ejemplo, 0,1 % ≈ $1.700 en esa factura) la ocultaría.

## Consecuencias

- Los cálculos son exactos y reproducibles.
- La tolerancia es un parámetro visible: cambiarla es una línea y la respuesta de la API la informa (`tolerancia`).
- El frontend no debe hacer aritmética con los montos; solo los formatea.
