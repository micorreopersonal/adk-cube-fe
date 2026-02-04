import streamlit as st
import os
from src.state import logout

def render_sidebar():
    """Renderiza el sidebar con el menú de navegación y botón de logout."""
    with st.sidebar:
        # --- BRANDING ---
        # Priorizar SVG si existe (instrucción explícita del usuario)
        logo_path = "src/images/logo.svg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
        elif os.path.exists("src/images/rimac.png"):
             st.image("src/images/rimac.png", width=180)
        else:
             st.title("🛡️ RIMAC | AI")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- DEBUGGER TOGGLE (TOP for visibility) ---
        from src.config import SHOW_DEBUG_UI
        if SHOW_DEBUG_UI:
             st.caption("🛠️ Configuración Developer")
             st.session_state.show_debugger = st.toggle("Modo Debugger", value=st.session_state.get("show_debugger", True))
             st.divider()

        # --- FILTROS DE SEGMENTO (Global Context) ---
        st.subheader("🎯 Filtros de Talento")
        
        # Binding directo al Atomic State "active_context"
        if "active_context" not in st.session_state:
             from src.state import init_session
             init_session()
             
        current_context = st.session_state.active_context
        
        filtro_talento = st.radio(
            "Foco de Análisis:",
            ["Global (Todos)", "Talento (Score 7-9)", "Hipos (Score 8-9)"],
            index=0,
            key="segment_filter_widget", # Widget key distinct from state key to avoid collisions if we were syncing manually, but here we just read/write
            help="Filtra los insights para centrarse en los grupos de talento crítico."
        )
        
        # Update Atomic Context
        current_context["segment_filter"] = filtro_talento
        
        if filtro_talento != "Global (Todos)":
            st.info(f"Focalizando en: **{filtro_talento}**")
            
        st.divider()
        
        # --- PROFILE CARD (Premium Design) ---
        from src.state import get_user
        user = get_user()
        
        # CSS HACK for nicer buttons in sidebar
        st.markdown("""
            <style>
            section[data-testid="stSidebar"] div.stButton > button {
                border: 1px solid #d1d5db !important;
                border-radius: 8px !important;
                transition: all 0.3s ease;
            }
            section[data-testid="stSidebar"] div.stButton > button:hover {
                border-color: #ef4444 !important;
                color: #ef4444 !important;
                background-color: #fef2f2 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        if user:
            with st.container(border=True):
                # Centered layout using columns
                c_space1, c_content, c_space2 = st.columns([1, 8, 1])
                with c_content:
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.markdown("### 👤")
                    st.markdown(f"**{user.name}**")
                    st.markdown(f"<span style='background-color:#F5F5F5; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #666;'>{user.role.upper()}</span>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
             st.caption("Modo Invitado")
        
        st.divider()
        
        st.divider()
        
        # --- VISUAL CONFIGURATION (THEME SETTINGS) ---
        with st.expander("🎨 Configuración Visual", expanded=False):
            st.caption("Personaliza los colores de los gráficos.")
            
            # Ensure defaults in session state
            from src.utils.chart_styles import ChartColors
            if "custom_colors" not in st.session_state:
                st.session_state.custom_colors = list(ChartColors.DEFAULTS)
                
            cols = st.columns(3)
            # We expose the first 3 colors for simplicity
            c1 = cols[0].color_picker("Color 1", st.session_state.custom_colors[0], key="cp_1")
            c2 = cols[1].color_picker("Color 2", st.session_state.custom_colors[1], key="cp_2")
            c3 = cols[2].color_picker("Color 3", st.session_state.custom_colors[2], key="cp_3")
            
            # Update state if changed
            if c1 != st.session_state.custom_colors[0] or \
               c2 != st.session_state.custom_colors[1] or \
               c3 != st.session_state.custom_colors[2]:
                   st.session_state.custom_colors[0] = c1
                   st.session_state.custom_colors[1] = c2
                   st.session_state.custom_colors[2] = c3
                   st.rerun()

            if st.button("🔄 Restablecer Colores", help="Vuelve a los colores corporativos."):
                del st.session_state["custom_colors"]
                st.rerun()
        
        st.divider()
        
        # --- ACTIONS FOOTER ---
        # Botón para limpiar historial
        if st.button("🗑️ Limpiar Historial", use_container_width=True, type="secondary", help="Borra la conversación actual para iniciar de cero."):
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "¡Hola de nuevo! Historial limpio. ¿En qué puedo ayudarte ahora?"
            })
            st.toast("Historial de chat borrado.", icon="🗑️")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Cerrar Sesión", use_container_width=True, type="primary"):
            logout()
