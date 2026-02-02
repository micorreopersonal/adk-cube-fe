import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid

class Visualizer:
    @staticmethod
    def render(content: list, key_prefix: str = ""):
        """
        Renders a list of visual blocks.
        """
        if not content:
            return

        for idx, block in enumerate(content):
            block_type = block.get("type")
            payload = block.get("payload")
            # Unique key for this block instance
            block_key = f"{key_prefix}_{idx}"
            
            if block_type == "text":
                variant = block.get("variant", "standard")
                severity = block.get("severity", "info")
                
                if variant == "insight":
                    if severity == "critical":
                        st.error(payload, icon="🚨")
                    elif severity == "warning":
                        st.warning(payload, icon="⚠️")
                    else:
                        st.info(payload, icon="ℹ️")
                elif variant == "clarification":
                    st.info(payload, icon="🤔") # Visual distinctivo para preguntas de clarificación
                else:
                    st.markdown(payload)
                
            elif block_type == "kpi_row":
                Visualizer._render_kpis(payload)
                
            elif block_type == "plot":
                Visualizer._render_plot(block, key_prefix=block_key)
                
            elif block_type == "table":
                Visualizer._render_table(payload, key_prefix=block_key)
            
            elif block_type == "data_series":
                metadata = block.get("metadata", {})
                Visualizer._render_interactive_series(payload, metadata, key_prefix=block_key)
            
            elif block_type == "debug_sql":
                from src.config import SHOW_DEBUG_UI
                if SHOW_DEBUG_UI:
                    with st.expander("🔍 Ver Query SQL (Debug)", expanded=False):
                        st.code(payload, language="sql")

            elif block_type == "talent_matrix":
                Visualizer._render_talent_matrix(payload, key_prefix=block_key)

    @staticmethod
    def _create_line_chart(data, metadata):
        fig = go.Figure()
        
        # Prepare custom data for tooltips
        months = data.get('months', [])
        
        # Determine specific colors
        COLOR_PRIMARY = '#EF3340' # Red
        COLOR_SECONDARY = '#3949AB' # Indigo
        COLOR_TERTIARY = '#757575' # Grey
        
        # Check if it is a comparison
        is_comparison = metadata.get("type") == "comparison"
        
        if is_comparison:
            # --- LOGIC FOR COMPARISON (Multi-Line) ---
            years = []
            if "primary_year" in metadata: years.append(str(metadata["primary_year"]))
            if "secondary_year" in metadata: years.append(str(metadata["secondary_year"]))
            
            # Map colors
            color_map = {
                0: COLOR_PRIMARY,    # Primary Year
                1: COLOR_SECONDARY,  # Secondary Year
                2: COLOR_TERTIARY
            }

            for idx, year_key in enumerate(years):
                year_color = color_map.get(idx, COLOR_TERTIARY)
                
                # General Turnover Line
                if year_key in data:
                    series_data = data[year_key]
                    # Voluntary Key
                    vol_key = f"{year_key} Voluntaria"
                    vol_data = data.get(vol_key, [0]*len(series_data))
                    
                    fig.add_trace(go.Scatter(
                        x=months,
                        y=series_data,
                        mode='lines+markers+text',
                        name=f'Rotación {year_key}',
                        line=dict(color=year_color, width=3),
                        marker=dict(size=8),
                        text=[f"{v:.2f}%" for v in series_data],
                        textposition="top center",
                        hovertemplate=f"<b>{year_key}</b><br>Mes: %{{x}}<br>Rotación: %{{y}}%<extra></extra>"
                    ))
                    
                    # Voluntary Line (Dashed)
                    fig.add_trace(go.Scatter(
                        x=months,
                        y=vol_data,
                        mode='lines+markers+text', # Text enabled
                        name=f'Voluntaria {year_key}',
                        line=dict(color=year_color, width=2, dash='dot'),
                        marker=dict(size=6, symbol='circle-open'),
                        text=[f"{v:.2f}%" for v in vol_data],
                        textposition="bottom center",
                        hovertemplate=f"<b>{year_key} (Vol)</b><br>Mes: %{{x}}<br>Rotación: %{{y}}%<extra></extra>"
                    ))

                    # Involuntary Line (Dotted - Diamond)
                    inv_key = f"{year_key} Involuntaria"
                    inv_data = data.get(inv_key, [0]*len(series_data))
                    
                    fig.add_trace(go.Scatter(
                        x=months,
                        y=inv_data,
                        mode='lines+markers+text', 
                        name=f'Involuntaria {year_key}',
                        line=dict(color=year_color, width=2, dash='dot'),
                        marker=dict(size=6, symbol='diamond-open'),
                        text=[f"{v:.2f}%" for v in inv_data],
                        textposition="bottom center",
                        hovertemplate=f"<b>{year_key} (Inv)</b><br>Mes: %{{x}}<br>Rotación: %{{y}}%<extra></extra>"
                    ))

        else:
            # --- LEGACY LOGIC (Single Year) ---
            hc = data.get('headcount', [None] * len(months))
            ceses = data.get('ceses', [None] * len(months))
            renuncias = data.get('renuncias', [None] * len(months))
            
            # Trace Rotación General
            fig.add_trace(go.Scatter(
                x=months,
                y=data.get('rotacion_general', []),
                mode='lines+markers+text',
                name='Rotación General',
                line=dict(color=COLOR_PRIMARY, width=3),
                marker=dict(size=8),
                text=[f"{v}%" for v in data.get('rotacion_general', [])],
                textposition="top center",
                customdata=list(zip(hc, ceses)),
                hovertemplate="<b>%{x}</b><br>Rotación: %{y}%<br>Dotación: %{customdata[0]}<br>Salidas Totales: %{customdata[1]}<extra></extra>"
            ))

            # Trace Rotación Involuntaria
            fig.add_trace(go.Scatter(
                x=months,
                y=data.get('rotacion_involuntaria', []),
                mode='lines+markers+text',
                name='Rotación Involuntaria',
                line=dict(color='#1E88E5', width=3, dash='dot'),
                marker=dict(size=8, symbol='diamond'),
                text=[f"{v}%" for v in data.get('rotacion_involuntaria', [])],
                textposition="bottom center",
                customdata=data.get('involuntarios', [0]*len(months)),
                hovertemplate="Involuntaria: %{y}%<br>Salidas Inv.: %{customdata}<extra></extra>"
            ))

            # Trace Rotación Voluntaria
            fig.add_trace(go.Scatter(
                x=months,
                y=data.get('rotacion_voluntaria', []),
                mode='lines+markers+text',
                name='Rotación Voluntaria',
                line=dict(color='#B0B0B0', width=3, dash='dot'),
                marker=dict(size=8),
                text=[f"{v}%" for v in data.get('rotacion_voluntaria', [])],
                textposition="top center",
                customdata=renuncias,
                hovertemplate="Voluntaria: %{y}%<br>Salidas Vol.: %{customdata}<extra></extra>"
            ))

        fig.update_layout(
            title=f"Dinámica Mensual de Rotación {metadata.get('year', '')}",
            xaxis_title="Mes",
            yaxis_title="Tasa de Rotación (%)",
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    @staticmethod
    def _create_bar_chart(data, metadata):
        months = data.get('months', [])
        hc = data.get('headcount', [None] * len(months))
        ceses = data.get('ceses', [None] * len(months))
        renuncias = data.get('renuncias', [None] * len(months))
        involuntarios = data.get('involuntarios', [None] * len(months))

        df_bar = pd.DataFrame({
            'Mes': months,
            'General': data.get('rotacion_general', []),
            'Voluntaria': data.get('rotacion_voluntaria', []),
            'Involuntaria': data.get('rotacion_involuntaria', []),
            'hc': hc,
            'ceses': ceses,
            'ren': renuncias
        })
        fig = go.Figure()
        
        # Bar General: Show HC and Total Salidas
        fig.add_trace(go.Bar(
            x=df_bar['Mes'],
            y=df_bar['General'],
            name='General',
            marker_color='#EF3340',
            text=df_bar['General'].apply(lambda x: f"{x}%"),
            textposition='auto',
            customdata=list(zip(df_bar['hc'], df_bar['ceses'])),
            hovertemplate="<b>%{x}</b><br>General: %{y}%<br>Dotación: %{customdata[0]}<br>Salidas Totales: %{customdata[1]}<extra></extra>"
        ))

        # Bar Voluntaria: Show only Salidas Vol.
        fig.add_trace(go.Bar(
            x=df_bar['Mes'],
            y=df_bar['Voluntaria'],
            name='Voluntaria',
            marker_color='#B0B0B0',
            text=df_bar['Voluntaria'].apply(lambda x: f"{x}%"),
            textposition='auto',
            customdata=df_bar['ren'],
            hovertemplate="Voluntaria: %{y}%<br>Salidas Vol.: %{customdata}<extra></extra>"
        ))

        # Bar Involuntaria
        fig.add_trace(go.Bar(
            x=df_bar['Mes'],
            y=df_bar['Involuntaria'],
            name='Involuntaria',
            marker_color='#1E88E5',
            text=df_bar['Involuntaria'].apply(lambda x: f"{x}%"),
            textposition='auto',
            customdata=df_bar['involuntarios'] if 'involuntarios' in df_bar else [0]*len(months),
            hovertemplate="Involuntaria: %{y}%<br>Salidas Inv.: %{customdata}<extra></extra>"
        ))

        fig.update_layout(
            title=f"Comparativa Mensual {metadata.get('year', '')}",
            xaxis_title="Mes",
            yaxis_title="Tasa de Rotación (%)",
            barmode='group',
            template='plotly_white',
            height=500
        )
        return fig

    @staticmethod
    def get_figures_from_content(content: list) -> list:
        """
        Extrae figuras de bloques visuales para su uso en reportes (PDF).
        Retorna lista de dicts: {'title': str, 'fig': go.Figure}
        """
        figures = []
        for block in content:
            if block.get("type") == "data_series":
                payload = block.get("payload", {})
                metadata = block.get("metadata", {})
                
                # Generamos ambas vistas para el reporte
                fig_line = Visualizer._create_line_chart(payload, metadata)
                figures.append({"title": "Tendencia Mensual", "fig": fig_line})
                
                fig_bar = Visualizer._create_bar_chart(payload, metadata)
                figures.append({"title": "Comparativa de Rotación", "fig": fig_bar})
                
            elif block.get("type") == "plot" and "data" in block:
                # Reconstruir plot simple (limitado por ahora)
                pass 
        return figures

    @staticmethod
    def _render_interactive_series(data: dict, metadata: dict, key_prefix: str = ""):
        """
        Renders an interactive time-series visualization with tabs for different views.
        """
        if not data:
            return
            
        # --- Filtering Logic ---
        all_months = data.get('months', [])
        
        # FIX: Normalizar longitudes de los arrays para evitar errores en pandas
        # Asegura que todos los arrays tengan el mismo largo que 'months' antes de filtrar
        target_len = len(all_months)
        keys_to_sync = ['rotacion_general', 'rotacion_voluntaria', 'rotacion_involuntaria', 'headcount', 'ceses', 'renuncias', 'involuntarios']
        
        for k in keys_to_sync:
            current_list = data.get(k, [])
            if current_list is None: 
                current_list = []
            current_list = list(current_list) # Force list type
            
            if len(current_list) < target_len:
                # Pad with None per consistency
                current_list.extend([None] * (target_len - len(current_list)))
                data[k] = current_list
            elif len(current_list) > target_len:
                # Truncate
                data[k] = current_list[:target_len]
        
        # Determine unique key for multiselect to avoid conflicts
        # Using a deterministic hash based on data content
        import hashlib
        data_hash = hashlib.md5(str(data).encode()).hexdigest()[:8]
        
        selected_months = st.multiselect(
            "📅 Filtrar Meses:",
            options=all_months,
            default=all_months,
            key=f"filter_months_{data_hash}_{key_prefix}"
        )
        
        # Apply filter if selection changes
        filtered_data = data.copy()
        if selected_months and len(selected_months) != len(all_months):
            # Get indices of selected months
            # Assumes 'months' are unique. If not, this logic might need refinement, 
            # but usually months in timeseries are unique.
            indices = [i for i, m in enumerate(all_months) if m in selected_months]
            
            # Helper to filter list by indices
            def filter_list(lst):
                return [lst[i] for i in indices] if lst and len(lst) == len(all_months) else lst

            # Filter all relevant keys
            filtered_data['months'] = filter_list(data.get('months', []))
            filtered_data['rotacion_general'] = filter_list(data.get('rotacion_general', []))
            filtered_data['rotacion_voluntaria'] = filter_list(data.get('rotacion_voluntaria', []))
            filtered_data['rotacion_involuntaria'] = filter_list(data.get('rotacion_involuntaria', []))
            filtered_data['headcount'] = filter_list(data.get('headcount', []))
            filtered_data['ceses'] = filter_list(data.get('ceses', []))
            filtered_data['renuncias'] = filter_list(data.get('renuncias', []))
            filtered_data['involuntarios'] = filter_list(data.get('involuntarios', []))
        
        if not selected_months:
             st.warning("⚠️ Selecciona al menos un mes para visualizar.")
             return

        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["📈 Gráfico de Línea", "📊 Gráfico de Barras", "📋 Tabla Detallada"])
        
        with tab1:
            fig = Visualizer._create_line_chart(filtered_data, metadata)
            st.plotly_chart(fig, width='stretch', key=f"line_{data_hash}_{key_prefix}")
        
        with tab2:
            fig = Visualizer._create_bar_chart(filtered_data, metadata)
            st.plotly_chart(fig, width='stretch', key=f"bar_{data_hash}_{key_prefix}")
        
        with tab3:
            # Detailed Table
            df_table = pd.DataFrame({
                'Mes': filtered_data.get('months', []),
                'Rotación General (%)': filtered_data.get('rotacion_general', []),
                'Rotación Voluntaria (%)': filtered_data.get('rotacion_voluntaria', []),
                'Rotación Involuntaria (%)': filtered_data.get('rotacion_involuntaria', []),
                'Headcount Base': filtered_data.get('headcount', []),
                'Total Ceses': filtered_data.get('ceses', []),
                'Renuncias': filtered_data.get('renuncias', []),
                'Involuntarias': filtered_data.get('involuntarios', [])
            })
            
            # Download button
            csv = df_table.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"rotacion_mensual_{metadata.get('year', '')}.csv",
                mime="text/csv",
                key=f"dl_series_{data_hash}_{key_prefix}"
            )
            
            st.dataframe(df_table, width='stretch', hide_index=True)
            st.caption(f"Mostrando {len(df_table)} meses seleccionados.")

    @staticmethod
    def _render_kpis(kpis: list):
        if not kpis:
            return
        cols = st.columns(len(kpis))
        for idx, kpi in enumerate(kpis):
            with cols[idx]:
                # Streamlit.metric solo acepta: 'normal', 'inverse', 'off'
                # Mapeo de intención semántica (Colors from backend -> Streamlit types)
                raw_color = kpi.get("color", "normal").lower()
                
                # Logic: 
                # red -> inverse (assuming bad thing increased or good thing decreased, standard behavior relies on delta sign)
                # But to force specific behaviors we might need to rely on delta coloring logic.
                # Streamlit defaults: Positive delta = Green (normal), Negative = Red (inverse).
                
                final_color = "normal"
                if raw_color in ["red", "inverse", "critical"]:
                    final_color = "inverse"
                elif raw_color in ["green", "normal", "good"]:
                    final_color = "normal"
                elif raw_color == "off":
                    final_color = "off"
                
                # Note: "orange" or "blue" are not supported by st.metric delta_color. 
                # We fallback to normal or off.

                st.metric(
                    label=kpi.get("label"),
                    value=kpi.get("value"),
                    delta=kpi.get("delta"),
                    delta_color=final_color,
                    help=kpi.get("tooltip_data")
                )

    @staticmethod
    def _render_plot(block: dict, key_prefix: str = ""):
        subtype = block.get("subtype", "bar")
        data = block.get("data", {})
        title = block.get("title", "")
        # Try to get axis labels from data keys if possible, or metadata
        x_label = block.get("x_label") or data.get("x_label") or "Categoría"
        y_label = block.get("y_label") or data.get("y_label") or "Valor"
        
        if title:
            st.subheader(title)

        # Prepare DataFrame for easier manipulation
        try:
            # Deterministic hash for keys
            import hashlib
            data_hash = hashlib.md5(str(data).encode()).hexdigest()[:8]
            
            df = None
            if "x" in data and "y" in data:
                df = pd.DataFrame({"x": data["x"], "y": data["y"]})
                
                # --- NUEVOS CAMPOS NOMINALES PARA MAPPING ---
                if "hc" in data: df["hc"] = data["hc"]
                if "ceses" in data: df["ceses"] = data["ceses"]
                
                # If category exists, add it
                if "category" in data:
                    df["category"] = data["category"]
            elif "names" in data and "values" in data:
                df = pd.DataFrame({"x": data["names"], "y": data["values"]})
                # Update labels if specific ones weren't provided
                if x_label == "Categoría": x_label = "Categoría"
                if y_label == "Valor": y_label = "Valor"

            if df is None:
                st.warning("Datos insuficientes para graficar.")
                return

            # Interactive Chart Switcher
            chart_type = st.radio(
                "Tipo de Gráfico:",
                ["Barras", "Línea", "Pie", "Area"],
                horizontal=True,
                key=f"chart_type_{data_hash}_{key_prefix}",
                index=0 if subtype == "bar" else (1 if subtype == "line" else 2)
            )

            # Tooltip Configuration
            hover_data = {}
            if "hc" in df.columns: hover_data["hc"] = True
            if "ceses" in df.columns: hover_data["ceses"] = True
            
            # Labels mapping for tooltips
            labels_map = {"x": x_label, "y": y_label, "hc": "Dotación", "ceses": "Salidas"}

            fig = None
            if chart_type == "Barras":
                fig = px.bar(
                    df, x="x", y="y",
                    color="category" if "category" in df.columns else None,
                    text_auto=True,
                    labels=labels_map,
                    hover_data=hover_data
                )
            elif chart_type == "Línea":
                fig = px.line(
                    df, x="x", y="y",
                    markers=True,
                    text="y",
                    labels=labels_map,
                    hover_data=hover_data
                )
                fig.update_traces(textposition="top center")
            elif chart_type == "Pie":
                fig = px.pie(
                    df, names="x", values="y",
                    title=f"Distribución - {title}",
                    hover_data=hover_data,
                    labels=labels_map
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
            elif chart_type == "Area":
                fig = px.area(
                    df, x="x", y="y",
                    markers=True,
                    labels=labels_map,
                    hover_data=hover_data
                )
            
            # Common Layout Updates
            if fig:
                if chart_type != "Pie":
                    fig.update_layout(
                        xaxis_title=x_label,
                        yaxis_title=y_label,
                        showlegend=True,
                        legend_title_text="Leyenda"
                    )
                
                # Custom hover template for better formatting
                if "hc" in df.columns and "ceses" in df.columns:
                     fig.update_traces(
                         hovertemplate="<b>%{x}</b><br>" + 
                                       f"{y_label}: %{{y}}<br>" +
                                       "Dotación: %{customdata[0]}<br>" +
                                       "Salidas: %{customdata[1]}<extra></extra>"
                     )
                else:
                    # Generic nice tooltip for other charts (e.g. Distribution)
                    fig.update_traces(
                        hovertemplate="<b>%{x}</b><br>" +
                                      f"{y_label}: %{{y}}<br><extra></extra>"
                    )

                st.plotly_chart(fig, width='stretch', key=f"plot_{data_hash}_{key_prefix}")

        except Exception as e:
            st.error(f"Error renderizando gráfico mejorado: {e}")

    @staticmethod
    def _render_table(data: list, key_prefix: str = ""):
        if data:
            df = pd.DataFrame(data)
            # FIX: Usar un hash determinista del contenido para mantener el estado de los filtros entre reruns.
            # COMBINED FIX: Añadir key_prefix para unicidad global (fix StreamlitDuplicateElementKey)
            import hashlib
            data_hash = hashlib.md5(str(data).encode()).hexdigest()[:8]
            unique_suffix = f"{data_hash}_{key_prefix}"
            
            # --- 1. Controles de Interacción (Client-Side) ---
            col1, col2 = st.columns([3, 1])
            with col1:
                # Buscador Genérico
                search = st.text_input("🔍 Filtrar resultados en tabla:", placeholder="Escribe para buscar (ej. 'Jefe', 'Finanzas')...", key=f"search_{unique_suffix}")
            
            with col2:
                # Botón de Descarga
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name="reporte_adk.csv",
                    mime="text/csv",
                    key=f"dl_table_{unique_suffix}"
                )

            # --- 2. Filtros Avanzados por Columna ---
            with st.expander("🌪️ Filtros por Columna", expanded=False):
                cols_filter = st.columns(3)
                filters = {}
                
                # Detectar columnas categóricas para filtrar
                # Prioridad: columnas de texto con menos de 50 valores únicos
                # AJUSTE: Incluir números con baja cardinalidad (ej. mapeo_talento 1-9)
                potential_filters = [
                    col for col in df.columns 
                    if (df[col].dtype == 'object' or pd.api.types.is_numeric_dtype(df[col])) 
                    and df[col].nunique() < 50
                ]
                
                # Crear widgets de filtro
                for idx, col in enumerate(potential_filters):
                    with cols_filter[idx % 3]:
                        options = sorted(df[col].dropna().unique().tolist())
                        filters[col] = st.multiselect(
                            f"{col.replace('_', ' ').title()}", 
                            options, 
                            key=f"filter_{col}_{unique_suffix}"
                        )

            # --- 3. Lógica de Filtrado Combinada ---
            df_display = df.copy()

            # A. Aplicar Filtros de Columna
            for col, selected_values in filters.items():
                if selected_values:
                    df_display = df_display[df_display[col].isin(selected_values)]

            # B. Aplicar Buscador Genérico
            if search:
                mask = df_display.apply(lambda x: x.astype(str).str.contains(search, case=False).any(), axis=1)
                df_display = df_display[mask]

            # --- 3. Renderizado con Configuración ---
            # Detectar columnas de fecha para formatearlas bonito
            column_config = {}
            for col in df_display.columns:
                if "fecha" in col.lower() or "date" in col.lower():
                    column_config[col] = st.column_config.DateColumn(col, format="DD/MM/YYYY")

            st.dataframe(
                df_display, 
                width='stretch', 
                hide_index=True,
                column_config=column_config
            )

    @staticmethod
    def _render_talent_matrix(payload: dict, key_prefix: str = ""):
        """
        Renders a 9-Box Talent Matrix (Performance vs Potential).
        Expects payload: {
            "title": str,
            "matrix": [[p3_perf1, p3_perf2, p3_perf3], [p2_perf1, ...], [p1_...]] (Top-down)
            OR
            "data": list of dicts [{"performance": 1..3, "potential": 1..3, "count": int}]
        }
        """
        title = payload.get("title", "Matriz de Talento (9-Box)")
        st.subheader(f"📊 {title}")
        
        # Grid definition
        labels_perf = ["Bajo", "Medio", "Alto"]
        labels_pot = ["Bajo", "Medio", "Alto"] # Note: Indices 0=Bajo, 1=Medio, 2=Alto
        
        # Initialize 3x3 grid (y=potential, x=performance)
        # We want y-axis (Potential) to go from 1 (Bottom) to 3 (Top)
        grid = [[0 for _ in range(3)] for _ in range(3)]
        
        # Fill grid from payload 'data' if provided
        data_list = payload.get("data", [])
        if data_list:
            for item in data_list:
                p_x = item.get("performance")
                p_y = item.get("potential")
                count = item.get("count", 0)
                
                # Manual Mapping to indices 0-2
                def get_idx(val):
                    if isinstance(val, int): return val - 1
                    s = str(val).lower()
                    if any(x in s for x in ["alto", "high", "3"]): return 2
                    if any(x in s for x in ["medio", "mid", "2"]): return 1
                    return 0 # Default to Bajo/Low
                
                idx_x = get_idx(p_x)
                idx_y = get_idx(p_y)
                
                if 0 <= idx_x <= 2 and 0 <= idx_y <= 2:
                    grid[idx_y][idx_x] += count
        
        # Matrix direct if present (expected format: [[pot3_p1..p3], [pot2...], [pot1...]])
        elif "matrix" in payload:
            raw_matrix = payload["matrix"]
            # Plotly Heatmap expects Y to go from bottom to top if we want 'Alto' at top.
            # If the backend sends pot3 as first row, we must reverse for Plotly if we use y=[Bajo, Medio, Alto]
            grid = raw_matrix[::-1] if len(raw_matrix) == 3 else raw_matrix

        # Annotations (counts)
        annotations = []
        for y_idx, row in enumerate(grid):
            for x_idx, val in enumerate(row):
                annotations.append(dict(
                    x=labels_perf[x_idx],
                    y=labels_pot[y_idx],
                    text=f"<b>{val}</b>",
                    showarrow=False,
                    font=dict(color="white" if val > 0 else "black", size=24)
                ))

        # Heatmap
        fig = go.Figure(data=go.Heatmap(
            z=grid,
            x=labels_perf,
            y=labels_pot,
            colorscale=[
                [0, "#F8F9FA"],    # Light Grey (Empty)
                [0.1, "#FFEBEE"],  # Very light red
                [0.5, "#EF9A9A"],  # Mid red
                [1.0, "#EF3340"]   # RIMAC RED (Full)
            ],
            showscale=False,
            hovertemplate="Desempeño: %{x}<br>Potencial: %{y}<br>Colaboradores: %{z}<extra></extra>"
        ))
        
        fig.update_layout(
            annotations=annotations,
            xaxis_title="Desempeño (Performance)",
            yaxis_title="Potencial (Potential)",
            height=500,
            width=500,
            margin=dict(l=40, r=20, t=40, b=40),
            xaxis=dict(tickfont=dict(size=14)),
            yaxis=dict(tickfont=dict(size=14), scaleanchor="x", scaleratio=1),
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"9box_{key_prefix}")
        
        with st.expander("📚 ¿Cómo leer el Mapeo de Talento?"):
            st.markdown("""
            La matriz **9-Box** cruza el desempeño actual con el potencial futuro:
            - **Caja 9 (Alto/Alto):** "Estrellas". Candidatos ideales para sucesión inmediata.
            - **Caja 7/8:** "Talento Emergente". Alto potencial con desempeño sólido.
            - **Caja 1 (Bajo/Bajo):** "Bajo desempeño". Requiere plan de acción o revisión de rol.
            """)
