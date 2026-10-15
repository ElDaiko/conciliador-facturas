"""Orquesta las reglas sobre todas las facturas y arma el resumen."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from app.domain import reglas
from app.domain.causas import CATALOGO, CodigoCausa, Hallazgo, TipoHallazgo
from app.domain.modelos import Factura, RegistroContable

# Causas cuya diferencia en pesos se suma en "diferencias de cálculo".
CAUSAS_DE_CALCULO = {
    CodigoCausa.IVA_DIFERENTE,
    CodigoCausa.RETENCION_DIFERENTE,
    CodigoCausa.TOTAL_DIFERENTE,
}


class EstadoFactura(StrEnum):
    CORRECTA = "CORRECTA"
    CON_INCONSISTENCIA = "CON_INCONSISTENCIA"


@dataclass(frozen=True)
class Calculos:
    """Valores calculados por el sistema, para mostrar junto a los reportados."""

    iva_esperado: Decimal | None
    retencion_esperada: Decimal | None
    total_esperado: Decimal | None
    valor_contabilizado: Decimal | None


@dataclass(frozen=True)
class ResultadoFactura:
    fila: int
    id_factura: str
    nit_proveedor: str
    fecha_factura: date | None
    concepto: str
    base_gravable: Decimal | None
    tarifa_iva: Decimal | None
    valor_iva: Decimal | None
    tarifa_retencion: Decimal | None
    valor_retencion: Decimal | None
    total_factura: Decimal | None
    estado: EstadoFactura
    causas: list[Hallazgo]
    advertencias: list[Hallazgo]
    calculos: Calculos

    def tiene_causa(self, codigo: CodigoCausa) -> bool:
        return any(causa.codigo == codigo for causa in self.causas)


@dataclass(frozen=True)
class ConteoCausa:
    codigo: CodigoCausa
    etiqueta: str
    tipo: TipoHallazgo
    cantidad: int


@dataclass(frozen=True)
class Resumen:
    total_registros: int
    facturas_unicas: int
    correctas: int
    con_inconsistencia: int
    con_advertencias: int
    registros_contables: int
    por_causa: list[ConteoCausa]
    monto_sin_contabilizar: Decimal
    monto_no_en_firme: Decimal
    monto_diferencias_calculo: Decimal


@dataclass(frozen=True)
class ResultadoConciliacion:
    resumen: Resumen
    detalle: list[ResultadoFactura]
    registros_contables_sin_factura: list[RegistroContable]


def conciliar(facturas: list[Factura], registros: list[RegistroContable]) -> ResultadoConciliacion:
    """Punto de entrada del dominio: evalúa cada factura y arma el resumen."""
    # Índice id_factura -> filas donde aparece (sirve para detectar duplicados).
    filas_por_id: dict[str, list[int]] = {}
    for factura in facturas:
        if factura.id_factura:
            filas_por_id.setdefault(factura.id_factura, []).append(factura.fila)

    # Índice id_factura -> registros contables (una factura puede tener varias líneas).
    registros_por_id: dict[str, list[RegistroContable]] = {}
    for registro in registros:
        if registro.id_factura:
            registros_por_id.setdefault(registro.id_factura, []).append(registro)

    detalle = []
    for factura in facturas:
        filas_mismo_id = filas_por_id.get(factura.id_factura, [])
        registros_factura = registros_por_id.get(factura.id_factura, [])
        detalle.append(_evaluar_factura(factura, filas_mismo_id, registros_factura))

    sin_factura = [r for r in registros if r.id_factura not in filas_por_id]

    return ResultadoConciliacion(
        resumen=_resumir(
            detalle, facturas_unicas=len(filas_por_id), total_contables=len(registros)
        ),
        detalle=detalle,
        registros_contables_sin_factura=sin_factura,
    )


def _evaluar_factura(
    factura: Factura, filas_mismo_id: list[int], registros: list[RegistroContable]
) -> ResultadoFactura:
    iva = reglas.multiplicar(factura.base_gravable, factura.tarifa_iva)
    retencion = reglas.multiplicar(factura.base_gravable, factura.tarifa_retencion)
    total = reglas.total_esperado(factura.base_gravable, iva, retencion)

    causas: list[Hallazgo] = []
    causas += reglas.validar_campos(factura)
    causas += reglas.validar_iva(factura, iva)
    causas += reglas.validar_retencion(factura, retencion)
    causas += reglas.validar_total(factura, total)
    causas += reglas.validar_duplicado(factura, filas_mismo_id)

    advertencias: list[Hallazgo] = []
    valor_contabilizado = None
    # Sin id no hay forma de cruzar con contabilidad; ya queda reportado como campo vacío.
    if factura.id_factura:
        contable = reglas.validar_contabilidad(factura, registros)
        causas += contable.inconsistencias
        advertencias += contable.advertencias
        valor_contabilizado = contable.valor_contabilizado

    if causas:
        estado = EstadoFactura.CON_INCONSISTENCIA
    else:
        estado = EstadoFactura.CORRECTA

    return ResultadoFactura(
        fila=factura.fila,
        id_factura=factura.id_factura,
        nit_proveedor=factura.nit_proveedor,
        fecha_factura=factura.fecha_factura,
        concepto=factura.concepto,
        base_gravable=factura.base_gravable,
        tarifa_iva=factura.tarifa_iva,
        valor_iva=factura.valor_iva,
        tarifa_retencion=factura.tarifa_retencion,
        valor_retencion=factura.valor_retencion,
        total_factura=factura.total_factura,
        estado=estado,
        causas=causas,
        advertencias=advertencias,
        calculos=Calculos(iva, retencion, total, valor_contabilizado),
    )


def _resumir(
    detalle: list[ResultadoFactura], facturas_unicas: int, total_contables: int
) -> Resumen:
    con_inconsistencia = 0
    con_advertencias = 0
    monto_sin_contabilizar = Decimal(0)
    monto_no_en_firme = Decimal(0)
    monto_diferencias = Decimal(0)
    cantidad_por_codigo: dict[CodigoCausa, int] = {}

    for resultado in detalle:
        if resultado.estado == EstadoFactura.CON_INCONSISTENCIA:
            con_inconsistencia += 1
        if resultado.advertencias:
            con_advertencias += 1

        # Una factura cuenta una sola vez por código, aunque tenga varios hallazgos iguales.
        codigos = {h.codigo for h in resultado.causas + resultado.advertencias}
        for codigo in codigos:
            cantidad_por_codigo[codigo] = cantidad_por_codigo.get(codigo, 0) + 1

        total = resultado.total_factura or Decimal(0)
        if resultado.tiene_causa(CodigoCausa.SIN_CONTABILIZAR):
            monto_sin_contabilizar += total
        if resultado.tiene_causa(CodigoCausa.ESTADO_NO_CONTABILIZADO):
            monto_no_en_firme += total

        for causa in resultado.causas:
            if causa.codigo in CAUSAS_DE_CALCULO and causa.diferencia is not None:
                monto_diferencias += abs(causa.diferencia)

    return Resumen(
        total_registros=len(detalle),
        facturas_unicas=facturas_unicas,
        correctas=len(detalle) - con_inconsistencia,
        con_inconsistencia=con_inconsistencia,
        con_advertencias=con_advertencias,
        registros_contables=total_contables,
        por_causa=_ordenar_conteo(cantidad_por_codigo),
        monto_sin_contabilizar=monto_sin_contabilizar,
        monto_no_en_firme=monto_no_en_firme,
        monto_diferencias_calculo=monto_diferencias,
    )


def _ordenar_conteo(cantidad_por_codigo: dict[CodigoCausa, int]) -> list[ConteoCausa]:
    """Ordena de mayor a menor cantidad; en empate, según el orden del catálogo."""
    orden_catalogo = list(CATALOGO)
    conteo = [
        ConteoCausa(codigo, CATALOGO[codigo][0], CATALOGO[codigo][1], cantidad)
        for codigo, cantidad in cantidad_por_codigo.items()
    ]
    conteo.sort(key=lambda c: (-c.cantidad, orden_catalogo.index(c.codigo)))
    return conteo
