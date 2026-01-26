# src/views/dashboard.py
import streamlit as st
from src.state import get_user, logout
from src.security.auth import AuthService
from src.services.api_client import ApiClient

def render_dashboard():
    user = get_user()
    auth = AuthService()
    api_client = ApiClient() 
    
    # --- Sidebar ---
    with st.sidebar:
        # Cambio de nombre: De "Rotación Agent" a la marca genérica
        st.title("🤖 Convertex AI") 
        
        st.info(f"Usuario: **{user.name}**")
        st.caption(f"Rol: {user.role.upper()}")
        
        if st.button("Cerrar Sesión"):
            logout()
            
    # --- UI Principal ---
    # Títulos neutrales para producción
    st.title("💬 Asistente Virtual Corporativo")
    st.markdown(f"Hola **{user.name}**. Estoy listo para ayudarte con tus tareas diarias.")
    
    # --- SECCIÓN DE TOOLS (OCULTA POR AHORA) ---
    # Comentamos la visualización de herramientas para limpiar la UI en el MVP.
    # El código se mantiene para cuando actives las funcionalidades específicas.
    """
    my_tools = auth.get_allowed_tools(user.role)
    cols = st.columns(len(my_tools)) if my_tools else []
    for idx, tool in enumerate(my_tools):
        with cols[idx]:
            st.success(f"🛠️ {tool}")
    """

    st.divider()

    # --- HISTORIAL DE CHAT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes anteriores
    from src.components.visualizer import Visualizer
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            # Soporte híbrido: Texto plano (Legacy) o Estructura Visual
            content = msg["content"]
            if isinstance(content, str):
                st.markdown(content)
            elif isinstance(content, list):
                Visualizer.render(content)

    # --- INPUT DEL USUARIO ---
    # Placeholder genérico
    if prompt := st.chat_input("Escribe tu consulta aquí..."):
        
        # 1. Mostrar mensaje usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. LLAMADA AL BACKEND REAL
        with st.spinner("Procesando..."):
            # El backend recibirá el rol del usuario y decidirá qué tools usar internamente
            response_data = api_client.send_chat(prompt, user)

        # 3. Mostrar respuesta AI
        if response_data:
            # Detectar tipo de respuesta
            res_type = response_data.get("response_type", "text")
            
            if res_type == "visual_package":
                content_payload = response_data.get("content", [])
                st.session_state.messages.append({"role": "assistant", "content": content_payload})
                with st.chat_message("assistant"):
                    Visualizer.render(content_payload)
            else:
                # Fallback / Legacy text
                ai_text = response_data.get("response", "Error: Respuesta sin formato esperado")
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
                with st.chat_message("assistant"):
                    st.markdown(ai_text)
            
            # --- DEBUGGER ---
            with st.expander("🛠️ Debug Backend JSON"):
                st.json(response_data)