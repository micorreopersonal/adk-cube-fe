# main.py
import streamlit as st
from src.state import init_session, get_user
from src.views.login import render_login
from src.views.dashboard import render_dashboard

# Configuración de página DEBE ser la primera instrucción de Streamlit
st.set_page_config(
    page_title="People Analytics Agent",
    page_icon="src/images/logo.svg",
    layout="wide"
)

from src.styles import apply_custom_css

def main():
    # 0. Aplicar Estilos Premium
    apply_custom_css()

    # 1. Asegurar que el estado existe
    init_session()
    
    # 2. Router: ¿Está logueado?
    user = get_user()
    
    if user is None:
        render_login()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()