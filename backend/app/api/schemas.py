"""Contrato JSON de la API (lo que recibe el frontend).

Los modelos se llenan directamente desde los objetos del dominio (`from_attributes=True`).
Los montos viajan como texto ("190000.00") para no perder precisión en JSON;
el frontend los convierte a número solo para mostrarlos.
"""

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer

from app.core.config import PRECISION_MONTOS, TOLERANCIA
from app.domain.causas import CodigoCausa, TipoHallazgo
from app.domain.conciliador import EstadoFactura

Monto = Annotated[
    Decimal,
    PlainSerializer(lambda valor: str(valor.quantize(PRECISION_MONTOS)), return_type=str),
]
Tarifa = Annotated[
    Decimal,
    PlainSerializer(lambda valor: f"{valor.normalize():f}", return_type=str),
]


class Esquema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HallazgoSchema(Esquema):
    codigo: CodigoCausa
    etiqueta: str
    tipo: TipoHallazgo
    detalle: str
    valor_reportado: Monto | None
    valor_esperado: Monto | None
    diferencia: Monto | None


class CalculosSchema(Esquema):
    iva_esperado: Monto | None
    retencion_esperada: Monto | None
    total_esperado: Monto | None
    valor_contabilizado: Monto | None


class ResultadoFacturaSchema(Esquema):
    fila: int
    id_factura: str
    nit_proveedor: str
    fecha_factura: date | None
    concepto: str
    base_gravable: Monto | None
    tarifa_iva: Tarifa | None
    valor_iva: Monto | None
    tarifa_retencion: Tarifa | None
    valor_retencion: Monto | None
    total_factura: Monto | None
    estado: EstadoFactura
    causas: list[HallazgoSchema]
    advertencias: list[HallazgoSchema]
    calculos: CalculosSchema


class ConteoCausaSchema(Esquema):
    codigo: CodigoCausa
    etiqueta: str
    tipo: TipoHallazgo
    cantidad: int


class ResumenSchema(Esquema):
    total_registros: int
    facturas_unicas: int
    correctas: int
    con_inconsistencia: int
    con_advertencias: int
    registros_contables: int
    por_causa: list[ConteoCausaSchema]
    monto_sin_contabilizar: Monto
    monto_no_en_firme: Monto
    monto_diferencias_calculo: Monto


class RegistroContableSchema(Esquema):
    fila: int
    id_factura: str
    fecha_contabilizacion: date | None
    cuenta_contable: str
    centro_costo: str
    valor_debito: Monto | None
    valor_credito: Monto | None
    estado: str


class ConciliacionRespuesta(Esquema):
    resumen: ResumenSchema
    detalle: list[ResultadoFacturaSchema]
    registros_contables_sin_factura: list[RegistroContableSchema]
    tolerancia: Monto = TOLERANCIA


class ErrorRespuesta(BaseModel):
    codigo: str
    mensaje: str
    archivo: str | None = None
