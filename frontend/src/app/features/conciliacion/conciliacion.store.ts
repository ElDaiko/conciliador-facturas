import { Injectable, computed, inject, signal } from '@angular/core';

import {
  CodigoCausa,
  ConciliacionRespuesta,
  EstadoFactura,
  ResultadoFactura,
} from '../../core/models/conciliacion.model';
import {
  ConciliacionApiService,
  mensajeDeError,
} from '../../core/services/conciliacion-api.service';

export type EstadoProceso = 'inicial' | 'cargando' | 'listo' | 'error';
export type FiltroEstado = 'TODAS' | EstadoFactura;
export type FiltroCausa = 'TODAS' | CodigoCausa;

/**
 * Estado de la pantalla de conciliación con signals.
 * Se provee en la página (no es global): al salir de la página, el estado se descarta.
 */
@Injectable()
export class ConciliacionStore {
  private readonly api = inject(ConciliacionApiService);

  // Archivos seleccionados
  readonly facturas = signal<File | null>(null);
  readonly contabilidad = signal<File | null>(null);

  // Proceso
  readonly estado = signal<EstadoProceso>('inicial');
  readonly resultado = signal<ConciliacionRespuesta | null>(null);
  readonly error = signal<string | null>(null);

  // Filtros de la tabla
  readonly filtroEstado = signal<FiltroEstado>('TODAS');
  readonly filtroCausa = signal<FiltroCausa>('TODAS');
  readonly busqueda = signal('');

  readonly cargando = computed(() => this.estado() === 'cargando');
  readonly puedeConciliar = computed(
    () => !!this.facturas() && !!this.contabilidad() && !this.cargando(),
  );

  readonly detalle = computed(() => this.resultado()?.detalle ?? []);

  /** Causas presentes en el resultado, para el filtro (inconsistencias primero). */
  readonly opcionesCausa = computed(() => this.resultado()?.resumen.por_causa ?? []);

  readonly detalleFiltrado = computed(() => {
    const estado = this.filtroEstado();
    const causa = this.filtroCausa();
    const texto = this.busqueda().trim().toLowerCase();

    return this.detalle().filter(
      (factura) =>
        (estado === 'TODAS' || factura.estado === estado) &&
        (causa === 'TODAS' || tieneCodigo(factura, causa)) &&
        (!texto || coincideBusqueda(factura, texto)),
    );
  });

  conciliar(): void {
    const facturas = this.facturas();
    const contabilidad = this.contabilidad();
    if (!facturas || !contabilidad || this.cargando()) {
      return;
    }

    this.estado.set('cargando');
    this.error.set(null);

    this.api.conciliar(facturas, contabilidad).subscribe({
      next: (respuesta) => {
        this.resultado.set(respuesta);
        this.limpiarFiltros();
        this.estado.set('listo');
      },
      error: (error: unknown) => {
        this.resultado.set(null);
        this.error.set(mensajeDeError(error));
        this.estado.set('error');
      },
    });
  }

  limpiarFiltros(): void {
    this.filtroEstado.set('TODAS');
    this.filtroCausa.set('TODAS');
    this.busqueda.set('');
  }

  reiniciar(): void {
    this.facturas.set(null);
    this.contabilidad.set(null);
    this.resultado.set(null);
    this.error.set(null);
    this.estado.set('inicial');
    this.limpiarFiltros();
  }
}

function tieneCodigo(factura: ResultadoFactura, codigo: CodigoCausa): boolean {
  return [...factura.causas, ...factura.advertencias].some((h) => h.codigo === codigo);
}

function coincideBusqueda(factura: ResultadoFactura, texto: string): boolean {
  return (
    factura.id_factura.toLowerCase().includes(texto) ||
    factura.nit_proveedor.toLowerCase().includes(texto) ||
    factura.concepto.toLowerCase().includes(texto)
  );
}
