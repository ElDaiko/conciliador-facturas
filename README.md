# Conciliador de facturas y retenciones

Prototipo web que cruza el archivo de **facturas de proveedores** con el de **registros contables**, aplica reglas contables y tributarias básicas y presenta un resumen y un detalle de las facturas correctas y de las que tienen inconsistencias, con la causa de cada una.

> Prueba técnica — Analista III, Gerencia de Evolución Contable y Tributaria.

## Contenido

- [Requisitos](#requisitos)
- [Estructura del repositorio](#estructura-del-repositorio)

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
