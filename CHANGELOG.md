# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [SemVer](https://semver.org/lang/es/).

## [Unreleased]

### Added
- Estructura inicial del monorepo (`backend/`, `frontend/`, `data/`, `docs/`).
- Archivos de muestra `data/facturas.csv` y `data/contabilidad.csv`.
- Backend: lector CSV defensivo, reglas de conciliación con `Decimal` y catálogo de causas, con pruebas automatizadas.
- API REST (`POST /api/conciliaciones`, `GET /api/health`) con errores en español y cabeceras de seguridad.
- Archivos de casos borde en `data/casos-borde/`.
- Frontend Angular 22: tokens de diseño, base accesible y componentes compartidos (botón, selector de archivo, tarjeta KPI, insignia de estado, alerta, indicador de carga, pipe de montos).
