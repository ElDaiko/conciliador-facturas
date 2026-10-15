"""Parámetros de negocio y de la API.

Se centralizan aquí para que cualquier supuesto (tolerancia, estados válidos,
columnas obligatorias) sea visible y fácil de ajustar.
"""

from decimal import Decimal

# Diferencia máxima aceptada (en pesos) entre un valor reportado y su valor calculado.
# Absorbe redondeos al peso sin ocultar diferencias reales (la menor en la muestra es $1.500).
TOLERANCIA = Decimal("1")

# Precisión con la que se exponen los montos calculados.
PRECISION_MONTOS = Decimal("0.01")

TAMANO_MAXIMO_ARCHIVO_BYTES = 5 * 1024 * 1024  # 5 MB

COLUMNAS_FACTURAS = (
    "id_factura",
    "nit_proveedor",
    "fecha_factura",
    "concepto",
    "base_gravable",
    "tarifa_iva",
    "valor_iva",
    "tarifa_retencion",
    "valor_retencion",
    "total_factura",
)

COLUMNAS_CONTABILIDAD = (
    "id_factura",
    "fecha_contabilizacion",
    "cuenta_contable",
    "centro_costo",
    "valor_debito",
    "valor_credito",
    "estado",
)

# Estados que indican que el registro contable quedó en firme (comparación sin mayúsculas).
ESTADOS_CONTABILIZADOS = frozenset({"contabilizada", "contabilizado"})
