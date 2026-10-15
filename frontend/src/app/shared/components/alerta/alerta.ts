import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { Icono, NombreIcono } from '../icono/icono';

export type TonoAlerta = 'error' | 'exito' | 'advertencia' | 'info';

const ICONO_POR_TONO: Record<TonoAlerta, NombreIcono> = {
  error: 'error',
  exito: 'correcto',
  advertencia: 'advertencia',
  info: 'info',
};

/**
 * Mensaje destacado. Los errores usan role="alert" (el lector de pantalla los anuncia
 * de inmediato); los demás, role="status" (se anuncian sin interrumpir).
 */
@Component({
  selector: 'app-alerta',
  imports: [Icono],
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    '[class]': "'alerta alerta--' + tono()",
    '[attr.role]': "tono() === 'error' ? 'alert' : 'status'",
  },
  template: `
    <app-icono [nombre]="icono()" [tamano]="22" />
    <div class="alerta__contenido">
      @if (titulo()) {
        <p class="alerta__titulo">{{ titulo() }}</p>
      }
      <ng-content />
    </div>
  `,
  styles: `
    :host {
      display: flex;
      gap: var(--espacio-3);
      padding: var(--espacio-4);
      border-radius: var(--radio-md);
      border-left: 4px solid currentColor;
    }
    .alerta__contenido {
      color: var(--color-texto);
    }
    .alerta__titulo {
      font-weight: var(--peso-negrita);
    }
    :host(.alerta--error) {
      background: var(--color-peligro-fondo);
      color: var(--color-peligro);
    }
    :host(.alerta--exito) {
      background: var(--color-exito-fondo);
      color: var(--color-exito);
    }
    :host(.alerta--advertencia) {
      background: var(--color-advertencia-fondo);
      color: var(--color-advertencia);
    }
    :host(.alerta--info) {
      background: var(--color-info-fondo);
      color: var(--color-info);
    }
    @media (forced-colors: active) {
      :host {
        border: 1px solid CanvasText;
      }
    }
  `,
})
export class Alerta {
  readonly tono = input<TonoAlerta>('info');
  readonly titulo = input<string>();

  protected readonly icono = computed(() => ICONO_POR_TONO[this.tono()]);
}
