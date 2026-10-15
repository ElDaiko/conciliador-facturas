import { ChangeDetectionStrategy, Component, input, model, output } from '@angular/core';

import { Boton } from '../../../shared/components/boton/boton';
import { SelectorArchivo } from '../../../shared/components/selector-archivo/selector-archivo';

/** Paso 1: selección de los dos archivos y acción de conciliar. */
@Component({
  selector: 'app-carga-archivos',
  imports: [Boton, SelectorArchivo],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './carga-archivos.html',
  styleUrl: './carga-archivos.scss',
})
export class CargaArchivos {
  readonly facturas = model<File | null>(null);
  readonly contabilidad = model<File | null>(null);
  readonly cargando = input(false);
  readonly puedeConciliar = input(false);
  readonly mostrarLimpiar = input(false);

  readonly conciliar = output();
  readonly limpiar = output();
}
