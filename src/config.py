import os
from dotenv import load_dotenv
import streamlit as st

# Cargar variables de entorno desde .env (solo para desarrollo local)
load_dotenv()

# Configuración de Backend
# Por defecto ahora apunta a LOCAL para desarrollo.
DEV_URL = "http://127.0.0.1:8080"
PROD_URL = "https://adk-people-analytics-backend-769557418506.us-central1.run.app"

# Usar BACKEND_URL de .env o entorno, si no existe usar local.
BACKEND_URL = os.getenv("BACKEND_URL", DEV_URL)

# Modo de ejecución
IS_PROD = os.getenv("PYTHON_ENV", "development") == "production"

if not IS_PROD:
    # Asegurar que en desarrollo se vea claro la URL que se está usando
    st.sidebar.info(f"🛠️ Modo: DESARROLLO")
    st.sidebar.caption(f"Backend: {BACKEND_URL}")
else:
    print(f"🌐 Iniciando modo PRODUCCIÓN (Backend: {BACKEND_URL})")
