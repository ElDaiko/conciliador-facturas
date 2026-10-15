import { ChangeDetectionStrategy, Component, input, signal } from '@angular/core';

import { ResultadoFactura } from '../../../core/models/conciliacion.model';
import { Boton } from '../../../shared/components/boton/boton';
import { InsigniaEstado } from '../../../shared/components/insignia-estado/insignia-estado';
import { MontoPipe } from '../../../shared/pipes/monto.pipe';
import { DetalleFactura } from '../detalle-factura/detalle-factura';

/**
 * Tabla de resultados. En escritorio es una tabla; en pantallas pequeñas cada fila
 * se muestra como tarjeta (solo cambia el CSS, los roles ARIA conservan la semántica).
 */
@Component({
  selector: 'app-tabla-resultados',
  imports: [Boton, InsigniaEstado, MontoPipe, DetalleFactura],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './tabla-resultados.html',
  styleUrl: './tabla-resultados.scss',
})
export class TablaResultados {
  readonly filas = input.required<ResultadoFactura[]>();

  /** Filas con el detalle desplegado (por número de fila del archivo). */
  private readonly abiertas = signal<ReadonlySet<number>>(new Set());

  protected estaAbierta(fila: number): boolean {
    return this.abiertas().has(fila);
  }

  protected alternar(fila: number): void {
    this.abiertas.update((actuales) => {
      const nuevas = new Set(actuales);
      if (nuevas.has(fila)) {
        nuevas.delete(fila);
      } else {
        nuevas.add(fila);
      }
      return nuevas;
    });
  }

  protected etiquetasCausas(factura: ResultadoFactura): string {
    return [...new Set(factura.causas.map((c) => c.etiqueta))].join(' · ');
  }
}
