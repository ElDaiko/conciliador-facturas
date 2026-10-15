import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import respuestaMuestra from '../../../testing/respuesta-muestra.json';
import { ConciliacionPage } from './conciliacion.page';

/** Prueba de integración: interfaz + store + servicio, con la respuesta real del backend. */
describe('ConciliacionPage', () => {
  let fixture: ComponentFixture<ConciliacionPage>;
  let html: HTMLElement;
  let http: HttpTestingController;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    fixture = TestBed.createComponent(ConciliacionPage);
    http = TestBed.inject(HttpTestingController);
    html = fixture.nativeElement;
    await fixture.whenStable();
  });

  afterEach(() => http.verify());

  async function cargar(posicion: number, nombre: string): Promise<void> {
    const campo = html.querySelectorAll<HTMLInputElement>('input[type="file"]')[posicion];
    Object.defineProperty(campo, 'files', {
      value: [new File(['x'], nombre)],
      configurable: true,
    });
    campo.dispatchEvent(new Event('change'));
    await fixture.whenStable();
  }

  function botonConciliar(): HTMLButtonElement {
    return [...html.querySelectorAll('button')].find((b) =>
      b.textContent?.includes('Conciliar archivos'),
    ) as HTMLButtonElement;
  }

  async function conciliarMuestra(): Promise<void> {
    await cargar(0, 'facturas.csv');
    await cargar(1, 'contabilidad.csv');
    botonConciliar().click();
    await fixture.whenStable();
    http.expectOne('/api/conciliaciones').flush(respuestaMuestra);
    await fixture.whenStable();
  }

  it('el botón se habilita solo con los dos archivos', async () => {
    expect(botonConciliar().disabled).toBe(true);
    await cargar(0, 'facturas.csv');
    expect(botonConciliar().disabled).toBe(true);
    await cargar(1, 'contabilidad.csv');
    expect(botonConciliar().disabled).toBe(false);
  });

  it('muestra el indicador de carga mientras procesa', async () => {
    await cargar(0, 'facturas.csv');
    await cargar(1, 'contabilidad.csv');
    botonConciliar().click();
    await fixture.whenStable();

    expect(html.querySelector('app-indicador-carga')?.textContent).toContain('Procesando');
    http.expectOne('/api/conciliaciones').flush(respuestaMuestra);
  });

  it('muestra el resumen y la tabla con los datos del backend', async () => {
    await conciliarMuestra();

    const kpis = [...html.querySelectorAll('app-tarjeta-kpi')].map((k) =>
      k.textContent?.replace(/\s+/g, ' ').trim(),
    );
    expect(kpis[0]).toContain('Facturas procesadas 50');
    expect(kpis[1]).toContain('Correctas 32');
    expect(kpis[2]).toContain('Con inconsistencia 18');
    expect(kpis[4]?.replace(/\s/g, ' ')).toContain('$ 11.521.700');
    expect(html.querySelectorAll('tbody tr.fila').length).toBe(50);
    expect(html.textContent).toContain('Mostrando 50 de 50 facturas.');
  });

  it('mueve el foco al título del resultado', async () => {
    await conciliarMuestra();
    expect(document.activeElement?.id).toBe('titulo-resultados');
  });

  it('filtra por estado con los botones de opción', async () => {
    await conciliarMuestra();
    const opcion = html.querySelector<HTMLInputElement>('input[value="CON_INCONSISTENCIA"]');
    opcion!.click();
    await fixture.whenStable();

    expect(html.querySelectorAll('tbody tr.fila').length).toBe(18);
    expect(html.textContent).toContain('Mostrando 18 de 50 facturas.');
  });

  it('despliega el detalle trazable de una factura', async () => {
    await conciliarMuestra();
    const fila = [...html.querySelectorAll('tbody tr.fila')].find((tr) =>
      tr.textContent?.includes('FAC-0006'),
    )!;
    const boton = fila.querySelector('button')!;
    expect(boton.getAttribute('aria-expanded')).toBe('false');

    boton.click();
    await fixture.whenStable();

    expect(boton.getAttribute('aria-expanded')).toBe('true');
    const detalle = html.querySelector(`#${boton.getAttribute('aria-controls')}`);
    expect(detalle?.textContent).toContain(
      'IVA reportado $215.000; esperado $190.000 (base $3.800.000 × 5%).',
    );
    expect(detalle?.textContent).toContain('Línea contable sin valor');
  });

  it('muestra el error del backend y le da el foco', async () => {
    await cargar(0, 'facturas.csv');
    await cargar(1, 'contabilidad.csv');
    botonConciliar().click();
    await fixture.whenStable();
    http
      .expectOne('/api/conciliaciones')
      .flush(
        { codigo: 'COLUMNAS_FALTANTES', mensaje: 'Faltan columnas: tarifa_iva.', archivo: 'f.csv' },
        { status: 400, statusText: 'Bad Request' },
      );
    await fixture.whenStable();

    const alerta = html.querySelector('app-alerta[role="alert"]');
    expect(alerta?.textContent).toContain('Faltan columnas: tarifa_iva.');
    expect(document.activeElement).toBe(alerta);
  });
});
