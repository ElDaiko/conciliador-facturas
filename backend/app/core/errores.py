"""Errores de negocio que la API traduce a respuestas HTTP."""


class ArchivoInvalidoError(Exception):
    """El archivo recibido no se puede procesar (formato, tamaño o estructura)."""

    def __init__(
        self,
        mensaje: str,
        *,
        codigo: str = "ARCHIVO_INVALIDO",
        archivo: str | None = None,
        status_code: int = 400,
    ) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
        self.archivo = archivo
        self.status_code = status_code
