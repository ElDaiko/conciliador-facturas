# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [SemVer](https://semver.org/lang/es/).

## [1.2.0] - 2026-10-15

### Added
- Colección de Postman (`postman/`) con entornos Local y Docker: 11 solicitudes y 47 verificaciones, incluidos los casos de error.
- Pruebas de punta a punta con Playwright (6 escenarios en escritorio y móvil) e integración en el CI.
- `engines` en `package.json` y `.npmrc` con antigüedad mínima de versiones, scripts de instalación revisados y validación de la versión de Node.

### Changed
- README resumido y organizado por secciones (stack, arquitectura, requisitos, ejecución, pruebas) con subsecciones de backend y frontend. El contrato de la API se consulta en Swagger o en la colección de Postman.

### Fixed
- Requisito de Node corregido a 22.22.3+ o 24.15+ (lo exige Angular 22).
- El build de Docker del frontend aplica la configuración de `.npmrc`.

## [1.1.2] - 2026-10-15

### Changed
- Declaración de IA: modo de planeación, nivel de esfuerzo por etapa, revisión por fases y auditoría contra el enunciado.

## [1.1.1] - 2026-10-15

### Changed
- Las decisiones técnicas quedan documentadas directamente en el README, como pide el enunciado. Se elimina `docs/adr/`.

## [1.1.0] - 2026-10-15

Extras opcionales: no cambian la funcionalidad ni la ejecución local oficial.

### Added
- Docker: `Dockerfile` del backend (sin root, con healthcheck), `Dockerfile` del frontend (build de Angular y nginx sin root que reenvía `/api`) y `docker-compose.yml`.
- Integración continua con GitHub Actions: lint, formato, pruebas y build del backend (Python 3.12 y 3.14) y del frontend (Node 24).

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
