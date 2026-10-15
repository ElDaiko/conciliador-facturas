import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-pie-pagina',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <footer class="pie">
      <div class="pie__contenido">
        <p>Prototipo con identidad visual inspirada en Bancolombia; no es un producto oficial.</p>
        <p>Datos ficticios. Los archivos se procesan en memoria y no se almacenan.</p>
      </div>
    </footer>
  `,
  styles: `
    .pie {
      margin-top: var(--espacio-6);
      background: var(--color-carbon);
      color: var(--color-sobre-carbon-tenue);
    }
    .pie__contenido {
      max-width: var(--ancho-contenido);
      margin-inline: auto;
      padding: var(--espacio-5) var(--espacio-4);
      font-size: var(--texto-sm);
      text-align: center;
    }
  `,
})
export class PiePagina {}
