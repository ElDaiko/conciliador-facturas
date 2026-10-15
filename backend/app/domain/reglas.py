"""Reglas de negocio de la conciliación.

Cada regla es una función pura: recibe datos del dominio y devuelve los hallazgos
que encuentra. Así se pueden probar de forma aislada y su resultado es trazable.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from app.core.config import ESTADOS_CONTABILIZADOS, TOLERANCIA
from app.domain.causas import CodigoCausa, Hallazgo
from app.domain.modelos import Factura, RegistroContable


def multiplicar(base: Decimal | None, tarifa: Decimal | None) -> Decimal | None:
    if base is None or tarifa is None:
        return None
    return base * tarifa


def total_esperado(
    base: Decimal | None, iva_esperado: Decimal | None, retencion_esperada: Decimal | None
) -> Decimal | None:
    """Regla 2: total = base gravable + IVA − retención (con los valores calculados)."""
    if base is None or iva_esperado is None or retencion_esperada is None:
        return None
    return base + iva_esperado - retencion_esperada


def difiere(reportado: Decimal | None, esperado: Decimal | None) -> bool:
    if reportado is None or esperado is None:
        return False
    return abs(reportado - esperado) > TOLERANCIA


def validar_campos(factura: Factura) -> list[Hallazgo]:
    hallazgos = []
    if factura.campos_vacios:
        hallazgos.append(
            Hallazgo(CodigoCausa.CAMPO_VACIO, f"Campos vacíos: {', '.join(factura.campos_vacios)}.")
        )
    if factura.campos_invalidos:
        hallazgos.append(
            Hallazgo(
                CodigoCausa.VALOR_INVALIDO,
                f"Valores no válidos (no numéricos, negativos o fecha distinta a AAAA-MM-DD): "
                f"{', '.join(factura.campos_invalidos)}.",
            )
        )
    return hallazgos


def validar_iva(factura: Factura, iva_esperado: Decimal | None) -> list[Hallazgo]:
    """Regla 1: IVA esperado = base gravable × tarifa de IVA."""
    if not difiere(factura.valor_iva, iva_esperado):
        return []
    return [
        Hallazgo(
            CodigoCausa.IVA_DIFERENTE,
            f"IVA reportado {pesos(factura.valor_iva)}; esperado {pesos(iva_esperado)} "
            f"(base {pesos(factura.base_gravable)} × {porcentaje(factura.tarifa_iva)}).",
            factura.valor_iva,
            iva_esperado,
        )
    ]


def validar_retencion(factura: Factura, retencion_esperada: Decimal | None) -> list[Hallazgo]:
    if not difiere(factura.valor_retencion, retencion_esperada):
        return []
    return [
        Hallazgo(
            CodigoCausa.RETENCION_DIFERENTE,
            f"Retención reportada {pesos(factura.valor_retencion)}; esperada "
            f"{pesos(retencion_esperada)} "
            f"(base {pesos(factura.base_gravable)} × {porcentaje(factura.tarifa_retencion)}).",
            factura.valor_retencion,
            retencion_esperada,
        )
    ]


def validar_total(factura: Factura, total: Decimal | None) -> list[Hallazgo]:
    if not difiere(factura.total_factura, total):
        return []
    return [
        Hallazgo(
            CodigoCausa.TOTAL_DIFERENTE,
            f"Total reportado {pesos(factura.total_factura)}; esperado {pesos(total)} "
            f"(base + IVA − retención).",
            factura.total_factura,
            total,
        )
    ]


def validar_duplicado(factura: Factura, filas_mismo_id: list[int]) -> list[Hallazgo]:
    """Regla 3: id_factura es la llave del cruce, por lo que debe ser único."""
    if len(filas_mismo_id) < 2:
        return []
    filas = ", ".join(str(f) for f in filas_mismo_id)
    return [
        Hallazgo(
            CodigoCausa.DUPLICADA,
            f"El id {factura.id_factura} aparece {len(filas_mismo_id)} veces (filas {filas}).",
        )
    ]


@dataclass
class ResultadoContable:
    """Lo que encuentra la validación contable de una factura."""

    inconsistencias: list[Hallazgo] = field(default_factory=list)
    advertencias: list[Hallazgo] = field(default_factory=list)
    valor_contabilizado: Decimal | None = None


def validar_contabilidad(factura: Factura, registros: list[RegistroContable]) -> ResultadoContable:
    """Regla 3 (facturas sin registro contable) y estado/valores de la contabilización."""
    resultado = ResultadoContable()

    if not registros:
        resultado.inconsistencias.append(
            Hallazgo(
                CodigoCausa.SIN_CONTABILIZAR,
                f"No existe registro contable para {factura.id_factura}.",
            )
        )
        return resultado

    for r in registros:
        problemas = [f"{campo} vacío" for campo in r.campos_vacios] + list(r.campos_invalidos)
        if problemas:
            resultado.inconsistencias.append(
                Hallazgo(
                    CodigoCausa.REGISTRO_CONTABLE_INCOMPLETO,
                    f"Registro contable de la fila {r.fila} con problemas: {', '.join(problemas)}.",
                )
            )
        if r.estado and r.estado.lower() not in ESTADOS_CONTABILIZADOS:
            resultado.inconsistencias.append(
                Hallazgo(
                    CodigoCausa.ESTADO_NO_CONTABILIZADO,
                    f"Registro contable en estado '{r.estado}' (fila {r.fila}).",
                )
            )
        if r.valor_debito == 0 and r.valor_credito == 0:
            resultado.advertencias.append(
                Hallazgo(
                    CodigoCausa.LINEA_CONTABLE_EN_CERO,
                    f"Línea contable sin valor (fila {r.fila}, cuenta {r.cuenta_contable}, "
                    f"centro de costo {r.centro_costo}).",
                )
            )

    debitos = _sumar([r.valor_debito for r in registros])
    creditos = _sumar([r.valor_credito for r in registros])
    resultado.valor_contabilizado = debitos

    if difiere(debitos, factura.total_factura):
        resultado.inconsistencias.append(
            Hallazgo(
                CodigoCausa.VALOR_CONTABLE_DIFERENTE,
                f"Valor contabilizado {pesos(debitos)}; total de la factura "
                f"{pesos(factura.total_factura)}.",
                debitos,
                factura.total_factura,
            )
        )
    if difiere(debitos, creditos):
        resultado.inconsistencias.append(
            Hallazgo(
                CodigoCausa.PARTIDA_DESCUADRADA,
                f"Débitos {pesos(debitos)} y créditos {pesos(creditos)} no son iguales.",
                debitos,
                creditos,
            )
        )

    # Fechas distintas de contabilización (sin repetir) para no duplicar advertencias.
    fechas = sorted({r.fecha_contabilizacion for r in registros if r.fecha_contabilizacion})
    resultado.advertencias += _validar_fechas(factura.fecha_factura, fechas)
    return resultado


def _validar_fechas(fecha_factura: date | None, fechas_contables: list[date]) -> list[Hallazgo]:
    if fecha_factura is None:
        return []
    hallazgos = []
    for fecha in fechas_contables:
        if fecha < fecha_factura:
            hallazgos.append(
                Hallazgo(
                    CodigoCausa.FECHA_CONTABLE_ANTERIOR,
                    f"Contabilizada el {fecha.isoformat()}, antes de la fecha de la factura "
                    f"({fecha_factura.isoformat()}).",
                )
            )
        elif (fecha.year, fecha.month) > (fecha_factura.year, fecha_factura.month):
            hallazgos.append(
                Hallazgo(
                    CodigoCausa.PERIODO_POSTERIOR,
                    f"Factura de {fecha_factura:%Y-%m} contabilizada en {fecha:%Y-%m} "
                    f"(revisar corte contable).",
                )
            )
    return hallazgos


def _sumar(valores: list[Decimal | None]) -> Decimal | None:
    """Suma solo si todos los valores existen; un valor faltante hace el total desconocido."""
    if None in valores:
        return None
    total = Decimal(0)
    for valor in valores:
        total += valor
    return total


def pesos(valor: Decimal | None) -> str:
    """Formato colombiano: $1.234.567 (decimales solo si existen). Ej.: 1500.5 -> $1.500,50"""
    if valor is None:
        return "N/D"
    redondeado = valor.quantize(Decimal("0.01"))
    # Python formatea en estilo inglés (1,234,567.89); se intercambian los separadores.
    ingles = f"{abs(redondeado):,.2f}"
    entero, decimales = ingles.split(".")
    texto = "$" + entero.replace(",", ".")
    if decimales != "00":
        texto += "," + decimales
    if redondeado < 0:
        texto = "-" + texto
    return texto


def porcentaje(tarifa: Decimal | None) -> str:
    """Convierte la fracción en porcentaje legible. Ej.: 0.025 -> 2,5%"""
    if tarifa is None:
        return "N/D"
    valor = (tarifa * 100).normalize()  # normalize() quita ceros sobrantes: 19.00 -> 19
    return f"{valor:f}".replace(".", ",") + "%"
