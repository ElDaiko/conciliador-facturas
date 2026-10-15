# ADR 0002: Backend en FastAPI con capas simples y sin persistencia

- **Estado:** aceptada
- **Fecha:** 2026-10-15

## Contexto

La prueba pide una API REST en Python (FastAPI, Flask o similar) que reciba dos CSV, aplique reglas y entregue un resumen y un detalle. No pide guardar históricos y aclara que no se espera una solución de producción.

## Decisión

- **FastAPI**: valida la entrada, genera la documentación Swagger (`/docs`) y los modelos de Pydantic sirven de contrato con el frontend.
- Tres capas:
  - `infra/`: lectura defensiva del CSV (codificación, separador, columnas).
  - `domain/`: modelos y reglas como funciones puras, sin dependencias de HTTP ni de archivos.
  - `api/`: ruta HTTP que coordina las dos anteriores, y manejo de errores en `main.py`.
- **Sin capa de aplicación** (casos de uso) ni repositorios: hay un único caso de uso y la ruta lo coordina en pocas líneas.
- **Sin base de datos**: cada solicitud se procesa en memoria y se descarta.
- Librería estándar `csv` en lugar de pandas.

## Alternativas consideradas

- **Flask:** también válido, pero requiere validación y documentación manuales.
- **Arquitectura hexagonal completa:** para un caso de uso, más archivos que lógica.
- **pandas:** potente, pero para 40–60 registros agrega una dependencia pesada sin necesidad.

## Consecuencias

- El dominio se prueba sin servidor (47 de las 60 pruebas no usan HTTP).
- Si los datos vinieran de otra fuente (base de datos, ERP), solo cambia `infra/`.
- Persistir el histórico requerirá agregar almacenamiento y, entonces sí, una capa de aplicación.
