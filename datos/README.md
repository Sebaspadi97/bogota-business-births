# Datos de origen

Descarga el archivo **Dinámica Empresarial Bogotá** (corte marzo 2026) desde Datos Abiertos Bogotá y guárdalo en esta carpeta:

https://datosabiertos.bogota.gov.co/en/dataset/dinamica-empresarial-bogota/resource/170b171a-19bb-46ca-83e8-3074fe7d74be

Nota: aunque tiene extensión `.xlsx`, el archivo es una tabla dBase (DBF); `scripts/read_dbf.py` lo lee. No se versiona aquí por su tamaño (63 MB). La base limpia resultante está en `tablas/00_datos_limpios.csv`.

Licencia de la fuente: CC BY-SA 4.0.
