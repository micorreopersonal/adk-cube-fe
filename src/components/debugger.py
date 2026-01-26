import streamlit as st

def render_debugger():
    """Muestra la respuesta bruta del backend si el modo debugger está activo."""
    if st.session_state.get("show_debugger", False):
        st.write("---")
        with st.expander("🔍 JSON Debugger (Raw Response)", expanded=True):
            if st.session_state.last_api_response:
                st.json(st.session_state.last_api_response)
            else:
                st.info("No hay respuestas registradas todavía.")
