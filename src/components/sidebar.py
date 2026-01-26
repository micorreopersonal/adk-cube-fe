import streamlit as st
from src.state import logout

def render_sidebar():
    """Renderiza el sidebar con el menú de navegación y botón de logout."""
    with st.sidebar:
        st.title("🤖 ADK Frontend")
        st.write("---")
        
        # Toggle para el debugger
        st.session_state.show_debugger = st.toggle("Modo Debugger", value=False)
        
        st.write("---")
        if st.button("Cerrar Sesión", use_container_width=True, type="primary"):
            logout()
