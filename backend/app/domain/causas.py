"""Catálogo de causas de inconsistencia y advertencias.

Las inconsistencias clasifican la factura como "Con inconsistencia".
Las advertencias se informan para revisión pero no cambian la clasificación.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class TipoHallazgo(StrEnum):
    INCONSISTENCIA = "INCONSISTENCIA"
    ADVERTENCIA = "ADVERTENCIA"


class CodigoCausa(StrEnum):
    CAMPO_VACIO = "CAMPO_VACIO"
    VALOR_INVALIDO = "VALOR_INVALIDO"
    IVA_DIFERENTE = "IVA_DIFERENTE"
    RETENCION_DIFERENTE = "RETENCION_DIFERENTE"
    TOTAL_DIFERENTE = "TOTAL_DIFERENTE"
    DUPLICADA = "DUPLICADA"
    SIN_CONTABILIZAR = "SIN_CONTABILIZAR"
    ESTADO_NO_CONTABILIZADO = "ESTADO_NO_CONTABILIZADO"
    VALOR_CONTABLE_DIFERENTE = "VALOR_CONTABLE_DIFERENTE"
    PARTIDA_DESCUADRADA = "PARTIDA_DESCUADRADA"
    REGISTRO_CONTABLE_INCOMPLETO = "REGISTRO_CONTABLE_INCOMPLETO"
    # Advertencias
    LINEA_CONTABLE_EN_CERO = "LINEA_CONTABLE_EN_CERO"
    PERIODO_POSTERIOR = "PERIODO_POSTERIOR"
    FECHA_CONTABLE_ANTERIOR = "FECHA_CONTABLE_ANTERIOR"


# Etiqueta corta para la interfaz y tipo de hallazgo de cada código.
CATALOGO: dict[CodigoCausa, tuple[str, TipoHallazgo]] = {
    CodigoCausa.CAMPO_VACIO: ("Campo obligatorio vacío", TipoHallazgo.INCONSISTENCIA),
    CodigoCausa.VALOR_INVALIDO: ("Valor con formato inválido", TipoHallazgo.INCONSISTENCIA),
    CodigoCausa.IVA_DIFERENTE: ("IVA mal calculado", TipoHallazgo.INCONSISTENCIA),
    CodigoCausa.RETENCION_DIFERENTE: ("Retención mal calculada", TipoHallazgo.INCONSISTENCIA),
    CodigoCausa.TOTAL_DIFERENTE: ("Total no cuadra", TipoHallazgo.INCONSISTENCIA),
    CodigoCausa.DUPLICADA: ("Factura duplicada", TipoHallazgo.INCONSISTENCIA),
    CodigoCausa.SIN_CONTABILIZAR: ("Sin registro contable", TipoHallazgo.INCONSISTENCIA),
    CodigoCausa.ESTADO_NO_CONTABILIZADO: (
        "Contabilización no está en firme",
        TipoHallazgo.INCONSISTENCIA,
    ),
    CodigoCausa.VALOR_CONTABLE_DIFERENTE: (
        "Valor contabilizado diferente",
        TipoHallazgo.INCONSISTENCIA,
    ),
    CodigoCausa.PARTIDA_DESCUADRADA: ("Débitos y créditos no cuadran", TipoHallazgo.INCONSISTENCIA),
    CodigoCausa.REGISTRO_CONTABLE_INCOMPLETO: (
        "Registro contable incompleto",
        TipoHallazgo.INCONSISTENCIA,
    ),
    CodigoCausa.LINEA_CONTABLE_EN_CERO: ("Línea contable sin valor", TipoHallazgo.ADVERTENCIA),
    CodigoCausa.PERIODO_POSTERIOR: ("Contabilizada en periodo posterior", TipoHallazgo.ADVERTENCIA),
    CodigoCausa.FECHA_CONTABLE_ANTERIOR: (
        "Contabilizada antes de la fecha de factura",
        TipoHallazgo.ADVERTENCIA,
    ),
}


@dataclass(frozen=True)
class Hallazgo:
    """Una causa concreta detectada en una factura, con los valores que la explican."""

    codigo: CodigoCausa
    detalle: str
    valor_reportado: Decimal | None = None
    valor_esperado: Decimal | None = None

    @property
    def etiqueta(self) -> str:
        return CATALOGO[self.codigo][0]

    @property
    def tipo(self) -> TipoHallazgo:
        return CATALOGO[self.codigo][1]

    @property
    def diferencia(self) -> Decimal | None:
        if self.valor_reportado is None or self.valor_esperado is None:
            return None
        return self.valor_reportado - self.valor_esperado
