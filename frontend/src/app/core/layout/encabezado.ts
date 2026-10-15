import { ChangeDetectionStrategy, Component } from '@angular/core';

/** Barra superior: amarillo de marca como fondo y texto oscuro (11.3:1). */
@Component({
  selector: 'app-encabezado',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <header class="encabezado">
      <div class="encabezado__contenido">
        <p class="encabezado__titulo">Conciliador de facturas</p>
        <p class="encabezado__subtitulo">Gerencia de Evolución Contable y Tributaria</p>
      </div>
    </header>
  `,
  styles: `
    @use 'mixins' as *;

    .encabezado {
      background: var(--color-marca);
      color: var(--color-sobre-marca);
    }
    .encabezado__contenido {
      max-width: var(--ancho-contenido);
      margin-inline: auto;
      padding: var(--espacio-4);

      @include desde(tablet) {
        padding-inline: var(--espacio-6);
      }
    }
    .encabezado__titulo {
      font-size: var(--texto-lg);
      font-weight: var(--peso-extra);
    }
    .encabezado__subtitulo {
      font-size: var(--texto-sm);
      font-weight: var(--peso-semi);
    }
  `,
})
export class Encabezado {}
