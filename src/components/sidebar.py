import streamlit as st
import os
from src.state import logout

def render_sidebar():
    """Renderiza el sidebar con el menú de navegación y botón de logout."""
    with st.sidebar:
        # --- BRANDING ---
        # Priorizar SVG si existe (instrucción explícita del usuario)
        logo_path = "src/images/logo.svg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
        elif os.path.exists("src/images/rimac.png"):
             st.image("src/images/rimac.png", width=180)
        else:
             st.title("🛡️ RIMAC | AI")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- DEBUGGER TOGGLE (TOP for visibility) ---
        from src.config import SHOW_DEBUG_UI
        if SHOW_DEBUG_UI:
             st.caption("🛠️ Configuración Developer")
             st.session_state.show_debugger = st.toggle("Modo Debugger", value=st.session_state.get("show_debugger", True))
             st.divider()

        # --- FILTROS DE SEGMENTO (EXECUTIVE REPORTING) ---
        st.subheader("🎯 Filtros de Talento")
        filtro_talento = st.radio(
            "Foco de Análisis:",
            ["Global (Todos)", "Talento (Score 7-9)", "Hipos (Score 8-9)"],
            index=0,
            key="segment_filter",
            help="Filtra los insights para centrarse en los grupos de talento crítico."
        )
        
        if filtro_talento != "Global (Todos)":
            st.info(f"Focalizando en: **{filtro_talento}**")
        
        st.divider()
        
        # --- ACTIONS FOOTER ---
        # Botón para limpiar historial
        if st.button("🗑️ Limpiar Historial", use_container_width=True, type="secondary", help="Borra la conversación actual para iniciar de cero."):
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "¡Hola de nuevo! Historial limpio. ¿En qué puedo ayudarte ahora?"
            })
            st.toast("Historial de chat borrado.", icon="🗑️")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Cerrar Sesión", use_container_width=True, type="primary"):
            logout()
