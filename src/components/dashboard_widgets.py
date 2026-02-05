# src/components/dashboard_widgets.py
import streamlit as st
from src.views.dashboard_content import (
    WELCOME_TITLE, 
    WELCOME_SUBTITLE, 
    ACTION_CARDS, 
    SUGGESTIONS_HEADER, 
    SUGGESTIONS_COLUMNS
)

def render_welcome_header(user, api_client):
    """Renderiza el encabezado de bienvenida y botón reiniciar."""
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        # Extraer primer nombre
        first_name = user.name.split(' ')[0]
        st.markdown(f"""
            <h1 style='color: #1A202C; font-size: 2.2rem;'>{WELCOME_TITLE.format(name=first_name)}</h1>
            <p style='color: #718096; font-size: 1.1rem;'>
                {WELCOME_SUBTITLE}
            </p>
        """, unsafe_allow_html=True)
    
    with h_col2:
        st.write("") 
        st.write("")
        if st.button("🗑️ Reiniciar", help="Borrar memoria del agente y limpiar chat", use_container_width=True):
             if api_client.reset_session(user):
                 st.session_state.messages = []
                 st.session_state.last_api_response = None
                 st.toast("Memoria del agente borrada.", icon="🧹")
                 st.rerun()
             else:
                 st.toast("Error al reiniciar sesión.", icon="❌")
    
    st.markdown("<br>", unsafe_allow_html=True)

def render_action_cards(user):
    """Renderiza las tarjetas de acción rápida."""
    # Solo mostrar si NO hay mensajes (estado inicial)
    if st.session_state.get("messages"):
        return

    cols = st.columns(len(ACTION_CARDS))
    is_privileged = user.role in ['admin', 'hr_bp']

    for idx, card in enumerate(ACTION_CARDS):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"### {card['title']}")
                st.caption(card['caption'])
                
                required_roles = card['role_required']
                # Si no requiere roles (None) O el usuario tiene rol privilegiado
                if required_roles is None or is_privileged:
                    if st.button(card['button_label'], key=f"btn_action_{card['key']}"):
                         st.session_state.messages.append({"role": "user", "content": card['prompt']})
                         st.rerun()
                else:
                    st.button("🔒 " + card['title'].split(" ")[-1], key=f"btn_disabled_{card['key']}", disabled=True, help="Requiere rol HR_BP o ADMIN")

def render_suggestions_grid():
    """Renderiza la cuadrícula de sugerencias."""
    # Solo mostrar si NO hay mensajes
    if st.session_state.get("messages"):
        return

    st.divider()
    st.markdown(SUGGESTIONS_HEADER)
    
    # CSS Hack for buttons alignment
    st.markdown("""
        <style>
        div[data-testid="stColumn"] button {
            justify-content: flex-start !important;
            text-align: left !important;
            border: 1px solid #cbd5e0 !important;
            border-radius: 8px !important;
            background-color: white !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            width: 100% !important;
        }
        div[data-testid="stColumn"] button p {
            text-align: left !important;
            width: 100%;
        }
        div[data-testid="stColumn"] button:hover {
            border-color: #a0aec0 !important;
            background-color: #f7fafc !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(SUGGESTIONS_COLUMNS))
    
    for idx, column_data in enumerate(SUGGESTIONS_COLUMNS):
        with cols[idx]:
            st.markdown(f"**{column_data['title']}**")
            for item in column_data['items']:
                # Usar key única basada en el título y label
                if st.button(item['label'], key=f"btn_sug_{idx}_{item['label'][:5]}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": item['prompt']})
                    st.rerun()
