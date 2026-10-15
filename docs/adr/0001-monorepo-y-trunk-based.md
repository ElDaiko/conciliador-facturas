# ADR 0001: Monorepo y desarrollo trunk-based

- **Estado:** aceptada
- **Fecha:** 2026-10-15

## Contexto

La prueba pide entregar el frontend y el backend "en un repositorio o archivo comprimido" y que la solución sea reproducible siguiendo solo el README. La desarrolla una sola persona en 4–5 horas de referencia.

## Decisión

- Un único repositorio con `backend/`, `frontend/`, `data/` y `docs/`.
- Desarrollo **trunk-based** sobre `main`, con commits pequeños según Conventional Commits y la etiqueta `v1.0.0` para la versión entregada.

## Alternativas consideradas

- **Dos repositorios:** obliga al evaluador a clonar y coordinar versiones de dos proyectos.
- **GitFlow** (`develop`, `feature/*`, `release/*`): aporta control cuando hay varios desarrolladores y versiones en paralelo; para una persona y una entrega única agrega ceremonia sin beneficio. La prueba no lo exige.

## Consecuencias

- Un solo `git clone` y un solo README para todo.
- El historial muestra la evolución por fases con mensajes que describen el porqué de cada cambio.
- Si el proyecto creciera a un equipo, se pueden adoptar ramas cortas con pull requests sin cambiar la estructura.
