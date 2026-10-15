import { TestBed } from '@angular/core/testing';

import { TarjetaKpi } from './tarjeta-kpi';

describe('TarjetaKpi', () => {
  it('muestra etiqueta, valor con cifras tabulares y detalle', async () => {
    const fixture = TestBed.createComponent(TarjetaKpi);
    fixture.componentRef.setInput('etiqueta', 'Con inconsistencia');
    fixture.componentRef.setInput('valor', 18);
    fixture.componentRef.setInput('detalle', '36 %');
    fixture.componentRef.setInput('tono', 'peligro');
    await fixture.whenStable();
    const html = fixture.nativeElement as HTMLElement;

    expect(html.querySelector('.kpi__etiqueta')?.textContent).toContain('Con inconsistencia');
    expect(html.querySelector('.kpi__valor.cifra')?.textContent?.trim()).toBe('18');
    expect(html.querySelector('.kpi__detalle')?.textContent).toContain('36 %');
    expect(html.querySelector('app-icono')).not.toBeNull();
  });

  it('el tono neutro no muestra ícono', async () => {
    const fixture = TestBed.createComponent(TarjetaKpi);
    fixture.componentRef.setInput('etiqueta', 'Facturas');
    fixture.componentRef.setInput('valor', 50);
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('app-icono')).toBeNull();
  });
});
