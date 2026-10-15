import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { Icono, NombreIcono } from '../icono/icono';

export type TipoInsignia = 'correcta' | 'inconsistencia' | 'advertencia';

const CONFIGURACION: Record<TipoInsignia, { icono: NombreIcono; texto: string }> = {
  correcta: { icono: 'correcto', texto: 'Correcta' },
  inconsistencia: { icono: 'error', texto: 'Con inconsistencia' },
  advertencia: { icono: 'advertencia', texto: 'Advertencia' },
};

/** Estado con color + ícono + texto: nunca se comunica solo con color. */
@Component({
  selector: 'app-insignia-estado',
  imports: [Icono],
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { '[class]': "'insignia insignia--' + tipo()" },
  template: `
    <app-icono [nombre]="config().icono" [tamano]="16" />
    <span>{{ texto() ?? config().texto }}</span>
  `,
  styles: `
    :host {
      display: inline-flex;
      align-items: center;
      gap: var(--espacio-1);
      padding: var(--espacio-1) var(--espacio-3);
      border-radius: var(--radio-pildora);
      font-size: var(--texto-sm);
      font-weight: var(--peso-negrita);
      white-space: nowrap;
    }
    :host(.insignia--correcta) {
      background: var(--color-exito-fondo);
      color: var(--color-exito);
    }
    :host(.insignia--inconsistencia) {
      background: var(--color-peligro-fondo);
      color: var(--color-peligro);
    }
    :host(.insignia--advertencia) {
      background: var(--color-advertencia-fondo);
      color: var(--color-advertencia);
    }
    @media (forced-colors: active) {
      :host {
        border: 1px solid CanvasText;
      }
    }
  `,
})
export class InsigniaEstado {
  readonly tipo = input.required<TipoInsignia>();
  /** Texto alternativo al predeterminado del tipo (por ejemplo, el nombre de una causa). */
  readonly texto = input<string>();

  protected readonly config = computed(() => CONFIGURACION[this.tipo()]);
}
