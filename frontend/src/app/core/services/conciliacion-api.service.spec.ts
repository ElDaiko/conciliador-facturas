import { HttpErrorResponse, provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ConciliacionApiService, mensajeDeError } from './conciliacion-api.service';

describe('ConciliacionApiService', () => {
  it('envía los dos archivos como multipart a /api/conciliaciones', () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const servicio = TestBed.inject(ConciliacionApiService);
    const http = TestBed.inject(HttpTestingController);
    const facturas = new File(['a'], 'facturas.csv');
    const contabilidad = new File(['b'], 'contabilidad.csv');

    servicio.conciliar(facturas, contabilidad).subscribe();

    const solicitud = http.expectOne('/api/conciliaciones');
    expect(solicitud.request.method).toBe('POST');
    const cuerpo = solicitud.request.body as FormData;
    expect((cuerpo.get('facturas') as File).name).toBe('facturas.csv');
    expect((cuerpo.get('contabilidad') as File).name).toBe('contabilidad.csv');
    http.verify();
  });
});

describe('mensajeDeError', () => {
  it('usa el mensaje en español que envía el backend', () => {
    const error = new HttpErrorResponse({
      status: 400,
      error: {
        codigo: 'COLUMNAS_FALTANTES',
        mensaje: 'Faltan columnas: tarifa_iva.',
        archivo: 'f.csv',
      },
    });
    expect(mensajeDeError(error)).toBe('Faltan columnas: tarifa_iva.');
  });

  it.each([0, 502, 503, 504])('explica que el servidor no está disponible (HTTP %s)', (status) => {
    expect(mensajeDeError(new HttpErrorResponse({ status, error: 'Bad Gateway' }))).toContain(
      'No fue posible conectar con el servidor',
    );
  });

  it('da un mensaje genérico para errores sin cuerpo conocido', () => {
    expect(mensajeDeError(new HttpErrorResponse({ status: 500, error: '<html>' }))).toContain(
      'error inesperado',
    );
    expect(mensajeDeError(new Error('x'))).toContain('error inesperado');
  });
});
