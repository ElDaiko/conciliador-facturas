from pathlib import Path

import pytest

from app.core.config import COLUMNAS_CONTABILIDAD, COLUMNAS_FACTURAS
from app.domain.conciliador import ResultadoConciliacion, conciliar
from app.domain.modelos import factura_desde_fila, registro_desde_fila
from app.infra.lector_csv import leer_csv

DATA = Path(__file__).resolve().parents[2] / "data"

ENCABEZADO_FACTURAS = ",".join(COLUMNAS_FACTURAS)
ENCABEZADO_CONTABILIDAD = ",".join(COLUMNAS_CONTABILIDAD)


def conciliar_textos(facturas: str, contabilidad: str) -> ResultadoConciliacion:
    """Concilia dos CSV escritos como texto (con encabezado)."""
    f = leer_csv(facturas.encode(), "facturas.csv", COLUMNAS_FACTURAS)
    c = leer_csv(contabilidad.encode(), "contabilidad.csv", COLUMNAS_CONTABILIDAD)
    return conciliar(
        [factura_desde_fila(x.numero, x.valores) for x in f],
        [registro_desde_fila(x.numero, x.valores) for x in c],
    )


@pytest.fixture(scope="session")
def resultado_muestra() -> ResultadoConciliacion:
    f = leer_csv((DATA / "facturas.csv").read_bytes(), "facturas.csv", COLUMNAS_FACTURAS)
    c = leer_csv(
        (DATA / "contabilidad.csv").read_bytes(), "contabilidad.csv", COLUMNAS_CONTABILIDAD
    )
    return conciliar(
        [factura_desde_fila(x.numero, x.valores) for x in f],
        [registro_desde_fila(x.numero, x.valores) for x in c],
    )
