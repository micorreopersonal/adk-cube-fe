# src/state.py
import streamlit as st
from src.security.models import UserProfile

def init_session():
    """Inicializa las variables de estado si no existen"""
    if "user" not in st.session_state:
        st.session_state.user = None

def get_user() -> UserProfile:
    return st.session_state.user

def set_user(user: UserProfile):
    st.session_state.user = user

def logout():
    st.session_state.user = None
    st.rerun()