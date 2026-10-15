"""Pruebas de la API HTTP con el cliente de pruebas de FastAPI (sin levantar servidor)."""

import pytest
from fastapi.testclient import TestClient

from app.api import routes
from app.main import app

from .conftest import DATA, ENCABEZADO_FACTURAS

client = TestClient(app)

FACTURAS = (DATA / "facturas.csv").read_bytes()
CONTABILIDAD = (DATA / "contabilidad.csv").read_bytes()


def enviar(facturas=("facturas.csv", FACTURAS), contabilidad=("contabilidad.csv", CONTABILIDAD)):
    archivos = {}
    if facturas:
        archivos["facturas"] = (facturas[0], facturas[1], "text/csv")
    if contabilidad:
        archivos["contabilidad"] = (contabilidad[0], contabilidad[1], "text/csv")
    return client.post("/api/conciliaciones", files=archivos)


def test_health():
    respuesta = client.get("/api/health")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_conciliacion_de_la_muestra():
    respuesta = enviar()
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()

    resumen = cuerpo["resumen"]
    assert resumen["total_registros"] == 50
    assert resumen["correctas"] == 32
    assert resumen["con_inconsistencia"] == 18
    assert resumen["monto_sin_contabilizar"] == "11521700.00"
    assert resumen["por_causa"][0] == {
        "codigo": "DUPLICADA",
        "etiqueta": "Factura duplicada",
        "tipo": "INCONSISTENCIA",
        "cantidad": 4,
    }
    # Las advertencias van después de todas las inconsistencias.
    tipos = [c["tipo"] for c in resumen["por_causa"]]
    assert tipos == sorted(tipos, key=lambda t: t == "ADVERTENCIA")
    assert len(cuerpo["detalle"]) == 50
    assert cuerpo["registros_contables_sin_factura"] == []
    assert cuerpo["tolerancia"] == "1.00"


def test_detalle_trae_valores_trazables():
    detalle = enviar().json()["detalle"]
    fac6 = next(d for d in detalle if d["id_factura"] == "FAC-0006")
    assert fac6["estado"] == "CON_INCONSISTENCIA"
    assert fac6["fecha_factura"] == "2026-03-07"
    assert fac6["tarifa_iva"] == "0.05"
    assert fac6["calculos"]["iva_esperado"] == "190000.00"
    assert fac6["causas"] == [
        {
            "codigo": "IVA_DIFERENTE",
            "etiqueta": "IVA mal calculado",
            "tipo": "INCONSISTENCIA",
            "detalle": "IVA reportado $215.000; esperado $190.000 (base $3.800.000 × 5%).",
            "valor_reportado": "215000.00",
            "valor_esperado": "190000.00",
            "diferencia": "25000.00",
        }
    ]
    assert fac6["advertencias"][0]["codigo"] == "LINEA_CONTABLE_EN_CERO"


def test_cabeceras_de_seguridad():
    respuesta = enviar()
    assert respuesta.headers["x-content-type-options"] == "nosniff"
    assert respuesta.headers["cache-control"] == "no-store"
    assert respuesta.headers["x-frame-options"] == "DENY"


@pytest.mark.parametrize(
    ("faltante", "kwargs"),
    [("contabilidad", {"contabilidad": None}), ("facturas", {"facturas": None})],
)
def test_falta_un_archivo(faltante, kwargs):
    respuesta = enviar(**kwargs)
    assert respuesta.status_code == 422
    assert respuesta.json() == {
        "codigo": "SOLICITUD_INVALIDA",
        "mensaje": f"Debe adjuntar el archivo de: {faltante}.",
        "archivo": None,
    }


def test_extension_invalida():
    respuesta = enviar(facturas=("facturas.txt", FACTURAS))
    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "codigo": "EXTENSION_INVALIDA",
        "mensaje": "El archivo 'facturas.txt' debe tener extensión .csv.",
        "archivo": "facturas.txt",
    }


def test_archivo_vacio():
    respuesta = enviar(contabilidad=("contabilidad.csv", b""))
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "ARCHIVO_VACIO"


def test_archivos_invertidos_indica_columnas_faltantes():
    respuesta = enviar(
        facturas=("contabilidad.csv", CONTABILIDAD), contabilidad=("facturas.csv", FACTURAS)
    )
    assert respuesta.status_code == 400
    cuerpo = respuesta.json()
    assert cuerpo["codigo"] == "COLUMNAS_FALTANTES"
    assert cuerpo["archivo"] == "contabilidad.csv"
    assert "nit_proveedor" in cuerpo["mensaje"]


def test_excel_renombrado_como_csv():
    respuesta = enviar(facturas=("facturas.csv", b"PK\x03\x04" + b"\x00" * 50))
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "FORMATO_NO_CSV"


def test_archivo_demasiado_grande(monkeypatch):
    monkeypatch.setattr(routes, "TAMANO_MAXIMO_ARCHIVO_BYTES", 100)
    respuesta = enviar()
    assert respuesta.status_code == 413
    assert respuesta.json()["codigo"] == "ARCHIVO_DEMASIADO_GRANDE"


def test_filas_con_datos_malos_no_detienen_el_proceso():
    facturas = f"{ENCABEZADO_FACTURAS}\nFAC-1,900,2026-01-01,X,abc,0.19,1,0,0,1\n".encode()
    respuesta = enviar(facturas=("f.csv", facturas))
    assert respuesta.status_code == 200
    (detalle,) = respuesta.json()["detalle"]
    assert detalle["base_gravable"] is None
    assert {c["codigo"] for c in detalle["causas"]} == {"VALOR_INVALIDO", "SIN_CONTABILIZAR"}
    # Todos los registros contables de la muestra quedan sin factura asociada.
    assert len(respuesta.json()["registros_contables_sin_factura"]) == 50


def test_ruta_inexistente():
    respuesta = client.get("/api/no-existe")
    assert respuesta.status_code == 404
    assert respuesta.json()["mensaje"] == "El recurso solicitado no existe."


def test_error_inesperado_no_expone_detalles(monkeypatch):
    def fallar(*_):
        raise RuntimeError("detalle interno secreto")

    monkeypatch.setattr(routes, "conciliar", fallar)
    respuesta = TestClient(app, raise_server_exceptions=False).post(
        "/api/conciliaciones",
        files={"facturas": ("f.csv", FACTURAS), "contabilidad": ("c.csv", CONTABILIDAD)},
    )
    assert respuesta.status_code == 500
    assert respuesta.json()["codigo"] == "ERROR_INTERNO"
    assert "secreto" not in respuesta.text
