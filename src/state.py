# src/state.py
import streamlit as st
import time
from typing import Dict, List, Any, Optional
from src.security.models import UserProfile

def init_session():
    """
    Inicializa el Estado Atómico de la aplicación.
    Garantiza que todas las claves críticas existan antes de cualquier renderizado.
    """
    # 1. Identidad y Seguridad
    if "user" not in st.session_state:
        st.session_state.user = None
        
    # 2. Memoria del Chat (Atomicidad)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [] # Lista de dicts: {'role', 'content', 'metadata'}
        
    # Compatibilidad con código legado que busca 'messages'
    if "messages" not in st.session_state:
        st.session_state.messages = st.session_state.chat_history 



    # 4. Telemetría y Debugging
    if "last_request_payload" not in st.session_state:
        st.session_state.last_request_payload = {}
        
    if "last_api_response" not in st.session_state:
        st.session_state.last_api_response = {}

    # 5. Backend Sync Heartbeat
    if "backend_sync" not in st.session_state:
        st.session_state.backend_sync = time.time()

def get_user() -> Optional[UserProfile]:
    return st.session_state.user

def set_user(user: UserProfile):
    st.session_state.user = user



def logout():
    st.session_state.clear() # Limpieza total para seguridad
    st.rerun()
