import os
from dotenv import load_dotenv
import streamlit as st

# Cargar variables de entorno desde .env (solo para desarrollo local)
load_dotenv()

# Configuración de Backend
# Por defecto ahora apunta a LOCAL para desarrollo.
DEV_URL = "http://127.0.0.1:8080"
# URL de Producción actualizada (adk-sandbox)
PROD_URL = "https://adk-people-analytics-backend-828393973311.us-central1.run.app"

# Usar BACKEND_URL de .env o entorno
# Si estamos en Cloud Run (PYTHON_ENV=production), forzamos PROD_URL si no viene por env.
IS_PROD = os.getenv("PYTHON_ENV", "development") == "production"

if IS_PROD:
    BACKEND_URL = os.getenv("BACKEND_URL", PROD_URL)
else:
    BACKEND_URL = os.getenv("BACKEND_URL", DEV_URL)

if IS_PROD:
    print(f"🌐 Iniciando modo PRODUCCIÓN (Backend: {BACKEND_URL})")
else:
    print(f"🛠️ Modo: DESARROLLO (Backend: {BACKEND_URL})")

# Constante global para controlar visibilidad de debug
SHOW_DEBUG_UI = not IS_PROD
