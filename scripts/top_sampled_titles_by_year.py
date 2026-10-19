# %% [markdown]
# # Identificación de los Títulos Más Prestados por Año (2006 - 2025)
#
# Este script procesa las muestras balanceadas de préstamos de la Biblioteca Pública de Seattle
# (`data/digital_checkout_title_sample_balanced_250k.csv` y
# `data/physical_checkout_title_sample_balanced_250k.csv`) para extraer los 10 títulos más
# prestados en cada año entre 2006 y 2025, de manera separada para préstamos digitales y físicos.
#
# ## Nota de Procedencia y Advertencia sobre el Muestreo (Provenance Caveat):
# > **ADVERTENCIA CRÍTICA**: Los resultados obtenidos en este análisis describen EXCLUSIVAMENTE
# > el comportamiento de la MUESTRA balanceada de 250,000 registros por clase de uso, y NO
# > representan el censo completo ni la totalidad de los préstamos del sistema bibliotecario de Seattle.
# >
# > El diseño muestral (`balanced_by_year_and_usageclass`) extrae una cantidad fija y estratificada
# > de registros mensuales. En consecuencia:
# > 1. Un título con alto volumen en esta muestra refleja alta circulación dentro de los registros
# >    muestreados, pero su volumen absoluto y posición relativa no son directamente extrapolables
# >    a la circulación total del catálogo de la biblioteca sin ponderación estadística.
# > 2. Las columnas de metadatos como `isbn` presentan una alta tasa de valores nulos (sparse, ~16-18% no nulo),
# >    por lo que se leen obligatoriamente con el tipo de datos texto (`str`) para evitar discrepancias.
# > 3. Para preservar los metadatos más representativos de cada título a lo largo de los diferentes meses
# >    del año, se selecciona el primer valor no nulo registrado (`first()`).

# %%
import os
import pandas as pd

# %% [markdown]
# ## 1. Configuración de rutas de archivos
#
# Definimos las rutas para los datos crudos en la raíz del proyecto (`data/`)
# y el directorio de salida del tablero (`dashboard/dashboard_data/`).
# El script está diseñado para ejecutarse desde la raíz del proyecto o desde `dashboard/`.

# %%
# Detección de la raíz del proyecto para localizar la carpeta 'data/'
if os.path.exists("data"):
    project_root = "."
elif os.path.exists(os.path.join("..", "data")):
    project_root = ".."
else:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Rutas de archivos fuente de entrada en data/ de la raíz del proyecto
digital_input_path = os.path.join(project_root, "data", "digital_checkout_title_sample_balanced_250k.csv")
physical_input_path = os.path.join(project_root, "data", "physical_checkout_title_sample_balanced_250k.csv")

# Directorio de salida para el tablero analítico en dashboard/dashboard_data/
output_directory = os.path.join(project_root, "dashboard", "dashboard_data")
os.makedirs(output_directory, exist_ok=True)

# Rutas de los archivos CSV de salida
digital_output_path = os.path.join(output_directory, "digital_top_sampled_titles_by_year.csv")
physical_output_path = os.path.join(output_directory, "physical_top_sampled_titles_by_year.csv")

# %% [markdown]
# ## 2. Función modular de procesamiento y agregación de títulos
#
# Diseñada con un estilo explícito y paso a paso para estudiantes de primer semestre de Python:
# - Se cargan los datos especificando `isbn` como texto (`str`).
# - Se filtran únicamente los años completos de interés (2006 a 2025).
# - Se agrupa por año (`checkoutyear`) y título (`title`), sumando `checkouts` y tomando el primer valor no nulo para los metadatos.
# - Se ordenan los títulos por total de préstamos de forma descendente y se asigna el rango anual (`yearly_rank`).
# - Se filtran los 10 títulos más prestados de cada año.

# %%
def process_top_sampled_titles(file_path, usage_label):
    # Paso 1: Carga de datos con tipos de datos controlados
    # Usamos dtype={'isbn': str} para preservar el formato textual de los códigos ISBN
    raw_dataframe = pd.read_csv(file_path, dtype={"isbn": str})
    
    # Paso 2: Filtrado por años completos del proyecto (2006 a 2025)
    valid_years_mask = (raw_dataframe["checkoutyear"] >= 2006) & (raw_dataframe["checkoutyear"] <= 2025)
    filtered_dataframe = raw_dataframe[valid_years_mask].copy()
    
    # Paso 3: Definición del diccionario de reglas de agregación
    # Sumamos los préstamos totales de la muestra y tomamos el primer valor no nulo de los metadatos
    aggregation_rules = {
        "checkouts": "sum",
        "creator": "first",
        "materialtype": "first",
        "checkouttype": "first",
        "publisher": "first",
        "publicationyear": "first",
        "subjects": "first",
        "isbn": "first",
        "usageclass": "first",
    }
    
    # Paso 4: Agrupación por año de préstamo y título de la obra
    # El parámetro as_index=False garantiza que 'checkoutyear' y 'title' se conserven como columnas regulares
    grouped_titles = (
        filtered_dataframe.groupby(["checkoutyear", "title"], as_index=False)
        .agg(aggregation_rules)
    )
    
    # Paso 5: Ordenamiento explícito dentro de cada año
    # Se ordena por año ascendente, préstamos descendente, y título ascendente para desempatar de forma determinista
    sorted_titles = grouped_titles.sort_values(
        by=["checkoutyear", "checkouts", "title"],
        ascending=[True, False, True]
    ).reset_index(drop=True)
    
    # Paso 6: Asignación de rango anual (yearly_rank) de 1 a N dentro de cada año
    sorted_titles["yearly_rank"] = (
        sorted_titles.groupby("checkoutyear").cumcount() + 1
    )
    
    # Paso 7: Selección de los 10 títulos principales por cada año
    is_top_10 = sorted_titles["yearly_rank"] <= 10
    top_10_by_year = sorted_titles[is_top_10].copy()
    
    # Paso 8: Selección y ordenamiento final de las columnas del reporte
    final_columns = [
        "checkoutyear",
        "yearly_rank",
        "title",
        "checkouts",
        "creator",
        "materialtype",
        "checkouttype",
        "publisher",
        "publicationyear",
        "subjects",
        "isbn",
        "usageclass",
    ]
    top_10_by_year = top_10_by_year[final_columns].reset_index(drop=True)
    
    return top_10_by_year

# %% [markdown]
# ## 3. Procesamiento y exportación de préstamos digitales

# %%
print(f"Iniciando procesamiento de préstamos digitales desde: {digital_input_path}")
digital_top_titles = process_top_sampled_titles(digital_input_path, usage_label="Digital")

# Guardar resultado en el archivo CSV de destino
digital_top_titles.to_csv(digital_output_path, index=False)
print(f"Archivo digital guardado exitosamente en: {digital_output_path}")
print(f"Filas generadas: {len(digital_top_titles)} (esperadas: 200 filas para 20 años x 10 títulos)")

# %% [markdown]
# ## 4. Procesamiento y exportación de préstamos físicos

# %%
print(f"\nIniciando procesamiento de préstamos físicos desde: {physical_input_path}")
physical_top_titles = process_top_sampled_titles(physical_input_path, usage_label="Physical")

# Guardar resultado en el archivo CSV de destino
physical_top_titles.to_csv(physical_output_path, index=False)
print(f"Archivo físico guardado exitosamente en: {physical_output_path}")
print(f"Filas generadas: {len(physical_top_titles)} (esperadas: 200 filas para 20 años x 10 títulos)")

# %% [markdown]
# ## 5. Verificación de integridad y validación de resultados

# %%
# Verificación de existencia y dimensiones para el archivo digital
assert os.path.exists(digital_output_path), f"Error: No existe el archivo {digital_output_path}"
assert len(digital_top_titles) == 200, f"Error: Se esperaban 200 filas en digital, pero hay {len(digital_top_titles)}"

# Verificación de existencia y dimensiones para el archivo físico
assert os.path.exists(physical_output_path), f"Error: No existe el archivo {physical_output_path}"
assert len(physical_top_titles) == 200, f"Error: Se esperaban 200 filas en físico, pero hay {len(physical_top_titles)}"

# Verificación de que cada año contiene exactamente los rangos 1 al 10
for yr in range(2006, 2026):
    digital_yr_ranks = list(digital_top_titles[digital_top_titles["checkoutyear"] == yr]["yearly_rank"])
    physical_yr_ranks = list(physical_top_titles[physical_top_titles["checkoutyear"] == yr]["yearly_rank"])
    assert digital_yr_ranks == list(range(1, 11)), f"Error en rangos de digital para el año {yr}"
    assert physical_yr_ranks == list(range(1, 11)), f"Error en rangos de físico para el año {yr}"

print("\nTodas las validaciones pasaron con éxito:")
print("- Ambos archivos CSV existen en dashboard/dashboard_data/")
print("- Cada archivo contiene exactamente 200 filas (10 títulos por año durante 20 años: 2006-2025)")
print("- Los rangos del 1 al 10 están asignados de manera estricta y consecutiva")

# Vista previa de los 3 títulos más prestados en 2024 (digital y físico)
print("\n--- Vista previa Digital (Top 3 en 2024) ---")
preview_digital_2024 = digital_top_titles[digital_top_titles["checkoutyear"] == 2024].head(3)
print(preview_digital_2024[["yearly_rank", "title", "checkouts", "creator", "materialtype"]].to_string(index=False))

print("\n--- Vista previa Físico (Top 3 en 2024) ---")
preview_physical_2024 = physical_top_titles[physical_top_titles["checkoutyear"] == 2024].head(3)
print(preview_physical_2024[["yearly_rank", "title", "checkouts", "creator", "materialtype"]].to_string(index=False))
