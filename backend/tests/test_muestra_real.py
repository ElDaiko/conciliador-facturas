"""Resultado esperado con los archivos de muestra entregados (data/)."""

from decimal import Decimal

from app.domain.causas import CodigoCausa as C
from app.domain.conciliador import EstadoFactura

INCONSISTENTES_ESPERADAS = {
    # (fila, id): causas
    (5, "FAC-0004"): {C.DUPLICADA},
    (7, "FAC-0006"): {C.IVA_DIFERENTE},
    (8, "FAC-0007"): {C.SIN_CONTABILIZAR},
    (10, "FAC-0009"): {C.TOTAL_DIFERENTE},
    (12, "FAC-0011"): {C.ESTADO_NO_CONTABILIZADO},
    (14, "FAC-0013"): {C.CAMPO_VACIO},
    (16, "FAC-0015"): {C.DUPLICADA},
    (19, "FAC-0018"): {C.IVA_DIFERENTE},
    (22, "FAC-0021"): {C.SIN_CONTABILIZAR},
    (24, "FAC-0023"): {C.TOTAL_DIFERENTE},
    (28, "FAC-0027"): {C.ESTADO_NO_CONTABILIZADO},
    (30, "FAC-0029"): {C.CAMPO_VACIO},
    (35, "FAC-0034"): {C.SIN_CONTABILIZAR},
    (37, "FAC-0036"): {C.TOTAL_DIFERENTE},
    (40, "FAC-0039"): {C.ESTADO_NO_CONTABILIZADO},
    (43, "FAC-0042"): {C.CAMPO_VACIO, C.SIN_CONTABILIZAR},
    (50, "FAC-0004"): {C.DUPLICADA, C.VALOR_CONTABLE_DIFERENTE},
    (51, "FAC-0015"): {C.DUPLICADA, C.VALOR_CONTABLE_DIFERENTE},
}


def test_resumen_general(resultado_muestra):
    r = resultado_muestra.resumen
    assert (r.total_registros, r.correctas, r.con_inconsistencia) == (50, 32, 18)
    assert r.facturas_unicas == 48
    assert r.registros_contables == 50
    assert resultado_muestra.registros_contables_sin_factura == ()


def test_cada_factura_tiene_las_causas_esperadas(resultado_muestra):
    obtenidas = {
        (d.fila, d.id_factura): {h.codigo for h in d.causas}
        for d in resultado_muestra.detalle
        if d.estado is EstadoFactura.CON_INCONSISTENCIA
    }
    assert obtenidas == INCONSISTENTES_ESPERADAS


def test_conteo_por_causa(resultado_muestra):
    conteo = {c.codigo: c.cantidad for c in resultado_muestra.resumen.por_causa}
    assert conteo == {
        C.DUPLICADA: 4,
        C.SIN_CONTABILIZAR: 4,
        C.TOTAL_DIFERENTE: 3,
        C.ESTADO_NO_CONTABILIZADO: 3,
        C.CAMPO_VACIO: 3,
        C.IVA_DIFERENTE: 2,
        C.VALOR_CONTABLE_DIFERENTE: 2,
        # Advertencias: no cambian la clasificación.
        C.LINEA_CONTABLE_EN_CERO: 7,
        C.PERIODO_POSTERIOR: 4,
        C.FECHA_CONTABLE_ANTERIOR: 1,
    }


def test_montos(resultado_muestra):
    r = resultado_muestra.resumen
    assert r.monto_sin_contabilizar == Decimal("11521700")
    assert r.monto_no_en_firme == Decimal("5572350")
    assert r.monto_diferencias_calculo == Decimal("106500")


def test_iva_mal_calculado_trae_valores_trazables(resultado_muestra):
    fac6 = next(d for d in resultado_muestra.detalle if d.id_factura == "FAC-0006")
    (hallazgo,) = fac6.causas
    assert hallazgo.valor_reportado == Decimal("215000")
    assert hallazgo.valor_esperado == Decimal("190000")
    assert hallazgo.diferencia == Decimal("25000")
    assert hallazgo.detalle == "IVA reportado $215.000; esperado $190.000 (base $3.800.000 × 5%)."
