import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { ResultadoFactura } from '../../../core/models/conciliacion.model';
import { InsigniaEstado } from '../../../shared/components/insignia-estado/insignia-estado';
import { MontoPipe } from '../../../shared/pipes/monto.pipe';
import { PorcentajePipe } from '../../../shared/pipes/porcentaje.pipe';

/** Trazabilidad de una factura: causas, advertencias y valores reportados frente a calculados. */
@Component({
  selector: 'app-detalle-factura',
  imports: [InsigniaEstado, MontoPipe, PorcentajePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './detalle-factura.html',
  styleUrl: './detalle-factura.scss',
})
export class DetalleFactura {
  readonly factura = input.required<ResultadoFactura>();
}
