/**
 * Contrato de la API (copia de backend/app/api/schemas.py).
 * Las propiedades conservan el snake_case del JSON para que la correspondencia sea directa.
 * Los montos llegan como texto ("190000.00") para no perder precisión.
 */

export type Monto = string;

export type EstadoFactura = 'CORRECTA' | 'CON_INCONSISTENCIA';
export type TipoHallazgo = 'INCONSISTENCIA' | 'ADVERTENCIA';

export type CodigoCausa =
  | 'CAMPO_VACIO'
  | 'VALOR_INVALIDO'
  | 'IVA_DIFERENTE'
  | 'RETENCION_DIFERENTE'
  | 'TOTAL_DIFERENTE'
  | 'DUPLICADA'
  | 'SIN_CONTABILIZAR'
  | 'ESTADO_NO_CONTABILIZADO'
  | 'VALOR_CONTABLE_DIFERENTE'
  | 'PARTIDA_DESCUADRADA'
  | 'REGISTRO_CONTABLE_INCOMPLETO'
  | 'LINEA_CONTABLE_EN_CERO'
  | 'PERIODO_POSTERIOR'
  | 'FECHA_CONTABLE_ANTERIOR';

export interface Hallazgo {
  codigo: CodigoCausa;
  etiqueta: string;
  tipo: TipoHallazgo;
  detalle: string;
  valor_reportado: Monto | null;
  valor_esperado: Monto | null;
  diferencia: Monto | null;
}

export interface Calculos {
  iva_esperado: Monto | null;
  retencion_esperada: Monto | null;
  total_esperado: Monto | null;
  valor_contabilizado: Monto | null;
}

export interface ResultadoFactura {
  fila: number;
  id_factura: string;
  nit_proveedor: string;
  fecha_factura: string | null;
  concepto: string;
  base_gravable: Monto | null;
  tarifa_iva: string | null;
  valor_iva: Monto | null;
  tarifa_retencion: string | null;
  valor_retencion: Monto | null;
  total_factura: Monto | null;
  estado: EstadoFactura;
  causas: Hallazgo[];
  advertencias: Hallazgo[];
  calculos: Calculos;
}

export interface ConteoCausa {
  codigo: CodigoCausa;
  etiqueta: string;
  tipo: TipoHallazgo;
  cantidad: number;
}

export interface Resumen {
  total_registros: number;
  facturas_unicas: number;
  correctas: number;
  con_inconsistencia: number;
  con_advertencias: number;
  registros_contables: number;
  por_causa: ConteoCausa[];
  monto_sin_contabilizar: Monto;
  monto_no_en_firme: Monto;
  monto_diferencias_calculo: Monto;
}

export interface RegistroContable {
  fila: number;
  id_factura: string;
  fecha_contabilizacion: string | null;
  cuenta_contable: string;
  centro_costo: string;
  valor_debito: Monto | null;
  valor_credito: Monto | null;
  estado: string;
}

export interface ConciliacionRespuesta {
  resumen: Resumen;
  detalle: ResultadoFactura[];
  registros_contables_sin_factura: RegistroContable[];
  tolerancia: Monto;
}

export interface ErrorApi {
  codigo: string;
  mensaje: string;
  archivo: string | null;
}
