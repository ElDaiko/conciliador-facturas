import { ChangeDetectionStrategy, Component } from '@angular/core';

import { Encabezado } from './core/layout/encabezado';
import { PiePagina } from './core/layout/pie-pagina';
import { ConciliacionPage } from './features/conciliacion/conciliacion.page';

@Component({
  selector: 'app-root',
  imports: [Encabezado, PiePagina, ConciliacionPage],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {}
