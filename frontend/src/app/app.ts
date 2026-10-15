import { ChangeDetectionStrategy, Component, signal } from '@angular/core';

import { Encabezado } from './core/layout/encabezado';
import { PiePagina } from './core/layout/pie-pagina';
import { Alerta } from './shared/components/alerta/alerta';
import { Boton } from './shared/components/boton/boton';
import { IndicadorCarga } from './shared/components/indicador-carga/indicador-carga';
import { InsigniaEstado } from './shared/components/insignia-estado/insignia-estado';
import { SelectorArchivo } from './shared/components/selector-archivo/selector-archivo';
import { TarjetaKpi } from './shared/components/tarjeta-kpi/tarjeta-kpi';
import { MontoPipe } from './shared/pipes/monto.pipe';

@Component({
  selector: 'app-root',
  imports: [
    Encabezado,
    PiePagina,
    Alerta,
    Boton,
    IndicadorCarga,
    InsigniaEstado,
    SelectorArchivo,
    TarjetaKpi,
    MontoPipe,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  // Vitrina temporal de la fase 3; en la fase 4 se reemplaza por la página de conciliación.
  protected readonly facturas = signal<File | null>(null);
  protected readonly contabilidad = signal<File | null>(null);
}
