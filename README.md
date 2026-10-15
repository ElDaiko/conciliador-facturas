# Conciliador de facturas y retenciones

Prototipo web que cruza el archivo de **facturas de proveedores** con el de **registros contables**, aplica reglas contables y tributarias, y muestra un resumen y el detalle de cada factura con la causa de cada inconsistencia.

> Prueba técnica — Analista III, Gerencia de Evolución Contable y Tributaria.
> Prototipo con identidad visual inspirada en Bancolombia; no es un producto oficial.

## Entregables

| Entregable | Ubicación |
|---|---|
| Código fuente | [`backend/`](backend/) (Python) y [`frontend/`](frontend/) (Angular) |
| Archivos de prueba | [`data/`](data/) (muestra entregada) y [`data/casos-borde/`](data/casos-borde/) (errores) |
| Colección de Postman | [`postman/`](postman/) |
| Presentación ejecutiva (5 diapositivas) | [`docs/presentacion/presentacion-conciliador.pptx`](docs/presentacion/presentacion-conciliador.pptx) |
| Declaración de uso de IA | [`docs/declaracion-ia.md`](docs/declaracion-ia.md) |

## Stack

### Backend

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.14 (mínima 3.12) | Lenguaje |
| FastAPI · uvicorn · python-multipart | 0.143 · 0.54 · 0.0.32 | API REST, servidor y recepción de archivos |
| pytest · httpx2 · ruff | 9.1 · 2.13 · 0.17 | Pruebas y lint (solo desarrollo) |

### Frontend

| Tecnología | Versión | Uso |
|---|---|---|
| Angular | 22.2 | Componentes standalone, signals, sin `zone.js` |
| SCSS · Open Sans (npm) | — · 5.3 | Estilos propios con tokens; tipografía libre sin CDN |
| Vitest · Playwright · ESLint · Prettier | 4.1 · 1.64 · 10 · 3.9 | Pruebas unitarias, E2E, lint y formato (solo desarrollo) |

### Herramientas

Postman (pruebas de la API), Docker Compose (opcional) y GitHub Actions (CI). Las dependencias tienen versiones fijas en `backend/requirements*.txt` y `frontend/package-lock.json`.

## Arquitectura

```
Navegador → Angular (4200) ──/api──▶ proxy ──▶ FastAPI (8000) → lector CSV → reglas → resumen + detalle (JSON)
```

### Backend

```
backend/app/
├── api/       Endpoints (POST /api/conciliaciones, GET /api/health) y contrato JSON (Pydantic)
├── domain/    Modelos, catálogo de causas, reglas (funciones puras) y conciliador
├── infra/     Lectura defensiva del CSV (codificación, separador, columnas)
└── core/      Configuración (tolerancia, columnas, estados) y errores
```

Sin base de datos: cada solicitud se procesa en memoria. Documentación interactiva en http://localhost:8000/docs (Swagger).

### Frontend

```
frontend/src/app/
├── core/                    Modelos del contrato de la API, servicio HTTP y layout
├── features/conciliacion/   Página, store (signals), carga, resumen, filtros, tabla y detalle
└── shared/                  Componentes reutilizables (botón, selector de archivo, KPI, insignia, alerta) y pipes
```

Solo la página conoce el store; los demás componentes reciben datos y emiten eventos. Interfaz **mobile first** y accesible (WCAG 2.2 AA): contraste verificado, estados con ícono y texto (nunca solo color), navegación por teclado y soporte de lectores de pantalla.

## Requisitos

| Herramienta | Versión | Necesaria para |
|---|---|---|
| Python | 3.12 o superior | Backend |
| Node.js | 22.22.3+ o 24.15+ | Frontend (Angular 22 lo exige; `engines` lo valida) |
| npm | 10 o superior (11 recomendado) | Frontend; con npm 11 se aplican las protecciones de `.npmrc` |
| Docker con Compose v2 | — | Opcional |
| Postman | — | Opcional, para probar la API |

No se requiere base de datos, credenciales ni variables de entorno. Todos los datos son ficticios.

## Cómo levantarlo

### Backend (terminal 1)

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/uvicorn app.main:app --port 8000
```

En Windows, reemplace `.venv/bin/` por `.venv\Scripts\`.

### Frontend (terminal 2)

```bash
cd frontend
npm ci
npm start
```

### Probar

1. Abra http://localhost:4200, cargue `data/facturas.csv` y `data/contabilidad.csv` y presione **Conciliar archivos**. Debe ver **50 facturas: 32 correctas y 18 con inconsistencia**.
2. **API con Postman:** importe `postman/conciliador.postman_collection.json` y el entorno `postman/local.postman_environment.json`. En *Settings → General → Working directory* elija la raíz del repositorio (las solicitudes cargan los archivos de `data/`). Ejecute la colección: 15 solicitudes con 62 verificaciones, incluidos los casos de error.
   Sin Postman, desde la raíz: `npx newman run postman/conciliador.postman_collection.json -e postman/local.postman_environment.json`.

### Con Docker (opcional)

```bash
docker compose up --build      # http://localhost:8080
docker compose down
```

nginx sirve el frontend y reenvía `/api` al backend, que no queda expuesto. Para Postman use el entorno `postman/docker.postman_environment.json`.

<details>
<summary>Docker con Colima (macOS) y solución de problemas</summary>

```bash
brew install colima docker docker-compose
colima start --cpu 2 --memory 4
```

- `docker: 'compose' is not a docker command` → agregue a `~/.docker/config.json`: `{ "cliPluginsExtraDirs": ["/opt/homebrew/lib/docker/cli-plugins"] }`.
- `Cannot connect to the Docker daemon` → `colima start`.
- Puerto 8080 ocupado → cambie `'8080:8080'` por `'8081:8080'` en `docker-compose.yml`.

</details>

## Pruebas

### Backend

```bash
cd backend
.venv/bin/pytest          # 67 pruebas: reglas, lector CSV, API y resultado de la muestra
.venv/bin/ruff check .
```

### Frontend

```bash
cd frontend
npm test                  # 50 pruebas unitarias y de integración (Vitest)
npm run lint              # incluye reglas de accesibilidad de plantillas
npm run build
```

### De punta a punta

```bash
cd frontend
npx playwright install chromium   # solo la primera vez
npm run e2e               # 7 escenarios en escritorio y en móvil; levanta backend y frontend
```

Requiere el entorno del backend (`backend/.venv`) ya creado. Escenarios: flujo principal, filtros, detalle trazable, archivo con columna faltante, archivo no CSV, Excel renombrado como CSV y servidor no disponible.

La integración continua ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) ejecuta todo lo anterior en cada *push* a `main`.

## Reglas de negocio

Cada factura queda **Correcta** o **Con inconsistencia**; una factura puede tener varias causas, y cada una muestra el valor reportado, el esperado y la diferencia. Tolerancia de **±$1** en las comparaciones.

| Causa | Regla | Origen |
|---|---|---|
| IVA mal calculado | `valor_iva` ≠ `base_gravable × tarifa_iva` | Enunciado (regla 1) |
| Total no cuadra | `total_factura` ≠ `base + IVA esperado − retención esperada` | Enunciado (regla 2) |
| Factura duplicada | `id_factura` repetido; se marcan todas las ocurrencias | Enunciado (regla 3) |
| Sin registro contable | `id_factura` ausente en contabilidad | Enunciado (regla 3) |
| Campo obligatorio vacío | Alguno de los 10 campos mínimos está vacío | Enunciado (campos obligatorios) |
| Contabilización no en firme | Estado contable distinto a `Contabilizada` | Derivada del caso (*estados de contabilización*) |
| Valor contabilizado diferente | Suma de débitos ≠ `total_factura` | Derivada del caso (*diferencias en valores*) |
| Retención mal calculada | `valor_retencion` ≠ `base_gravable × tarifa_retencion` | Derivada del caso (*retenciones*) |
| Valor inválido · Partida descuadrada · Registro contable incompleto | Formato inválido · débitos ≠ créditos · registro contable con campos vacíos | Adicional (robustez) |

**Advertencias** (no cambian la clasificación): línea contable en 0, contabilizada en un periodo posterior y fecha contable anterior a la factura.

## Resultado esperado

Con `data/facturas.csv` y `data/contabilidad.csv`: **50 facturas (48 únicas), 32 correctas y 18 con inconsistencia**; $11.521.700 sin contabilizar, $5.572.350 con contabilización no en firme y $106.500 en diferencias de cálculo.

- Duplicadas: FAC-0004 y FAC-0015 (las dos ocurrencias de cada una).
- Sin registro contable: FAC-0007, FAC-0021, FAC-0034 y FAC-0042.
- Total no cuadra: FAC-0009, FAC-0023 y FAC-0036. IVA mal calculado: FAC-0006 y FAC-0018.
- Campo vacío: FAC-0013 (NIT), FAC-0029 (concepto) y FAC-0042 (fecha).
- Contabilización pendiente: FAC-0011, FAC-0027 y FAC-0039.

Lo verifican `backend/tests/test_muestra_real.py`, la colección de Postman y las pruebas E2E. Es el resultado según los supuestos de abajo: aplicando solo las reglas explícitas del enunciado sería **35 / 15** (las 3 pendientes pasarían a correctas), y marcando solo la segunda ocurrencia de cada duplicado, **34 / 16**.

## Supuestos

- El total se valida con el IVA y la retención **esperados**, para que cada error aparezca con su causa raíz (FAC-0006 y FAC-0018 tienen solo el IVA alterado).
- `id_factura` es la llave del cruce (contabilidad no tiene NIT); por eso un mismo id con NIT distinto es duplicado.
- La fórmula de la regla 2 corresponde al **neto a pagar**: en la práctica la retención la practica el comprador. Se aplica tal como la define la prueba.
- Contabilidad es una representación simplificada (débito = crédito por línea); el valor contabilizado es la suma de débitos del `id_factura`.
- Las tarifas se aceptan como `0.19`, `19` o `19%`; los estados válidos son `Contabilizada`/`Contabilizado`.
- Se aceptan CSV en UTF-8 (con o sin BOM) o Windows-1252, separados por `,` o `;`, con punto decimal, de hasta 5 MB.
- Se rechazan con un mensaje que explica cómo corregirlos: libros de Excel o PDF renombrados como `.csv`, archivos en UTF-16 ("Texto Unicode" de Excel), archivos con caracteres nulos (dañados) y CSV con comillas sin cerrar (se indica la línea). Ver `data/casos-borde/`.
- El resultado 50 / 32 / 18 es el de esta solución; la empresa no entregó un resultado oficial.

## Decisiones técnicas

### Backend

- **FastAPI**: valida la entrada y genera Swagger; Pydantic define el contrato con el frontend.
- **Capas `infra` / `domain` / `api`**, sin capa de casos de uso ni base de datos: hay un único caso de uso y las reglas se prueban sin servidor.
- **`Decimal`** para montos: con `float`, 11 de las 50 facturas fallan una comparación exacta.
- **Tolerancia de ±$1**: un porcentaje ocultaría la menor diferencia real de la muestra ($1.500).
- **Montos como texto en el JSON**, para no perder precisión; errores con forma única `{codigo, mensaje, archivo}` en español.
- **Seguridad básica**: límite de 5 MB, sin almacenamiento, cabeceras de seguridad, `Cache-Control: no-store` y logs sin datos de facturas.

### Frontend

- **Angular 22** (versión estable vigente) con standalone, zoneless y signals.
- **Signals para el estado** (`signal`, `computed`, `input`, `model`); el observable de `HttpClient` solo en el servicio, y el store vuelca el resultado en signals.
- **SCSS propio con tokens** en lugar de una librería de componentes: control del contraste y del aspecto.
- **Proxy para `/api`** (nginx en Docker) en lugar de CORS: el navegador ve un solo origen.
- **`.npmrc`**: solo versiones publicadas hace más de 2 días, scripts de instalación revisados (`allowScripts`) y versión de Node validada con `engines`.

### General

- **Monorepo trunk-based** con Conventional Commits: un desarrollador y una entrega.
- **Docker y CI son opcionales**: la ejecución oficial (`pip` + `npm`) no exige instalar nada más.

## Alcance

**Funcionalidades no completadas:** ninguna. Todo lo solicitado en el enunciado está implementado y probado.

**Limitaciones conocidas**

- Solo se acepta punto decimal en los montos (no `1.234,56`).
- La contabilidad se valida con la representación simplificada del archivo de muestra (débito = crédito por línea), no como un asiento contable completo.

## Uso de inteligencia artificial

Se usó IA generativa; el detalle está en [`docs/declaracion-ia.md`](docs/declaracion-ia.md).

---

Versiones etiquetadas y cambios en [`CHANGELOG.md`](CHANGELOG.md).
