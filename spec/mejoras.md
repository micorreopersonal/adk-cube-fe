### ACTUALIZACIÓN DE ESPECIFICACIONES: CAPACIDAD "EXECUTIVE INSIGHTS & REPORTING"

Esta actualización define la interacción entre la detección de anomalías del Backend y la respuesta visual del Frontend para el reporte de un solo clic.

---

#### 1. REFUERZO TÉCNICO AL BACKEND (Lógica de Hallazgos)
El Backend no solo debe enviar datos crudos, sino también metadatos de "Insight" para alimentar el reporte ejecutivo.

* **Cálculo de Anomalías:** El motor debe comparar el resultado actual contra umbrales críticos de 2025.
    * [cite_start]**Trigger de Reporte:** Si la rotación de una División (UO2) supera el promedio general de **37.21%** [cite: 239][cite_start], o si una unidad como **Transformación** llega al **45.06%**[cite: 383], se debe activar el flag de reporte.
* **Estructura del Payload (JSON de salida):**
    ```json
    {
      "tool_name": "predict_attrition_factors",
      "anomalia_detectada": true,
      [cite_start]"insight_ejecutivo": "Alerta: La división de Transformación presenta una rotación del 45.06%, impulsada por motivos de 'Renuncia' (676 casos totales en el año)[cite: 383, 552].",
      "data_reporte": { ... }
    }
    ```

---

#### 2. ESPECIFICACIÓN TÉCNICA FRONTEND (Streamlit UX)
El Frontend actuará como el presentador de la historia estratégica.

* **Detección Visual de Anomalías:** * Si `anomalia_detectada == true`, el contenedor del KPI principal debe cambiar su borde a **Rojo RIMAC (#EF3340)**.
* **Funcionalidad: "Generación de Reporte Ejecutivo en un Click":**
    * **Botón Dinámico:** Usar `st.download_button` que solo aparecerá o se resaltará (brillo) cuando se detecte una anomalía.
    * [cite_start]**Contenido del Descargable:** El Frontend debe formatear el `insight_ejecutivo` junto con los principales motivos de cese detectados, como **Oportunidad Laboral** (9 menciones) o **Condiciones de Trabajo** (5 menciones)[cite: 1020, 1021].
    * **Brillo (UX):** Utilizar un mensaje de éxito `st.success("Reporte Estratégico Generado")` tras la descarga.

---

#### 3. MAPEO DE SEGMENTOS DE TALENTO CRÍTICO (Filtros de UI)
El Frontend debe permitir filtrar rápidamente estos dos cortes definidos por el negocio:
* [cite_start]**TALENTO (7, 8 y 9):** Reportar sobre la base de **18.79%** de rotación anual[cite: 707].
* [cite_start]**HIPOS (8 y 9):** Reportar sobre la base de **13.37%** de rotación anual[cite: 776].



#### 4. TABLA DE ACCIONES DE DISEÑO
| Elemento | Lógica de Frontend | Valor de Referencia / Brillo |
| :--- | :--- | :--- |
| **KPI Rotación ADMI** | Mostrar valor actual vs 2025. | [cite_start]Alerta si > **20.52%**[cite: 308]. |
| **KPI Rotación FFVV** | Mostrar valor actual vs 2025. | [cite_start]Alerta si > **75.55%**[cite: 906]. |
| **Gráfico Causas** | Mostrar principales motivos de cese. | [cite_start]Priorizar 'RENUNCIA' (**676**) y 'PERIODO DE PRUEBA' (**191**)[cite: 550, 552]. |