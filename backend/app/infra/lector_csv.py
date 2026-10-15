"""Lectura defensiva de archivos CSV.

Convierte los bytes recibidos en una lista de filas (diccionarios de texto) y
valida la estructura mínima. No interpreta valores: eso le corresponde al dominio.
"""

import csv
import io
from dataclasses import dataclass

from app.core.errores import ArchivoInvalidoError

# utf-8-sig elimina el BOM que agrega Excel; cp1252 cubre CSV exportados en Windows en español.
CODIFICACIONES = ("utf-8-sig", "cp1252")
DELIMITADORES = ",;"


@dataclass(frozen=True)
class FilaCsv:
    numero: int  # Línea del archivo (el encabezado es la línea 1).
    valores: dict[str, str]


def leer_csv(
    contenido: bytes, nombre: str, columnas_obligatorias: tuple[str, ...]
) -> list[FilaCsv]:
    if not contenido.strip():
        raise ArchivoInvalidoError(
            f"El archivo '{nombre}' está vacío.", codigo="ARCHIVO_VACIO", archivo=nombre
        )

    texto = _decodificar(contenido, nombre)
    lector = csv.reader(io.StringIO(texto, newline=""), delimiter=_detectar_delimitador(texto))

    try:
        encabezado = next(lector)
    except (StopIteration, csv.Error) as exc:
        raise ArchivoInvalidoError(
            f"No fue posible leer el encabezado de '{nombre}'.", archivo=nombre
        ) from exc

    columnas = [_normalizar_columna(c) for c in encabezado]
    faltantes = [c for c in columnas_obligatorias if c not in columnas]
    if faltantes:
        raise ArchivoInvalidoError(
            f"Al archivo '{nombre}' le faltan columnas obligatorias: {', '.join(faltantes)}.",
            codigo="COLUMNAS_FALTANTES",
            archivo=nombre,
        )

    filas: list[FilaCsv] = []
    try:
        for valores in lector:
            if not any(v.strip() for v in valores):
                continue  # Líneas en blanco al final del archivo.
            fila: dict[str, str] = {}
            for posicion, columna in enumerate(columnas):
                if columna not in columnas_obligatorias:
                    continue  # Las columnas adicionales se ignoran.
                # Si la fila trae menos valores que el encabezado, lo faltante queda vacío.
                fila[columna] = valores[posicion].strip() if posicion < len(valores) else ""
            filas.append(FilaCsv(numero=lector.line_num, valores=fila))
    except csv.Error as exc:
        raise ArchivoInvalidoError(
            f"El archivo '{nombre}' tiene un formato CSV inválido (línea {lector.line_num}).",
            archivo=nombre,
        ) from exc

    if not filas:
        raise ArchivoInvalidoError(
            f"El archivo '{nombre}' no contiene registros.", codigo="ARCHIVO_VACIO", archivo=nombre
        )
    return filas


def _decodificar(contenido: bytes, nombre: str) -> str:
    for codificacion in CODIFICACIONES:
        try:
            return contenido.decode(codificacion)
        except UnicodeDecodeError:
            continue
    raise ArchivoInvalidoError(
        f"No fue posible leer '{nombre}': la codificación no es UTF-8 ni Windows-1252.",
        codigo="CODIFICACION_INVALIDA",
        archivo=nombre,
    )


def _detectar_delimitador(texto: str) -> str:
    primera_linea = texto.split("\n", 1)[0]
    try:
        return csv.Sniffer().sniff(primera_linea, delimiters=DELIMITADORES).delimiter
    except csv.Error:
        return ","


def _normalizar_columna(nombre: str) -> str:
    return nombre.strip().lower().replace(" ", "_")
