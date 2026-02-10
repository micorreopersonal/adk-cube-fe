# src/examples/executive_report_streaming_example.py
"""
Example integration of SSE-based Executive Report Streaming.

This file demonstrates how to integrate the streaming component into your dashboard.
Copy the relevant sections to your actual dashboard implementation.
"""

import streamlit as st
from src.components.executive_report_stream import ExecutiveReportStreamer
from src.services.api_client import ApiClient


def example_integration_in_chat():
    """
    Example 1: Detect executive report requests in chat and use streaming.
    """
    message = st.text_input("Tu consulta:", key="chat_input")
    
    if st.button("Enviar"):
        # Detect if message is requesting executive report
        keywords = ["reporte ejecutivo", "informe ejecutivo", "executive report"]
        is_executive_report = any(kw in message.lower() for kw in keywords)
        
        if is_executive_report:
            # Extract period (simple example - enhance with regex)
            period = "2025"  # Default
            if "2024" in message:
                period = "2024"
            elif any(f"2025-{m:02d}" in message for m in range(1, 13)):
                # Extract month if specified
                for m in range(1, 13):
                    if f"2025-{m:02d}" in message:
                        period = f"2025-{m:02d}"
                        break
            
            st.markdown("### 📊 Generando Reporte Ejecutivo con Streaming")
            
            # Use streaming component
            ExecutiveReportStreamer.render(
                period=period,
                user=st.session_state.user
            )
        else:
            # Normal chat flow
            api_client = ApiClient()
            response = api_client.send_chat(message, st.session_state.user)
            
            if response:
                # Render normal response
                from src.components.visualizer import Visualizer
                content = response.get("content", [])
                Visualizer.render(content, key_prefix="chat")


def example_dedicated_interface():
    """
    Example 2: Dedicated interface for executive reports.
    """
    st.title("📊 Reportes Ejecutivos")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        period = st.text_input(
            "Período:",
            value="2025",
            help="Formato: YYYY o YYYY-MM (ej. 2025 o 2025-01)"
        )
    
    with col2:
        uo2_filter = st.text_input(
            "Filtro UO2 (opcional):",
            value="",
            help="Filtrar por división específica"
        )
    
    if st.button("🚀 Generar Reporte Streaming"):
        ExecutiveReportStreamer.render(
            period=period,
            user=st.session_state.user,
            uo2_filter=uo2_filter if uo2_filter else None
        )


def example_sidebar_button():
    """
    Example 3: Add quick access button in sidebar.
    """
    # In your sidebar component
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Acciones Rápidas")
    
    if st.sidebar.button("📊 Reporte Ejecutivo 2025", use_container_width=True):
        # Set flag in session state
        st.session_state.trigger_executive_report = True
        st.session_state.report_period = "2025"
        st.rerun()
    
    # In your main content area
    if st.session_state.get("trigger_executive_report"):
        st.session_state.trigger_executive_report = False  # Reset flag
        
        ExecutiveReportStreamer.render(
            period=st.session_state.report_period,
            user=st.session_state.user
        )


# ------------------------------
# Testing & Validation Examples
# ------------------------------

def test_sse_parsing():
    """
    Test SSE data parsing logic.
    """
    sample_sse_lines = [
        "data: {\"section_id\": \"header\", \"blocks\": [], \"progress\": 0}",
        "",
        "data: {\"section_id\": \"headline\", \"blocks\": [{\"type\": \"text\", \"payload\": \"Test\"}], \"progress\": 14}",
        ""
    ]
    
    import json
    for line in sample_sse_lines:
        if line.startswith("data: "):
            data_str = line[6:]
            section_data = json.loads(data_str)
            print(f"Parsed: {section_data['section_id']} - {section_data['progress']}%")


if __name__ == "__main__":
    # Run examples
    st.set_page_config(page_title="SSE Streaming Examples", layout="wide")
    
    example_choice = st.sidebar.radio(
        "Select Example:",
        ["Chat Integration", "Dedicated Interface", "Sidebar Button"]
    )
    
    if example_choice == "Chat Integration":
        example_integration_in_chat()
    elif example_choice == "Dedicated Interface":
        example_dedicated_interface()
    elif example_choice == "Sidebar Button":
        example_sidebar_button()
