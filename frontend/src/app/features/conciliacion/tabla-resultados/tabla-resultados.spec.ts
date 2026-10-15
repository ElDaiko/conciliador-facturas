import { TestBed } from '@angular/core/testing';

import respuestaMuestra from '../../../../testing/respuesta-muestra.json';
import { ConciliacionRespuesta } from '../../../core/models/conciliacion.model';
import { TablaResultados } from './tabla-resultados';

const MUESTRA = respuestaMuestra as ConciliacionRespuesta;

describe('TablaResultados', () => {
  it('cada fila comunica su estado con texto, no solo con color', async () => {
    const fixture = TestBed.createComponent(TablaResultados);
    fixture.componentRef.setInput('filas', MUESTRA.detalle.slice(0, 7));
    await fixture.whenStable();
    const filas = [...fixture.nativeElement.querySelectorAll('tbody tr.fila')] as HTMLElement[];

    expect(filas[0].textContent).toContain('Correcta');
    const fac6 = filas.find((f) => f.textContent?.includes('FAC-0006'))!;
    expect(fac6.textContent).toContain('Con inconsistencia');
    expect(fac6.textContent).toContain('IVA mal calculado');
    expect(fac6.textContent).toContain('+ 1 advertencia');
  });

  it('el botón de detalle tiene un nombre accesible único por factura', async () => {
    const fixture = TestBed.createComponent(TablaResultados);
    fixture.componentRef.setInput('filas', MUESTRA.detalle.slice(0, 2));
    await fixture.whenStable();
    const botones = [...fixture.nativeElement.querySelectorAll('button')] as HTMLElement[];

    expect(botones[0].textContent?.replace(/\s+/g, ' ').trim()).toBe(
      'Ver detalle de FAC-0001, fila 2',
    );
  });

  it('muestra un mensaje cuando no hay filas', async () => {
    const fixture = TestBed.createComponent(TablaResultados);
    fixture.componentRef.setInput('filas', []);
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('No hay facturas que coincidan');
  });
});
