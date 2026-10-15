import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SelectorArchivo } from './selector-archivo';

describe('SelectorArchivo', () => {
  let fixture: ComponentFixture<SelectorArchivo>;
  let html: HTMLElement;

  beforeEach(async () => {
    fixture = TestBed.createComponent(SelectorArchivo);
    fixture.componentRef.setInput('etiqueta', 'Archivo de facturas');
    await fixture.whenStable();
    html = fixture.nativeElement;
  });

  function campo(): HTMLInputElement {
    return html.querySelector('input[type="file"]') as HTMLInputElement;
  }

  async function seleccionar(archivo: File): Promise<void> {
    // jsdom no implementa DataTransfer: se simula la lista de archivos del input.
    Object.defineProperty(campo(), 'files', { value: [archivo], configurable: true });
    campo().dispatchEvent(new Event('change'));
    await fixture.whenStable();
  }

  it('el campo nativo está asociado a una etiqueta visible', () => {
    const etiqueta = html.querySelector('label');
    expect(etiqueta?.getAttribute('for')).toBe(campo().id);
    expect(etiqueta?.textContent).toContain('Archivo de facturas');
    expect(campo().getAttribute('accept')).toContain('.csv');
  });

  it('acepta un CSV y muestra su nombre', async () => {
    await seleccionar(new File(['a,b'], 'facturas.csv', { type: 'text/csv' }));
    expect(fixture.componentInstance.archivo()?.name).toBe('facturas.csv');
    expect(html.textContent).toContain('facturas.csv');
    expect(html.querySelector('button')?.getAttribute('aria-label')).toBe('Quitar facturas.csv');
  });

  it('rechaza un archivo que no es CSV y lo anuncia como inválido', async () => {
    await seleccionar(new File(['x'], 'facturas.txt'));
    expect(fixture.componentInstance.archivo()).toBeNull();
    expect(html.textContent).toContain('"facturas.txt" no es un archivo CSV.');
    expect(campo().getAttribute('aria-invalid')).toBe('true');
    expect(campo().getAttribute('aria-describedby')).toContain('-error');
  });

  it('a una hoja de cálculo le sugiere guardarla como CSV', async () => {
    await seleccionar(new File(['x'], 'facturas.xlsx'));
    expect(fixture.componentInstance.archivo()).toBeNull();
    expect(html.textContent).toContain('"facturas.xlsx" es una hoja de cálculo.');
    expect(html.textContent).toContain('CSV UTF-8');
  });

  it('rechaza un archivo vacío', async () => {
    await seleccionar(new File([], 'vacio.csv'));
    expect(html.textContent).toContain('"vacio.csv" está vacío.');
  });

  it('al quitar el archivo, el foco vuelve al campo', async () => {
    await seleccionar(new File(['a,b'], 'facturas.csv'));
    (html.querySelector('button') as HTMLButtonElement).click();
    await fixture.whenStable();
    await Promise.resolve();

    expect(fixture.componentInstance.archivo()).toBeNull();
    expect(document.activeElement).toBe(campo());
  });
});
