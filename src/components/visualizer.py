import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Union, Optional, List, Dict, Any
from src.schemas import VisualBlock, KPICard
from src.utils.chart_styles import ChartColors, ChartLayouts

class Visualizer:
    """
    Central component for rendering all visual elements in the application.
    
    Responsibilities:
    1. Orchestration: Iterates through visual blocks and dispatches to specific renderers.
    2. Fault Tolerance: Encapsulates rendering logic in try-except blocks to prevent UI crashes.
    3. Consistency: Applies standardized styles (ChartLayouts, ChartColors) across all visuals.
    4. Interactivity: Manages filtering, searching, and downloads for data components.
    """
    @staticmethod
    def render(content: List[Dict[str, Any]], key_prefix: str = ""):
        """
        Main entry point. Renders a list of visual blocks with Error Boundaries.
        
        Args:
            content: List of visual blocks (dictionaries or Pydantic models).
            key_prefix: Unique string to namespace widgets and keys.
        """
        if not content:
            return

        for idx, raw_block in enumerate(content):
            # --- 1. Contract Layer (Validation) ---
            try:
                # Validate the block structure using Pydantic
                # If raw_block is already a dict, we validate it.
                if isinstance(raw_block, dict):
                   block = VisualBlock(**raw_block)
                else:
                   # Fallback or skip if malformed
                   continue
            except Exception as e:
                # Validation Error: Log but continue rendering other blocks
                # In dev mode, we might want to show this.
                from src.config import SHOW_DEBUG_UI
                if SHOW_DEBUG_UI:
                    st.error(f"❌ Contract Violation (Block #{idx}): {e}")
                continue

            # --- 2. Block Rendering (With Error Boundary) ---
            block_key = f"{key_prefix}_{idx}"
            
            try:
                Visualizer._render_block(block, block_key)
            except Exception as e:
                # --- 3. Error Boundary (Fallback) ---
                st.error(f"⚠️ Error visualizando bloque '{block.type}': {e}")
                # Log full trace for devs
                # st.caption(traceback.format_exc())

    @staticmethod
    def _render_block(block: VisualBlock, block_key: str):
        """
        Dispatches the visual block to the appropriate internal renderer.
        
        Args:
            block: The VisualBlock Pydantic model containing type, payload, and metadata.
            block_key: Unique identifier for widget state stability.
        """
        b_type = block.type
        payload = block.payload
        metadata = block.metadata or {}
        
        if b_type == "text":
            Visualizer._render_text(block)
                
        # --- V2: Semantic Cube Contract ---
        elif b_type == "KPI_ROW":
            # Payload is List[IndicatorInternal]
            Visualizer._render_kpis_v2(payload)

        elif b_type == "CHART":
            # Payload is ChartPayload dict with labels/datasets
            Visualizer._render_chart_v2(payload, block.subtype, metadata, block_key)

        elif b_type == "TABLE":
            # Payload is TablePayload dict with headers/rows
            Visualizer._render_table_v2(payload, metadata, block_key)
            
        # --- V1: Legacy Handover ---
        elif b_type == "kpi_row":
            if isinstance(payload, list):
                 Visualizer._render_kpis(payload) # Legacy renderer
                
        elif b_type == "plot":
            if isinstance(payload, dict):
                 Visualizer._render_plot_block(payload, metadata, block_key) 
                
        elif b_type == "table":
             if isinstance(payload, list): # Legacy is list of dicts
                Visualizer._render_table(payload, key_prefix=block_key)
            
        elif b_type == "data_series":
             if isinstance(payload, dict):
                Visualizer._render_interactive_series(payload, metadata, key_prefix=block_key)
            
        elif b_type == "debug_sql":
            from src.config import SHOW_DEBUG_UI
            if SHOW_DEBUG_UI:
                with st.expander("🔍 Ver Query SQL (Debug)", expanded=False):
                    st.code(str(payload), language="sql")

        elif b_type == "talent_matrix":
             if isinstance(payload, dict):
                Visualizer._render_talent_matrix(payload, key_prefix=block_key)
        
        elif b_type == "churn_alert":
             # Alias for Critical Insight
             st.error(f"⚠️ {payload.get('value', 'Riesgo Detectado')}", icon="🔥")
             
        elif b_type == "metric_delta":
             # Single Metric Rendering
             st.metric(
                label=payload.get("label", "Métrica"),
                value=payload.get("value"),
                delta=payload.get("delta"),
                delta_color=payload.get("delta_color", "normal")
             )
        
        elif b_type == "plotly_chart":
             # Render Plotly JSON directly
             try:
                 fig = go.Figure(payload)
                 st.plotly_chart(fig, use_container_width=True, key=block_key)
             except Exception as e:
                 st.error(f"Error renderizando Plotly: {e}")

        else:
             pass

    @staticmethod
    def _render_text(block: VisualBlock):
        variant = block.variant
        severity = block.severity
        content = block.payload
        if isinstance(content, dict):
            content = content.get("text", str(content))
        
        if variant == "insight":
            if severity == "critical":
                st.error(content, icon="🚨")
            elif severity == "warning":
                st.warning(content, icon="⚠️")
            else:
                st.info(content, icon="ℹ️")
        elif variant == "clarification":
            st.info(content, icon="🤔")
        else:
            st.markdown(content)

    # --- V2 RENDERERS ---

    @staticmethod
    def _render_kpis_v2(kpis: list):
        if not kpis: return
        cols = st.columns(len(kpis))
        for idx, item in enumerate(kpis):
            # Compatibility: Pydantic vs Dict
            if hasattr(item, "dict"): item = item.dict()
            elif hasattr(item, "model_dump"): item = item.model_dump()
            
            with cols[idx]:
                # Map STATUS -> Streamlit Colors
                status_val = (item.get("status") or "standard").upper()
                delta_color = "normal"
                if status_val in ["CRITICAL", "BAD", "RED"]:
                    delta_color = "inverse"
                elif status_val in ["SUCCESS", "GOOD", "GREEN"]:
                    delta_color = "normal"
                elif status_val in ["NEUTRAL", "STANDARD", "BLUE"]:
                    delta_color = "off"
                
                # Render
                st.metric(
                    label=item.get("label"),
                    value=item.get("value"),
                    delta=item.get("delta"),
                    delta_color=delta_color,
                    help=item.get("tooltip")
                )

    @staticmethod
    def format_metric_value(value: Union[float, int, None], fmt: Optional[dict] = None) -> str:
        """
        Format a metric value based on backend format metadata.
        
        Args:
            value: The numeric value to format
            fmt: Format dict with {unit_type, symbol, decimals}
        
        Returns:
            Formatted string (e.g., "25.50%", "S/1,250.00", "462")
        """
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        
        # Default format (percentage with 2 decimals) for backward compatibility
        if not fmt:
            return f"{value:.2f}%"
        
        # Extract format properties
        decimals = fmt.get("decimals", 2)
        symbol = fmt.get("symbol")
        unit_type = fmt.get("unit_type", "percentage")
        
        # Round to specified decimals
        rounded = f"{value:.{decimals}f}"
        
        # Apply symbol based on unit_type
        if symbol:
            if unit_type == "percentage":
                return f"{rounded}{symbol}"  # "25.50%"
            else:  # currency or other prefix symbols
                return f"{symbol}{rounded}"  # "S/1,250.00"
        
        return rounded  # "462" (count without symbol)
    
    @staticmethod
    def _aggregate_small_slices(labels: list, values: list, threshold_percent: float = 0.02) -> tuple:
        """
        Aggregates values smaller than a threshold into an "Others" category.
        """
        if not values or sum(values) == 0:
            return labels, values

        total = sum(values)
        new_labels = []
        new_values = []
        other_sum = 0
        
        for i, val in enumerate(values):
            # Check if val is None (dirty data)
            if val is None: val = 0
            
            if val / total >= threshold_percent:
                new_labels.append(labels[i])
                new_values.append(val)
            else:
                other_sum += val
                
        if other_sum > 0:
            new_labels.append("Otros (Menor Impacto)")
            new_values.append(other_sum)
            
        return new_labels, new_values

    @staticmethod
    def _render_chart_v2(payload: Dict[str, Any], subtype: str, metadata: Dict[str, Any], key_prefix: str):
        """
        Renders standardized charts (Pie, Line, Bar) based on the V2 Payload Schema.
        
        Args:
            payload: Dict containing 'labels' (List[str]) and 'datasets' (List[Dict]).
            subtype: 'PIE', 'LINE', or 'BAR'.
            metadata: Configuration for titles, legends, etc.
            key_prefix: Unique key namespace.
        """
        # Payload: { labels: [], datasets: [{label, data, ...}] }
        if hasattr(payload, "dict"): payload = payload.dict() # Handle Pydantic
        
        labels = payload.get("labels", [])
        datasets = payload.get("datasets", [])
        
        if not datasets:
            st.warning("⚠️ Gráfico sin datos.")
            return

        # --- FILTERING LOGIC ---
        import hashlib
        data_hash = hashlib.md5(str(payload).encode()).hexdigest()[:8]
        
        selected_labels = st.multiselect(
            "🔍 Filtrar Dimensión:",
            options=labels,
            default=labels,
            key=f"filter_v2_{key_prefix}_{data_hash}"
        )
        
        if not selected_labels:
            st.warning("⚠️ Selecciona al menos un elemento.")
            return

        # Apply Filter
        indices = [i for i, label in enumerate(labels) if label in selected_labels]
        filtered_labels = selected_labels
        filtered_datasets = []
        for ds in datasets:
            new_ds = ds.copy()
            new_ds["data"] = [ds["data"][i] for i in indices]
            filtered_datasets.append(new_ds)

        # --- BRANCHING BY SUBTYPE ---
        if subtype and subtype.upper() == "PIE":
            # --- PIE CHART MODE ---
            tab_list = ["🥧 Gráfico de Torta", "📋 Tabla"]
            tabs = st.tabs(tab_list)
            
            with tabs[0]:
                # Assuming first dataset for Pie
                if not filtered_datasets:
                    st.info("No data for Pie Chart")
                else:
                    ds = filtered_datasets[0] # Pie charts typically visualize one series
                    
                    # --- SMART GROUPING (LONG TAIL) ---
                    # Group values < 2% into "Otros" to avoid visual clutter
                    final_labels, final_values = Visualizer._aggregate_small_slices(filtered_labels, ds["data"])
                    
                    # Colores RIMAC (Dynamic)
                    colors = ChartColors.get_colors()
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=final_labels, 
                        values=final_values,
                        hole=0.4, # Donut style by default as it looks more modern
                        marker=dict(colors=colors),
                        textinfo='label+percent',
                        hovertemplate="<b>%{label}</b><br>Valor: %{value}<br>Porcentaje: %{percent}<extra></extra>"
                    )])
                    
                    # Apply Standard Layout
                    layout = ChartLayouts.get_pie_layout(
                        title=metadata.get("title", ""),
                        show_legend=metadata.get("show_legend", True)
                    )
                    fig.update_layout(layout)

                    st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_pie_{data_hash}")
                    
        else:
            # --- DEFAULT MODE (LINE/BAR) ---
            tab_list = ["📈 Línea", "📊 Barras", "📋 Tabla"]
            tabs = st.tabs(tab_list)
            
            # Colors
            # Colors
            COLORS = ChartColors.get_colors()
            
            # --- TAB 1 & 2: Charts ---
            for tab_idx, chart_type_target in enumerate(["LINE", "BAR"]):
                with tabs[tab_idx]:
                    fig = go.Figure()
                    for idx, ds in enumerate(filtered_datasets):
                        ds_label = ds.get("label", f"Serie {idx+1}")
                        ds_data = ds.get("data", [])
                        color = ds.get("color") or COLORS[idx % len(COLORS)]
                        
                        # Extract format metadata from dataset
                        ds_format = ds.get("format")
                        if ds_format and hasattr(ds_format, "dict"):
                            ds_format = ds_format.dict()
                        
                        if chart_type_target == "BAR":
                            fig.add_trace(go.Bar(
                                x=filtered_labels,
                                y=ds_data,
                                name=ds_label,
                                marker_color=color,
                                text=[Visualizer.format_metric_value(v, ds_format) for v in ds_data],
                                textposition="auto"
                            ))
                        else: # LINE
                            fig.add_trace(go.Scatter(
                                x=filtered_labels,
                                y=ds_data,
                                mode='lines+markers+text',
                                name=ds_label,
                                line=dict(color=color, width=3),
                                marker=dict(size=8),
                                text=[Visualizer.format_metric_value(v, ds_format) for v in ds_data],
                                textposition="top center"
                            ))

                    
                    # Apply Standard Cartesian Layout
                    layout = ChartLayouts.get_cartesian_layout(
                        title=metadata.get("title", ""),
                        x_label="Dimension",
                        y_label=metadata.get("y_axis_label", "Valor"),
                        show_legend=metadata.get("show_legend", True)
                    )
                    fig.update_layout(layout)
                    st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_{chart_type_target}_{data_hash}")

        # --- TABLE TAB (Shared Logic) ---
        # The table tab index depends on the mode
        table_tab_index = 1 if (subtype and subtype.upper() == "PIE") else 2
        
        with tabs[table_tab_index]:
            # Reconstruct Table from Labes + Datasets (Filtered)
            table_dict = {"Eje": filtered_labels}
            for ds in filtered_datasets:
                ds_label = ds.get("label", "Serie")
                table_dict[ds_label] = ds.get("data", [])
            
            df_table = pd.DataFrame(table_dict)
            st.dataframe(df_table, use_container_width=True, hide_index=True)
            
            # Download Button
            csv = df_table.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"reporte_{key_prefix}.csv",
                mime='text/csv',
                key=f"dl_{key_prefix}_{data_hash}"
            )

    @staticmethod
    def _render_table_v2(payload: Dict[str, Any], metadata: Dict[str, Any], key_prefix: str):
        """
        Renders a rich interactive table with client-side filtering and search.
        
        Args:
            payload: Dict containing 'headers' (List[str]) and 'rows' (List[List]).
            metadata: Configuration for title and column formats.
            key_prefix: Unique namespace.
        """
        # Payload: { headers: [], rows: [] }
        if hasattr(payload, "dict"): payload = payload.dict()
        
        headers = payload.get("headers", [])
        rows = payload.get("rows", [])
        
        if not headers or not rows:
            st.warning("⚠️ Tabla sin datos.")
            return
        
        # Create DataFrame
        df_original = pd.DataFrame(rows, columns=headers)
        df = df_original.copy()  # Working copy for filters
        
        # --- TITLE (from metadata or can be passed from summary) ---
        title = metadata.get("title", "")
        if title:
            st.markdown(f"#### {title}")
        
        # --- FILTERS IN EXPANDER ---
        with st.expander("🔍 **Filtros Avanzados**", expanded=False):
            # Detect categorical columns (string types with reasonable unique values)
            filter_cols = []
            for col in headers:
                unique_vals = df_original[col].dropna().unique()
                if len(unique_vals) < 50 and df_original[col].dtype == 'object':
                    filter_cols.append(col)
            
            if filter_cols:
                st.caption("Selecciona valores para filtrar. Deja vacío para ver todos.")
                
                # Create multiselect filters in columns (up to 3 per row for better layout)
                cols_per_row = min(3, len(filter_cols))
                
                active_filters = {}
                for row_idx in range(0, len(filter_cols), cols_per_row):
                    filter_row = filter_cols[row_idx:row_idx + cols_per_row]
                    cols = st.columns(len(filter_row))
                    
                    for idx, col_name in enumerate(filter_row):
                        with cols[idx]:
                            unique_values = sorted(df_original[col_name].dropna().unique().tolist())
                            selected = st.multiselect(
                                f"{col_name}",
                                options=unique_values,
                                default=[],  # EMPTY BY DEFAULT
                                key=f"filter_{key_prefix}_{col_name}",
                                placeholder="Todos"
                            )
                            if selected:  # Only apply if user selected something
                                active_filters[col_name] = selected
                
                # Apply all active filters
                for col_name, selected_values in active_filters.items():
                    df = df[df[col_name].isin(selected_values)]
            
            # --- SEARCH BAR (Global text search) ---
            st.markdown("---")
            search_term = st.text_input(
                "🔎 Búsqueda por texto:", 
                key=f"search_{key_prefix}",
                placeholder="Buscar en cualquier columna..."
            )
            
            if search_term:
                mask = df.astype(str).apply(
                    lambda row: row.str.contains(search_term, case=False, na=False).any(), 
                    axis=1
                )
                df = df[mask]
        
        # --- STATS ---
        total_records = len(df_original)
        filtered_records = len(df)
        
        if filtered_records < total_records:
            st.info(f"📊 Mostrando **{filtered_records}** de **{total_records}** registros (filtrado activo)")
        else:
            st.caption(f"📊 **{total_records}** registros totales")
        
        # --- FORMAT NUMERIC COLUMNS TO 2 DECIMALS ---
        # Apply formatting to numeric columns (likely rotation rates)
        for col in df.columns:
            if df[col].dtype in ['float64', 'float32']:
                # Format to 2 decimals for display
                df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else x)
        
        # --- RENDER TABLE ---
        st.dataframe(df, use_container_width=True, hide_index=True, height=400)
        
        # --- DOWNLOAD BUTTON ---
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=csv,
            file_name=f"{key_prefix}_export.csv",
            mime='text/csv',
            key=f"dl_table_{key_prefix}",
            use_container_width=True
        )

    @staticmethod
    def _detect_x_axis(data: Dict[str, Any]) -> Optional[str]:
        """Helper to find the likely x-axis key."""
        # Priority 1: 'months' for backward compatibility
        if 'months' in data: return 'months'
        # Priority 2: Common categorical keys
        for key in ['division', 'area', 'uo', 'category', 'names', 'labels', 'x', 'anio', 'year', 'periodo']:
            if key in data: return key
        # Priority 3: First key that is a list of strings (heuristic)
        for key, val in data.items():
            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], str):
                return key
        return None

    @staticmethod
    def _get_plotting_keys(data: Dict[str, Any], x_key: str, metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """Determines which series to plot based on strict metadata or heuristics."""
        if metadata and metadata.get("series_names"):
            return list(metadata.get("series_names").keys())
        # Fallback: Exclude known non-metric keys
        return [k for k in data.keys() if k not in [x_key, 'headcount', 'ceses', 'renuncias', 'involuntarios', 'anio', 'year', 'periodo']]

    @staticmethod
    def _create_line_chart(data: Dict[str, Any], metadata: Dict[str, Any]) -> go.Figure:
        """
        Generates a Plotly Line Chart from normalized data.
        
        Features:
        - Supports multiple series per X-axis.
        - Handles grouping (grouped lines by category).
        - Applies semantic styling (e.g., dotted lines for 'voluntary' turnover).
        
        Args:
            data: Standardized data dictionary.
            metadata: Chart configuration (titles, labels).
            
        Returns:
            go.Figure: The configured Plotly figure.
        """
        fig = go.Figure()
        x_key = Visualizer._detect_x_axis(data) or 'months'
        x_values = data.get(x_key, [])
        
        # Determine strict list of metrics to plot
        keys = Visualizer._get_plotting_keys(data, x_key, metadata)
        
        # Check for Grouping (Long Format)
        # If X-axis has duplicates, we likely need to group by another column (e.g. anio)
        has_duplicates = len(x_values) != len(set(x_values))
        group_col = None
        
        if has_duplicates:
             # Find candidate: not X, not a metric
             candidates = [k for k in data.keys() if k != x_key and k not in keys]
             if candidates:
                 group_col = candidates[0] # Take first candidate like 'anio'

        # Paleta de colores RIMAC y complementarios
        COLORS = ChartColors.get_colors()
        
        if group_col:
            # --- Grouped Line Chart ---
            unique_groups = sorted(list(set(data[group_col])))
            for g_idx, group_val in enumerate(unique_groups):
                # Filter indices
                indices = [i for i, x in enumerate(data[group_col]) if x == group_val]
                
                for k_idx, key in enumerate(keys):
                    # Filter data
                    y_subset = [data[key][i] for i in indices]
                    x_subset = [data[x_key][i] for i in indices]
                    
                    series_name = metadata.get("series_names", {}).get(key, key)
                    trace_name = f"{series_name} ({group_val})"
                    
                    color = COLORS[(g_idx * len(keys) + k_idx) % len(COLORS)]
                    
                    fig.add_trace(go.Scatter(
                        x=x_subset,
                        y=y_subset,
                        mode='lines+markers+text',
                        name=trace_name,
                        line=dict(color=color, width=3),
                        text=[f"{v:.1f}%" if isinstance(v, (int, float)) and v < 100 else v for v in y_subset],
                        textposition="top center",
                        hovertemplate=f"<b>{trace_name}</b><br>{x_key}: %{{x}}<br>Valor: %{{y}}<extra></extra>"
                    ))
        else:
            # --- Standard Line Chart ---
            for idx, key in enumerate(keys):
                series_data = data[key]
                color = COLORS[idx % len(COLORS)]
                
                # Detect special semantics
                line_style = dict(color=color, width=3)
                marker_symbol = 'circle'
                if "voluntaria" in key.lower():
                    line_style.update({'dash': 'dot', 'width': 2})
                    marker_symbol = 'circle-open'
                elif "involuntaria" in key.lower():
                    line_style.update({'dash': 'dashdot', 'width': 2})
                    marker_symbol = 'diamond-open'

                series_name = metadata.get("series_names", {}).get(key, key)

                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=series_data,
                    mode='lines+markers+text',
                    name=series_name,
                    line=line_style,
                    marker=dict(size=8, symbol=marker_symbol),
                    text=[f"{v:.2f}%" if isinstance(v, (int, float)) else v for v in series_data],
                    textposition="top center",
                    hovertemplate=f"<b>{series_name}</b><br>{x_key.capitalize()}: %{{x}}<br>Valor: %{{y}}%<extra></extra>"
                ))

        layout = ChartLayouts.get_cartesian_layout(
            title=metadata.get('title', f"Dinámica {metadata.get('year', '')}"),
            x_label=x_key.capitalize(),
            y_label=metadata.get('y_label', "Valor"),
            show_legend=True
        )
        fig.update_layout(layout)
        return fig

    @staticmethod
    def _create_bar_chart(data: Dict[str, Any], metadata: Dict[str, Any]) -> go.Figure:
        """
        Generates a Plotly Bar Chart (Grouped or Stacked).
        
        Args:
            data: Standardized data dictionary.
            metadata: Chart configuration.
            
        Returns:
            go.Figure: The configured Plotly figure.
        """
        fig = go.Figure()
        x_key = Visualizer._detect_x_axis(data) or 'months'
        x_values = data.get(x_key, [])
        
        keys = Visualizer._get_plotting_keys(data, x_key, metadata)
        
        # Check for Grouping
        has_duplicates = len(x_values) != len(set(x_values))
        group_col = None
        if has_duplicates:
            candidates = [k for k in data.keys() if k != x_key and k not in keys]
            if candidates: group_col = candidates[0]

        COLORS = ChartColors.get_colors()
        
        if group_col:
            # --- Grouped Bar Chart ---
            # Sort X-Axis to ensure groups are clustered properly on categorical axes
            # Actually, standard bar charts handle categories. 
            # We just need to add traces per Group.
            unique_groups = sorted(list(set(data[group_col])))
            
            for g_idx, group_val in enumerate(unique_groups):
                indices = [i for i, x in enumerate(data[group_col]) if x == group_val]
                
                for k_idx, key in enumerate(keys):
                    y_subset = [data[key][i] for i in indices]
                    x_subset = [data[x_key][i] for i in indices]
                    
                    series_name = metadata.get("series_names", {}).get(key, key)
                    trace_name = f"{series_name} ({group_val})" if len(keys) > 1 else str(group_val)
                    
                    if len(keys) == 1:
                         # Single metric, group is the legend
                         color = COLORS[g_idx % len(COLORS)]
                    else:
                         color = COLORS[k_idx % len(COLORS)] # Metric is color, or mix? Let's use group color for simple comparison

                    fig.add_trace(go.Bar(
                        x=x_subset,
                        y=y_subset,
                        name=trace_name,
                        marker_color=color,
                        text=[f"{v:.1f}" if isinstance(v, (int, float)) else v for v in y_subset],
                        textposition='auto',
                        hovertemplate=f"<b>{trace_name}</b><br>{x_key}: %{{x}}<br>Valor: %{{y}}<extra></extra>"
                    ))
        else:
            # --- Standard Bar Chart ---
            for idx, key in enumerate(keys):
                series_data = data[key]
                color = COLORS[idx % len(COLORS)]
                series_name = metadata.get("series_names", {}).get(key, key)
                
                fig.add_trace(go.Bar(
                    x=x_values,
                    y=series_data,
                    name=series_name,
                    marker_color=color,
                    text=[f"{v:.1f}%" if isinstance(v, (int, float)) else v for v in series_data],
                    textposition='auto',
                    hovertemplate=f"<b>{series_name}</b><br>{x_key.capitalize()}: %{{x}}<br>Valor: %{{y}}%<extra></extra>"
                ))

        layout = ChartLayouts.get_cartesian_layout(
            title=metadata.get('title', f"Comparativa {metadata.get('year', '')}"),
            x_label=x_key.capitalize(),
            y_label=metadata.get('y_label', "Valor"),
            show_legend=True
        )
        layout['barmode'] = 'group' # Specific to Bar Charts
        fig.update_layout(layout)
        return fig

    @staticmethod
    def get_figures_from_content(content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrae figuras de bloques visuales para su uso en reportes (PDF).
        """
        figures = []
        for block in content:
            if block.get("type") == "data_series":
                payload = block.get("payload", {})
                metadata = block.get("metadata", {})
                
                # Generamos ambas vistas para el reporte
                fig_line = Visualizer._create_line_chart(payload, metadata)
                figures.append({"title": "Tendencia", "fig": fig_line})
                
                fig_bar = Visualizer._create_bar_chart(payload, metadata)
                figures.append({"title": "Comparativa", "fig": fig_bar})
                
            elif block.get("type") == "plot" and "data" in block:
                # Reconstruir plot simple (limitado por ahora)
                pass 
        return figures

    @staticmethod
    def _normalize_wide_data(data: dict) -> dict:
        """
        Attempts to transform 'wide' comparison data (e.g. anio_2024, ceses_2024, anio_2025, ceses_2025)
        into a standard 'long' format (e.g. Periodo: [2024, 2025], Ceses: [851, 1130]).
        """
        import re
        
        # 1. Identify distinct years/periods from keys like 'anio_2024', 'year_2025'
        years = set()
        pattern = re.compile(r'.*_(20\d{2})$') # Matches suffixes like _2024
        
        for key in data.keys():
            match = pattern.search(key)
            if match:
                years.add(match.group(1))
        
        if not years:
            return None
            
        sorted_years = sorted(list(years))
        
        # 2. Reconstruct metrics
        # We need to find the "base" metric names. 
        # e.g. 'ceses_2024' -> base 'ceses'
        normalized = {"Periodo": sorted_years}
        
        # Find all metric bases
        metric_bases = set()
        for key in data.keys():
            for y in sorted_years:
                if key.endswith(f"_{y}"):
                    base = key.replace(f"_{y}", "")
                    # Filter out the dimension keys themselves (anio_, year_)
                    if base not in ['anio', 'year', 'periodo']:
                        metric_bases.add(base)
        
        if not metric_bases:
             return None

        # 3. Build lists
        for metric in metric_bases:
            values = []
            for y in sorted_years:
                # Construct key e.g. ceses_2024
                # Data values are lists like [851], so take [0]
                col_key = f"{metric}_{y}"
                val_list = data.get(col_key, [None])
                val = val_list[0] if val_list else None
                values.append(val)
            normalized[metric] = values
            
        return normalized

    @staticmethod
    def _render_interactive_series(data: Dict[str, Any], metadata: Dict[str, Any], key_prefix: str = ""):
        """
        Renders a multi-tab view (Line, Bar, Table) for a dataset.
        Includes automatic X-axis detection and dynamic filtering.
        """
        if not data:
            return
            
        # --- X-Axis Detection ---
        x_key = Visualizer._detect_x_axis(data)
        
        # Fallback: Try Wide Format Normalization
        if not x_key:
            normalized = Visualizer._normalize_wide_data(data)
            if normalized:
                data = normalized
                x_key = "Periodo" # We created this key
        
        if not x_key:
             st.warning("⚠️ No se pudo detectar una serie válida para el Eje X.")
             return
             
        x_values = data.get(x_key, [])
        target_len = len(x_values)
        
        # Identificar series de datos (excluyendo eje X)
        all_keys = [k for k in data.keys() if k != x_key]
        
        # --- Normalización Dinámica ---
        for k in all_keys:
            current_list = data.get(k, [])
            if current_list is None: current_list = []
            current_list = list(current_list)
            
            if len(current_list) < target_len:
                current_list.extend([None] * (target_len - len(current_list)))
                data[k] = current_list
            elif len(current_list) > target_len:
                data[k] = current_list[:target_len]
        
        import hashlib
        data_hash = hashlib.md5(str(data).encode()).hexdigest()[:8]
        
        selected_items = st.multiselect(
            f"📅 Filtrar {x_key.capitalize()}:",
            options=x_values,
            default=x_values,
            key=f"filter_{x_key}_{data_hash}_{key_prefix}"
        )
        
        # Aplicar filtro dinámicamente
        filtered_data = {x_key: []}
        if selected_items:
            indices = [i for i, m in enumerate(x_values) if m in selected_items]
            filtered_data[x_key] = selected_items
            for k in all_keys:
                 filtered_data[k] = [data[k][i] for i in indices]
        
        if not selected_items:
             st.warning("⚠️ Selecciona al menos un elemento para visualizar.")
             return

        tab1, tab2, tab3 = st.tabs(["📈 Gráfico de Línea", "📊 Gráfico de Barras", "📋 Tabla Detallada"])
        
        with tab1:
            fig = Visualizer._create_line_chart(filtered_data, metadata)
            st.plotly_chart(fig, use_container_width=True, key=f"line_{data_hash}_{key_prefix}")
        
        with tab2:
            fig = Visualizer._create_bar_chart(filtered_data, metadata)
            st.plotly_chart(fig, use_container_width=True, key=f"bar_{data_hash}_{key_prefix}")
        
        with tab3:
            # Construcción dinámica del DataFrame para la tabla
            table_dict = {x_key.capitalize(): filtered_data[x_key]}
            for k in all_keys:
                # Formatear el nombre de la columna
                col_name = k.replace('_', ' ').title()
                if any(x in k.lower() for x in ['rotacion', 'tasa', 'porcentaje']):
                    col_name += ' (%)'
                table_dict[col_name] = filtered_data[k]
                
            df_table = pd.DataFrame(table_dict)
            
            csv = df_table.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"reporte_{x_key}_{metadata.get('year', '')}.csv",
                mime="text/csv",
                key=f"dl_series_{data_hash}_{key_prefix}"
            )
            
            st.dataframe(df_table, use_container_width=True, hide_index=True)
            st.caption(f"Mostrando {len(df_table)} elementos seleccionados.")

    @staticmethod
    def _render_kpis(kpis: list):
        if not kpis:
            return
        cols = st.columns(len(kpis))
        for idx, kpi in enumerate(kpis):
            # Compatibility: Handle Pydantic Models (from new Engine) vs Dicts (legacy)
            if hasattr(kpi, "dict"): 
                kpi = kpi.dict()
            elif hasattr(kpi, "model_dump"): # Pydantic v2
                kpi = kpi.model_dump()
                
            with cols[idx]:
                # Streamlit.metric solo acepta: 'normal', 'inverse', 'off'
                # Mapeo de intención semántica (Colors from backend -> Streamlit types)
                # Mapping: red->inverse (red), green->normal (green), blue/standard->off (gray)
                raw_color = str(kpi.get("color", "standard")).lower()
                
                final_color = "normal"
                if raw_color in ["red", "inverse", "critical"]:
                    final_color = "inverse"
                elif raw_color in ["green", "good"]:
                    final_color = "normal"
                elif raw_color in ["blue", "standard", "off", "neutral"]:
                    final_color = "off"
                
                st.metric(
                    label=kpi.get("label"),
                    value=kpi.get("value"),
                    delta=kpi.get("delta"),
                    delta_color=final_color,
                    help=kpi.get("tooltip_data")
                )

    @staticmethod
    def _render_plot_block(payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None, key_prefix: str = ""):
        """
        Legacy/Simplified renderer for direct plot payloads.
        Supports automatic chart switching (Bar/Line/Pie/Area).
        """
        subtype = payload.get("subtype", "bar")
        data = payload.get("data", {})
        title = payload.get("title", "")
        if metadata:
             # Metadata might override or augment
             title = metadata.get("title", title)
             
        # Try to get axis labels from data keys if possible, or metadata
        x_label = payload.get("x_label") or data.get("x_label") or "Categoría"
        y_label = payload.get("y_label") or data.get("y_label") or "Valor"
        
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
                    hover_data=hover_data,
                    color_discrete_sequence=ChartColors.get_colors()
                )
            elif chart_type == "Línea":
                fig = px.line(
                    df, x="x", y="y",
                    markers=True,
                    text="y",
                    labels=labels_map,
                    hover_data=hover_data,
                    color_discrete_sequence=ChartColors.get_colors()
                )
                fig.update_traces(textposition="top center")
            elif chart_type == "Pie":
                fig = px.pie(
                    df, names="x", values="y",
                    title=f"Distribución - {title}",
                    hover_data=hover_data,
                    labels=labels_map,
                    color_discrete_sequence=ChartColors.get_colors()
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
            elif chart_type == "Area":
                fig = px.area(
                    df, x="x", y="y",
                    markers=True,
                    labels=labels_map,
                    hover_data=hover_data,
                    color_discrete_sequence=ChartColors.get_colors()
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

                st.plotly_chart(fig, use_container_width=True, key=f"plot_{data_hash}_{key_prefix}")

        except Exception as e:
            st.error(f"Error renderizando gráfico mejorado: {e}")

    # --- HELPER: Dynamic Metric Formatting ---
    @staticmethod
    def format_metric_value(value: Union[float, int, None], fmt: Optional[dict] = None) -> str:
        """
        Format a metric value based on backend format metadata.
        
        Args:
            value: The numeric value to format
            fmt: Format dict with {unit_type, symbol, decimals}
        
        Returns:
            Formatted string (e.g., "25.50%", "S/1,250.00", "462")
        """
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        
        # Default format (percentage with 2 decimals) for backward compatibility
        if not fmt:
            return f"{value:.2f}%"
        
        # Extract format properties
        decimals = fmt.get("decimals", 2)
        symbol = fmt.get("symbol")
        unit_type = fmt.get("unit_type", "percentage")
        
        # Round to specified decimals
        rounded = f"{value:.{decimals}f}"
        
        # Apply symbol based on unit_type
        if symbol:
            if unit_type == "percentage":
                return f"{rounded}{symbol}"  # "25.50%"
            else:  # currency or other prefix symbols
                return f"{symbol}{rounded}"  # "S/1,250.00"
        
        return rounded  # "462" (count without symbol)
    
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
                [0, "#F8F9FA"],          # Empty
                [1.0, ChartColors.get_colors()[0]] # Primary Color (Dynamic)
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
        
        st.plotly_chart(fig, width="stretch", key=f"9box_{key_prefix}")
        
        with st.expander("📚 ¿Cómo leer el Mapeo de Talento?"):
            st.markdown("""
            La matriz **9-Box** cruza el desempeño actual con el potencial futuro:
            - **Caja 9 (Alto/Alto):** "Estrellas". Candidatos ideales para sucesión inmediata.
            - **Caja 7/8:** "Talento Emergente". Alto potencial con desempeño sólido.
            - **Caja 1 (Bajo/Bajo):** "Bajo desempeño". Requiere plan de acción o revisión de rol.
            """)
