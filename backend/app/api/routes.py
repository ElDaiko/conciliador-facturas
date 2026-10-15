"""Endpoints HTTP.

La ruta solo coordina: lee los archivos, los convierte a objetos del dominio,
llama al conciliador y devuelve el resultado. No contiene reglas de negocio.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app import __version__
from app.api.schemas import ConciliacionRespuesta, ErrorRespuesta
from app.core.config import COLUMNAS_CONTABILIDAD, COLUMNAS_FACTURAS, TAMANO_MAXIMO_ARCHIVO_BYTES
from app.core.errores import ArchivoInvalidoError
from app.domain.conciliador import conciliar
from app.domain.modelos import factura_desde_fila, registro_desde_fila
from app.infra.lector_csv import leer_csv

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

RESPUESTAS_DE_ERROR = {
    400: {"model": ErrorRespuesta, "description": "Archivo inválido (extensión, vacío, columnas)"},
    413: {"model": ErrorRespuesta, "description": "Archivo demasiado grande"},
    422: {"model": ErrorRespuesta, "description": "Falta alguno de los archivos"},
}


@router.get("/health", tags=["sistema"], summary="Estado del servicio")
def health() -> dict[str, str]:
    return {"estado": "ok", "version": __version__}


@router.post(
    "/conciliaciones",
    tags=["conciliación"],
    summary="Concilia facturas contra registros contables",
    response_model=ConciliacionRespuesta,
    responses=RESPUESTAS_DE_ERROR,
)
def crear_conciliacion(
    facturas: Annotated[UploadFile, File(description="CSV de facturas de proveedores")],
    contabilidad: Annotated[UploadFile, File(description="CSV de registros contables")],
) -> ConciliacionRespuesta:
    filas_facturas = leer_csv(
        _leer_contenido(facturas, "facturas"), _nombre(facturas, "facturas"), COLUMNAS_FACTURAS
    )
    filas_contables = leer_csv(
        _leer_contenido(contabilidad, "contabilidad"),
        _nombre(contabilidad, "contabilidad"),
        COLUMNAS_CONTABILIDAD,
    )

    lista_facturas = [factura_desde_fila(f.numero, f.valores) for f in filas_facturas]
    lista_registros = [registro_desde_fila(f.numero, f.valores) for f in filas_contables]
    resultado = conciliar(lista_facturas, lista_registros)

    # Solo se registran conteos, nunca datos de facturas o proveedores.
    logger.info(
        "Conciliación: %s facturas, %s correctas, %s con inconsistencia",
        resultado.resumen.total_registros,
        resultado.resumen.correctas,
        resultado.resumen.con_inconsistencia,
    )
    return ConciliacionRespuesta.model_validate(resultado)


def _nombre(archivo: UploadFile, campo: str) -> str:
    return archivo.filename or campo


def _leer_contenido(archivo: UploadFile, campo: str) -> bytes:
    nombre = _nombre(archivo, campo)
    if not nombre.lower().endswith(".csv"):
        raise ArchivoInvalidoError(
            f"El archivo '{nombre}' debe tener extensión .csv.",
            codigo="EXTENSION_INVALIDA",
            archivo=nombre,
        )

    # Se lee un byte más del máximo: si llega a leerlo, el archivo es demasiado grande.
    contenido = archivo.file.read(TAMANO_MAXIMO_ARCHIVO_BYTES + 1)
    if len(contenido) > TAMANO_MAXIMO_ARCHIVO_BYTES:
        limite_mb = TAMANO_MAXIMO_ARCHIVO_BYTES // (1024 * 1024)
        raise ArchivoInvalidoError(
            f"El archivo '{nombre}' supera el tamaño máximo de {limite_mb} MB.",
            codigo="ARCHIVO_DEMASIADO_GRANDE",
            archivo=nombre,
            status_code=413,
        )
    return contenido
