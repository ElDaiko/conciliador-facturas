import pytest

from app.core.config import COLUMNAS_FACTURAS
from app.core.errores import ArchivoInvalidoError
from app.infra.lector_csv import leer_csv

from .conftest import ENCABEZADO_FACTURAS

FILA = "FAC-1,900123456,2026-01-10,Consultoría,1000000,0.19,190000,0.04,40000,1150000"


def leer(contenido: bytes):
    return leer_csv(contenido, "facturas.csv", COLUMNAS_FACTURAS)


def test_bom_utf8_no_afecta_la_primera_columna():
    filas = leer(f"﻿{ENCABEZADO_FACTURAS}\n{FILA}".encode())
    assert filas[0].valores["id_factura"] == "FAC-1"
    assert filas[0].numero == 2


def test_codificacion_windows_1252():
    filas = leer(f"{ENCABEZADO_FACTURAS}\n{FILA}".encode("cp1252"))
    assert filas[0].valores["concepto"] == "Consultoría"


def test_separador_punto_y_coma():
    contenido = f"{ENCABEZADO_FACTURAS}\n{FILA}".replace(",", ";").encode()
    assert leer(contenido)[0].valores["total_factura"] == "1150000"


def test_encabezados_con_mayusculas_y_espacios():
    encabezado = ",".join(f" {c.upper()} " for c in COLUMNAS_FACTURAS)
    assert leer(f"{encabezado}\n{FILA}".encode())[0].valores["id_factura"] == "FAC-1"


def test_columnas_extra_se_ignoran_y_lineas_vacias_se_saltan():
    contenido = f"{ENCABEZADO_FACTURAS},extra\n{FILA},x\n\n,,,\n".encode()
    filas = leer(contenido)
    assert len(filas) == 1
    assert "extra" not in filas[0].valores


def test_fila_corta_completa_con_vacios():
    filas = leer(f"{ENCABEZADO_FACTURAS}\nFAC-1,900123456".encode())
    assert filas[0].valores["total_factura"] == ""


@pytest.mark.parametrize("contenido", [b"", b"  \n \n"])
def test_archivo_vacio(contenido):
    with pytest.raises(ArchivoInvalidoError) as exc:
        leer(contenido)
    assert exc.value.codigo == "ARCHIVO_VACIO"


def test_solo_encabezado():
    with pytest.raises(ArchivoInvalidoError, match="no contiene registros"):
        leer(ENCABEZADO_FACTURAS.encode())


def test_columnas_faltantes_se_listan():
    encabezado = ENCABEZADO_FACTURAS.replace("tarifa_iva,", "").replace(",total_factura", "")
    with pytest.raises(ArchivoInvalidoError) as exc:
        leer(f"{encabezado}\nx".encode())
    assert exc.value.codigo == "COLUMNAS_FALTANTES"
    assert exc.value.mensaje.endswith("tarifa_iva, total_factura.")
