import path from 'node:path';

import { expect, Page, test } from '@playwright/test';

const DATA = path.resolve(__dirname, '../../data');
const archivo = (nombre: string) => path.join(DATA, nombre);

async function cargar(page: Page, facturas: string, contabilidad: string): Promise<void> {
  await page.getByLabel('Archivo de facturas').setInputFiles(archivo(facturas));
  await page.getByLabel('Archivo de contabilidad').setInputFiles(archivo(contabilidad));
}

async function conciliarMuestra(page: Page): Promise<void> {
  await cargar(page, 'facturas.csv', 'contabilidad.csv');
  await page.getByRole('button', { name: 'Conciliar archivos' }).click();
  await expect(
    page.getByRole('heading', { name: '2. Resultado de la conciliación' }),
  ).toBeVisible();
}

const kpi = (page: Page, etiqueta: string) =>
  page.locator('app-tarjeta-kpi').filter({ hasText: etiqueta }).locator('.kpi__valor');

test.beforeEach(async ({ page }) => {
  await page.goto('/');
});

test('flujo principal: carga, concilia y muestra el resumen de la muestra', async ({ page }) => {
  const conciliar = page.getByRole('button', { name: 'Conciliar archivos' });
  await expect(conciliar).toBeDisabled();

  await cargar(page, 'facturas.csv', 'contabilidad.csv');
  await expect(conciliar).toBeEnabled();
  await conciliar.click();

  const titulo = page.getByRole('heading', { name: '2. Resultado de la conciliación' });
  await expect(titulo).toBeFocused();
  await expect(kpi(page, 'Facturas procesadas')).toHaveText('50');
  await expect(kpi(page, 'Correctas')).toHaveText('32');
  await expect(kpi(page, 'Con inconsistencia')).toHaveText('18');
  await expect(kpi(page, 'Monto sin contabilizar')).toHaveText(/\$\s11\.521\.700/);
  await expect(page.getByText('Mostrando 50 de 50 facturas.')).toBeVisible();
  await expect(page.locator('tbody tr.fila')).toHaveCount(50);
});

test('filtra por estado, por causa y por texto', async ({ page }) => {
  await conciliarMuestra(page);
  const filas = page.locator('tbody tr.fila');

  await page.getByRole('radio', { name: /Con inconsistencia/ }).check();
  await expect(page.getByText('Mostrando 18 de 50 facturas.')).toBeVisible();
  await expect(filas).toHaveCount(18);

  await page.getByLabel('Causa').selectOption('SIN_CONTABILIZAR');
  await expect(filas).toHaveCount(4);

  await page.getByRole('button', { name: 'Limpiar filtros' }).click();
  await page.getByLabel('Buscar').fill('FAC-0004');
  await expect(filas).toHaveCount(2);
});

test('muestra el detalle trazable de una factura', async ({ page }) => {
  await conciliarMuestra(page);
  const boton = page.getByRole('button', { name: /Ver detalle de FAC-0006/ });
  await expect(boton).toHaveAttribute('aria-expanded', 'false');

  await boton.click();
  await expect(page.getByRole('button', { name: /Ocultar detalle de FAC-0006/ })).toHaveAttribute(
    'aria-expanded',
    'true',
  );
  const detalle = page.locator('#detalle-7');
  await expect(detalle).toContainText('IVA reportado $215.000; esperado $190.000');
  await expect(detalle).toContainText('Línea contable sin valor');
});

test('muestra el error del backend cuando falta una columna', async ({ page }) => {
  await cargar(page, 'casos-borde/facturas_sin_columna_tarifa_iva.csv', 'contabilidad.csv');
  await page.getByRole('button', { name: 'Conciliar archivos' }).click();

  const alerta = page.getByRole('alert');
  await expect(alerta).toContainText('No fue posible procesar los archivos');
  await expect(alerta).toContainText('le faltan columnas obligatorias: tarifa_iva');
});

test('rechaza en el navegador un archivo que no es CSV', async ({ page }) => {
  await page.getByLabel('Archivo de facturas').setInputFiles(archivo('casos-borde/facturas.txt'));
  await expect(page.getByText('"facturas.txt" no es un archivo CSV.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Conciliar archivos' })).toBeDisabled();
});

test('informa cuando el servidor no está disponible', async ({ page }) => {
  // Simula la respuesta del proxy cuando el backend está detenido.
  await page.route('**/api/conciliaciones', (ruta) =>
    ruta.fulfill({ status: 502, contentType: 'text/plain', body: 'Bad Gateway' }),
  );
  await cargar(page, 'facturas.csv', 'contabilidad.csv');
  await page.getByRole('button', { name: 'Conciliar archivos' }).click();

  await expect(page.getByRole('alert')).toContainText('No fue posible conectar con el servidor');
});
