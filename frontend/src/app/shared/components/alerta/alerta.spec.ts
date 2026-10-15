import { TestBed } from '@angular/core/testing';

import { Alerta, TonoAlerta } from './alerta';

describe('Alerta', () => {
  it.each([
    ['error', 'alert'],
    ['exito', 'status'],
    ['advertencia', 'status'],
    ['info', 'status'],
  ] as [TonoAlerta, string][])('el tono %s usa role="%s"', async (tono, rol) => {
    const fixture = TestBed.createComponent(Alerta);
    fixture.componentRef.setInput('tono', tono);
    fixture.componentRef.setInput('titulo', 'Título');
    await fixture.whenStable();
    const html = fixture.nativeElement as HTMLElement;

    expect(html.getAttribute('role')).toBe(rol);
    expect(html.textContent).toContain('Título');
  });
});
