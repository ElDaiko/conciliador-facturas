import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  Injector,
  afterNextRender,
  effect,
  inject,
  viewChild,
} from '@angular/core';

import { Alerta } from '../../shared/components/alerta/alerta';
import { IndicadorCarga } from '../../shared/components/indicador-carga/indicador-carga';
import { MontoPipe } from '../../shared/pipes/monto.pipe';
import { CargaArchivos } from './carga-archivos/carga-archivos';
import { ConciliacionStore } from './conciliacion.store';
import { FiltrosResultados } from './filtros-resultados/filtros-resultados';
import { ResumenConciliacion } from './resumen-conciliacion/resumen-conciliacion';
import { TablaResultados } from './tabla-resultados/tabla-resultados';

/** Página contenedora: conecta el store con los componentes de presentación. */
@Component({
  selector: 'app-conciliacion-page',
  imports: [
    Alerta,
    IndicadorCarga,
    MontoPipe,
    CargaArchivos,
    FiltrosResultados,
    ResumenConciliacion,
    TablaResultados,
  ],
  providers: [ConciliacionStore],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './conciliacion.page.html',
  styleUrl: './conciliacion.page.scss',
})
export class ConciliacionPage {
  protected readonly store = inject(ConciliacionStore);
  private readonly injector = inject(Injector);
  private readonly tituloResultados = viewChild<ElementRef<HTMLElement>>('tituloResultados');
  private readonly alertaError = viewChild('alertaError', { read: ElementRef });

  constructor() {
    // Al terminar el proceso se mueve el foco al resultado (o al error) para que
    // quien usa teclado o lector de pantalla sepa que la pantalla cambió.
    effect(() => {
      const estado = this.store.estado();
      if (estado !== 'listo' && estado !== 'error') {
        return;
      }
      afterNextRender(
        () => {
          const destino = estado === 'listo' ? this.tituloResultados() : this.alertaError();
          destino?.nativeElement.focus();
        },
        { injector: this.injector },
      );
    });
  }
}
