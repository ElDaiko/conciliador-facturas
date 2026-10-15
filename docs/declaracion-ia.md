# Declaración de uso de inteligencia artificial generativa

**Sí se usó IA generativa** en esta solución.

- **Herramienta:** Claude Code (Anthropic), con el modelo Claude Opus 5.5, como asistente de programación en la terminal.
- **Rastro en el repositorio:** los commits generados con asistencia incluyen la línea `Co-Authored-By: Claude`.

## Cómo se usó

**1. Planear antes de ejecutar (plan mode).** El análisis del enunciado y de los datos, la arquitectura y el plan por fases se hicieron en el modo de planeación de Claude Code, en el que la herramienta puede leer y analizar, pero no modificar archivos. El candidato revisó el plan, ajustó el alcance y lo aprobó antes de que se escribiera código. Así las decisiones de diseño quedaron tomadas por una persona y no sobre la marcha, y se evitó rehacer trabajo.

**2. Esfuerzo de razonamiento según la tarea.** Se usó el mismo modelo con distinto nivel de esfuerzo:

| Etapa | Modelo | Esfuerzo | Razón |
|---|---|---|---|
| Planeación y arquitectura | Claude Opus 5.5 | Alto | Es donde hay ambigüedad (reglas del enunciado, interpretación de los datos) y decisiones que condicionan todo lo demás |
| Ejecución de tareas | Claude Opus 5.5 | Medio | Con el plan aprobado, las tareas están acotadas; un esfuerzo menor reduce tiempo y consumo de tokens sin perder calidad |

**3. Fases cortas con revisión humana.** La implementación se dividió en fases (motor de reglas, API, sistema visual, pantalla, entregables). Al cerrar cada una, la IA presentaba lo hecho y cómo verificarlo, y el candidato lo revisaba antes de autorizar la siguiente. Las ambigüedades se resolvieron con preguntas explícitas al candidato, no con supuestos de la IA.

**4. Auditoría contra el enunciado.** Al final se pidió a la IA contrastar la solución, punto por punto, con el documento de la prueba. Esto llevó a identificar en el README qué reglas son del enunciado y cuáles son derivadas o adicionales, a mostrar cómo cambia el resultado según la interpretación y a llevar las decisiones técnicas al README, como pide el enunciado.

## En qué partes se usó y con qué propósito

| Parte de la solución | Uso de la IA | Propósito |
|---|---|---|
| Análisis del enunciado | Lectura del PDF, identificación de ambigüedades en las reglas y lista de preguntas abiertas | Entender el alcance y los riesgos antes de programar |
| Análisis de los datos de muestra | Script exploratorio que aplicó las reglas a los CSV y detectó los casos presentes (duplicados, vacíos, sin contabilizar, diferencias) | Fundamentar las interpretaciones con evidencia de los datos |
| Plan y arquitectura | Propuesta de estructura del repositorio, capas del backend, componentes del frontend y fases de trabajo | Organizar el desarrollo en 4–5 horas de referencia |
| Backend (Python) | Generación del código: lector CSV, modelos, reglas, conciliador, API, manejo de errores | Implementar las reglas y el servicio REST |
| Frontend (Angular) | Generación del código: tokens de diseño, componentes compartidos, store, servicio, pantalla de conciliación | Implementar la interfaz y la integración con la API |
| Pruebas | Generación de las pruebas automatizadas (60 de backend, 49 de frontend y 6 escenarios E2E con Playwright), la colección de Postman y los archivos de `data/casos-borde/` | Verificar las reglas, los errores y la correspondencia entre lo procesado y lo mostrado |
| Verificación visual | Revisión en el navegador (escritorio, 320 px y 375 px), navegación con teclado y árbol de accesibilidad | Detectar y corregir problemas de diseño responsive y de accesibilidad |
| Documentación | Redacción del README, el CHANGELOG y esta declaración | Documentar instalación, reglas, supuestos y decisiones |
| Configuración y seguridad de dependencias | `engines`, `.npmrc` (antigüedad mínima de versiones y scripts de instalación revisados) | Instalación reproducible y menor riesgo en la cadena de suministro |
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
- Conservar los extras (Docker, CI y reglas adicionales) marcados como opcionales, y documentar las decisiones técnicas en el README.
- Simplificar el código del backend para priorizar la legibilidad sobre la concisión.

## Cómo se validó lo generado

- **Pruebas automatizadas** de backend y frontend, incluida una prueba que fija el resultado de la muestra (50 / 32 / 18) y una prueba de integración del frontend con la respuesta real del backend.
- **Lint y formato** en ambos proyectos (ruff, ESLint con reglas de accesibilidad, Prettier).
- **Pruebas de punta a punta** con Playwright (escritorio y móvil) y **colección de Postman** ejecutada con Newman contra la ejecución local y contra Docker.
- **Contraste de colores** calculado con la fórmula de WCAG 2.2 para cada par usado.
- **Revisión del candidato** al cierre de cada fase, con los comandos de verificación incluidos en el README.

## Límites

- Las interpretaciones de las reglas ambiguas y su efecto en el resultado están documentados en el README (secciones Supuestos y Resultado con los archivos de prueba).
- La IA solo trabajó con los archivos ficticios entregados en la prueba y con casos de prueba creados para ella. No tuvo acceso a datos reales, credenciales ni sistemas corporativos.
- Todo lo generado se trató como una propuesta: se aceptó después de revisarlo y verificarlo con los mecanismos del punto anterior.
