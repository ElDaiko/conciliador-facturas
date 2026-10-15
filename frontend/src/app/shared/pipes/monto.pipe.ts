import { Pipe, PipeTransform } from '@angular/core';

const FORMATO_PESOS = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

/**
 * Formatea montos en pesos colombianos: "11521700.00" → "$ 11.521.700".
 * La API envía los montos como texto para no perder precisión; se convierten
 * a número solo para mostrarlos.
 */
@Pipe({ name: 'monto' })
export class MontoPipe implements PipeTransform {
  transform(valor: string | number | null | undefined): string {
    if (valor === null || valor === undefined || valor === '') {
      return '—';
    }
    const numero = Number(valor);
    return Number.isFinite(numero) ? FORMATO_PESOS.format(numero) : '—';
  }
}
