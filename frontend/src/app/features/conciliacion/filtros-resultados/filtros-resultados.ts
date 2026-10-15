import { ChangeDetectionStrategy, Component, computed, input, model, output } from '@angular/core';

import { ConteoCausa, Resumen } from '../../../core/models/conciliacion.model';
import { Boton } from '../../../shared/components/boton/boton';
import { FiltroCausa, FiltroEstado } from '../conciliacion.store';

interface OpcionEstado {
  valor: FiltroEstado;
  texto: string;
  cantidad: number;
}

/** Filtros de la tabla: estado (botones de opción), causa (lista) y búsqueda libre. */
@Component({
  selector: 'app-filtros-resultados',
  imports: [Boton],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './filtros-resultados.html',
  styleUrl: './filtros-resultados.scss',
})
export class FiltrosResultados {
  readonly estado = model<FiltroEstado>('TODAS');
  readonly causa = model<FiltroCausa>('TODAS');
  readonly busqueda = model('');
  readonly resumen = input.required<Resumen>();
  readonly limpiar = output();

  protected readonly opcionesEstado = computed<OpcionEstado[]>(() => [
    { valor: 'TODAS', texto: 'Todas', cantidad: this.resumen().total_registros },
    { valor: 'CORRECTA', texto: 'Correctas', cantidad: this.resumen().correctas },
    {
      valor: 'CON_INCONSISTENCIA',
      texto: 'Con inconsistencia',
      cantidad: this.resumen().con_inconsistencia,
    },
  ]);

  protected readonly causasInconsistencia = computed(() => this.filtrarPorTipo('INCONSISTENCIA'));
  protected readonly causasAdvertencia = computed(() => this.filtrarPorTipo('ADVERTENCIA'));

  protected readonly hayFiltros = computed(
    () => this.estado() !== 'TODAS' || this.causa() !== 'TODAS' || this.busqueda() !== '',
  );

  protected alCambiarCausa(evento: Event): void {
    this.causa.set((evento.target as HTMLSelectElement).value as FiltroCausa);
  }

  protected alBuscar(evento: Event): void {
    this.busqueda.set((evento.target as HTMLInputElement).value);
  }

  private filtrarPorTipo(tipo: ConteoCausa['tipo']): ConteoCausa[] {
    return this.resumen().por_causa.filter((c) => c.tipo === tipo);
  }
}
