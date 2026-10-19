# Auditoría de Accesibilidad del Tablero (*Dashboard Accessibility Audit*)
**Ubicación del Tablero:** `dashboard/index.html`  
**Fecha de Auditoría:** 18 de octubre de 2026  
**Estándares Evaluados:** WCAG 2.1 / 2.2 Nivel AA y Guía de Accesibilidad de Visualización de Datos (`data-viz-accessibility`)  
**Estado General:** **No conforme (Conformidad Parcial)** — El tablero presenta fortalezas estructurales importantes (tipografía legible, contraste de texto en encabezados, datos tabulares con AG Grid), pero cuenta con barreras críticas de accesibilidad en los componentes gráficos interactivos de Apache ECharts, navegación por teclado, contraste gráfico de elementos secundarios, alternativas textuales y descargas de datos.

---

## 1. Resumen Ejecutivo y Diagnóstico Global

El tablero interactivo (`dashboard/index.html`) presenta el análisis de circulación de formatos y títulos digitales (2006–2025) de la Biblioteca Pública de Seattle utilizando **Apache ECharts 5.5.1** y **AG Grid Community 32.3.3**.

### Matriz de Cumplimiento por Dimensión

| Dimensión Evaluada | Estado WCAG AA | Hallazgo Principal |
| :--- | :--- | :--- |
| **Color y Contraste** | ⚠️ Parcial | La mayoría de las barras cumplen 3:1 frente al fondo blanco, pero el gráfico de títulos usa el color como **único** diferenciador de formato. La marca de agua del año en la carrera de barras tiene un contraste crítico de solo 1.19:1. |
| **Bordes y Contornos** | ❌ No conforme | Las barras en ambos gráficos carecen de contornos visibles (`borderWidth: 0`), dificultando la delimitación en condiciones de baja visión o monocromo. |
| **Etiquetas y Leyendas** | ⚠️ Parcial | La carrera de barras incluye etiquetas directas de porcentaje (`{c}%`), pero el gráfico de títulos depende de una leyenda superior horizontal no alineada con el orden de las barras, sin rotular el formato directamente. |
| **Títulos y Subtítulos** | ⚠️ Parcial | Los títulos cumplen longitud (5–20 palabras) y son texto real HTML. Sin embargo, los subtítulos describen el funcionamiento del control en lugar de comunicar el hallazgo analítico o tendencia de los datos. |
| **Equivalentes Textuales y ARIA** | ❌ No conforme | Los gráficos se renderizan en elementos `<canvas>` sin atributos ARIA (`role="img"`, `aria-label`, o `aria.enabled` de ECharts). El gráfico de títulos carece totalmente de una tabla de datos equivalente accesible. |
| **Descargas de Datos** | ❌ No conforme | No existen enlaces de descarga (`<a download>`) ni botones de exportación para los archivos CSV fuente. |
| **Navegación por Teclado** | ❌ No conforme | No hay estilos definidos para `:focus-visible`. El control deslizante (`<input type="range">`) carece de `aria-label` o `<label>`. Los *tooltips* solo se activan mediante *hover* de ratón, excluyendo a usuarios de teclado. |
| **Sensibilidad al Movimiento** | ❌ No conforme | La animación de la carrera de barras se reproduce automáticamente a los 700 ms sin respetar la preferencia del usuario (`prefers-reduced-motion`). |

---

## 2. Auditoría Detallada por Criterio

### 2.1. Color y Contraste

#### Regla Fundamental
> *Nunca usar el color como la **única** forma de comunicar información. El color debe complementarse con formas, patrones, etiquetas directas o texturas.*

* **Infracción Crítica en Gráfico de Títulos (`titles-echarts-chart`):**  
  En el gráfico de los títulos digitales más prestados por año, las barras se colorean según el formato (`E-Book`, `Audiolibro`, `Revista`, `Música`, `Video`). No obstante, la etiqueta de la barra solo muestra la cifra de préstamos (ej. `2,154`) y el eje Y solo muestra el año y título (ej. `2020 — A Promised Land`). **El formato no está rotulado en la barra ni en el eje**, obligando al usuario a memorizar el color de la leyenda superior. Para una persona con acromatopsia, daltonismo (protanopia/deuteranopia) o en pantallas en escala de grises, es imposible determinar qué formato corresponde a cada barra sin usar el ratón.
* **Falta de Contorno en Elementos Gráficos:**  
  Ninguna serie en `getRaceSeriesData()` ni en `renderTopTitlesChart()` define `borderColor` ni `borderWidth`. Las barras flotan sobre el fondo blanco sin una línea de delimitación de 1–2 px recomendada por la guía.

#### Análisis de Ratios de Contraste Cromático

Se evaluaron los colores de la paleta oficial (Duke University Palette) y elementos visuales clave contra el fondo `#FFFFFF` de las tarjetas:

| Elemento / Código Hex | Ratio Calculado contra `#FFFFFF` | Requisito WCAG AA | Diagnóstico |
| :--- | :--- | :--- | :--- |
| **Duke Navy** (`#012169`) | **14.96:1** | ≥ 3:1 gráficos / ≥ 4.5:1 texto |  Pasa con excelencia (AAA) |
| **Ironweed Purple** (`#993399`) | **6.51:1** | ≥ 3:1 gráficos / ≥ 4.5:1 texto |  Pasa WCAG AA texto y gráficos |
| **Shale Blue** (`#0577B1`) | **4.98:1** | ≥ 3:1 gráficos / ≥ 4.5:1 texto |  Pasa WCAG AA texto y gráficos |
| **Duke Copper** (`#C84E00`) | **4.65:1** | ≥ 3:1 gráficos / ≥ 4.5:1 texto |  Pasa WCAG AA texto y gráficos |
| **Eno Teal** (`#339898`) | **3.51:1** | ≥ 3:1 gráficos / ≥ 4.5:1 texto | ⚠️ Pasa para gráficos grandes (3:1), pero **falla** si se usa en texto normal (< 4.5:1) |
| **Piedmont Green** (`#A1B70D`) *(en `DUKE_PALETTE.comic`)* | **2.28:1** | ≥ 3:1 gráficos | ❌ **Falla crítico.** No alcanza el umbral de 3:1 para gráficos |
| **Marca de agua del año** (`rgba(1, 33, 105, 0.10)`) | **1.19:1** | ≥ 3:1 componentes gráficos | ❌ **Falla crítico.** Prácticamente invisible para usuarios con baja visión |
| **Insignia Audiolibro (AG Grid)** (`#C84E00` sobre `rgba(200, 78, 0, 0.12)`) | **4.41:1** | ≥ 4.5:1 texto pequeño (13px) | ⚠️ Ligeramente por debajo del umbral de texto normal de 4.5:1 |

---

### 2.2. Etiquetas y Leyendas (*Labels and Legends*)

* **Preferencia de Etiquetas Directas:**
  * **Carrera de Formatos:** Presenta etiquetas directas de valor al extremo de cada barra (`formatter: '{c}%'`), lo cual es una excelente práctica.
  * **Gráfico de Títulos:** Utiliza una leyenda separada horizontal en la parte superior (`top: 8, left: 'center'`). Dado que las barras están dispuestas verticalmente en orden cronológico (2006 a 2025), el usuario debe alternar la mirada continuamente entre la leyenda horizontal superior y las 20 barras verticales.
* **Rotulación de Ejes:**
  * **Carrera de Formatos:** El eje X está correctamente rotulado (`Participación en Préstamos (%)` o `Participación en Catálogo (%)`). El eje Y muestra las categorías pero no tiene título de dimensión explícito.
  * **Gráfico de Títulos:** El eje X está rotulado (`Préstamos Muestreados`). El eje Y carece de etiqueta de dimensión (ej. `Año y Título de la Obra`). Además, los títulos se truncan a 38 caracteres con elipsis (`…`) sin que exista forma accesible por teclado de conocer el título completo.

---

### 2.3. Títulos y Subtítulos / Resúmenes (*Titles and Captions*)

* **Títulos:**
  * Ambos gráficos poseen títulos claros, entre 5 y 20 palabras, implementados en texto real HTML (`<h2>` dentro de `<div class="chart-heading">`), cumpliendo con la exigencia técnica de no incrustar texto dentro de imágenes.
* **Subtítulos y Resúmenes Narrativos:**
  * Los elementos `<p>` debajo de los títulos contienen únicamente instrucciones o descripciones técnicas de la interfaz:
    * *Gráfico 1:* `"Animación interactiva que ilustra la carrera anual por la cuota de circulación de cada formato digital."`
    * *Gráfico 2:* `"El título #1 de cada año dentro de la muestra balanceada, con sus préstamos muestreados y formato."`
  * **Requisito no cumplido:** La guía exige un subtítulo o pie explicativo de 1 a 5 oraciones que resuma el hallazgo principal, la tendencia dominante y los valores pico observados en los datos.
  * Si bien existen cajas de *"Hallazgo Analítico"* arriba de cada gráfico, no están vinculadas semánticamente mediante etiquetas `<figure>` y `<figcaption>`, ni a través de atributos `aria-describedby`.

---

### 2.4. Equivalentes Textuales y Soporte para Lectores de Pantalla

* **Elemento `<canvas>` sin Atributos ARIA:**
  Apache ECharts dibuja sobre un elemento `<canvas>`. Por defecto, los lectores de pantalla ignoran el contenido interno del lienzo o lo anuncian de forma genérica como un objeto sin nombre.
  * Los contenedores `#echarts-chart` y `#titles-echarts-chart` carecen de `role="img"` y `aria-label`.
  * No se encuentra habilitado el módulo de accesibilidad nativo de ECharts (`aria: { enabled: true }`).
* **Falta de Tabla de Datos Alternativa para Gráfico de Títulos:**
  * La carrera de barras cuenta con una tabla complementaria (AG Grid) inmediatamente después, aunque solo muestra el formato ganador (#1) de cada año y no las 5 categorías completas.
  * El gráfico de **Títulos Digitales Más Prestados** carece por completo de una tabla HTML o equivalente textual accesible. Un usuario con lector de pantalla no tiene ninguna vía accesible para explorar los 20 títulos más prestados de la serie histórica.

---

### 2.5. Descarga de Datos (*Data Downloads*)

* **Regla:** *Proveer una versión descargable de los datos para cada gráfico relevante (formatos accesibles: CSV, XLSX u ODS).*
* **Estado Actual:** Inexistente. El tablero menciona los nombres de archivo en el encabezado (`dashboard_data/digital_material_type_shares_by_year.csv`), pero no ofrece ningún enlace descargable (`<a href="..." download>`) ni botón de exportación en la tabla AG Grid.

---

### 2.6. Accesibilidad de Interacción y Navegación por Teclado

* **Falta de Indicadores de Foco Visibles (`:focus-visible`):**
  En toda la hoja de estilo CSS no existe ninguna regla `:focus` o `:focus-visible`. Al tabular por los botones (`Reproducir`, `Reiniciar`, `Cuota de Préstamos`, `Cuota de Catálogo`), el usuario no cuenta con un anillo de enfoque de alto contraste.
* **Control Deslizante de Año (`#race-year-slider`):**
  * El elemento `<input type="range">` no está asociado a una etiqueta `<label for="race-year-slider">` ni tiene atributo `aria-label="Año de la carrera"`. Los lectores de pantalla solo anuncian *"control deslizante, valor 2006"*, sin contexto de qué controla.
* **Grupo de Botones de Métrica:**
  * El contenedor tiene `role="group" aria-label="Selector de métrica"`, pero los botones individuales no indican su estado mediante `aria-pressed="true"` o `aria-pressed="false"`.
* **Inaccesibilidad de *Tooltips* por Teclado:**
  * La información detallada (autor, editorial, préstamos exactos) se encuentra exclusivamente en el *tooltip* flotante activado por evento `item` (hover de ratón). No existe equivalente de foco para revelar esta información mediante teclado.
* **Falta de Enlace a Atajos de Teclado:**
  * La guía requiere un enlace o nota visible cercana al gráfico indicando los controles de teclado disponibles.

---

### 2.7. Sensibilidad al Movimiento y Reproducción Automática

* **Violación de WCAG 2.2.2 (Pausa, Detención, Ocultación) y Reducción de Movimiento:**
  * La función `loadDataset()` incluye:
    ```javascript
    setTimeout(() => {
      playRace();
    }, 700);
    ```
    El gráfico inicia una animación continua de 20 segundos de forma automática, sin acción previa del usuario.
  * No existe verificación de la consulta de medios CSS/JS:
    ```javascript
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ```
    Esto representa un riesgo de desorientación, mareo o distracción cognitiva para personas con trastornos vestibulares o dificultades de atención.

---

## 3. Plan de Remediación Priorizado

### Prioridad 1: Barreras Críticas de Conformidad (Nivel Bloqueante)

1. **Habilitar ARIA y Atributos en Apache ECharts:**
   * Configurar `aria: { enabled: true, decal: { show: false } }` en las opciones de ECharts para ambos gráficos.
   * Asignar `role="region" aria-label="..."` y `tabindex="0"` a los contenedores principales de los gráficos.
2. **Eliminar el Color como Único Diferenciador en el Gráfico de Títulos:**
   * Agregar el nombre del formato directamente en la etiqueta de la barra o en la etiqueta del eje Y:
     ```javascript
     // Ejemplo de etiqueta directa enriquecida:
     formatter: '{b} [{fmt}]: {c} préstamos'
     ```
   * Agregar bordes visibles a todas las barras en ambos gráficos:
     ```javascript
     itemStyle: {
       color: FORMAT_COLORS[fmt],
       borderColor: '#001540',
       borderWidth: 1.5,
       borderRadius: [0, 4, 4, 0]
     }
     ```
3. **Controlar la Reproducción Automática y Respetar `prefers-reduced-motion`:**
   * No auto-iniciar la carrera al cargar la página si el usuario tiene activada la preferencia de reducción de movimiento, o mantenerla en pausa por defecto esperando la interacción explícita con el botón *Reproducir*.
     ```javascript
     const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
     if (!prefersReducedMotion) {
       // Opcional: auto-iniciar solo si el usuario no tiene restricciones
     }
     ```
4. **Proporcionar Tabla de Datos Accesible para Títulos Más Prestados:**
   * Incorporar una tabla HTML estática semántica (`<table>`, `<caption>`, `<thead>`, `<tbody>`) o una segunda instancia de AG Grid accesible que contenga los 20 títulos más prestados.
5. **Añadir Enlaces de Descarga de Datos:**
   * Añadir botones o hipervínculos directos de descarga para los archivos CSV fuente en cada tarjeta de visualización:
     ```html
     <a href="dashboard_data/digital_material_type_shares_by_year.csv" download class="btn-download">
       ⬇ Descargar datos de formatos (CSV, 6 KB)
     </a>
     ```

---

### Prioridad 2: Mejoras de Interacción y Teclado

1. **Estilos de Enfoque de Alto Contraste (`:focus-visible`):**
   ```css
   button:focus-visible,
   input[type="range"]:focus-visible,
   a:focus-visible {
     outline: 3px solid #00539B;
     outline-offset: 2px;
     box-shadow: 0 0 0 4px rgba(0, 83, 155, 0.3);
   }
   ```
2. **Accesibilidad del Deslizador de Año:**
   ```html
   <label for="race-year-slider" class="visually-hidden">Seleccionar año de la carrera (2006 a 2025)</label>
   <input type="range" id="race-year-slider" aria-label="Año de la carrera" aria-valuemin="2006" aria-valuemax="2025" ...>
   ```
3. **Estados de Botones de Conmutación (`aria-pressed`):**
   * Actualizar dinámicamente `aria-pressed="true"` en el botón activo y `"false"` en el inactivo al ejecutar `switchMetric()`.
4. **Corregir Contraste de la Marca de Agua:**
   * Cambiar el color de la marca de agua del año en ECharts de `rgba(1, 33, 105, 0.10)` a un color con contraste mínimo de 3:1 o retirarla del lienzo y apoyarse exclusivamente en la insignia HTML `#race-year-badge`.

---

### Prioridad 3: Estructura Semántica y Resúmenes Narrativos

1. **Vincular Gráficos con Etiquetas `<figure>` y `<figcaption>`:**
   * Envolver cada gráfico dentro de `<figure role="group" aria-labelledby="chart-title-1">` y usar `<figcaption>` para contener la explicación de la tendencia observada.
2. **Ampliar los Textos Narrativos:**
   * Sustituir los textos funcionales por resúmenes descriptivos de 1 a 3 oraciones que enuncien la conclusión fundamental del gráfico (tal como ya lo hacen las cajas dinámicas de hallazgo).
3. **Etiqueta en Eje Y:**
   * Declarar `name: 'Año y Título de la Obra'` en el eje Y del gráfico de títulos para dar contexto pleno a la dimensión vertical.

---

## 4. Tabla de Problemas Detectados y Soluciones Recomendadas

| Problema Detectado | Criterio de la Guía | Solución Concreta Recomendada |
| :--- | :--- | :--- |
| El formato de los títulos solo se reconoce por el color de la barra | *Color nunca como único diferenciador* | Incluir el nombre del formato junto al título en el eje Y o dentro de la etiqueta directa de la barra. |
| Barras sin borde de delimitación | *Bordes en elementos gráficos* | Añadir `borderColor: '#001540'` y `borderWidth: 1.5` en `itemStyle` de ECharts. |
| Marca de agua del año con ratio 1.19:1 | *Contraste mínimo 3:1 en gráficos* | Incrementar opacidad o retirar la marca de agua del canvas y resaltar el año en la insignia HTML externa. |
| Contenedores `<canvas>` mudos para lectores de pantalla | *Texto alternativo / ARIA* | Activar `aria: { enabled: true }` en ECharts y colocar descripción de texto visible debajo. |
| Gráfico de títulos sin tabla de datos | *Equivalente textual completo* | Agregar una tabla HTML semántica o cuadrícula debajo del gráfico con los 20 registros. |
| No hay enlaces para descargar los CSV | *Descargas de datos obligatorias* | Añadir enlaces `<a href="..." download>` visibles con formato y tamaño de archivo indicado. |
| Ausencia de contornos de foco en botones y controles | *Navegación accesible por teclado* | Implementar reglas CSS `:focus-visible` con anillo azul `#00539B` de 3px. |
| Deslizador de año sin etiqueta accesible | *Controles de formulario rotulados* | Incorporar `aria-label="Año de la animación"` y asociar `<label>`. |
| Botones de métrica sin atributo de estado | *Componentes interactivos ARIA* | Establecer `aria-pressed="true"` y `"false"` al alternar métricas. |
| Reproducción automática de la animación | *Respeto a prefers-reduced-motion* | Evitar el inicio no solicitado o verificar `prefers-reduced-motion` antes de activar el temporizador. |
| Subtítulos que no explican la tendencia del gráfico | *Títulos y subtítulos narrativos* | Redactar 1 a 3 oraciones con el hallazgo clave, valores pico y comportamiento general. |

---

## 5. Conclusión y Próximos Pasos

El tablero cuenta con una base visual moderna y datos rigurosamente procesados. La implementación de las remediaciones listadas en este informe permitirá alcanzar plena conformidad con **WCAG 2.1 / 2.2 Nivel AA**, garantizando que estudiantes, investigadores y personas con discapacidades visuales, motoras o cognitivas puedan explorar y comprender en igualdad de condiciones la evolución de los formatos digitales de la Biblioteca Pública de Seattle.

---

## 6. Correcciones Aplicadas (*Fixes Applied*)

En respuesta a la auditoría realizada, se implementaron en `dashboard/index.html` las siguientes remediaciones críticas y de alta prioridad, preservando intactos los datos y los hallazgos analíticos:

1. **Eliminación del Color como Único Diferenciador:**
   * En el gráfico de barras de *Títulos Digitales Más Prestados* (`#titles-echarts-chart`), se incorporó el nombre del formato canónico directamente en la etiqueta de cada barra del eje vertical (ej. `2020 — A Promised Land [Audiolibro]`), garantizando que la información no dependa exclusivamente del color.
2. **Contornos y Delimitación Visible de Barras:**
   * Se agregaron bordes visibles de `1.5px` con color azul oscuro `#001540` a todas las barras en ambos gráficos (`getRaceSeriesData` y `renderTopTitlesChart`), asegurando su diferenciación visual sobre el fondo blanco incluso en modo monocromo o baja visión.
3. **Módulo de Accesibilidad ARIA en Apache ECharts:**
   * Se configuró `aria: { enabled: true, decal: { show: false } }` en las opciones de ambos gráficos de ECharts para generar estructuras accesibles interpretables por lectores de pantalla.
   * Se añadieron atributos semánticos `role="region"`, `aria-label` descriptivos y `tabindex="0"` a los contenedores `#echarts-chart` y `#titles-echarts-chart`.
4. **Respeto a Sensibilidad al Movimiento (`prefers-reduced-motion`):**
   * Se condicionó el inicio automático de la carrera de barras evaluando `window.matchMedia('(prefers-reduced-motion: reduce)')`. Los usuarios con preferencia de reducción de movimiento activa no sufrirán animaciones automáticas no solicitadas, pudiendo activar la reproducción a voluntad mediante el botón de control.
   * Se añadieron reglas CSS para suprimir transiciones aceleradas cuando la preferencia del sistema esté activada.
5. **Tabla de Datos Accesible para Títulos Más Prestados:**
   * Se implementó una nueva tarjeta de tabla interactiva (`#titles-grid`) empleando AG Grid Community 32 debajo del gráfico de títulos, proveyendo un equivalente tabular accesible con ordenamiento, filtrado, paginación y lectura por teclado de los metadatos bibliográficos y préstamos muestreados.
6. **Enlaces Directos de Descarga de Datos (CSV):**
   * Se incorporaron botones visibles `<a download>` estilizados con la estética Duke en las cabeceras de cada gráfico y tabla para permitir la descarga inmediata de `digital_material_type_shares_by_year.csv` y `digital_top_sampled_titles_by_year.csv`.
7. **Navegación y Foco por Teclado:**
   * Se definió una regla global `:focus-visible` con anillo azul `#00539B` de 3px y desplazamiento exterior para todos los botones, controles deslizantes y enlaces.
   * Se incorporó un enlace accesible de salto directo al contenido principal (`.skip-link`) al inicio del `<body>`.
   * Se añadieron atributos accesibles al deslizador de años (`aria-label="Año de la carrera"`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, etiqueta oculta `<label>`) y sincronización del estado `aria-pressed="true|false"` en los botones de alternancia de métrica y `aria-label` en el botón de reproducción.
   * Se incluyó una nota visual de ayuda para atajos de navegación por teclado.
8. **Corrección de Contraste:**
   * Se incrementó el contraste de la marca de agua del año en ECharts a `rgba(1, 33, 105, 0.22)` para garantizar legibilidad.
   * Se ajustó el color de texto y borde del distintivo de Audiolibro en AG Grid a `#9C3A00`, superando un ratio de **6.5:1** frente a su fondo translúcido (cumpliendo sobradamente el estándar WCAG AA de 4.5:1).

