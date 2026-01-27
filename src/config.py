import os
from dotenv import load_dotenv
import streamlit as st

# Cargar variables de entorno desde .env
load_dotenv()

# Default to Production if not set
PROD_URL = "https://adk-people-analytics-backend-769557418506.us-central1.run.app"
BACKEND_URL = os.getenv("BACKEND_URL", PROD_URL)
