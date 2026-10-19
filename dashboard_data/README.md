# Procedencia y Diccionario de Datos del Tablero de Préstamos (Dashboard Data)

Este directorio contiene los conjuntos de datos en formato CSV preparados para el tablero (*dashboard*) analítico de préstamos del Sistema de Bibliotecas Públicas de Seattle (*Seattle Public Library*).

Cada conjunto de datos ha sido generado mediante scripts reproducibles de Python en formato de celdas porcentuales (`# %%`) ubicados en `dashboard/scripts/`, a partir de los datos fuente documentados en `data/README.md`.

---

## 1. Mapeo de Procedencia de Archivos y Scripts Generadores

| Archivo Generado en `dashboard/dashboard_data/` | Script Generador en `dashboard/scripts/` | Archivo(s) Fuente en `data/` | Naturaleza de los Datos | Cobertura Temporal |
| :--- | :--- | :--- | :--- | :--- |
| `annual_digital_physical_share.csv` | [`dashboard/scripts/annual_digital_physical_share.py`](file:///Users/juanestebanperdomoortiz/Downloads/coding-agents-for-data-science/Session%201/dashboard/scripts/annual_digital_physical_share.py) | `data/combined_checkout_totals_by_month_usageclass.csv` | **Completa** (Totales agregados a nivel sistema) | 2005–2026 (Años completos: 2006–2025) |
| `digital_top_sampled_titles_by_year.csv` | [`dashboard/scripts/top_sampled_titles_by_year.py`](file:///Users/juanestebanperdomoortiz/Downloads/coding-agents-for-data-science/Session%201/dashboard/scripts/top_sampled_titles_by_year.py) | `data/digital_checkout_title_sample_balanced_250k.csv` | **Muestreada** (Muestra balanceada de 250k títulos) | 2006–2025 |
| `physical_top_sampled_titles_by_year.csv` | [`dashboard/scripts/top_sampled_titles_by_year.py`](file:///Users/juanestebanperdomoortiz/Downloads/coding-agents-for-data-science/Session%201/dashboard/scripts/top_sampled_titles_by_year.py) | `data/physical_checkout_title_sample_balanced_250k.csv` | **Muestreada** (Muestra balanceada de 250k títulos) | 2006–2025 |
| `digital_material_type_shares_by_year.csv` | [`dashboard/scripts/material_type_shares_by_year.py`](file:///Users/juanestebanperdomoortiz/Downloads/coding-agents-for-data-science/Session%201/dashboard/scripts/material_type_shares_by_year.py) | `data/digital_checkout_title_sample_balanced_250k.csv` | **Muestreada** (Muestra balanceada de 250k títulos) | 2006–2025 |
| `physical_material_type_shares_by_year.csv` | [`dashboard/scripts/material_type_shares_by_year.py`](file:///Users/juanestebanperdomoortiz/Downloads/coding-agents-for-data-science/Session%201/dashboard/scripts/material_type_shares_by_year.py) | `data/physical_checkout_title_sample_balanced_250k.csv` | **Muestreada** (Muestra balanceada de 250k títulos) | 2006–2025 |

---

## 2. Salvedades Metodológicas Críticas

1. **Cobertura Temporal y Años Incompletos**:
   - El archivo de totales a nivel de sistema (`combined_checkout_totals_by_month_usageclass.csv`) abarca desde **abril de 2005 hasta abril de 2026**.
   - Por tanto, **2005 tiene 9 meses** registrados (abril a diciembre) y **2026 tiene 4 meses** registrados (enero a abril). Ambos son años parciales e incompletos.
   - Los únicos años completos que cuentan con los 12 meses registrados para ambas clases de uso (`Physical` y `Digital`) son los **20 años entre 2006 y 2025**. El archivo `annual_digital_physical_share.csv` incluye la columna booleana `is_complete_year` para filtrar adecuadamente estos años en las visualizaciones del tablero.
2. **Salvedad de Procedencia sobre Títulos Más Prestados**:
   - Cualquier resultado referente al "título más prestado" (*most checked out title*) describe **exclusivamente la muestra balanceada** de 250,000 registros por formato y **no la totalidad del catálogo ni la circulación absoluta** de la Biblioteca Pública de Seattle. Los títulos, rangos anuales (`yearly_rank`) y préstamos totales acumulados en la muestra no deben extrapolarse como cifras censales directas.
3. **Distribución de Formatos y Materiales**:
   - Los archivos de participación por tipo de material (`material_type_shares_by_year`) provienen de las muestras balanceadas anuales (12,500 filas por año y formato). Reflejan fielmente las tendencias estructurales y la composición de los catálogos en circulación, pero las sumas de préstamos corresponden al espacio muestral.

---

## 3. Diccionario de Datos por Archivo

### 3.1. `annual_digital_physical_share.csv`
- **Descripción**: Resumen anual consolidado de préstamos físicos y digitales del sistema completo.
- **Granularidad**: 1 fila = 1 año calendario (22 filas: 2005 a 2026).
- **Columnas**:
  - `checkout_year` (*int*): Año del período.
  - `is_complete_year` (*bool*): `True` si contiene los 12 meses completos (2006 a 2025); `False` si es parcial (2005 y 2026).
  - `months_recorded` (*int*): Número de meses reportados en el año (9 para 2005, 12 para 2006–2025, 4 para 2026).
  - `physical_checkouts` (*int*): Total de préstamos físicos registrados en el sistema.
  - `digital_checkouts` (*int*): Total de préstamos digitales registrados en el sistema.
  - `total_checkouts` (*int*): Suma de préstamos físicos y digitales.
  - `physical_share` (*float*): Proporción de préstamos físicos sobre el total anual (`physical_checkouts / total_checkouts`).
  - `digital_share` (*float*): Proporción de préstamos digitales sobre el total anual (`digital_checkouts / total_checkouts`).

### 3.2. `digital_top_sampled_titles_by_year.csv` y `physical_top_sampled_titles_by_year.csv`
- **Descripción**: Los 10 títulos más prestados de la muestra para cada año (2006 a 2025), preservando todos los metadatos bibliográficos.
- **Granularidad**: 1 fila = 1 título en 1 año (200 filas por archivo: 20 años × 10 rangos).
- **Columnas**:
  - `checkoutyear` (*int*): Año de circulación.
  - `yearly_rank` (*int*): Posición en el ranking de la muestra para ese año (1 a 10).
  - `title` (*str*): Título de la obra.
  - `checkouts` (*int*): Préstamos totales acumulados en la muestra durante ese año.
  - `creator` (*str*): Autor, creador o entidad responsable.
  - `materialtype` (*str*): Tipo de material (ej. `EBOOK`, `AUDIOBOOK`, `BOOK`, `VIDEODISC`).
  - `checkouttype` (*str*): Sistema de checkout (ej. `OverDrive`, `Horizon`).
  - `publisher` (*str*): Editorial o casa publicadora.
  - `publicationyear` (*str/float*): Año de publicación de la obra.
  - `subjects` (*str*): Materias o descriptores temáticos.
  - `isbn` (*str*): Código ISBN asociado (leído como texto debido a valores mixtos/dispersos).
  - `usageclass` (*str*): `"Digital"` o `"Physical"`.

### 3.3. `digital_material_type_shares_by_year.csv` y `physical_material_type_shares_by_year.csv`
- **Descripción**: Participación anual de cada formato o tipo de material en la muestra para préstamos digitales y físicos por separado.
- **Granularidad**: 1 fila = 1 combinación de (año, tipo de material).
- **Columnas**:
  - `checkoutyear` (*int*): Año de circulación (2006 a 2025).
  - `materialtype` (*str*): Tipo de material (ej. `EBOOK`, `AUDIOBOOK`, `BOOK`, `VIDEODISC`, `SOUNDDISC`).
  - `sample_row_count` (*int*): Cantidad de registros título-mes de este tipo de material en el año.
  - `sample_checkouts` (*int*): Préstamos acumulados en la muestra para este formato en el año.
  - `year_total_rows` (*int*): Total de registros título-mes en la muestra para ese año (12,500).
  - `year_total_checkouts` (*int*): Total de préstamos acumulados en la muestra para ese año.
  - `row_share` (*float*): Proporción de filas del formato sobre el total anual de la muestra (`sample_row_count / year_total_rows`).
  - `checkout_share` (*float*): Proporción de préstamos del formato sobre el total de préstamos anuales muestreados (`sample_checkouts / year_total_checkouts`).

---

## 4. Instrucciones de Regeneración de Datos

**Directorio de trabajo requerido**: Raíz del proyecto (`Session 1/`).

Para regenerar todos los archivos CSV en `dashboard/dashboard_data/` desde la raíz del proyecto, ejecute los siguientes comandos en la terminal utilizando el entorno virtual:

```bash
# 1. Regenerar participación anual de préstamos físicos y digitales (datos completos)
.venv/bin/python dashboard/scripts/annual_digital_physical_share.py

# 2. Regenerar los títulos más prestados de la muestra por año (digital y físico)
.venv/bin/python dashboard/scripts/top_sampled_titles_by_year.py

# 3. Regenerar participación de tipos de material de la muestra por año (digital y físico)
.venv/bin/python dashboard/scripts/material_type_shares_by_year.py
```
