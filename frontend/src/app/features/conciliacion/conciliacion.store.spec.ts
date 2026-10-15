import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { Subject } from 'rxjs';

import respuestaMuestra from '../../../testing/respuesta-muestra.json';
import { ConciliacionRespuesta } from '../../core/models/conciliacion.model';
import { ConciliacionApiService } from '../../core/services/conciliacion-api.service';
import { ConciliacionStore } from './conciliacion.store';

const MUESTRA = respuestaMuestra as ConciliacionRespuesta;

describe('ConciliacionStore', () => {
  let store: ConciliacionStore;
  let respuesta$: Subject<ConciliacionRespuesta>;

  beforeEach(() => {
    respuesta$ = new Subject();
    TestBed.configureTestingModule({
      providers: [
        ConciliacionStore,
        { provide: ConciliacionApiService, useValue: { conciliar: () => respuesta$ } },
      ],
    });
    store = TestBed.inject(ConciliacionStore);
  });

  function seleccionarArchivos(): void {
    store.facturas.set(new File(['a'], 'facturas.csv'));
    store.contabilidad.set(new File(['b'], 'contabilidad.csv'));
  }

  it('solo permite conciliar con los dos archivos seleccionados', () => {
    expect(store.puedeConciliar()).toBe(false);
    store.facturas.set(new File(['a'], 'facturas.csv'));
    expect(store.puedeConciliar()).toBe(false);
    store.contabilidad.set(new File(['b'], 'contabilidad.csv'));
    expect(store.puedeConciliar()).toBe(true);
  });

  it('pasa por "cargando" y guarda el resultado', () => {
    seleccionarArchivos();
    store.conciliar();
    expect(store.estado()).toBe('cargando');
    expect(store.puedeConciliar()).toBe(false);

    respuesta$.next(MUESTRA);
    expect(store.estado()).toBe('listo');
    expect(store.detalle().length).toBe(50);
  });

  it('guarda el mensaje de error del backend', () => {
    seleccionarArchivos();
    store.conciliar();
    respuesta$.error(
      new HttpErrorResponse({ status: 400, error: { codigo: 'X', mensaje: 'Archivo vacío.' } }),
    );
    expect(store.estado()).toBe('error');
    expect(store.error()).toBe('Archivo vacío.');
    expect(store.resultado()).toBeNull();
  });

  describe('filtros', () => {
    beforeEach(() => {
      seleccionarArchivos();
      store.conciliar();
      respuesta$.next(MUESTRA);
    });

    it('por estado', () => {
      store.filtroEstado.set('CON_INCONSISTENCIA');
      expect(store.detalleFiltrado().length).toBe(18);
      store.filtroEstado.set('CORRECTA');
      expect(store.detalleFiltrado().length).toBe(32);
    });

    it('por causa (incluye advertencias)', () => {
      store.filtroCausa.set('SIN_CONTABILIZAR');
      expect(store.detalleFiltrado().map((f) => f.id_factura)).toEqual([
        'FAC-0007',
        'FAC-0021',
        'FAC-0034',
        'FAC-0042',
      ]);
      store.filtroCausa.set('PERIODO_POSTERIOR');
      expect(store.detalleFiltrado().length).toBe(4);
    });

    it('por búsqueda de id, NIT o concepto, combinada con el estado', () => {
      store.busqueda.set('fac-0004');
      expect(store.detalleFiltrado().length).toBe(2);
      store.busqueda.set('900782207');
      expect(store.detalleFiltrado()[0].id_factura).toBe('FAC-0006');
      store.busqueda.set('arrendamiento');
      store.filtroEstado.set('CORRECTA');
      expect(store.detalleFiltrado().every((f) => f.estado === 'CORRECTA')).toBe(true);
    });

    it('reiniciar deja la pantalla en su estado inicial', () => {
      store.filtroEstado.set('CORRECTA');
      store.reiniciar();
      expect(store.estado()).toBe('inicial');
      expect(store.resultado()).toBeNull();
      expect(store.facturas()).toBeNull();
      expect(store.filtroEstado()).toBe('TODAS');
    });
  });
});
