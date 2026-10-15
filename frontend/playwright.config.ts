import { defineConfig, devices } from '@playwright/test';

const enCI = !!process.env['CI'];

/**
 * Pruebas de punta a punta: un navegador real contra el frontend (4200) y el backend (8000) reales.
 * Requiere el entorno del backend creado (backend/.venv), como indica el README.
 */
export default defineConfig({
  testDir: './e2e',
  testMatch: '**/*.e2e.ts',
  fullyParallel: true,
  forbidOnly: enCI,
  retries: enCI ? 1 : 0,
  reporter: enCI ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: 'http://localhost:4200',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'escritorio', use: { ...devices['Desktop Chrome'] } },
    { name: 'movil', use: { ...devices['Pixel 7'] } },
  ],
  webServer: [
    {
      command: '.venv/bin/uvicorn app.main:app --port 8000',
      cwd: '../backend',
      url: 'http://localhost:8000/api/health',
      reuseExistingServer: !enCI,
    },
    {
      command: 'npm start',
      url: 'http://localhost:4200',
      reuseExistingServer: !enCI,
      timeout: 120_000,
    },
  ],
});
