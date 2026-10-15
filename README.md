# Conciliador de facturas y retenciones

Prototipo web que cruza el archivo de **facturas de proveedores** con el de **registros contables**, aplica reglas contables y tributarias básicas y presenta un resumen y un detalle de las facturas correctas y de las que tienen inconsistencias, con la causa de cada una.

> Prueba técnica — Analista III, Gerencia de Evolución Contable y Tributaria.
>
> Prototipo con identidad visual inspirada en Bancolombia; no es un producto oficial.

## Contenido

- [Requisitos](#requisitos)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Ejecución del backend](#ejecución-del-backend)
- [API](#api)
- [Ejecución del frontend](#ejecución-del-frontend)
- [Diseño y accesibilidad](#diseño-y-accesibilidad)
- [Reglas de negocio](#reglas-de-negocio)
- [Resultado esperado con los archivos de prueba](#resultado-esperado-con-los-archivos-de-prueba)
- [Supuestos](#supuestos)

## Requisitos

| Herramienta | Versión probada | Mínima |
|---|---|---|
| Python | 3.14.7 | 3.12 |
| Node.js | 24.19.0 | 22 LTS |
| npm | 11.17.0 | 10 |
| Angular CLI | 22.2 (incluida en `devDependencies`, no requiere instalación global) | — |
| Git | 2.50 | — |

No se requiere base de datos, credenciales ni acceso a sistemas corporativos. Todos los datos son ficticios.

## Estructura del repositorio

```
.
├── backend/     API REST en Python (FastAPI)
├── frontend/    Aplicación web en Angular
├── data/        Archivos CSV de prueba (casos-borde/ para probar errores)
└── docs/        Reglas de negocio, decisiones (ADR), declaración de IA y presentación
```

## Ejecución del backend

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

### Dependencias del backend

| Paquete | Versión | Uso |
|---|---|---|
| fastapi | 0.143.2 | Framework de la API REST |
| uvicorn | 0.54.0 | Servidor ASGI |
| python-multipart | 0.0.32 | Recepción de archivos (`multipart/form-data`) |
| pytest | 9.1.1 | Pruebas (solo desarrollo) |
| httpx2 | 2.13.1 | Cliente HTTP para las pruebas de la API (solo desarrollo) |
| ruff | 0.17.1 | Lint y formato (solo desarrollo) |

## API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/health` | Estado del servicio |
| `POST` | `/api/conciliaciones` | Recibe los dos CSV y devuelve el resultado de la conciliación |

### `POST /api/conciliaciones`

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

### Errores

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

### Seguridad

- Sin base de datos ni almacenamiento: los archivos se procesan en memoria y se descartan.
- Límite de 5 MB por archivo y validación de extensión y estructura.
- Cabeceras `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`; en `/api/*` también `Cache-Control: no-store` (información financiera) y `Content-Security-Policy`.
- El log registra solo conteos, nunca datos de facturas o proveedores. Los errores inesperados no exponen trazas al cliente.

## Ejecución del frontend

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

### Dependencias del frontend

| Paquete | Versión | Uso |
|---|---|---|
| Angular | 22.2 | Framework (componentes standalone, signals, sin zone.js) |
| @fontsource/nunito-sans | 5.3 | Tipografía libre instalada por npm (sin CDN: el build funciona sin conexión) |
| Vitest + jsdom | 4.1 / 28 | Pruebas unitarias (solo desarrollo) |
| angular-eslint | 22.6 | Lint de TypeScript y plantillas (solo desarrollo) |
| Prettier | 3.9 | Formato (solo desarrollo) |

No se usa una librería de componentes: los estilos son SCSS propio con tokens de diseño.

## Diseño y accesibilidad

**Identidad visual** (inspirada, no oficial): amarillo como acento, gris carbón para texto y encabezados, fondos blancos y grises claros, bordes redondeados y espacio generoso. Sin logo ni tipografía propietaria. Los tokens están en `frontend/src/styles/_tokens.scss`.

**Mobile first:** los estilos base son para pantallas pequeñas y se amplían desde 640 px y 1024 px. Verificado en 320 px, 375 px y escritorio.

**Accesibilidad (objetivo WCAG 2.2 AA):**

- **Contraste verificado** en todos los pares de colores (texto ≥ 4,5:1, bordes de controles ≥ 3:1). El amarillo solo se usa como fondo con texto oscuro (11,3:1); nunca como texto sobre blanco (1,46:1).
- **El estado nunca se comunica solo con color:** verde + ícono + "Correcta", rojo + ícono + "Con inconsistencia", naranja + ícono para advertencias. La advertencia es naranja, no ámbar, para no confundirse con el amarillo de marca.
- **Teclado:** enlace "Saltar al contenido", foco visible en todos los controles (contorno oscuro con separación blanca, visible sobre blanco y sobre amarillo) y foco devuelto al campo al quitar un archivo.
- **Lectores de pantalla:** `lang="es"`, regiones `header`/`main`/`footer`, un solo `h1`, campos de archivo nativos con etiqueta y descripción asociadas, `aria-invalid` en errores, errores anunciados con `role="alert"` y estados de carga con `role="status"`. Los íconos son decorativos (`aria-hidden`) porque siempre van con texto.
- **Objetivos táctiles** de al menos 44 × 44 px, tamaños en `rem` (respeta el tamaño de letra del usuario), cifras con `tabular-nums`, soporte de `prefers-reduced-motion` y de modo de alto contraste (`forced-colors`).
- **Validación automática:** ESLint con `templateAccessibility` de angular-eslint y pruebas unitarias que verifican roles, etiquetas y textos de estado.

## Reglas de negocio

Cada factura se clasifica como **Correcta** o **Con inconsistencia**. Una factura puede tener varias causas a la vez, y cada causa muestra el valor reportado, el valor esperado y la diferencia.

| Código | Causa | Regla |
|---|---|---|
| `CAMPO_VACIO` | Campo obligatorio vacío | Cualquiera de los 10 campos mínimos está vacío. Los cálculos que dependen de un valor faltante se omiten. |
| `VALOR_INVALIDO` | Valor con formato inválido | Montos no numéricos o negativos, o fechas con formato distinto a `AAAA-MM-DD`. |
| `IVA_DIFERENTE` | IVA mal calculado | `valor_iva` ≠ `base_gravable × tarifa_iva` (regla 1). |
| `RETENCION_DIFERENTE` | Retención mal calculada | `valor_retencion` ≠ `base_gravable × tarifa_retencion`. |
| `TOTAL_DIFERENTE` | Total no cuadra | `total_factura` ≠ `base + IVA esperado − retención esperada` (regla 2). |
| `DUPLICADA` | Factura duplicada | El `id_factura` aparece más de una vez. Se marcan todas las ocurrencias (regla 3). |
| `SIN_CONTABILIZAR` | Sin registro contable | El `id_factura` no existe en contabilidad (regla 3). |
| `ESTADO_NO_CONTABILIZADO` | Contabilización no está en firme | El registro contable tiene un estado distinto a `Contabilizada` (por ejemplo, `Pendiente`). |
| `VALOR_CONTABLE_DIFERENTE` | Valor contabilizado diferente | La suma de débitos del `id_factura` ≠ `total_factura`. |
| `PARTIDA_DESCUADRADA` | Débitos y créditos no cuadran | La suma de débitos ≠ la suma de créditos del `id_factura`. |
| `REGISTRO_CONTABLE_INCOMPLETO` | Registro contable incompleto | El registro contable tiene campos vacíos o inválidos. |

**Advertencias** (se informan, pero no cambian la clasificación):

| Código | Advertencia | Regla |
|---|---|---|
| `LINEA_CONTABLE_EN_CERO` | Línea contable sin valor | Línea con débito y crédito en 0. |
| `PERIODO_POSTERIOR` | Contabilizada en periodo posterior | El mes de contabilización es posterior al de la factura (revisar corte). |
| `FECHA_CONTABLE_ANTERIOR` | Contabilizada antes de la fecha de factura | `fecha_contabilizacion` < `fecha_factura`. |

Se aplica una tolerancia de **±$1** en todas las comparaciones de valores.

## Resultado esperado con los archivos de prueba

Con `data/facturas.csv` y `data/contabilidad.csv`:

| Indicador | Valor |
|---|---|
| Registros de factura | **50** (48 `id_factura` únicos) |
| Correctas | **32** |
| Con inconsistencia | **18** |
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
