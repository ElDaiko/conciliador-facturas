"""Orquesta las reglas sobre todas las facturas y arma el resumen."""

from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from app.domain import reglas
from app.domain.causas import CATALOGO, CodigoCausa, Hallazgo, TipoHallazgo
from app.domain.modelos import Factura, RegistroContable

CAUSAS_DE_CALCULO = frozenset(
    {CodigoCausa.IVA_DIFERENTE, CodigoCausa.RETENCION_DIFERENTE, CodigoCausa.TOTAL_DIFERENTE}
)


class EstadoFactura(StrEnum):
    CORRECTA = "CORRECTA"
    CON_INCONSISTENCIA = "CON_INCONSISTENCIA"


@dataclass(frozen=True)
class Calculos:
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
    causas: tuple[Hallazgo, ...]
    advertencias: tuple[Hallazgo, ...]
    calculos: Calculos


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
    por_causa: tuple[ConteoCausa, ...]
    monto_sin_contabilizar: Decimal
    monto_no_en_firme: Decimal
    monto_diferencias_calculo: Decimal


@dataclass(frozen=True)
class ResultadoConciliacion:
    resumen: Resumen
    detalle: tuple[ResultadoFactura, ...]
    registros_contables_sin_factura: tuple[RegistroContable, ...]


def conciliar(
    facturas: Sequence[Factura], registros: Sequence[RegistroContable]
) -> ResultadoConciliacion:
    filas_por_id: dict[str, list[int]] = defaultdict(list)
    for f in facturas:
        if f.id_factura:
            filas_por_id[f.id_factura].append(f.fila)

    registros_por_id: dict[str, list[RegistroContable]] = defaultdict(list)
    for r in registros:
        if r.id_factura:
            registros_por_id[r.id_factura].append(r)

    detalle = tuple(
        _evaluar_factura(f, filas_por_id.get(f.id_factura, []), registros_por_id) for f in facturas
    )
    sin_factura = tuple(r for r in registros if r.id_factura not in filas_por_id)
    return ResultadoConciliacion(
        resumen=_resumir(detalle, len(filas_por_id), len(registros)),
        detalle=detalle,
        registros_contables_sin_factura=sin_factura,
    )


def _evaluar_factura(
    f: Factura,
    filas_mismo_id: Sequence[int],
    registros_por_id: dict[str, list[RegistroContable]],
) -> ResultadoFactura:
    iva = reglas.multiplicar(f.base_gravable, f.tarifa_iva)
    retencion = reglas.multiplicar(f.base_gravable, f.tarifa_retencion)
    total = reglas.total_esperado(f.base_gravable, iva, retencion)

    causas = [
        *reglas.validar_campos(f),
        *reglas.validar_iva(f, iva),
        *reglas.validar_retencion(f, retencion),
        *reglas.validar_total(f, total),
        *reglas.validar_duplicado(f, filas_mismo_id),
    ]
    advertencias: list[Hallazgo] = []
    valor_contabilizado = None
    # Sin id no hay forma de cruzar con contabilidad; ya queda reportado como campo vacío.
    if f.id_factura:
        inconsistencias_contables, advertencias, valor_contabilizado = reglas.validar_contabilidad(
            f, registros_por_id.get(f.id_factura, [])
        )
        causas.extend(inconsistencias_contables)

    return ResultadoFactura(
        fila=f.fila,
        id_factura=f.id_factura,
        nit_proveedor=f.nit_proveedor,
        fecha_factura=f.fecha_factura,
        concepto=f.concepto,
        base_gravable=f.base_gravable,
        tarifa_iva=f.tarifa_iva,
        valor_iva=f.valor_iva,
        tarifa_retencion=f.tarifa_retencion,
        valor_retencion=f.valor_retencion,
        total_factura=f.total_factura,
        estado=EstadoFactura.CON_INCONSISTENCIA if causas else EstadoFactura.CORRECTA,
        causas=tuple(causas),
        advertencias=tuple(advertencias),
        calculos=Calculos(iva, retencion, total, valor_contabilizado),
    )


def _resumir(
    detalle: Sequence[ResultadoFactura], facturas_unicas: int, registros_contables: int
) -> Resumen:
    # Cada factura cuenta una vez por código, aunque tenga varios hallazgos del mismo tipo.
    conteo = Counter(
        codigo for r in detalle for codigo in {h.codigo for h in (*r.causas, *r.advertencias)}
    )
    orden = list(CATALOGO)
    por_causa = tuple(
        ConteoCausa(codigo, CATALOGO[codigo][0], CATALOGO[codigo][1], cantidad)
        for codigo, cantidad in sorted(conteo.items(), key=lambda c: (-c[1], orden.index(c[0])))
    )

    def total_con(codigo: CodigoCausa) -> Decimal:
        return sum(
            (
                r.total_factura
                for r in detalle
                if r.total_factura is not None and any(h.codigo == codigo for h in r.causas)
            ),
            Decimal(0),
        )

    diferencias = sum(
        (
            abs(h.diferencia)
            for r in detalle
            for h in r.causas
            if h.codigo in CAUSAS_DE_CALCULO and h.diferencia is not None
        ),
        Decimal(0),
    )
    con_inconsistencia = sum(1 for r in detalle if r.estado is EstadoFactura.CON_INCONSISTENCIA)
    return Resumen(
        total_registros=len(detalle),
        facturas_unicas=facturas_unicas,
        correctas=len(detalle) - con_inconsistencia,
        con_inconsistencia=con_inconsistencia,
        con_advertencias=sum(1 for r in detalle if r.advertencias),
        registros_contables=registros_contables,
        por_causa=por_causa,
        monto_sin_contabilizar=total_con(CodigoCausa.SIN_CONTABILIZAR),
        monto_no_en_firme=total_con(CodigoCausa.ESTADO_NO_CONTABILIZADO),
        monto_diferencias_calculo=diferencias,
    )
