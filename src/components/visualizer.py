import streamlit as st
import pandas as pd
import plotly.express as px

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
                st.markdown(payload)
                
            elif block_type == "kpi_row":
                Visualizer._render_kpis(payload)
                
            elif block_type == "plot":
                Visualizer._render_plot(block)
                
            elif block_type == "table":
                Visualizer._render_table(payload)

    @staticmethod
    def _render_kpis(kpis: list):
        if not kpis:
            return
        cols = st.columns(len(kpis))
        for idx, kpi in enumerate(kpis):
            with cols[idx]:
                st.metric(
                    label=kpi.get("label"),
                    value=kpi.get("value"),
                    delta=kpi.get("delta"),
                    delta_color=kpi.get("color", "normal")
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

            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error renderizando gráfico: {e}")

    @staticmethod
    def _render_table(data: list):
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
