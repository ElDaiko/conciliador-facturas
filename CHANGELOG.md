# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [SemVer](https://semver.org/lang/es/).

## [1.0.0] - 2026-10-15

Primera versión entregable del prototipo.

### Added
- Estructura del monorepo (`backend/`, `frontend/`, `data/`, `docs/`) y archivos de muestra.
- Backend: lector CSV defensivo, reglas de conciliación con `Decimal` y catálogo de causas, con pruebas automatizadas.
- API REST (`POST /api/conciliaciones`, `GET /api/health`) con errores en español y cabeceras de seguridad.
- Archivos de casos borde en `data/casos-borde/`.
- Frontend Angular 22: tokens de diseño accesibles, componentes compartidos y pantalla de conciliación con resumen, filtros por estado, causa y búsqueda, tabla responsive y detalle trazable por factura.
- Documentación: README con trazabilidad al enunciado, reglas por origen y resultados alternativos; ADR 0001–0005; declaración de uso de IA; presentación ejecutiva de 5 diapositivas.

### Fixed
- Mensaje de "servidor no disponible" cuando el proxy responde 502/503/504.
- Archivos de prueba conservados byte a byte (saltos de línea CRLF originales).
