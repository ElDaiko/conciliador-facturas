# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [SemVer](https://semver.org/lang/es/).

## [1.4.1] - 2026-10-15

### Fixed
- Presentación, diapositiva 4: el gráfico de inconsistencias por causa mostraba números en lugar del nombre de cada causa en algunos visores. Ahora las barras se dibujan con formas y texto, legibles en cualquier programa.
- Presentación: textos ajustados para que no afirmen más de lo que el sistema hace (los valores reportado, esperado y diferencia aplican a las causas de cálculo; la conciliación se ejecuta con un clic) ni más de lo que dice el enunciado ("puede generar reprocesos").

## [1.4.0] - 2026-10-15

### Added
- Validación de archivos corruptos o errados con mensajes que explican cómo corregirlos: libros de Excel, ZIP o PDF renombrados como `.csv` (`FORMATO_NO_CSV`), archivos en UTF-16 (`CODIFICACION_NO_SOPORTADA`) y archivos con caracteres nulos (`ARCHIVO_DANADO`).
- En el frontend, mensaje específico para hojas de cálculo (`.xlsx`, `.xls`, `.xlsm`, `.ods`).
- Casos borde, pruebas de backend, escenario E2E y solicitudes de Postman para cada caso.
- Declaración de IA: mejoras propuestas por el candidato.

### Fixed
- Un CSV con una comilla sin cerrar se procesaba parcialmente sin avisar; ahora se rechaza indicando la línea donde empieza el problema.

## [1.3.0] - 2026-10-15

### Changed
- Identidad visual más cercana al sitio de referencia, sin cambios funcionales: amarillo `#FDDA24`, carbón `#2C2A29`, fondo `#F7F7F7`, tipografía Open Sans, encabezado con barra superior carbón, botones tipo píldora (amarillo y carbón), tarjetas con esquinas casi rectas y sombra suave, titulares más grandes y pie color carbón. Contraste WCAG AA verificado.
- Presentación con la nueva paleta y una captura actualizada del prototipo.

## [1.2.1] - 2026-10-15

### Changed
- README: la sección de alcance declara que no hay funcionalidades solicitadas sin completar y lista solo las limitaciones conocidas; se retira la lista de funcionalidades no solicitadas.
- Presentación: la diapositiva 5 muestra solo los beneficios esperados (proceso actual frente al prototipo), sin siguientes pasos.

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
