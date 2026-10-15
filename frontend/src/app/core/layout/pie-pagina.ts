import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-pie-pagina',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <footer class="pie">
      <p>Prototipo con identidad visual inspirada en Bancolombia; no es un producto oficial.</p>
      <p>Datos ficticios. Los archivos se procesan en memoria y no se almacenan.</p>
    </footer>
  `,
  styles: `
    .pie {
      max-width: var(--ancho-contenido);
      margin-inline: auto;
      padding: var(--espacio-5) var(--espacio-4);
      font-size: var(--texto-sm);
      color: var(--color-texto-tenue);
      text-align: center;
    }
  `,
})
export class PiePagina {}
