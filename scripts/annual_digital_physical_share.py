# %% [markdown]
# # Participación Anual de Préstamos Digitales vs. Físicos (2005 - 2026)
#
# Este script procesa el conjunto de datos agregados mensual del Sistema de Bibliotecas
# Públicas de Seattle (`data/combined_checkout_totals_by_month_usageclass.csv`) para calcular
# los totales anuales de préstamos y la proporción de préstamos físicos y digitales.
# El resultado final se genera y guarda en `dashboard/dashboard_data/annual_digital_physical_share.csv`
# para alimentar directamente el tablero de visualización interactivo.
#
# ## Consideraciones Críticas sobre los Datos y Metodología:
# 1. **Naturaleza de los Datos**:
#    - Este archivo contiene datos agregados a nivel de todo el sistema bibliotecario (no es una muestra).
#    - Cada fila representa los totales para una combinación específica de año, mes y clase de uso (`Physical` o `Digital`).
# 2. **Cobertura Temporal y Años Incompletos**:
#    - El conjunto de datos inicia en abril de 2005 y culmina en abril de 2026.
#    - El año 2005 tiene 9 meses registrados (abril a diciembre).
#    - El año 2026 tiene 4 meses registrados (enero a abril).
#    - Los años completos con 12 meses registrados abarcan de 2006 a 2025 inclusive.
# 3. **Identificación de Años Completos**:
#    - Se incluye explícitamente la columna booleana `is_complete_year` (`True` para 2006-2025,
#      `False` para 2005 y 2026) y la columna `months_recorded` con el conteo de meses,
#      permitiendo que los usuarios del tablero filtren o distingan visualmente los años incompletos.
# 4. **Columnas del Tablero Generadas**:
#    - `checkout_year`: Año del período de préstamo.
#    - `is_complete_year`: Indicador booleano de año completo (12 meses).
#    - `months_recorded`: Conteo de meses observados en el año.
#    - `physical_checkouts`: Préstamos físicos totales del año.
#    - `digital_checkouts`: Préstamos digitales totales del año.
#    - `total_checkouts`: Suma total de préstamos del año (físicos + digitales).
#    - `physical_share`: Participación de préstamos físicos (`physical_checkouts / total_checkouts`).
#    - `digital_share`: Participación de préstamos digitales (`digital_checkouts / total_checkouts`).

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

# Ruta al archivo de totales mensuales agregados en data/ de la raíz del proyecto
input_file_path = os.path.join(project_root, "data", "combined_checkout_totals_by_month_usageclass.csv")

# Directorio de salida del tablero en dashboard/dashboard_data/
output_directory = os.path.join(project_root, "dashboard", "dashboard_data")
os.makedirs(output_directory, exist_ok=True)

# Ruta del archivo CSV de salida
output_file_path = os.path.join(output_directory, "annual_digital_physical_share.csv")

print(f"Ruta de archivo de entrada: {input_file_path}")
print(f"Ruta de archivo de salida: {output_file_path}")

# %% [markdown]
# ## 2. Carga e inspección preliminar de datos agregados
#
# Cargamos el archivo CSV y verificamos las dimensiones y tipos de datos iniciales.

# %%
# Cargar datos desde el archivo CSV
monthly_totals_df = pd.read_csv(input_file_path)

print(f"Total de filas leídas: {len(monthly_totals_df)}")
print(f"Columnas disponibles: {list(monthly_totals_df.columns)}")

# %% [markdown]
# ## 3. Conteo de meses registrados por año
#
# Para identificar los años completos e incompletos, calculamos la cantidad de meses únicos
# presentes en el conjunto de datos para cada año calendario.

# %%
# Agrupar por año y contar los meses únicos observados
months_per_year_series = monthly_totals_df.groupby("checkout_year")["checkout_month"].nunique()

# Convertir la serie en un DataFrame con nombres de columna descriptivos
months_per_year_df = months_per_year_series.reset_index()
months_per_year_df = months_per_year_df.rename(columns={"checkout_month": "months_recorded"})

print("Resumen de meses registrados por año:")
print(months_per_year_df.to_string(index=False))

# %% [markdown]
# ## 4. Agregación anual por clase de uso (Física y Digital)
#
# De forma explícita y paso a paso, calculamos los totales anuales de préstamos para cada formato:
# 1. Filtramos las filas de préstamos físicos y sumamos `total_checkouts` por año.
# 2. Filtramos las filas de préstamos digitales y sumamos `total_checkouts` por año.

# %%
# Paso 4.1: Filtrar registros de clase de uso física
is_physical_row = monthly_totals_df["usageclass"] == "Physical"
physical_monthly_df = monthly_totals_df[is_physical_row].copy()

# Sumar préstamos físicos por año
physical_annual_series = physical_monthly_df.groupby("checkout_year")["total_checkouts"].sum()
physical_annual_df = physical_annual_series.reset_index()
physical_annual_df = physical_annual_df.rename(columns={"total_checkouts": "physical_checkouts"})

# Paso 4.2: Filtrar registros de clase de uso digital
is_digital_row = monthly_totals_df["usageclass"] == "Digital"
digital_monthly_df = monthly_totals_df[is_digital_row].copy()

# Sumar préstamos digitales por año
digital_annual_series = digital_monthly_df.groupby("checkout_year")["total_checkouts"].sum()
digital_annual_df = digital_annual_series.reset_index()
digital_annual_df = digital_annual_df.rename(columns={"total_checkouts": "digital_checkouts"})

# %% [markdown]
# ## 5. Fusión de tablas y cálculo de participaciones
#
# Integramos el conteo de meses, los préstamos físicos y los préstamos digitales en una
# única tabla anual consolidada. Luego calculamos:
# - La bandera booleana `is_complete_year` (True para 2006-2025, False para 2005 y 2026).
# - El gran total anual (`total_checkouts`).
# - La proporción física (`physical_share`).
# - La proporción digital (`digital_share`).

# %%
# Paso 5.1: Unir la información de meses registrados con los préstamos físicos
annual_summary_df = pd.merge(months_per_year_df, physical_annual_df, on="checkout_year", how="left")

# Paso 5.2: Unir con los préstamos digitales
annual_summary_df = pd.merge(annual_summary_df, digital_annual_df, on="checkout_year", how="left")

# Llenar posibles valores faltantes con cero y asegurar tipos de datos enteros
annual_summary_df["physical_checkouts"] = annual_summary_df["physical_checkouts"].fillna(0).astype(int)
annual_summary_df["digital_checkouts"] = annual_summary_df["digital_checkouts"].fillna(0).astype(int)

# Paso 5.3: Crear la columna booleana para identificar años completos (2006 a 2025)
annual_summary_df["is_complete_year"] = (annual_summary_df["checkout_year"] >= 2006) & (annual_summary_df["checkout_year"] <= 2025)

# Paso 5.4: Calcular el total de préstamos del año
annual_summary_df["total_checkouts"] = annual_summary_df["physical_checkouts"] + annual_summary_df["digital_checkouts"]

# Paso 5.5: Calcular las participaciones relativas de cada clase de uso
annual_summary_df["physical_share"] = annual_summary_df["physical_checkouts"] / annual_summary_df["total_checkouts"]
annual_summary_df["digital_share"] = annual_summary_df["digital_checkouts"] / annual_summary_df["total_checkouts"]

# Paso 5.6: Reordenar las columnas en el orden exacto solicitado para el tablero
ordered_columns = [
    "checkout_year",
    "is_complete_year",
    "months_recorded",
    "physical_checkouts",
    "digital_checkouts",
    "total_checkouts",
    "physical_share",
    "digital_share",
]

annual_dashboard_df = annual_summary_df[ordered_columns].copy()
annual_dashboard_df = annual_dashboard_df.sort_values("checkout_year").reset_index(drop=True)

# %% [markdown]
# ## 6. Validaciones de calidad y consistencia de los datos
#
# Realizamos pruebas automáticas de aserción para garantizar la integridad de los resultados:
# - Que los años cubran exactamente de 2005 a 2026 (22 filas).
# - Que 2005 tenga 9 meses y 2026 tenga 4 meses.
# - Que los años 2006 a 2025 tengan exactamente 12 meses y `is_complete_year == True`.
# - Que la suma de participaciones físicas y digitales sea igual a 1.0 en todos los años.
# - Que el total sea la suma exacta de préstamos físicos y digitales.

# %%
# Validación 1: Verificar rango de años y número de filas
assert len(annual_dashboard_df) == 22, f"Error: Se esperaban 22 filas, se encontraron {len(annual_dashboard_df)}."
assert annual_dashboard_df["checkout_year"].min() == 2005, "Error: El año inicial debe ser 2005."
assert annual_dashboard_df["checkout_year"].max() == 2026, "Error: El año final debe ser 2026."

# Validación 2: Verificar meses registrados en años incompletos
months_2005 = annual_dashboard_df.loc[annual_dashboard_df["checkout_year"] == 2005, "months_recorded"].values[0]
months_2026 = annual_dashboard_df.loc[annual_dashboard_df["checkout_year"] == 2026, "months_recorded"].values[0]
assert months_2005 == 9, f"Error: El año 2005 debe tener 9 meses, tiene {months_2005}."
assert months_2026 == 4, f"Error: El año 2026 debe tener 4 meses, tiene {months_2026}."

# Validación 3: Verificar años completos
complete_years_df = annual_dashboard_df[annual_dashboard_df["is_complete_year"]]
assert len(complete_years_df) == 20, f"Error: Se esperaban 20 años completos, se encontraron {len(complete_years_df)}."
assert (complete_years_df["months_recorded"] == 12).all(), "Error: Todos los años completos deben tener 12 meses."

# Validación 4: Consistencia matemática de totales y participaciones
sum_check = (annual_dashboard_df["physical_checkouts"] + annual_dashboard_df["digital_checkouts"] == annual_dashboard_df["total_checkouts"]).all()
assert sum_check, "Error: La suma de préstamos físicos y digitales no coincide con el total."

share_sum = (annual_dashboard_df["physical_share"] + annual_dashboard_df["digital_share"]).round(6)
assert (share_sum == 1.0).all(), "Error: La suma de proporciones no es igual a 1.0."

print("Todas las validaciones se completaron exitosamente.")

# %% [markdown]
# ## 7. Exportación del conjunto de datos del tablero y resumen de hallazgos
#
# Guardamos la tabla en formato CSV y presentamos una vista previa junto con hallazgos clave.

# %%
# Guardar archivo CSV final
annual_dashboard_df.to_csv(output_file_path, index=False)
print(f"Archivo guardado satisfactoriamente en: {output_file_path}")

# Imprimir vista previa de la tabla completa
print("\n--- Vista preliminar de datos anuales (dashboard/dashboard_data/annual_digital_physical_share.csv) ---")
print(annual_dashboard_df.to_string(index=False))

# Hallazgos analíticos clave
crossover_rows = annual_dashboard_df[annual_dashboard_df["digital_share"] > annual_dashboard_df["physical_share"]]
first_crossover_year = crossover_rows["checkout_year"].min()

print("\n--- Hallazgos Analíticos Clave ---")
print(f"1. Cobertura total: {annual_dashboard_df['checkout_year'].min()} a {annual_dashboard_df['checkout_year'].max()} ({len(annual_dashboard_df)} años).")
print(f"2. Años completos (12 meses): 2006 a 2025 (20 años). Años parciales: 2005 (9 meses), 2026 (4 meses).")
print(f"3. Primer año en que los préstamos digitales superaron a los físicos: {first_crossover_year} "
      f"(Digital: {annual_dashboard_df.loc[annual_dashboard_df['checkout_year'] == first_crossover_year, 'digital_share'].values[0]:.2%}, "
      f"Físico: {annual_dashboard_df.loc[annual_dashboard_df['checkout_year'] == first_crossover_year, 'physical_share'].values[0]:.2%}).")
print(f"4. Proporción digital en 2006 (primer año completo): {annual_dashboard_df.loc[annual_dashboard_df['checkout_year'] == 2006, 'digital_share'].values[0]:.2%}.")
print(f"5. Proporción digital en 2025 (último año completo): {annual_dashboard_df.loc[annual_dashboard_df['checkout_year'] == 2025, 'digital_share'].values[0]:.2%}.")
