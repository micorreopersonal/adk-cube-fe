import os
from dotenv import load_dotenv
import streamlit as st

# Cargar variables de entorno desde .env (solo para desarrollo local)
load_dotenv()

# Configuración de Backend
# Por defecto ahora apunta a LOCAL para desarrollo.
DEV_URL = "http://127.0.0.1:8000"
# URL de Producción actualizada (adk-sandbox)
PROD_URL = "https://adk-people-analytics-backend-qyezaun3zq-uc.a.run.app"

# APP_MODE: 'development' o 'production'
# Este es el "Master Switch" que pidió el usuario.
APP_MODE = os.getenv("APP_MODE", os.getenv("PYTHON_ENV", "development")).lower()
IS_PROD = APP_MODE == "production"

if IS_PROD:
    BACKEND_URL = os.getenv("BACKEND_URL", PROD_URL)
    print(f"🌐 MODO NUBE ACTIVO (Backend: {BACKEND_URL})")
else:
    BACKEND_URL = os.getenv("BACKEND_URL", DEV_URL)
    print(f"🛠️ MODO LOCAL ACTIVO (Backend: {BACKEND_URL})")

# Constante global para controlar visibilidad de debug (Inversa a IS_PROD)
SHOW_DEBUG_UI = not IS_PROD
