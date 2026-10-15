# Conciliador de facturas y retenciones

Prototipo web que cruza el archivo de **facturas de proveedores** con el de **registros contables**, aplica reglas contables y tributarias básicas y presenta un resumen y un detalle de las facturas correctas y de las que tienen inconsistencias, con la causa de cada una.

> Prueba técnica — Analista III, Gerencia de Evolución Contable y Tributaria.

## Contenido

- [Requisitos](#requisitos)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Reglas de negocio](#reglas-de-negocio)
- [Resultado esperado con los archivos de prueba](#resultado-esperado-con-los-archivos-de-prueba)
- [Supuestos](#supuestos)

## Requisitos

| Herramienta | Versión probada | Mínima |
|---|---|---|
| Python | 3.14.7 | 3.12 |
| Node.js | 24.19.0 | 22 LTS |
| npm | 11.17.0 | 10 |
| Git | 2.50 | — |

No se requiere base de datos, credenciales ni acceso a sistemas corporativos. Todos los datos son ficticios.

## Estructura del repositorio

```
.
├── backend/     API REST en Python (FastAPI)
├── frontend/    Aplicación web en Angular
├── data/        Archivos CSV de prueba
└── docs/        Reglas de negocio, decisiones (ADR), declaración de IA y presentación
```

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
