import { ChangeDetectionStrategy, Component } from '@angular/core';

/**
 * Encabezado inspirado en el sitio de referencia: barra superior carbón y barra
 * principal blanca. El distintivo amarillo es propio (no es el logo del banco).
 */
@Component({
  selector: 'app-encabezado',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <header class="encabezado">
      <div class="encabezado__superior">
        <p class="encabezado__contenido encabezado__gerencia">
          Gerencia de Evolución Contable y Tributaria
        </p>
      </div>
      <div class="encabezado__principal">
        <div class="encabezado__contenido">
          <p class="encabezado__marca">
            <span class="encabezado__distintivo" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="18" height="18" focusable="false">
                <path
                  d="m6 12.5 4 4 8-9"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
            Conciliador de facturas
          </p>
        </div>
      </div>
    </header>
  `,
  styles: `
    @use 'mixins' as *;

    .encabezado__contenido {
      max-width: var(--ancho-contenido);
      margin-inline: auto;
      padding-inline: var(--espacio-4);

      @include desde(tablet) {
        padding-inline: var(--espacio-6);
      }
    }
    .encabezado__superior {
      background: var(--color-carbon);
      color: var(--color-sobre-carbon);
    }
    .encabezado__gerencia {
      padding-block: var(--espacio-2);
      font-size: var(--texto-xs);
      font-weight: var(--peso-semi);
    }
    .encabezado__principal {
      background: var(--color-fondo);
      box-shadow: var(--sombra-suave);
    }
    .encabezado__marca {
      display: flex;
      align-items: center;
      gap: var(--espacio-3);
      padding-block: var(--espacio-4);
      font-size: var(--texto-lg);
      font-weight: var(--peso-extra);
      letter-spacing: -0.01em;
    }
    .encabezado__distintivo {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 2rem;
      height: 2rem;
      border-radius: var(--radio-md);
      background: var(--color-marca);
      color: var(--color-sobre-marca);
    }
  `,
})
export class Encabezado {}
