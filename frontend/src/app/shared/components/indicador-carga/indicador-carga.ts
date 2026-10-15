import { ChangeDetectionStrategy, Component, input } from '@angular/core';

/**
 * Indicador de proceso en curso. El texto es visible (no solo la animación),
 * y role="status" hace que el lector de pantalla lo anuncie.
 */
@Component({
  selector: 'app-indicador-carga',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { role: 'status', class: 'carga' },
  template: `
    <span class="carga__circulo" aria-hidden="true"></span>
    <span>{{ mensaje() }}</span>
  `,
  styles: `
    :host {
      display: inline-flex;
      align-items: center;
      gap: var(--espacio-3);
      font-weight: var(--peso-semi);
    }
    .carga__circulo {
      width: 1.5rem;
      height: 1.5rem;
      border: 3px solid var(--color-borde);
      border-top-color: var(--color-texto);
      border-radius: 50%;
      animation: girar 0.8s linear infinite;
    }
    @keyframes girar {
      to {
        transform: rotate(360deg);
      }
    }
  `,
})
export class IndicadorCarga {
  readonly mensaje = input('Procesando…');
}
