import os
from dotenv import load_dotenv
import streamlit as st

# Cargar variables de entorno desde .env
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    st.error("Error: La variable de entorno BACKEND_URL no está configurada en el archivo .env.")
    st.stop()
