# ADR 0005: Angular con signals, SCSS propio y proxy sin CORS

- **Estado:** aceptada
- **Fecha:** 2026-10-15

## Contexto

El frontend tiene una sola pantalla: cargar archivos, ver el resumen, filtrar la tabla y revisar el detalle. Debe ser accesible, funcionar en móvil y tener una identidad visual inspirada en el banco sin copiar su marca.

## Decisiones

- **Angular 22** standalone, *zoneless* y `OnPush`, con la API de signals (`signal`, `computed`, `input`, `model`, `output`).
- **Estado en un store de signals** provisto en la página, sin NgRx.
- **Contenedor y presentación:** solo la página conoce el store.
- **SCSS propio con tokens** (variables CSS) en lugar de Angular Material u otra librería; tipografía libre instalada por npm, sin CDN.
- **Proxy de desarrollo** (`proxy.conf.json`) para `/api`, en lugar de habilitar CORS en la API.

## Alternativas consideradas

- **NgRx:** útil con muchos flujos y efectos; aquí multiplicaría el código para un solo flujo lineal.
- **Angular Material:** acelera formularios complejos, pero su aspecto es difícil de adaptar y añade peso para una pantalla.
- **CORS en FastAPI:** funciona, pero abre la API a otros orígenes; con el proxy el navegador ve un solo origen, igual que en un despliegue real detrás de un mismo dominio.

## Consecuencias

- Menos dependencias y control total del contraste y del aspecto (verificado contra WCAG 2.2 AA).
- Los componentes compartidos (botón, selector de archivo, KPI, insignia, alerta) son pequeños y tienen pruebas propias.
- Un despliegue real necesita un servidor web (por ejemplo, nginx) que sirva el frontend y reenvíe `/api`, como hace el proxy en desarrollo.
