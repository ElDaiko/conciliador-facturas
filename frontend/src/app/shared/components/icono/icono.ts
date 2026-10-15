import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

export type NombreIcono =
  'correcto' | 'error' | 'advertencia' | 'info' | 'subir' | 'archivo' | 'cerrar' | 'chevron';

// Trazos propios (24x24, estilo lineal). Sin librerías ni CDN.
const TRAZOS: Record<NombreIcono, string[]> = {
  correcto: ['M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z', 'm8 12 3 3 5-6'],
  error: ['M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z', 'M12 7.5v5.5', 'M12 16.5h.01'],
  advertencia: [
    'M10.3 4.2 2.6 17.5A2 2 0 0 0 4.3 20.5h15.4a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0Z',
    'M12 9.5V13',
    'M12 16.5h.01',
  ],
  info: ['M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z', 'M12 11v5.5', 'M12 7.5h.01'],
  subir: ['M12 15V4', 'm7 9 5-5 5 5', 'M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3'],
  archivo: [
    'M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8Z',
    'M14 3v5h5',
    'M9 13h6',
    'M9 17h6',
  ],
  cerrar: ['M6 6l12 12', 'M18 6 6 18'],
  chevron: ['m9 6 6 6-6 6'],
};

/**
 * Ícono decorativo: siempre acompaña a un texto visible, por eso se oculta
 * a los lectores de pantalla (aria-hidden).
 */
@Component({
  selector: 'app-icono',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { 'aria-hidden': 'true', class: 'icono' },
  template: `
    <svg
      viewBox="0 0 24 24"
      [attr.width]="tamano()"
      [attr.height]="tamano()"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      focusable="false"
    >
      @for (trazo of trazos(); track $index) {
        <path [attr.d]="trazo" />
      }
    </svg>
  `,
  styles: `
    :host {
      display: inline-flex;
      flex-shrink: 0;
    }
  `,
})
export class Icono {
  readonly nombre = input.required<NombreIcono>();
  readonly tamano = input(20);

  protected readonly trazos = computed(() => TRAZOS[this.nombre()]);
}
