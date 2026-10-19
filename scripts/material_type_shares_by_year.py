# %% [markdown]
# # Participación de Tipos de Material por Año en Préstamos Digitales y Físicos
#
# Este script procesa las muestras balanceadas de títulos de préstamos del Sistema de Bibliotecas
# Públicas de Seattle (`Seattle Public Library`) para calcular la participación de cada tipo de
# material (`materialtype`) año tras año, de forma separada para préstamos digitales y físicos.
#
# ## Advertencia y Notas Metodológicas Críticas:
# - **Naturaleza de los datos**: Los registros analizados corresponden a una muestra balanceada por año
#   (250,000 registros para el formato digital y 250,000 registros para el formato físico, cubriendo
#   el período 2006 a 2025 con 12,500 registros por año cada uno).
# - **Alcance de los totales**: Los conteos de filas y sumas de préstamos aquí calculados reflejan la
#   distribución interna de la muestra balanceada, no el volumen absoluto total de todo el sistema
#   bibliotecario. Cualquier conclusión describe fielmente las proporciones muestrales.
# - **Años completos**: La muestra abarca exclusivamente años completos (2006 a 2025, 12 meses por año).
#
# ## Métricas Calculadas:
# - `checkoutyear`: Año del período de préstamo.
# - `materialtype`: Formato o tipo de material (ej. EBOOK, AUDIOBOOK, BOOK, VIDEODISC).
# - `sample_row_count`: Cantidad de filas título-mes en la muestra para ese año y tipo de material.
# - `sample_checkouts`: Suma total de préstamos en la muestra para ese año y tipo de material.
# - `year_total_rows`: Total de filas título-mes en la muestra para ese año.
# - `year_total_checkouts`: Total de préstamos en la muestra para ese año.
# - `row_share`: Proporción de filas (`sample_row_count / year_total_rows`).
# - `checkout_share`: Proporción de préstamos (`sample_checkouts / year_total_checkouts`).

# %%
import os
import pandas as pd

# %% [markdown]
# ## 1. Definición de rutas de archivos
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

# Rutas de los archivos fuente de datos muestreados en data/ de la raíz del proyecto
digital_input_path = os.path.join(project_root, "data", "digital_checkout_title_sample_balanced_250k.csv")
physical_input_path = os.path.join(project_root, "data", "physical_checkout_title_sample_balanced_250k.csv")

# Directorio de salida para el tablero en dashboard/dashboard_data/
dashboard_data_dir = os.path.join(project_root, "dashboard", "dashboard_data")
os.makedirs(dashboard_data_dir, exist_ok=True)

# Rutas de los archivos de salida
digital_output_path = os.path.join(dashboard_data_dir, "digital_material_type_shares_by_year.csv")
physical_output_path = os.path.join(dashboard_data_dir, "physical_material_type_shares_by_year.csv")

print(f"Ruta de entrada digital: {digital_input_path}")
print(f"Ruta de entrada física: {physical_input_path}")
print(f"Directorio de salida: {dashboard_data_dir}")

# %% [markdown]
# ## 2. Función explicativa para procesar la participación de materiales
#
# Para mantener el código claro, estructurado y fácil de comprender para estudiantes de primer
# semestre de Python, implementamos los cálculos paso a paso usando variables intermedias descriptivas:
#
# 1. Agrupar por año y tipo de material para contar filas (`sample_row_count`).
# 2. Agrupar por año y tipo de material para sumar préstamos (`sample_checkouts`).
# 3. Combinar ambos resultados por material.
# 4. Calcular los totales del año completo (`year_total_rows` y `year_total_checkouts`).
# 5. Unir los totales anuales a cada fila de material.
# 6. Calcular las proporciones (`row_share` y `checkout_share`).
# 7. Validar que las proporciones anuales sumen exactamente 1.0 (100%).

# %%
def process_material_shares(input_file_path, usage_label):
    """
    Lee un archivo de muestra de préstamos y calcula la participación anual
    por tipo de material de manera explícita y paso a paso.
    """
    print(f"\n==================================================")
    print(f"Procesando datos para: {usage_label}")
    print(f"Archivo fuente: {input_file_path}")
    print(f"==================================================")
    
    # Paso 1: Cargar los datos desde el archivo CSV
    df = pd.read_csv(input_file_path)
    print(f"Filas cargadas: {len(df):,}")
    print(f"Columnas disponibles: {list(df.columns)}")
    
    # Paso 2: Conteo de filas por año y tipo de material
    grouped_rows = (
        df.groupby(["checkoutyear", "materialtype"])
        .size()
        .reset_index(name="sample_row_count")
    )
    
    # Paso 3: Suma de préstamos por año y tipo de material
    grouped_checkouts = (
        df.groupby(["checkoutyear", "materialtype"])["checkouts"]
        .sum()
        .reset_index(name="sample_checkouts")
    )
    
    # Paso 4: Unir las estadísticas de filas y préstamos por material
    material_stats = pd.merge(
        grouped_rows,
        grouped_checkouts,
        on=["checkoutyear", "materialtype"],
        how="inner"
    )
    
    # Paso 5: Calcular totales anuales en la muestra (total de filas por año)
    year_rows = (
        df.groupby("checkoutyear")
        .size()
        .reset_index(name="year_total_rows")
    )
    
    # Paso 6: Calcular totales anuales en la muestra (total de préstamos por año)
    year_checkouts = (
        df.groupby("checkoutyear")["checkouts"]
        .sum()
        .reset_index(name="year_total_checkouts")
    )
    
    # Paso 7: Unir ambos totales anuales en una tabla de referencia por año
    year_totals = pd.merge(
        year_rows,
        year_checkouts,
        on="checkoutyear",
        how="inner"
    )
    
    # Paso 8: Unir los totales anuales a cada grupo de material
    shares_df = pd.merge(
        material_stats,
        year_totals,
        on="checkoutyear",
        how="left"
    )
    
    # Paso 9: Calcular las proporciones (shares)
    shares_df["row_share"] = shares_df["sample_row_count"] / shares_df["year_total_rows"]
    shares_df["checkout_share"] = shares_df["sample_checkouts"] / shares_df["year_total_checkouts"]
    
    # Paso 10: Seleccionar el orden exacto de columnas requerido
    target_columns = [
        "checkoutyear",
        "materialtype",
        "sample_row_count",
        "sample_checkouts",
        "year_total_rows",
        "year_total_checkouts",
        "row_share",
        "checkout_share"
    ]
    shares_df = shares_df[target_columns].copy()
    
    # Paso 11: Ordenar por año cronológico y por mayor participación en préstamos
    shares_df = shares_df.sort_values(
        by=["checkoutyear", "checkout_share"],
        ascending=[True, False]
    ).reset_index(drop=True)
    
    # Paso 12: Verificaciones de integridad y consistencia
    # La suma de row_share por año debe ser igual a 1.0
    row_share_sum_check = shares_df.groupby("checkoutyear")["row_share"].sum()
    checkout_share_sum_check = shares_df.groupby("checkoutyear")["checkout_share"].sum()
    
    is_row_share_valid = (row_share_sum_check.round(5) == 1.0).all()
    is_checkout_share_valid = (checkout_share_sum_check.round(5) == 1.0).all()
    
    print(f"Validación suma de row_share == 1.0 en todos los años: {is_row_share_valid}")
    print(f"Validación suma de checkout_share == 1.0 en todos los años: {is_checkout_share_valid}")
    
    assert is_row_share_valid, "Error: Las proporciones de filas no suman 1.0 por año."
    assert is_checkout_share_valid, "Error: Las proporciones de préstamos no suman 1.0 por año."
    
    return shares_df

# %% [markdown]
# ## 3. Procesamiento y guardado de préstamos digitales
#
# Ejecutamos la función para los datos de préstamos digitales y guardamos el resultado
# en `dashboard_data/digital_material_type_shares_by_year.csv`.

# %%
digital_shares_df = process_material_shares(digital_input_path, "Digital")

# Guardar archivo CSV resultante
digital_shares_df.to_csv(digital_output_path, index=False)
print(f"Archivo guardado exitosamente: {digital_output_path}")
print(f"Dimensiones de la tabla digital: {digital_shares_df.shape[0]} filas, {digital_shares_df.shape[1]} columnas")

# Mostrar vista previa de los primeros registros
print("\n--- Primeras 10 filas de participación digital ---")
print(digital_shares_df.head(10).to_string(index=False))

# %% [markdown]
# ## 4. Procesamiento y guardado de préstamos físicos
#
# Ejecutamos la función para los datos de préstamos físicos y guardamos el resultado
# en `dashboard_data/physical_material_type_shares_by_year.csv`.

# %%
physical_shares_df = process_material_shares(physical_input_path, "Physical")

# Guardar archivo CSV resultante
physical_shares_df.to_csv(physical_output_path, index=False)
print(f"Archivo guardado exitosamente: {physical_output_path}")
print(f"Dimensiones de la tabla física: {physical_shares_df.shape[0]} filas, {physical_shares_df.shape[1]} columnas")

# Mostrar vista previa de los primeros registros
print("\n--- Primeras 10 filas de participación física ---")
print(physical_shares_df.head(10).to_string(index=False))

# %% [markdown]
# ## 5. Resumen de tipos de material dominantes a lo largo del tiempo
#
# Identificamos el tipo de material principal (con mayor `checkout_share`)
# para cada año en ambas clases de uso.

# %%
print("\n==================================================")
print("RESUMEN DE MATERIALES DOMINANTES POR AÑO")
print("==================================================")

# Formato digital: material dominante por año
digital_top_per_year = digital_shares_df.loc[
    digital_shares_df.groupby("checkoutyear")["checkout_share"].idxmax()
][["checkoutyear", "materialtype", "checkout_share", "row_share"]]

print("\n--- Formato Digital: Material con mayor participación de préstamos por año ---")
print(digital_top_per_year.to_string(index=False))

# Formato físico: material dominante por año
physical_top_per_year = physical_shares_df.loc[
    physical_shares_df.groupby("checkoutyear")["checkout_share"].idxmax()
][["checkoutyear", "materialtype", "checkout_share", "row_share"]]

print("\n--- Formato Físico: Material con mayor participación de préstamos por año ---")
print(physical_top_per_year.to_string(index=False))
