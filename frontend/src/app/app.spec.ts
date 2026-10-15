import { TestBed } from '@angular/core/testing';

import { App } from './app';

describe('App (estructura accesible)', () => {
  async function renderizar(): Promise<HTMLElement> {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    return fixture.nativeElement as HTMLElement;
  }

  it('ofrece "Saltar al contenido" como primer elemento enfocable', async () => {
    const html = await renderizar();
    const enlace = html.querySelector('a');
    expect(enlace?.textContent).toContain('Saltar al contenido');
    expect(enlace?.getAttribute('href')).toBe('#contenido');
    expect(html.querySelector('main#contenido')).not.toBeNull();
  });

  it('tiene regiones de encabezado, contenido y pie', async () => {
    const html = await renderizar();
    expect(html.querySelector('header')).not.toBeNull();
    expect(html.querySelector('main')).not.toBeNull();
    expect(html.querySelector('footer')?.textContent).toContain(
      'Prototipo con identidad visual inspirada en Bancolombia; no es un producto oficial.',
    );
  });

  it('tiene un único h1', async () => {
    const html = await renderizar();
    expect(html.querySelectorAll('h1').length).toBe(1);
  });
});
