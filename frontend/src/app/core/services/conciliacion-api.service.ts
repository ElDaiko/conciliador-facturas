import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ConciliacionRespuesta, ErrorApi } from '../models/conciliacion.model';

/** Comunicación con la API de Python. La URL es relativa: en desarrollo la resuelve el proxy. */
@Injectable({ providedIn: 'root' })
export class ConciliacionApiService {
  private readonly http = inject(HttpClient);

  conciliar(facturas: File, contabilidad: File): Observable<ConciliacionRespuesta> {
    const formulario = new FormData();
    // Los nombres de los campos deben coincidir con los parámetros del endpoint en FastAPI.
    formulario.append('facturas', facturas);
    formulario.append('contabilidad', contabilidad);
    return this.http.post<ConciliacionRespuesta>('/api/conciliaciones', formulario);
  }
}

const SERVIDOR_NO_DISPONIBLE =
  'No fue posible conectar con el servidor. Verifique que el backend esté en ejecución en el puerto 8000.';

// 0: sin conexión. 502/503/504: el proxy o un balanceador no pudo llegar a la API.
const ESTADOS_SIN_SERVIDOR = [0, 502, 503, 504];

/** Convierte cualquier error HTTP en un mensaje claro para el usuario. */
export function mensajeDeError(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    const cuerpo = error.error as Partial<ErrorApi> | null;
    if (cuerpo && typeof cuerpo.mensaje === 'string') {
      return cuerpo.mensaje;
    }
    if (ESTADOS_SIN_SERVIDOR.includes(error.status)) {
      return SERVIDOR_NO_DISPONIBLE;
    }
  }
  return 'Ocurrió un error inesperado al procesar los archivos. Intente de nuevo.';
}
