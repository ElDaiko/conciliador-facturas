# Declaración de uso de inteligencia artificial generativa

**Sí se usó IA generativa** en esta solución.

- **Herramienta:** Claude Code (Anthropic), con el modelo Claude Opus 5.5, como asistente de programación en la terminal.
- **Modo de trabajo:** desarrollo por fases con pausas. Al cerrar cada fase, el candidato revisaba el resultado y decidía si continuar o ajustar.
- **Rastro en el repositorio:** los commits generados con asistencia incluyen la línea `Co-Authored-By: Claude`.

## En qué partes se usó y con qué propósito

| Parte de la solución | Uso de la IA | Propósito |
|---|---|---|
| Análisis del enunciado | Lectura del PDF, identificación de ambigüedades en las reglas y lista de preguntas abiertas | Entender el alcance y los riesgos antes de programar |
| Análisis de los datos de muestra | Script exploratorio que aplicó las reglas a los CSV y detectó los casos presentes (duplicados, vacíos, sin contabilizar, diferencias) | Fundamentar las interpretaciones con evidencia de los datos |
| Plan y arquitectura | Propuesta de estructura del repositorio, capas del backend, componentes del frontend y fases de trabajo | Organizar el desarrollo en 4–5 horas de referencia |
| Backend (Python) | Generación del código: lector CSV, modelos, reglas, conciliador, API, manejo de errores | Implementar las reglas y el servicio REST |
| Frontend (Angular) | Generación del código: tokens de diseño, componentes compartidos, store, servicio, pantalla de conciliación | Implementar la interfaz y la integración con la API |
| Pruebas | Generación de las pruebas automatizadas (60 de backend y 49 de frontend) y de los archivos de `data/casos-borde/` | Verificar las reglas, los errores y la correspondencia entre lo procesado y lo mostrado |
| Verificación visual | Revisión en el navegador (escritorio, 320 px y 375 px), navegación con teclado y árbol de accesibilidad | Detectar y corregir problemas de diseño responsive y de accesibilidad |
| Documentación | Redacción del README, los ADR, el CHANGELOG y esta declaración | Documentar instalación, reglas, supuestos y decisiones |
| Docker e integración continua | Generación de los Dockerfile, la configuración de nginx, `docker-compose.yml` y el workflow de GitHub Actions; instalación y prueba con Colima | Ofrecer una ejecución alternativa con un solo comando y verificación automática en cada cambio |
| Presentación | Generación de la presentación de 5 diapositivas a partir de los resultados reales de la muestra | Comunicar la propuesta al equipo funcional |

## Decisiones tomadas por el candidato

La IA propuso opciones; estas decisiones las tomó el candidato:

- Desarrollo **trunk-based** con Conventional Commits en lugar de GitFlow completo.
- Estructura de frontend con `shared/` y `features/` en lugar de *atomic design* de cuatro niveles.
- **SCSS propio con tokens**, sin librería de componentes.
- **Identidad visual** inspirada en el banco: amarillo solo como fondo con texto oscuro, advertencia en naranja (no ámbar), estados siempre con ícono y texto, tipografía libre instalada por npm y aviso de que no es un producto oficial.
- **Accesibilidad y mobile first** como requisitos de la interfaz.
- Docker como extra opcional al final y README incremental desde el inicio.
- Mantener el estado contable `Pendiente` como **inconsistencia** (regla derivada del caso) y documentarlo con el resultado alternativo.
- Simplificar el código del backend para priorizar la legibilidad sobre la concisión.

## Cómo se validó lo generado

- **Pruebas automatizadas** de backend y frontend, incluida una prueba que fija el resultado de la muestra (50 / 32 / 18) y una prueba de integración del frontend con la respuesta real del backend.
- **Lint y formato** en ambos proyectos (ruff, ESLint con reglas de accesibilidad, Prettier).
- **Ejecución de punta a punta** con los dos servidores: carga de los archivos, filtros, detalle por factura y casos de error (archivo inválido, backend detenido).
- **Contraste de colores** calculado con la fórmula de WCAG 2.2 para cada par usado.
- **Revisión del candidato** al cierre de cada fase, con los comandos de verificación incluidos en el README.

## Límites

- Las interpretaciones de las reglas ambiguas y su efecto en el resultado están en [ADR 0004](adr/0004-interpretacion-de-reglas.md) y en el README.
- No se usó IA con datos reales: todos los datos son los archivos ficticios entregados en la prueba y casos de prueba creados para ella.
