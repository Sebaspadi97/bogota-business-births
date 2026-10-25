# Radiografía del emprendimiento en Bogotá · v1

**Sebas Padilla Lab · Pilar Data · Versión 1 (25 oct 2026)**

> **Pregunta:** ¿En qué localidades y sectores de Bogotá nacen más empresas, y quiénes las lideran?

## English summary
**Where are Bogotá's new businesses born?** Descriptive analysis of Bogotá's open business-registry data (Q1 2026): 21,407 new businesses (~238 per day, 4.6 per 100 active). Southern localities (Ciudad Bolívar, Bosa, Usme) have the highest creation rates; bars are the #1 activity among new firms (~17 per day); 45.1% of new firms have a woman as legal representative vs. 41.1% of existing ones. Includes a data-quality audit of the source file (a DBF disguised as .xlsx, zero cancellations, inconsistent locality codes). Python · pandas · matplotlib.

## En 30 segundos
- Entre enero y marzo de 2026 nacieron **21.407 empresas** en Bogotá: unas **238 por día**. Equivalen a **4,6 por cada 100** empresas vigentes (465.498).
- La renovación empresarial es más alta en el sur: **Ciudad Bolívar (6,7)**, **Bosa (6,5)** y **Usme (6,3)** crean más empresas por cada 100 existentes. Chapinero, que concentra las empresas grandes, tiene la tasa más baja (3,0).
- En volumen absoluto lideran **Suba (2.604)** y **Kennedy (2.421)**.
- **Dato curioso:** la actividad con más empresas nuevas es la de **bares**: 1.503 en el trimestre, unos 17 por día (CIIU 5630, expendio de bebidas alcohólicas para consumo en el establecimiento). Su tasa de creación es de 10,6 por cada 100 vigentes.
- **Más mujeres al frente:** el 45,1 % de las empresas nuevas tiene una mujer como representante legal, frente al 41,1 % de las vigentes. En Tunjuelito (53,3 %) y Usme (52,5 %) las mujeres ya son mayoría entre las empresas nuevas.
- El 99,9 % de las empresas nuevas son microempresas, y el 63,6 % se registra como persona natural.

## Puente con el caso "¿Dónde abrir un café en Bogotá?"
- Cafeterías (CIIU 5613): 3.934 vigentes y 201 nuevas en el trimestre (tasa de 5,1). Las localidades con más cafeterías son Kennedy (366), Suba (345) y Engativá (323).
- Restaurantes (CIIU 5611): 707 nuevos en el trimestre.

## Datos
- **Fuente:** [Dinámica Empresarial Bogotá](https://datosabiertos.bogota.gov.co/en/dataset/dinamica-empresarial-bogota/resource/170b171a-19bb-46ca-83e8-3074fe7d74be), Datos Abiertos Bogotá, actualizado el 22 may 2026.
- **Licencia:** CC BY-SA 4.0. Las tablas, los gráficos y los datos derivados de este análisis se comparten bajo la **misma licencia CC BY-SA 4.0**.
- **Corte:** marzo de 2026. "Creadas" es el acumulado del año corrido (enero–marzo).
- **Unidad:** 44.743 registros agregados por localidad × tamaño × rama × CIIU × organización jurídica × sexo del representante legal.

### Hallazgos de calidad de datos (importantes para leer el análisis)
1. **El archivo ".xlsx" es en realidad una tabla dBase (DBF).** Excel y pandas no lo abren directamente; se lee con `scripts/read_dbf.py`.
2. **Las empresas canceladas vienen en cero en todo el archivo.** Por eso esta versión no mide cierres ni supervivencia.
3. **Solo hay un corte (marzo 2026).** No es posible ver tendencias ni estacionalidad.
4. **Los códigos de localidad no coinciden con los oficiales** (Chapinero aparece con código 19, que oficialmente es Ciudad Bolívar). El análisis usa el nombre de la localidad, que es coherente con el perfil de cada una.
5. **Sumapaz no aparece**, y 23.000 empresas vigentes (4,9 %) están "Sin localidad".
6. **Los códigos CIIU perdieron los ceros a la izquierda** (0010 aparece como 10). Se corrigieron a cuatro dígitos. Los códigos 0010, 0081, 0082 y 0090 son clasificaciones de la DIAN (asalariados, rentistas, etc.), no actividades CIIU.
7. 6.878 registros tienen el sexo del representante legal como "Indeterminado"; los porcentajes de mujeres se calculan sobre sexo conocido.

## Indicadores
- **Tasa de creación** = empresas creadas en ene–mar 2026 ÷ empresas vigentes a marzo × 100. Es una tasa trimestral, no anual.
- **% mujeres** = empresas con representante legal femenino ÷ (femenino + masculino) × 100.

## Contenido de la carpeta
| Archivo | Contenido |
| --- | --- |
| `tablas/resultados_dinamica_empresarial_bogota.xlsx` | Indicadores clave, calidad de datos y 10 tablas (localidad, rama, tamaño, organización, top 25 actividades, mujeres por localidad y rama, bares, cafeterías, localidad × rama) |
| `tablas/00_datos_limpios.csv` | Base limpia: columnas renombradas, CIIU a 4 dígitos, nombres de localidad con tildes |
| `graficos/01_tasa_creacion_localidad.png` | Tasa de creación por localidad |
| `graficos/02_mujeres_localidad.png` | % de mujeres representantes legales: vigentes frente a nuevas |
| `graficos/03_top_actividades.png` | 10 actividades con más empresas nuevas |
| `scripts/read_dbf.py` · `scripts/analisis.py` | Código reproducible (Python + pandas + matplotlib) |
| `fuentes/` | Tipografías de la marca (Montserrat y Open Sans, licencia SIL Open Font License) usadas en los gráficos |

Para reproducir: descarga el archivo de la fuente en `datos/` (no se versiona por su tamaño, 63 MB), `pip install -r requirements.txt` y luego `python scripts/analisis.py datos/conjunto-dinamica-empresarial-bogota-21052026.xlsx .`

## Limitaciones y próximos pasos (v2)
- Sin cancelaciones no se puede medir supervivencia ni creación neta. Para v2: buscar otro corte del portal o los informes de la Cámara de Comercio de Bogotá y Confecámaras.
- Con un solo corte no hay tendencia. Cuando se publique el próximo corte, se puede comparar.
- La tasa favorece a las localidades con pocas empresas vigentes; conviene complementarla con empresas por cada 1.000 habitantes (proyecciones de población por localidad).
- Las descripciones CIIU provienen de la Resolución DIAN 0139 de 2012 (CIIU Rev. 4 A.C.).

## Licencia
- **Código** (`scripts/`): © 2026 Sebastián Padilla Castaño. Todos los derechos reservados. Puedes leerlo y ejecutarlo para revisar el análisis, pero no reutilizarlo ni redistribuirlo sin autorización.
- **Datos, tablas y gráficos:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es). Los datos derivados (`tablas/`) y los gráficos (`graficos/`) provienen de un conjunto publicado bajo CC BY-SA 4.0, por lo que se comparten bajo la misma licencia.
- **Tipografías** (`fuentes/`): Montserrat y Open Sans, bajo SIL Open Font License 1.1 (ver `fuentes/OFL-*.txt`).
- Ver `LICENSE.md`.

---
Parte de **Sebas Padilla Lab** · De los datos a las decisiones.
