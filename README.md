# Conciliador de facturas y retenciones

Prototipo web que cruza el archivo de **facturas de proveedores** con el de **registros contables**, aplica reglas contables y tributarias básicas y presenta un resumen y un detalle de las facturas correctas y de las que tienen inconsistencias, con la causa de cada una.

> Prueba técnica — Analista III, Gerencia de Evolución Contable y Tributaria.
>
> Prototipo con identidad visual inspirada en Bancolombia; no es un producto oficial.

## Entregables

| # | Entregable solicitado | Ubicación |
|---|---|---|
| 1 | Código fuente del frontend y del backend | [`frontend/`](frontend/) (Angular) y [`backend/`](backend/) (Python, FastAPI) |
| 2 | README con instalación y ejecución | Este archivo |
| 3 | Archivos de prueba | [`data/`](data/) (muestra entregada) y [`data/casos-borde/`](data/casos-borde/) (errores) |
| 4 | Presentación ejecutiva (5 diapositivas) | [`docs/presentacion/`](docs/presentacion/) |
| 5 | Declaración de uso de IA generativa | [`docs/declaracion-ia.md`](docs/declaracion-ia.md) |

## Contenido

- [Requisitos](#requisitos)
- [Inicio rápido](#inicio-rápido)
- [Trazabilidad con el enunciado](#trazabilidad-con-el-enunciado)
- [Reglas de negocio](#reglas-de-negocio)
- [Resultado con los archivos de prueba](#resultado-con-los-archivos-de-prueba)
- [Supuestos](#supuestos)
- [Decisiones técnicas](#decisiones-técnicas)
- [Funcionalidades no incluidas](#funcionalidades-no-incluidas)
- [Uso de inteligencia artificial](#uso-de-inteligencia-artificial)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Backend](#backend)
- [Frontend](#frontend)
- [Docker (opcional)](#docker-opcional)
- [Integración continua](#integración-continua)
- [Control de versiones](#control-de-versiones)

## Requisitos

| Herramienta | Versión probada | Mínima |
|---|---|---|
| Python | 3.14.7 | 3.12 |
| Node.js | 24.19.0 | 22 LTS |
| npm | 11.17.0 | 10 |
| Angular CLI | 22.2 (incluida en `devDependencies`, no requiere instalación global) | — |
| Git | 2.50 | — |

No se requiere base de datos, credenciales, variables de entorno ni acceso a sistemas corporativos. Todas las herramientas son de libre acceso y todos los datos son ficticios.

## Inicio rápido

**Terminal 1 — backend** (desde la raíz del repositorio):

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/uvicorn app.main:app --port 8000
```

**Terminal 2 — frontend** (desde la raíz del repositorio):

```bash
cd frontend
npm ci
npm start
```

Abra http://localhost:4200, cargue `data/facturas.csv` y `data/contabilidad.csv` y presione **Conciliar archivos**. Debe obtener **50 facturas: 32 correctas y 18 con inconsistencia** (ver [Resultado con los archivos de prueba](#resultado-con-los-archivos-de-prueba)).

> En Windows, reemplace `.venv/bin/` por `.venv\Scripts\`.

## Trazabilidad con el enunciado

| Requisito del enunciado | Implementación | Verificación |
|---|---|---|
| Regla 1: IVA esperado = base gravable × tarifa de IVA | `backend/app/domain/reglas.py` → `validar_iva` | `tests/test_reglas.py`, `tests/test_muestra_real.py` |
| Regla 2: total = base gravable + IVA − retención | `reglas.py` → `total_esperado`, `validar_total` | Ídem |
| Regla 3: facturas duplicadas y sin registro contable | `reglas.py` → `validar_duplicado`, `validar_contabilidad` | Ídem |
| Regla 4: clasificar como Correcta o Con inconsistencia e indicar la causa | `domain/conciliador.py` → `_evaluar_factura`; catálogo en `domain/causas.py` | Ídem |
| Regla 5: resumen con el total de facturas y el número de inconsistencias | `conciliador.py` → `_resumir`; tarjetas del resumen en el frontend | `test_muestra_real.py`, `conciliacion.page.spec.ts` |
| API REST en Python (FastAPI, Flask o similar) | FastAPI: `backend/app/main.py`, `api/routes.py` | `tests/test_api.py` |
| Recibir los archivos CSV y leer su información | `POST /api/conciliaciones` (multipart) + `infra/lector_csv.py` | `tests/test_lector_csv.py`, `test_api.py` |
| Servicio que entregue el resumen y el detalle | Respuesta `{ resumen, detalle, ... }` ([API](#api)) | `test_api.py` |
| Manejo básico de errores de archivo y campos obligatorios | Errores 400/413/422 en español; causa `CAMPO_VACIO` por fila | `test_api.py`, `data/casos-borde/` |
| Pantalla para cargar los archivos y ejecutar el procesamiento | `features/conciliacion/carga-archivos/` | `conciliacion.page.spec.ts` |
| Resumen con el total de facturas y las inconsistencias | `resumen-conciliacion/` | Ídem |
| Tabla de resultados con filtro por estado | `tabla-resultados/`, `filtros-resultados/` | Ídem |
| Consumir la API de Python desde Angular | `core/services/conciliacion-api.service.ts` | `conciliacion-api.service.spec.ts` |
| Mensajes básicos de carga y error | `indicador-carga`, `alerta` | `conciliacion.page.spec.ts` |
| README con versiones, dependencias, comandos y configuración | Este archivo | Clon limpio siguiendo solo este README |
| Supuestos, decisiones y funcionalidades no completadas documentados | [Supuestos](#supuestos), [Decisiones](#decisiones-técnicas), [No incluidas](#funcionalidades-no-incluidas) | — |
| Sin información real, credenciales ni datos sensibles | Solo datos ficticios; sin secretos en el código | — |

Lo que va **más allá del enunciado** se identifica como tal en las reglas (columna *Origen*) y en las secciones de backend y frontend.

## Reglas de negocio

Cada factura se clasifica como **Correcta** o **Con inconsistencia**. Una factura puede tener varias causas a la vez, y cada causa muestra el valor reportado, el valor esperado y la diferencia. Se aplica una tolerancia de **±$1** en todas las comparaciones de valores.

**Origen:** *Enunciado* = regla explícita de la prueba · *Derivada del caso* = no está entre las 5 reglas, pero se desprende de la descripción del caso · *Adicional* = validación de robustez propia.

| Código | Causa | Regla | Origen |
|---|---|---|---|
| `IVA_DIFERENTE` | IVA mal calculado | `valor_iva` ≠ `base_gravable × tarifa_iva` | Enunciado (regla 1) |
| `TOTAL_DIFERENTE` | Total no cuadra | `total_factura` ≠ `base + IVA esperado − retención esperada` | Enunciado (regla 2) |
| `DUPLICADA` | Factura duplicada | El `id_factura` aparece más de una vez; se marcan todas las ocurrencias | Enunciado (regla 3) |
| `SIN_CONTABILIZAR` | Sin registro contable | El `id_factura` no existe en contabilidad | Enunciado (regla 3) |
| `CAMPO_VACIO` | Campo obligatorio vacío | Cualquiera de los 10 campos mínimos está vacío; los cálculos que dependen de él se omiten | Enunciado (manejo de campos obligatorios; los datos incluyen *campos vacíos*) |
| `ESTADO_NO_CONTABILIZADO` | Contabilización no está en firme | El registro contable tiene un estado distinto a `Contabilizada` (por ejemplo, `Pendiente`) | Derivada del caso (*"estados de contabilización"*) |
| `VALOR_CONTABLE_DIFERENTE` | Valor contabilizado diferente | La suma de débitos del `id_factura` ≠ `total_factura` | Derivada del caso (*"diferencias en valores"*) |
| `RETENCION_DIFERENTE` | Retención mal calculada | `valor_retencion` ≠ `base_gravable × tarifa_retencion` | Derivada del caso (*conciliador de facturas y retenciones*) |
| `VALOR_INVALIDO` | Valor con formato inválido | Montos no numéricos o negativos, o fechas con formato distinto a `AAAA-MM-DD` | Adicional |
| `PARTIDA_DESCUADRADA` | Débitos y créditos no cuadran | La suma de débitos ≠ la suma de créditos del `id_factura` | Adicional |
| `REGISTRO_CONTABLE_INCOMPLETO` | Registro contable incompleto | El registro contable tiene campos vacíos o inválidos | Adicional |

**Advertencias** (adicionales): se informan para revisión, pero **no cambian la clasificación**.

| Código | Advertencia | Regla |
|---|---|---|
| `LINEA_CONTABLE_EN_CERO` | Línea contable sin valor | Línea con débito y crédito en 0 |
| `PERIODO_POSTERIOR` | Contabilizada en periodo posterior | El mes de contabilización es posterior al de la factura (revisar corte) |
| `FECHA_CONTABLE_ANTERIOR` | Contabilizada antes de la fecha de factura | `fecha_contabilizacion` < `fecha_factura` |

## Resultado con los archivos de prueba

La prueba no entrega un resultado esperado. Este es el que produce la solución con `data/facturas.csv` y `data/contabilidad.csv`, **según las reglas y los supuestos documentados**:

| Indicador | Valor |
|---|---|
| Registros de factura | **50** (48 `id_factura` únicos) |
| Correctas | **32** |
| Con inconsistencia | **18** |
| Con advertencias | 11 (no cambian la clasificación) |
| Monto sin contabilizar | $11.521.700 (4 facturas) |
| Monto con contabilización no en firme | $5.572.350 (3 facturas) |
| Diferencias de cálculo (IVA + total) | $106.500 |

| Fila | Factura | Causas |
|---|---|---|
| 5 | FAC-0004 | Duplicada |
| 7 | FAC-0006 | IVA mal calculado (reporta $215.000, esperado $190.000) |
| 8 | FAC-0007 | Sin registro contable |
| 10 | FAC-0009 | Total no cuadra (+$50.000) |
| 12 | FAC-0011 | Contabilización en estado Pendiente |
| 14 | FAC-0013 | Campo vacío: nit_proveedor |
| 16 | FAC-0015 | Duplicada |
| 19 | FAC-0018 | IVA mal calculado (reporta $645.500, esperado $655.500) |
| 22 | FAC-0021 | Sin registro contable |
| 24 | FAC-0023 | Total no cuadra (−$20.000) |
| 28 | FAC-0027 | Contabilización en estado Pendiente |
| 30 | FAC-0029 | Campo vacío: concepto |
| 35 | FAC-0034 | Sin registro contable |
| 37 | FAC-0036 | Total no cuadra (+$1.500) |
| 40 | FAC-0039 | Contabilización en estado Pendiente |
| 43 | FAC-0042 | Campo vacío: fecha_factura · Sin registro contable |
| 50 | FAC-0004 | Duplicada · Valor contabilizado diferente |
| 51 | FAC-0015 | Duplicada · Valor contabilizado diferente |

La prueba automatizada `backend/tests/test_muestra_real.py` verifica este resultado.

**Cómo cambia el resultado con otras interpretaciones** (calculado con el mismo código):

| Interpretación | Correctas | Con inconsistencia | Diferencia |
|---|---|---|---|
| **Implementada** (enunciado + reglas derivadas) | **32** | **18** | — |
| Solo las reglas explícitas del enunciado | 35 | 15 | FAC-0011, FAC-0027 y FAC-0039 (estado `Pendiente`) pasarían a correctas |
| Duplicado = solo la segunda ocurrencia | 34 | 16 | La primera ocurrencia de FAC-0004 y FAC-0015 pasaría a correcta |

Se mantiene `ESTADO_NO_CONTABILIZADO` como inconsistencia porque una factura cuyo registro contable está pendiente no está conciliada, y el caso menciona explícitamente las diferencias en *"estados de contabilización"*. Las demás reglas derivadas y adicionales no cambian el conteo con estos archivos.

## Supuestos

1. **El total se valida con el IVA y la retención esperados**, no con los reportados. Así, un IVA mal calculado aparece solo como `IVA_DIFERENTE` y no se arrastra como `TOTAL_DIFERENTE`. En la muestra, FAC-0006 y FAC-0018 tienen el total bien calculado y solo el IVA alterado.
2. **`id_factura` es la llave del cruce.** `contabilidad.csv` no tiene NIT, así que un mismo `id_factura` con NIT distinto (FAC-0004, FAC-0015) se trata como duplicado. Se marcan todas las ocurrencias porque no es posible saber cuál es la válida.
3. **Matiz contable:** en la práctica, la factura del proveedor no descuenta la retención; la practica el comprador al pagar. La fórmula de la prueba (`base + IVA − retención`) corresponde al **valor neto a pagar**. Se aplica tal como la define la prueba.
4. **Formato simplificado de contabilidad:** cada línea trae débito = crédito en la misma fila. El valor contabilizado de una factura es la suma de sus débitos. Una factura puede repartirse en varias líneas (por ejemplo, por centro de costo).
5. **Las líneas contables en 0** (FAC-0001 a FAC-0006 tienen una segunda línea sin valor) no afectan el valor contabilizado, por lo que se reportan como advertencia.
6. **Tarifas:** se aceptan como fracción (`0.19`), número (`19`) o porcentaje (`19%`). Un valor mayor que 1 se interpreta como porcentaje.
7. **Tolerancia de ±$1** para absorber redondeos al peso. Una tolerancia porcentual ocultaría diferencias reales: la menor de la muestra es de $1.500.
8. **Estados válidos:** `Contabilizada` o `Contabilizado`, sin distinguir mayúsculas. Cualquier otro estado se considera no en firme.
9. **Montos con `Decimal`**, nunca `float`: con `float`, 11 de las 50 facturas fallan una comparación exacta por errores de redondeo binario.
10. **Archivos aceptados:** CSV en UTF-8 (con o sin BOM) o Windows-1252, separados por coma o punto y coma, con punto decimal. Las columnas adicionales se ignoran.
11. **`ESTADO_NO_CONTABILIZADO` es una regla derivada del caso**, no una de las 5 reglas explícitas; su efecto en el resultado está en la tabla anterior.
12. **El resultado 50/32/18 es el de esta solución**, no un resultado oficial entregado por la empresa.

## Decisiones técnicas

Registradas como ADR (*Architecture Decision Records*) en [`docs/adr/`](docs/adr/):

| ADR | Decisión |
|---|---|
| [0001](docs/adr/0001-monorepo-y-trunk-based.md) | Monorepo y desarrollo trunk-based con Conventional Commits |
| [0002](docs/adr/0002-backend-fastapi-sin-persistencia.md) | FastAPI con capas `infra`/`domain`/`api`, sin capa de aplicación ni base de datos |
| [0003](docs/adr/0003-decimal-y-tolerancia.md) | Montos con `Decimal`, tolerancia de ±$1 y montos como texto en el JSON |
| [0004](docs/adr/0004-interpretacion-de-reglas.md) | Interpretación de las reglas ambiguas del enunciado |
| [0005](docs/adr/0005-frontend-signals-sin-libreria-ui.md) | Angular con signals, SCSS propio sin librería de componentes y proxy sin CORS |

## Funcionalidades no incluidas

Fuera del alcance de un prototipo de 4–5 horas; quedan como siguientes pasos:

- **Persistencia e histórico** de conciliaciones (hoy cada solicitud se procesa en memoria y se descarta).
- **Exportar resultados** a Excel o CSV.
- **Otras retenciones:** ReteIVA, ReteICA, bases mínimas en UVT y tarifas por concepto.
- **Validación del NIT** con dígito de verificación y consistencia entre cuenta contable (PUC) y concepto.
- **Asiento contable completo** (gasto, IVA descontable, retención por pagar, proveedores): el archivo de muestra trae una representación simplificada.
- **CSV con coma decimal** (`1.234,56`): se aceptan `,` y `;` como separadores, pero solo punto decimal.
- **Paginación** en la tabla y procesamiento de archivos grandes en segundo plano.
- **Autenticación y autorización**, HTTPS y despliegue en un entorno real.

## Uso de inteligencia artificial

Se usó IA generativa. El detalle de en qué partes y con qué propósito está en [`docs/declaracion-ia.md`](docs/declaracion-ia.md).

## Estructura del repositorio

```
.
├── backend/     API REST en Python (FastAPI)
├── frontend/    Aplicación web en Angular
├── data/        Archivos CSV de prueba (casos-borde/ para probar errores)
├── docs/        Decisiones (ADR), declaración de IA y presentación
├── .github/     Integración continua (GitHub Actions)
└── docker-compose.yml   Ejecución opcional con Docker
```

## Backend

### Ejecución

Desde la raíz del repositorio:

```bash
cd backend
python3 -m venv .venv                              # entorno aislado de dependencias
.venv/bin/pip install -r requirements-dev.txt     # dependencias con versiones fijas
.venv/bin/uvicorn app.main:app --port 8000         # inicia la API
```

> En Windows, reemplace `.venv/bin/` por `.venv\Scripts\`.

- API: http://localhost:8000/api
- Documentación interactiva (Swagger): http://localhost:8000/docs. Desde ahí se pueden cargar los archivos y probar el servicio sin el frontend.

Prueba rápida desde otra terminal, en la raíz del repositorio:

```bash
curl -F facturas=@data/facturas.csv -F contabilidad=@data/contabilidad.csv \
     http://localhost:8000/api/conciliaciones
```

Pruebas automatizadas y lint:

```bash
cd backend
.venv/bin/pytest            # 60 pruebas
.venv/bin/ruff check .      # lint
```

#### Dependencias

| Paquete | Versión | Uso |
|---|---|---|
| fastapi | 0.143.2 | Framework de la API REST |
| uvicorn | 0.54.0 | Servidor ASGI |
| python-multipart | 0.0.32 | Recepción de archivos (`multipart/form-data`) |
| pytest | 9.1.1 | Pruebas (solo desarrollo) |
| httpx2 | 2.13.1 | Cliente HTTP para las pruebas de la API (solo desarrollo) |
| ruff | 0.17.1 | Lint y formato (solo desarrollo) |

### API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/health` | Estado del servicio |
| `POST` | `/api/conciliaciones` | Recibe los dos CSV y devuelve el resultado de la conciliación |

#### `POST /api/conciliaciones`

**Solicitud:** `multipart/form-data` con dos archivos: `facturas` y `contabilidad`. El servicio no guarda nada: cada solicitud se procesa en memoria.

**Respuesta 200** (resumida):

```json
{
  "resumen": {
    "total_registros": 50,
    "facturas_unicas": 48,
    "correctas": 32,
    "con_inconsistencia": 18,
    "con_advertencias": 11,
    "registros_contables": 50,
    "por_causa": [
      { "codigo": "DUPLICADA", "etiqueta": "Factura duplicada", "tipo": "INCONSISTENCIA", "cantidad": 4 }
    ],
    "monto_sin_contabilizar": "11521700.00",
    "monto_no_en_firme": "5572350.00",
    "monto_diferencias_calculo": "106500.00"
  },
  "detalle": [
    {
      "fila": 7,
      "id_factura": "FAC-0006",
      "nit_proveedor": "900782207",
      "fecha_factura": "2026-03-07",
      "concepto": "Consultoría profesional",
      "base_gravable": "3800000.00",
      "tarifa_iva": "0.05",
      "valor_iva": "215000.00",
      "tarifa_retencion": "0",
      "valor_retencion": "0.00",
      "total_factura": "3990000.00",
      "estado": "CON_INCONSISTENCIA",
      "causas": [
        {
          "codigo": "IVA_DIFERENTE",
          "etiqueta": "IVA mal calculado",
          "tipo": "INCONSISTENCIA",
          "detalle": "IVA reportado $215.000; esperado $190.000 (base $3.800.000 × 5%).",
          "valor_reportado": "215000.00",
          "valor_esperado": "190000.00",
          "diferencia": "25000.00"
        }
      ],
      "advertencias": [
        { "codigo": "LINEA_CONTABLE_EN_CERO", "etiqueta": "Línea contable sin valor", "tipo": "ADVERTENCIA", "detalle": "Línea contable sin valor (fila 51, cuenta 512010, centro de costo CC1002).", "valor_reportado": null, "valor_esperado": null, "diferencia": null }
      ],
      "calculos": {
        "iva_esperado": "190000.00",
        "retencion_esperada": "0.00",
        "total_esperado": "3990000.00",
        "valor_contabilizado": "3990000.00"
      }
    }
  ],
  "registros_contables_sin_factura": [],
  "tolerancia": "1.00"
}
```

- `fila` es la línea del archivo original (el encabezado es la línea 1), para ubicar la factura en Excel.
- Los montos viajan como **texto** para no perder precisión en JSON.
- `por_causa` lista primero las inconsistencias y luego las advertencias.

#### Errores

Todos los errores tienen la misma forma, con el mensaje en español:

```json
{ "codigo": "COLUMNAS_FALTANTES", "mensaje": "Al archivo 'facturas.csv' le faltan columnas obligatorias: tarifa_iva.", "archivo": "facturas.csv" }
```

| HTTP | Código | Cuándo |
|---|---|---|
| 400 | `EXTENSION_INVALIDA` | El archivo no tiene extensión `.csv` |
| 400 | `ARCHIVO_VACIO` | El archivo está vacío o solo tiene encabezado |
| 400 | `COLUMNAS_FALTANTES` | Faltan columnas obligatorias (se listan) |
| 400 | `CODIFICACION_INVALIDA` | El archivo no está en UTF-8 ni Windows-1252 |
| 400 | `ARCHIVO_INVALIDO` | El contenido no es un CSV legible |
| 413 | `ARCHIVO_DEMASIADO_GRANDE` | El archivo supera 5 MB |
| 422 | `SOLICITUD_INVALIDA` | Falta alguno de los dos archivos |
| 500 | `ERROR_INTERNO` | Error inesperado (el detalle técnico queda solo en el log del servidor) |

Los datos inválidos en **filas individuales** (montos en letras, fechas mal escritas) no rechazan el archivo: esas facturas se marcan con `VALOR_INVALIDO` o `CAMPO_VACIO` y el resto se procesa. En `data/casos-borde/` hay archivos para probar cada caso.

#### Seguridad

- Sin base de datos ni almacenamiento: los archivos se procesan en memoria y se descartan.
- Límite de 5 MB por archivo y validación de extensión y estructura.
- Cabeceras `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`; en `/api/*` también `Cache-Control: no-store` (información financiera) y `Content-Security-Policy`.
- El log registra solo conteos, nunca datos de facturas o proveedores. Los errores inesperados no exponen trazas al cliente.

## Frontend

### Ejecución

Desde la raíz del repositorio, en otra terminal (con el backend corriendo en el puerto 8000):

```bash
cd frontend
npm ci          # instala las versiones exactas de package-lock.json
npm start       # http://localhost:4200
```

`npm start` usa `proxy.conf.json`: las llamadas a `/api` se reenvían a `http://localhost:8000`, así el navegador ve un solo origen y la API no necesita habilitar CORS.

Pruebas, lint y build:

```bash
cd frontend
npm test              # pruebas unitarias (Vitest)
npm run lint          # ESLint con reglas de accesibilidad de plantillas
npm run format:check  # formato (Prettier)
npm run build         # build de producción en dist/
```

#### Dependencias

| Paquete | Versión | Uso |
|---|---|---|
| Angular | 22.2 | Framework (componentes standalone, signals, sin zone.js) |
| @fontsource/nunito-sans | 5.3 | Tipografía libre instalada por npm (sin CDN: el build funciona sin conexión) |
| Vitest + jsdom | 4.1 / 28 | Pruebas unitarias (solo desarrollo) |
| angular-eslint | 22.6 | Lint de TypeScript y plantillas (solo desarrollo) |
| Prettier | 3.9 | Formato (solo desarrollo) |

No se usa una librería de componentes: los estilos son SCSS propio con tokens de diseño.

### Uso paso a paso

Con el backend (puerto 8000) y el frontend (puerto 4200) en ejecución:

1. Abra http://localhost:4200.
2. En **1. Cargar archivos**, seleccione `data/facturas.csv` y `data/contabilidad.csv`, con clic, teclado o arrastrándolos. El botón **Conciliar archivos** se habilita cuando están los dos.
3. Presione **Conciliar archivos**. Se muestra un indicador de carga y, al terminar, el foco pasa al resultado.
4. En **2. Resultado de la conciliación** se ven los indicadores (50 facturas: 32 correctas y 18 con inconsistencia), los montos afectados y el conteo por causa.
5. En **3. Detalle por factura**, filtre por estado (Todas / Correctas / Con inconsistencia), por causa o por texto (factura, NIT o concepto).
6. Presione **Ver detalle** en una factura para ver cada causa con el valor reportado, el esperado y la diferencia, sus advertencias y la tabla de cálculos (por ejemplo, FAC-0006: IVA reportado $215.000, esperado $190.000).
7. **4. Registros contables sin factura** lista los registros contables huérfanos (ninguno en la muestra).
8. Para probar errores, use los archivos de `data/casos-borde/`. Si el backend está detenido, la interfaz lo indica con un mensaje claro.

### Arquitectura

```
frontend/src/app/
├── core/
│   ├── layout/                     Encabezado y pie de página
│   ├── models/                     Interfaces del contrato de la API (copia de los schemas de Pydantic)
│   └── services/                   ConciliacionApiService (HttpClient) y traducción de errores
├── features/conciliacion/
│   ├── conciliacion.page.*         Contenedor: conecta el store con los componentes y gestiona el foco
│   ├── conciliacion.store.ts       Estado con signals: archivos, proceso, resultado, filtros y valores derivados
│   ├── carga-archivos/             Paso 1: selección de archivos
│   ├── resumen-conciliacion/       Paso 2: indicadores y distribución por causa
│   ├── filtros-resultados/         Filtros por estado, causa y búsqueda
│   ├── tabla-resultados/           Tabla en escritorio y tarjetas en móvil
│   └── detalle-factura/            Trazabilidad de una factura
└── shared/                         Componentes y pipes reutilizables (botón, selector, KPI, insignia, alerta, montos)
```

- **Contenedor y presentación:** solo la página conoce el store; los demás componentes reciben datos por `input()`/`model()` y emiten eventos por `output()`.
- **Estado con signals**, sin librerías: el store se provee en la página, así que el estado se descarta al salir de ella. Los filtros son `computed()` sobre el resultado.
- **Sin CORS:** la URL de la API es relativa (`/api/...`) y en desarrollo la resuelve `proxy.conf.json`.
- **Pruebas:** unitarias de componentes, servicio y store, y una prueba de integración de la página que usa la respuesta real del backend (`src/testing/respuesta-muestra.json`), para verificar que lo procesado coincide con lo mostrado.

### Diseño y accesibilidad

**Identidad visual** (inspirada, no oficial): amarillo como acento, gris carbón para texto y encabezados, fondos blancos y grises claros, bordes redondeados y espacio generoso. Sin logo ni tipografía propietaria. Los tokens están en `frontend/src/styles/_tokens.scss`.

**Mobile first:** los estilos base son para pantallas pequeñas y se amplían desde 640 px y 1024 px. Verificado en 320 px, 375 px y escritorio.

**Accesibilidad (objetivo WCAG 2.2 AA):**

- **Contraste verificado** en todos los pares de colores (texto ≥ 4,5:1, bordes de controles ≥ 3:1). El amarillo solo se usa como fondo con texto oscuro (11,3:1); nunca como texto sobre blanco (1,46:1).
- **El estado nunca se comunica solo con color:** verde + ícono + "Correcta", rojo + ícono + "Con inconsistencia", naranja + ícono para advertencias. La advertencia es naranja, no ámbar, para no confundirse con el amarillo de marca.
- **Teclado:** enlace "Saltar al contenido", foco visible en todos los controles (contorno oscuro con separación blanca, visible sobre blanco y sobre amarillo) y foco devuelto al campo al quitar un archivo.
- **Lectores de pantalla:** `lang="es"`, regiones `header`/`main`/`footer`, un solo `h1`, campos de archivo nativos con etiqueta y descripción asociadas, `aria-invalid` en errores, errores anunciados con `role="alert"` y estados de carga con `role="status"`. Los íconos son decorativos (`aria-hidden`) porque siempre van con texto.
- **Objetivos táctiles** de al menos 44 × 44 px, tamaños en `rem` (respeta el tamaño de letra del usuario), cifras con `tabular-nums`, soporte de `prefers-reduced-motion` y de modo de alto contraste (`forced-colors`).
- **Validación automática:** ESLint con `templateAccessibility` de angular-eslint y pruebas unitarias que verifican roles, etiquetas y textos de estado.

## Docker (opcional)

La forma oficial de ejecutar la solución es la del [Inicio rápido](#inicio-rápido). Docker es una alternativa que levanta todo con un solo comando y sirve el frontend compilado para producción.

```bash
docker compose up --build      # http://localhost:8080
docker compose down            # detiene y elimina los contenedores
```

| Servicio | Imagen base | Qué hace |
|---|---|---|
| `backend` | `python:3.14-slim` | API FastAPI. Corre sin root, con *healthcheck* sobre `/api/health`. No expone puertos al exterior. |
| `frontend` | `node:24-alpine` (build) → `nginxinc/nginx-unprivileged:1.29-alpine` | nginx sirve Angular y reenvía `/api` al backend (mismo papel que `proxy.conf.json` en desarrollo). Escucha en el puerto 8080, sin root. |

El frontend espera a que el backend esté sano antes de arrancar.

**Requisito:** un motor de Docker con Compose v2 (Docker Desktop, Colima, Rancher Desktop u otro). Probado con Colima 0.10.3, Docker 29.5 y Compose 5.6 en macOS.

<details>
<summary>Instalación con Colima en macOS y solución de problemas</summary>

```bash
brew install colima docker docker-compose
colima start --cpu 2 --memory 4
```

- **`docker: 'compose' is not a docker command`**: el plugin de Homebrew debe registrarse en `~/.docker/config.json`:
  ```json
  { "cliPluginsExtraDirs": ["/opt/homebrew/lib/docker/cli-plugins"] }
  ```
- **`Cannot connect to the Docker daemon`**: la máquina virtual no está corriendo; ejecute `colima start` (verifique con `colima status`).
- **El puerto 8080 está ocupado**: cambie `'8080:8080'` por `'8081:8080'` en `docker-compose.yml` y abra http://localhost:8081.
- **Al terminar**: `colima stop` libera la memoria de la máquina virtual.

</details>

## Integración continua

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) se ejecuta en GitHub Actions en cada *push* o *pull request* a `main`:

| Trabajo | Pasos |
|---|---|
| Backend (Python 3.12 y 3.14) | `ruff check`, `ruff format --check`, `pytest` |
| Frontend (Node 24) | `npm ci`, `lint`, `format:check`, `test`, `build` |

Python 3.12 es la versión mínima declarada; 3.14 es la de desarrollo. Los pasos se verificaron en local (incluido Python 3.13). El workflow se ejecutará en GitHub cuando el repositorio se publique.

## Control de versiones

- Desarrollo **trunk-based** sobre `main` con commits pequeños según [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/) (`feat`, `fix`, `test`, `docs`, `refactor`, `build`, `chore`).
- Versiones etiquetadas: **`v1.0.0`** (entrega base) y **`v1.1.0`** (Docker y CI opcionales); los cambios están en [`CHANGELOG.md`](CHANGELOG.md).
- Se eligió trunk-based en lugar de GitFlow porque es un proyecto de un solo desarrollador y la prueba no exige un flujo de ramas (ver [ADR 0001](docs/adr/0001-monorepo-y-trunk-based.md)).
