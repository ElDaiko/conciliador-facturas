import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  computed,
  input,
  model,
  signal,
  viewChild,
} from '@angular/core';

import { Boton } from '../boton/boton';
import { Icono } from '../icono/icono';

const TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024;
let siguienteId = 0;

/**
 * Selección de un archivo CSV con clic, teclado o arrastrar y soltar.
 * Usa un <input type="file"> nativo asociado a su <label>: funciona con lector de pantalla
 * y teclado sin reimplementar nada. Valida extensión y tamaño antes de enviar.
 *
 * Uso: <app-selector-archivo etiqueta="Archivo de facturas" [(archivo)]="facturas" />
 */
@Component({
  selector: 'app-selector-archivo',
  imports: [Boton, Icono],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './selector-archivo.html',
  styleUrl: './selector-archivo.scss',
})
export class SelectorArchivo {
  readonly etiqueta = input.required<string>();
  readonly ayuda = input('Formato CSV, máximo 5 MB.');
  readonly deshabilitado = input(false);
  readonly archivo = model<File | null>(null);

  protected readonly id = `selector-archivo-${siguienteId++}`;
  protected readonly error = signal<string | null>(null);
  protected readonly arrastrando = signal(false);
  protected readonly tamanoLegible = computed(() => formatearTamano(this.archivo()?.size ?? 0));

  private readonly campo = viewChild.required<ElementRef<HTMLInputElement>>('campo');

  protected alCambiar(): void {
    this.seleccionar(this.campo().nativeElement.files?.[0] ?? null);
  }

  protected alArrastrar(evento: DragEvent): void {
    evento.preventDefault();
    if (!this.deshabilitado()) {
      this.arrastrando.set(true);
    }
  }

  protected alSoltar(evento: DragEvent): void {
    evento.preventDefault();
    this.arrastrando.set(false);
    if (!this.deshabilitado()) {
      this.seleccionar(evento.dataTransfer?.files[0] ?? null);
    }
  }

  protected quitar(): void {
    this.archivo.set(null);
    this.error.set(null);
    this.campo().nativeElement.value = '';
    // Devuelve el foco al campo para que el usuario de teclado no lo pierda.
    queueMicrotask(() => this.campo().nativeElement.focus());
  }

  private seleccionar(archivo: File | null): void {
    if (!archivo) {
      return;
    }
    const mensaje = validar(archivo);
    this.error.set(mensaje);
    this.archivo.set(mensaje ? null : archivo);
    if (mensaje) {
      this.campo().nativeElement.value = '';
    }
  }
}

const EXTENSIONES_HOJA_DE_CALCULO = ['.xlsx', '.xls', '.xlsm', '.ods'];

function validar(archivo: File): string | null {
  const nombre = archivo.name.toLowerCase();
  if (EXTENSIONES_HOJA_DE_CALCULO.some((extension) => nombre.endsWith(extension))) {
    return `"${archivo.name}" es una hoja de cálculo. Ábrala en Excel y use "Guardar como" → "CSV UTF-8".`;
  }
  if (!nombre.endsWith('.csv')) {
    return `"${archivo.name}" no es un archivo CSV.`;
  }
  if (archivo.size === 0) {
    return `"${archivo.name}" está vacío.`;
  }
  if (archivo.size > TAMANO_MAXIMO_BYTES) {
    return `"${archivo.name}" supera el máximo de 5 MB.`;
  }
  return null;
}

function formatearTamano(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1).replace('.', ',')} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1).replace('.', ',')} MB`;
}
