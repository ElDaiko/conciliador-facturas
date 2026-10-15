"""Aplicación FastAPI: configuración, manejo de errores y cabeceras de seguridad.

Ejecutar: uvicorn app.main:app --port 8000   (documentación interactiva en /docs)
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api.routes import router
from app.api.schemas import ErrorRespuesta
from app.core.errores import ArchivoInvalidoError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Conciliador de facturas y retenciones",
    version=__version__,
    description=(
        "Cruza el archivo de facturas de proveedores con el de registros contables, "
        "valida IVA, retención, total, duplicados y estado de contabilización, "
        "y devuelve un resumen y el detalle por factura."
    ),
)
app.include_router(router)


def _error(status_code: int, codigo: str, mensaje: str, archivo: str | None = None) -> JSONResponse:
    cuerpo = ErrorRespuesta(codigo=codigo, mensaje=mensaje, archivo=archivo)
    return JSONResponse(status_code=status_code, content=cuerpo.model_dump())


@app.exception_handler(ArchivoInvalidoError)
async def manejar_archivo_invalido(_: Request, exc: ArchivoInvalidoError) -> JSONResponse:
    return _error(exc.status_code, exc.codigo, exc.mensaje, exc.archivo)


@app.exception_handler(RequestValidationError)
async def manejar_solicitud_invalida(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Traduce los errores de validación de FastAPI (en inglés) a un mensaje claro."""
    faltantes = [str(e["loc"][-1]) for e in exc.errors() if e.get("type") == "missing"]
    if faltantes:
        mensaje = f"Debe adjuntar el archivo de: {', '.join(faltantes)}."
    else:
        mensaje = (
            "La solicitud no es válida. Envíe los dos archivos CSV como multipart/form-data "
            "en los campos 'facturas' y 'contabilidad'."
        )
    return _error(422, "SOLICITUD_INVALIDA", mensaje)


@app.exception_handler(StarletteHTTPException)
async def manejar_error_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    mensajes = {404: "El recurso solicitado no existe.", 405: "Método HTTP no permitido."}
    mensaje = mensajes.get(exc.status_code, str(exc.detail))
    return _error(exc.status_code, f"HTTP_{exc.status_code}", mensaje)


@app.exception_handler(Exception)
async def manejar_error_inesperado(_: Request, exc: Exception) -> JSONResponse:
    # El detalle técnico queda en el log del servidor; al cliente no se le exponen trazas.
    logger.exception("Error inesperado", exc_info=exc)
    return _error(500, "ERROR_INTERNO", "Ocurrió un error inesperado al procesar los archivos.")


@app.middleware("http")
async def agregar_cabeceras_de_seguridad(request: Request, call_next):
    respuesta = await call_next(request)
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "DENY"
    respuesta.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api/"):
        # Las respuestas tienen información financiera: no se guardan en caché.
        respuesta.headers["Cache-Control"] = "no-store"
        respuesta.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return respuesta
