from decimal import Decimal

import pytest

from app.domain.causas import CodigoCausa as C
from app.domain.conciliador import EstadoFactura
from app.domain.reglas import pesos, porcentaje

from .conftest import ENCABEZADO_CONTABILIDAD, ENCABEZADO_FACTURAS, conciliar_textos

FACTURA_OK = "FAC-1,900123456,2026-01-10,Servicio,1000000,0.19,190000,0.04,40000,1150000"
CONTABLE_OK = "FAC-1,2026-01-12,513595,CC1,1150000,1150000,Contabilizada"


def evaluar(facturas: list[str], contables: list[str]):
    return conciliar_textos(
        "\n".join([ENCABEZADO_FACTURAS, *facturas]),
        "\n".join([ENCABEZADO_CONTABILIDAD, *contables]),
    )


def causas(resultado, indice=0):
    return {h.codigo for h in resultado.detalle[indice].causas}


def advertencias(resultado, indice=0):
    return {h.codigo for h in resultado.detalle[indice].advertencias}


def test_factura_correcta():
    r = evaluar([FACTURA_OK], [CONTABLE_OK])
    d = r.detalle[0]
    assert d.estado is EstadoFactura.CORRECTA
    assert d.causas == []
    assert d.calculos.iva_esperado == Decimal("190000")
    assert d.calculos.retencion_esperada == Decimal("40000")
    assert d.calculos.total_esperado == Decimal("1150000")
    assert d.calculos.valor_contabilizado == Decimal("1150000")


def test_iva_diferente_no_arrastra_error_al_total():
    # El total está bien calculado con el IVA esperado; solo el valor_iva está mal.
    fila = "FAC-1,900123456,2026-01-10,Servicio,1000000,0.19,180000,0.04,40000,1150000"
    assert causas(evaluar([fila], [CONTABLE_OK])) == {C.IVA_DIFERENTE}


def test_total_diferente():
    fila = "FAC-1,900123456,2026-01-10,Servicio,1000000,0.19,190000,0.04,40000,1151500"
    r = evaluar([fila], ["FAC-1,2026-01-12,513595,CC1,1151500,1151500,Contabilizada"])
    (h,) = r.detalle[0].causas
    assert h.codigo is C.TOTAL_DIFERENTE
    assert h.diferencia == Decimal("1500")


def test_retencion_diferente():
    fila = "FAC-1,900123456,2026-01-10,Servicio,1000000,0.19,190000,0.04,25000,1150000"
    assert C.RETENCION_DIFERENTE in causas(evaluar([fila], [CONTABLE_OK]))


@pytest.mark.parametrize("total", ["1150001", "1149999"])
def test_tolerancia_de_un_peso(total):
    fila = f"FAC-1,900123456,2026-01-10,Servicio,1000000,0.19,190000,0.04,40000,{total}"
    contable = f"FAC-1,2026-01-12,513595,CC1,{total},{total},Contabilizada"
    assert causas(evaluar([fila], [contable])) == set()


@pytest.mark.parametrize("tarifa", ["0.19", "19", "19%"])
def test_tarifa_en_distintos_formatos(tarifa):
    fila = f"FAC-1,900123456,2026-01-10,Servicio,1000000,{tarifa},190000,0.04,40000,1150000"
    assert causas(evaluar([fila], [CONTABLE_OK])) == set()


def test_duplicada_marca_todas_las_ocurrencias():
    r = evaluar([FACTURA_OK, FACTURA_OK], [CONTABLE_OK])
    assert causas(r, 0) == {C.DUPLICADA}
    assert C.DUPLICADA in causas(r, 1)
    assert r.detalle[0].causas[0].detalle == "El id FAC-1 aparece 2 veces (filas 2, 3)."
    assert r.resumen.facturas_unicas == 1


def test_sin_contabilizar():
    r = evaluar([FACTURA_OK], ["FAC-9,2026-01-12,513595,CC1,1,1,Contabilizada"])
    assert causas(r) == {C.SIN_CONTABILIZAR}
    assert r.resumen.monto_sin_contabilizar == Decimal("1150000")
    assert [x.id_factura for x in r.registros_contables_sin_factura] == ["FAC-9"]


@pytest.mark.parametrize("estado", ["Pendiente", "Anulada", "Rechazada"])
def test_estado_no_contabilizado(estado):
    contable = f"FAC-1,2026-01-12,513595,CC1,1150000,1150000,{estado}"
    assert causas(evaluar([FACTURA_OK], [contable])) == {C.ESTADO_NO_CONTABILIZADO}


def test_estado_contabilizado_sin_importar_mayusculas():
    contable = "FAC-1,2026-01-12,513595,CC1,1150000,1150000,CONTABILIZADO"
    assert causas(evaluar([FACTURA_OK], [contable])) == set()


def test_factura_distribuida_en_varios_centros_de_costo_se_suma():
    contables = [
        "FAC-1,2026-01-12,513595,CC1,650000,650000,Contabilizada",
        "FAC-1,2026-01-12,513595,CC2,500000,500000,Contabilizada",
    ]
    r = evaluar([FACTURA_OK], contables)
    assert causas(r) == set()
    assert r.detalle[0].calculos.valor_contabilizado == Decimal("1150000")


def test_valor_contabilizado_diferente():
    contable = "FAC-1,2026-01-12,513595,CC1,1100000,1100000,Contabilizada"
    (h,) = evaluar([FACTURA_OK], [contable]).detalle[0].causas
    assert h.codigo is C.VALOR_CONTABLE_DIFERENTE
    assert h.diferencia == Decimal("-50000")


def test_partida_descuadrada():
    contable = "FAC-1,2026-01-12,513595,CC1,1150000,1000000,Contabilizada"
    assert causas(evaluar([FACTURA_OK], [contable])) == {C.PARTIDA_DESCUADRADA}


def test_campos_vacios_omiten_calculos_dependientes():
    fila = "FAC-1,,2026-01-10,Servicio,,0.19,190000,0.04,40000,1150000"
    r = evaluar([fila], [CONTABLE_OK])
    assert causas(r) == {C.CAMPO_VACIO}
    assert r.detalle[0].causas[0].detalle == "Campos vacíos: nit_proveedor, base_gravable."
    assert r.detalle[0].calculos.iva_esperado is None
    assert r.detalle[0].calculos.total_esperado is None


def test_valores_invalidos():
    fila = "FAC-1,900123456,10/01/2026,Servicio,abc,0.19,-5,0.04,40000,1150000"
    assert causas(evaluar([fila], [CONTABLE_OK])) == {C.VALOR_INVALIDO}


def test_factura_sin_id_no_se_cruza_ni_se_marca_duplicada():
    fila = ",900123456,2026-01-10,Servicio,1000000,0.19,190000,0.04,40000,1150000"
    r = evaluar([fila, fila], [CONTABLE_OK])
    assert causas(r, 0) == {C.CAMPO_VACIO}
    assert causas(r, 1) == {C.CAMPO_VACIO}


def test_registro_contable_incompleto():
    contable = "FAC-1,2026-01-12,,CC1,,1150000,Contabilizada"
    assert causas(evaluar([FACTURA_OK], [contable])) == {C.REGISTRO_CONTABLE_INCOMPLETO}


def test_advertencias_no_cambian_la_clasificacion():
    contables = [
        "FAC-1,2026-02-03,513595,CC1,1150000,1150000,Contabilizada",
        "FAC-1,2026-02-03,511010,CC2,0,0,Contabilizada",
    ]
    r = evaluar([FACTURA_OK], contables)
    assert r.detalle[0].estado is EstadoFactura.CORRECTA
    assert advertencias(r) == {C.LINEA_CONTABLE_EN_CERO, C.PERIODO_POSTERIOR}
    assert r.resumen.con_advertencias == 1


def test_fecha_contable_anterior_a_la_factura():
    contable = "FAC-1,2026-01-05,513595,CC1,1150000,1150000,Contabilizada"
    assert advertencias(evaluar([FACTURA_OK], [contable])) == {C.FECHA_CONTABLE_ANTERIOR}


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (Decimal("1234567"), "$1.234.567"),
        (Decimal("190000.00"), "$190.000"),
        (Decimal("1500.5"), "$1.500,50"),
        (Decimal("-25000"), "-$25.000"),
        (None, "N/D"),
    ],
)
def test_formato_pesos(valor, esperado):
    assert pesos(valor) == esperado


@pytest.mark.parametrize(
    ("tarifa", "esperado"),
    [(Decimal("0.19"), "19%"), (Decimal("0.025"), "2,5%"), (Decimal("0.0"), "0%")],
)
def test_formato_porcentaje(tarifa, esperado):
    assert porcentaje(tarifa) == esperado
