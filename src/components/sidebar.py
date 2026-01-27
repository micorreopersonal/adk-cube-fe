import streamlit as st
from src.state import logout

def render_sidebar():
    """Renderiza el sidebar con el menú de navegación y botón de logout."""
    with st.sidebar:
        st.title("🛡️ RIMAC | AI")
        st.write("---")
        
        st.write("---")
        
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
        
        st.write("---")
        
        # Toggle para el debugger
        st.session_state.show_debugger = st.toggle("Modo Debugger", value=False)
        
        st.write("---")
        
        # Botón para limpiar historial
        if st.button("🗑️ Limpiar Historial", use_container_width=True, type="secondary", help="Borra la conversación actual para iniciar de cero."):
            st.session_state.messages = []
            # Opcional: Agregar mensaje de bienvenida inicial en el historial
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "¡Hola de nuevo! Historial limpio. ¿En qué puedo ayudarte ahora?"
            })
            st.toast("Historial de chat borrado.", icon="🗑️")
            st.rerun()

        st.write("---")
        if st.button("Cerrar Sesión", width='stretch', type="primary"):
            logout()
