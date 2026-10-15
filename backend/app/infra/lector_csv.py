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

# Primeros bytes ("firma") de formatos que suelen llegar renombrados como .csv.
FIRMAS_NO_CSV = (
    (b"PK\x03\x04", "un libro de Excel (.xlsx) o un archivo comprimido"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "un libro de Excel antiguo (.xls)"),
    (b"%PDF", "un documento PDF"),
)
BOM_UTF16 = (b"\xff\xfe", b"\xfe\xff")
SUGERENCIA_GUARDAR = "Ábralo en Excel y use 'Guardar como' → 'CSV UTF-8 (delimitado por comas)'."


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

    _validar_que_sea_texto(contenido, nombre)
    texto = _decodificar(contenido, nombre)
    # strict=True: una comilla sin cerrar genera error en vez de absorber el resto del archivo.
    lector = csv.reader(
        io.StringIO(texto, newline=""), delimiter=_detectar_delimitador(texto), strict=True
    )

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
    while True:
        # Línea donde empieza el registro: si tiene una comilla sin cerrar, el error se
        # detecta al final del archivo, pero el problema está aquí.
        linea_inicio = lector.line_num + 1
        try:
            valores = next(lector)
        except StopIteration:
            break
        except csv.Error as exc:
            raise ArchivoInvalidoError(
                f"El archivo '{nombre}' tiene un formato CSV inválido en la línea "
                f"{linea_inicio}. Revise si hay comillas sin cerrar.",
                archivo=nombre,
            ) from exc
        if not any(v.strip() for v in valores):
            continue  # Líneas en blanco al final del archivo.
        fila: dict[str, str] = {}
        for posicion, columna in enumerate(columnas):
            if columna not in columnas_obligatorias:
                continue  # Las columnas adicionales se ignoran.
            # Si la fila trae menos valores que el encabezado, lo faltante queda vacío.
            fila[columna] = valores[posicion].strip() if posicion < len(valores) else ""
        filas.append(FilaCsv(numero=lector.line_num, valores=fila))

    if not filas:
        raise ArchivoInvalidoError(
            f"El archivo '{nombre}' no contiene registros.", codigo="ARCHIVO_VACIO", archivo=nombre
        )
    return filas


def _validar_que_sea_texto(contenido: bytes, nombre: str) -> None:
    """Rechaza archivos binarios o dañados con un mensaje que explique qué hacer."""
    for firma, descripcion in FIRMAS_NO_CSV:
        if contenido.startswith(firma):
            raise ArchivoInvalidoError(
                f"El archivo '{nombre}' parece ser {descripcion}, no un CSV. {SUGERENCIA_GUARDAR}",
                codigo="FORMATO_NO_CSV",
                archivo=nombre,
            )
    if contenido.startswith(BOM_UTF16):
        raise ArchivoInvalidoError(
            f"El archivo '{nombre}' está en UTF-16 ('Texto Unicode' de Excel), que no se admite. "
            f"{SUGERENCIA_GUARDAR}",
            codigo="CODIFICACION_NO_SOPORTADA",
            archivo=nombre,
        )
    if b"\x00" in contenido:
        raise ArchivoInvalidoError(
            f"El archivo '{nombre}' contiene caracteres nulos: puede estar dañado o no ser un "
            "archivo de texto.",
            codigo="ARCHIVO_DANADO",
            archivo=nombre,
        )


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
