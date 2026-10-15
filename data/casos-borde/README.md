# Casos borde

Archivos para probar el manejo de errores. Para los de facturas, use `data/contabilidad.csv` como segundo archivo, y viceversa.

| Archivo | Qué prueba | Respuesta esperada |
|---|---|---|
| `facturas_sin_columna_tarifa_iva.csv` | Falta una columna obligatoria | **400** `COLUMNAS_FALTANTES`: indica que falta `tarifa_iva` |
| `contabilidad_vacio.csv` | Archivo sin contenido | **400** `ARCHIVO_VACIO` |
| `facturas.txt` | Extensión distinta a `.csv` | **400** `EXTENSION_INVALIDA` |
| `facturas_punto_y_coma.csv` | Separador `;` (Excel en español) | **200**: se procesa igual que con coma |
| `facturas_valores_invalidos.csv` | Fecha `15/03/2026`, monto en letras, monto negativo y tarifas como `4%` o `19` | **200**: FAC-0001 correcta (tarifas `0%`/`4%` normalizadas); FAC-0002, FAC-0003 y FAC-0005 con `VALOR_INVALIDO` |
| `facturas_excel_renombrado.csv` | Libro de Excel renombrado como `.csv` | **400** `FORMATO_NO_CSV`: sugiere guardarlo como CSV UTF-8 |
| `facturas_utf16.csv` | Excel guardado como "Texto Unicode" (UTF-16) | **400** `CODIFICACION_NO_SOPORTADA` |
| `facturas_danado.csv` | Archivo con caracteres nulos (dañado) | **400** `ARCHIVO_DANADO` |
| `facturas_comillas_sin_cerrar.csv` | Una comilla sin cerrar en la fila de FAC-0003 | **400** `ARCHIVO_INVALIDO`: indica la línea; no se procesa a medias |
| Solo un archivo | Falta el segundo archivo | **422** `SOLICITUD_INVALIDA` |
| Archivos invertidos | Contabilidad en el campo de facturas | **400** `COLUMNAS_FALTANTES` |
