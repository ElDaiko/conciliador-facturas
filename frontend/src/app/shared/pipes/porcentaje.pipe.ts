import { Pipe, PipeTransform } from '@angular/core';

const FORMATO_PORCENTAJE = new Intl.NumberFormat('es-CO', {
  style: 'percent',
  maximumFractionDigits: 2,
});

/** Formatea una fracción como porcentaje: "0.025" → "2,5 %". */
@Pipe({ name: 'porcentaje' })
export class PorcentajePipe implements PipeTransform {
  transform(valor: string | number | null | undefined): string {
    if (valor === null || valor === undefined || valor === '') {
      return '—';
    }
    const numero = Number(valor);
    return Number.isFinite(numero) ? FORMATO_PORCENTAJE.format(numero) : '—';
  }
}
