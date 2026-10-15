"""Entidades del dominio y conversión desde las filas del CSV.

Los montos se manejan con Decimal para evitar errores de redondeo binario:
con float, 11 de las 50 facturas de la muestra fallan una comparación exacta.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

CIEN = Decimal(100)


@dataclass(frozen=True)
class Factura:
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
    campos_vacios: tuple[str, ...] = ()
    campos_invalidos: tuple[str, ...] = ()


@dataclass(frozen=True)
class RegistroContable:
    fila: int
    id_factura: str
    fecha_contabilizacion: date | None
    cuenta_contable: str
    centro_costo: str
    valor_debito: Decimal | None
    valor_credito: Decimal | None
    estado: str
    campos_vacios: tuple[str, ...] = ()
    campos_invalidos: tuple[str, ...] = ()


class _Conversor:
    """Convierte los textos de una fila a tipos del dominio.

    Mientras convierte, va anotando qué campos venían vacíos o con formato inválido.
    Un valor que no se puede convertir queda como None.
    """

    def __init__(self, valores: dict[str, str]) -> None:
        self.valores = valores
        self.vacios: list[str] = []
        self.invalidos: list[str] = []

    def texto(self, campo: str) -> str:
        valor = self.valores.get(campo, "")
        if not valor:
            self.vacios.append(campo)
        return valor

    def monto(self, campo: str) -> Decimal | None:
        valor = self.texto(campo)
        if not valor:
            return None
        numero = _a_decimal(valor.replace("$", ""))
        if numero is None or numero < 0:
            self.invalidos.append(campo)
            return None
        return numero

    def tarifa(self, campo: str) -> Decimal | None:
        """Acepta 0.19, 19 o 19%; siempre devuelve la fracción (0.19)."""
        valor = self.texto(campo)
        if not valor:
            return None
        es_porcentaje = valor.endswith("%")
        numero = _a_decimal(valor.rstrip("%"))
        if numero is None or numero < 0:
            self.invalidos.append(campo)
            return None
        if es_porcentaje or numero > 1:
            numero = numero / CIEN
        if numero > 1:
            self.invalidos.append(campo)
            return None
        return numero

    def fecha(self, campo: str) -> date | None:
        valor = self.texto(campo)
        if not valor:
            return None
        try:
            return date.fromisoformat(valor)
        except ValueError:
            self.invalidos.append(campo)
            return None


def factura_desde_fila(numero: int, valores: dict[str, str]) -> Factura:
    c = _Conversor(valores)
    return Factura(
        fila=numero,
        id_factura=c.texto("id_factura"),
        nit_proveedor=c.texto("nit_proveedor"),
        fecha_factura=c.fecha("fecha_factura"),
        concepto=c.texto("concepto"),
        base_gravable=c.monto("base_gravable"),
        tarifa_iva=c.tarifa("tarifa_iva"),
        valor_iva=c.monto("valor_iva"),
        tarifa_retencion=c.tarifa("tarifa_retencion"),
        valor_retencion=c.monto("valor_retencion"),
        total_factura=c.monto("total_factura"),
        campos_vacios=tuple(c.vacios),
        campos_invalidos=tuple(c.invalidos),
    )


def registro_desde_fila(numero: int, valores: dict[str, str]) -> RegistroContable:
    c = _Conversor(valores)
    return RegistroContable(
        fila=numero,
        id_factura=c.texto("id_factura"),
        fecha_contabilizacion=c.fecha("fecha_contabilizacion"),
        cuenta_contable=c.texto("cuenta_contable"),
        centro_costo=c.texto("centro_costo"),
        valor_debito=c.monto("valor_debito"),
        valor_credito=c.monto("valor_credito"),
        estado=c.texto("estado"),
        campos_vacios=tuple(c.vacios),
        campos_invalidos=tuple(c.invalidos),
    )


def _a_decimal(texto: str) -> Decimal | None:
    try:
        numero = Decimal(texto.strip())
    except InvalidOperation:
        return None
    return numero if numero.is_finite() else None
