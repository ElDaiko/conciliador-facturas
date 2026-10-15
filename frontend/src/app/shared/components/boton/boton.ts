import { ChangeDetectionStrategy, Component, input } from '@angular/core';

export type VarianteBoton = 'primario' | 'secundario' | 'texto';

/**
 * Estilos de botón aplicados sobre el <button> nativo: se conserva la semántica,
 * el soporte de teclado y los estados (disabled) sin reimplementarlos.
 *
 * Uso: <button appBoton variante="primario" type="button">Procesar</button>
 */
@Component({
  // Selector de atributo intencional: se aplica sobre el <button> nativo.
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'button[appBoton]',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    class: 'boton',
    '[class.boton--primario]': "variante() === 'primario'",
    '[class.boton--secundario]': "variante() === 'secundario'",
    '[class.boton--texto]': "variante() === 'texto'",
    '[class.boton--bloque]': 'bloque()',
  },
  template: '<ng-content />',
  styleUrl: './boton.scss',
})
export class Boton {
  readonly variante = input<VarianteBoton>('primario');
  /** Ocupa todo el ancho disponible (útil en móvil). */
  readonly bloque = input(false);
}
