# src/views/login.py
import streamlit as st
import os # <--- Importante para leer variables de entorno
from src.security.auth import AuthService
from src.state import set_user

def render_login():
    # Actualizamos el título para ser consistentes con la marca
    st.markdown("### 🔒 Vertex AI Access")
    
    auth = AuthService()
    
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar Sesión")
        
        if submitted:
            user = auth.login(username, password)
            if user:
                set_user(user)
                st.success("Acceso concedido.")
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
    
    # --- LÓGICA DE PRODUCCIÓN ---
    # Solo mostramos los hints si la variable SHOW_LOGIN_HINTS es "True" (comportamiento por defecto).
    # Cuando despliegues en Cloud Run, configuraremos esta variable como "False" en el comando de deploy.
    if os.getenv("SHOW_LOGIN_HINTS", "True") == "True":
        with st.expander("Ayuda para pruebas (Solo Dev)"):
            st.code("User: admin / Pass: p014654 (Admin)\nUser: Paul / Pass: admin123 (Admin)")