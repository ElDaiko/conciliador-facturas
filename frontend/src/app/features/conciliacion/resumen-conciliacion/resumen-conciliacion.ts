import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { ConteoCausa, Monto, Resumen } from '../../../core/models/conciliacion.model';
import { TarjetaKpi } from '../../../shared/components/tarjeta-kpi/tarjeta-kpi';
import { MontoPipe } from '../../../shared/pipes/monto.pipe';
import { PorcentajePipe } from '../../../shared/pipes/porcentaje.pipe';

/** Paso 2: indicadores del resultado y distribución por causa. */
@Component({
  selector: 'app-resumen-conciliacion',
  imports: [TarjetaKpi, MontoPipe, PorcentajePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './resumen-conciliacion.html',
  styleUrl: './resumen-conciliacion.scss',
})
export class ResumenConciliacion {
  readonly resumen = input.required<Resumen>();
  readonly tolerancia = input.required<Monto>();

  protected readonly fraccionCorrectas = computed(() =>
    fraccion(this.resumen().correctas, this.resumen().total_registros),
  );
  protected readonly fraccionInconsistentes = computed(() =>
    fraccion(this.resumen().con_inconsistencia, this.resumen().total_registros),
  );
  protected readonly inconsistencias = computed(() =>
    this.resumen().por_causa.filter((c) => c.tipo === 'INCONSISTENCIA'),
  );
  protected readonly advertencias = computed(() =>
    this.resumen().por_causa.filter((c) => c.tipo === 'ADVERTENCIA'),
  );

  /** Ancho de la barra de cada causa, relativo al total de facturas. */
  protected anchoBarra(causa: ConteoCausa): string {
    return `${fraccion(causa.cantidad, this.resumen().total_registros) * 100}%`;
  }
}

function fraccion(parte: number, total: number): number {
  return total ? parte / total : 0;
}
