# src/views/login.py
import streamlit as st
import os 
from src.security.auth import AuthService
from src.state import set_user

def render_login():
    # Centered Layout Strategy
    col1, col2, col3 = st.columns([1, 0.8, 1])
    
    with col2:
        # spacer to push content down slightly
        st.write("") 
        st.write("") 
        
        # --- LOGIN CARD ---
        with st.container(border=True):
            # 1. Header: Logo & Title
            col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
            with col_logo_2:
                if os.path.exists("src/images/logo.svg"):
                    st.image("src/images/logo.svg", use_container_width=True)
            
            st.markdown("""
                <div style='text-align: center; margin-bottom: 2rem;'>
                    <h2 style='color: #1A202C; margin-bottom: 0px;'>People Analytics</h2>
                    <p style='color: #718096; font-size: 0.9rem;'>Agente Inteligente de Gestión de Talento</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 2. Form
            auth = AuthService()
            with st.form("login_form", border=False):
                username = st.text_input("Usuario", placeholder="ej. admin")
                password = st.text_input("Contraseña", type="password", placeholder="••••••")
                
                st.write("") # Spacer
                submitted = st.form_submit_button("Ingresar", use_container_width=True)
                
                if submitted:
                    user = auth.login(username, password)
                    if user:
                        set_user(user)
                        st.success("Acceso concedido.")
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")

        # --- FOOTER / DEV HELP ---
        st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.8rem; margin-top: 2rem;'>© 2026 Rimac Seguros y Reaseguros</div>", unsafe_allow_html=True)

        if os.getenv("SHOW_LOGIN_HINTS", "True") == "True":
            with st.expander("🛠️ Credenciales de Prueba"):
                st.code("User: admin / Pass: p014654\nUser: Paul / Pass: admin123")