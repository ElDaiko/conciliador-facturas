import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { Icono, NombreIcono } from '../icono/icono';

export type TonoKpi = 'neutro' | 'exito' | 'peligro' | 'advertencia';

const ICONO_POR_TONO: Record<TonoKpi, NombreIcono | null> = {
  neutro: null,
  exito: 'correcto',
  peligro: 'error',
  advertencia: 'advertencia',
};

/** Indicador del resumen: etiqueta, valor destacado y detalle opcional. */
@Component({
  selector: 'app-tarjeta-kpi',
  imports: [Icono],
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { '[class]': "'kpi kpi--' + tono()" },
  templateUrl: './tarjeta-kpi.html',
  styleUrl: './tarjeta-kpi.scss',
})
export class TarjetaKpi {
  readonly etiqueta = input.required<string>();
  readonly valor = input.required<string | number>();
  readonly detalle = input<string>();
  readonly tono = input<TonoKpi>('neutro');

  protected readonly icono = computed(() => ICONO_POR_TONO[this.tono()]);
}
