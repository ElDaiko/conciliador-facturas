import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';

import { Boton } from './boton';

@Component({
  imports: [Boton],
  template: `
    <button appBoton type="button">Primario</button>
    <button appBoton variante="secundario" type="button" disabled>Secundario</button>
  `,
})
class Anfitrion {}

describe('Boton', () => {
  it('conserva el <button> nativo y aplica la variante', async () => {
    const fixture = TestBed.createComponent(Anfitrion);
    await fixture.whenStable();
    const [primario, secundario] = fixture.nativeElement.querySelectorAll('button');

    expect(primario.classList).toContain('boton--primario');
    expect(primario.textContent.trim()).toBe('Primario');
    expect(secundario.classList).toContain('boton--secundario');
    expect(secundario.disabled).toBe(true);
  });
});
