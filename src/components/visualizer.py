import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid

class Visualizer:
    @staticmethod
    def render(content: list):
        """
        Renders a list of visual blocks.
        """
        if not content:
            return

        for block in content:
            block_type = block.get("type")
            payload = block.get("payload")
            
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
                Visualizer._render_plot(block)
                
            elif block_type == "table":
                Visualizer._render_table(payload)
            
            elif block_type == "data_series":
                metadata = block.get("metadata", {})
                Visualizer._render_interactive_series(payload, metadata)
            
            elif block_type == "debug_sql":
                with st.expander("🔍 Ver Query SQL (Debug)", expanded=False):
                    st.code(payload, language="sql")

    @staticmethod
    def _create_line_chart(data, metadata):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.get('months', []),
            y=data.get('rotacion_general', []),
            mode='lines+markers+text',
            name='Rotación General',
            line=dict(color='#EF3340', width=3), # RIMAC Red
            marker=dict(size=8),
            text=[f"{v}%" for v in data.get('rotacion_general', [])],
            textposition="top center"
        ))
        fig.add_trace(go.Scatter(
            x=data.get('months', []),
            y=data.get('rotacion_voluntaria', []),
            mode='lines+markers+text',
            name='Rotación Voluntaria',
            line=dict(color='#B0B0B0', width=3, dash='dot'), # Gris secundario
            marker=dict(size=8),
            text=[f"{v}%" for v in data.get('rotacion_voluntaria', [])],
            textposition="top center"
        ))
        fig.update_layout(
            title=f"Evolución Mensual de Rotación {metadata.get('year', '')}",
            xaxis_title="Mes",
            yaxis_title="Tasa de Rotación (%)",
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        return fig

    @staticmethod
    def _create_bar_chart(data, metadata):
        df_bar = pd.DataFrame({
            'Mes': data.get('months', []),
            'General': data.get('rotacion_general', []),
            'Voluntaria': data.get('rotacion_voluntaria', [])
        })
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_bar['Mes'],
            y=df_bar['General'],
            name='General',
            marker_color='#EF3340', # RIMAC Red
            text=df_bar['General'].apply(lambda x: f"{x}%"),
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            x=df_bar['Mes'],
            y=df_bar['Voluntaria'],
            name='Voluntaria',
            marker_color='#B0B0B0', # Gris neutro
            text=df_bar['Voluntaria'].apply(lambda x: f"{x}%"),
            textposition='auto'
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
    def _render_interactive_series(data: dict, metadata: dict):
        """
        Renders an interactive time-series visualization with tabs for different views.
        """
        if not data:
            return
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["📈 Gráfico de Línea", "📊 Gráfico de Barras", "📋 Tabla Detallada"])
        
        with tab1:
            fig = Visualizer._create_line_chart(data, metadata)
            st.plotly_chart(fig, width='stretch', key=f"line_{str(uuid.uuid4())}")
        
        with tab2:
            fig = Visualizer._create_bar_chart(data, metadata)
            st.plotly_chart(fig, width='stretch', key=f"bar_{str(uuid.uuid4())}")
        
        with tab3:
            # Detailed Table
            df_table = pd.DataFrame({
                'Mes': data.get('months', []),
                'Rotación General (%)': data.get('rotacion_general', []),
                'Rotación Voluntaria (%)': data.get('rotacion_voluntaria', []),
                'Headcount Base': data.get('headcount', []),
                'Total Ceses': data.get('ceses', []),
                'Renuncias': data.get('renuncias', [])
            })
            
            # Download button
            csv = df_table.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"rotacion_mensual_{metadata.get('year', '')}.csv",
                mime="text/csv",
                key=f"dl_series_{str(uuid.uuid4())}"
            )
            
            st.dataframe(df_table, width='stretch', hide_index=True)
            st.caption(f"Total de {len(df_table)} meses registrados.")

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
                    delta_color=final_color
                )

    @staticmethod
    def _render_plot(block: dict):
        subtype = block.get("subtype")
        data = block.get("data", {})
        title = block.get("title", "")
        
        if title:
            st.subheader(title)
            
        try:
            if subtype == "bar":
                fig = px.bar(
                    x=data.get("x"), 
                    y=data.get("y"),
                    color=data.get("category") if "category" in data else None
                )
            elif subtype == "line":
                fig = px.line(x=data.get("x"), y=data.get("y"))
            elif subtype == "pie":
                fig = px.pie(names=data.get("names"), values=data.get("values"))
            else:
                st.warning(f"Tipo de gráfico no soportado: {subtype}")
                return

            st.plotly_chart(fig, width='stretch', key=f"plot_{str(uuid.uuid4())}")
            
        except Exception as e:
            st.error(f"Error renderizando gráfico: {e}")

    @staticmethod
    def _render_table(data: list):
        if data:
            df = pd.DataFrame(data)
            # FIX: Usar un hash determinista del contenido para mantener el estado de los filtros entre reruns.
            # Si usamos uuid.uuid4(), el key cambia cada vez y se pierden los filtros seleccionados.
            import hashlib
            data_hash = hashlib.md5(str(data).encode()).hexdigest()[:8]
            unique_suffix = data_hash
            
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
                potential_filters = [
                    col for col in df.columns 
                    if df[col].dtype == 'object' and df[col].nunique() < 50
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
