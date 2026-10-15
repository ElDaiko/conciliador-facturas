import { TestBed } from '@angular/core/testing';

import { InsigniaEstado, TipoInsignia } from './insignia-estado';

describe('InsigniaEstado', () => {
  async function renderizar(tipo: TipoInsignia, texto?: string): Promise<HTMLElement> {
    const fixture = TestBed.createComponent(InsigniaEstado);
    fixture.componentRef.setInput('tipo', tipo);
    if (texto) {
      fixture.componentRef.setInput('texto', texto);
    }
    await fixture.whenStable();
    return fixture.nativeElement as HTMLElement;
  }

  it.each([
    ['correcta', 'Correcta'],
    ['inconsistencia', 'Con inconsistencia'],
    ['advertencia', 'Advertencia'],
  ] as const)(
    'el estado %s se comunica con texto e ícono, no solo con color',
    async (tipo, texto) => {
      const html = await renderizar(tipo);
      expect(html.textContent?.trim()).toBe(texto);
      expect(html.querySelector('app-icono svg')).not.toBeNull();
      expect(html.classList).toContain(`insignia--${tipo}`);
    },
  );

  it('permite un texto propio', async () => {
    const html = await renderizar('advertencia', 'Línea contable sin valor');
    expect(html.textContent?.trim()).toBe('Línea contable sin valor');
  });

  it('el ícono queda oculto para lectores de pantalla', async () => {
    const html = await renderizar('correcta');
    expect(html.querySelector('app-icono')?.getAttribute('aria-hidden')).toBe('true');
  });
});
