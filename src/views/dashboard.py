# src/views/dashboard.py
import streamlit as st
from src.state import get_user
from src.services.api_client import ApiClient
from src.components.sidebar import render_sidebar
from src.components.dashboard_widgets import (
    render_welcome_header,
    render_action_cards,
    render_suggestions_grid
)
from src.components.visualizer import Visualizer
from src.config import SHOW_DEBUG_UI
import json
import re

def render_dashboard():
    user = get_user()
    api_client = ApiClient() 
    
    # --- Sidebar ---
    render_sidebar()



    # --- UI Principal ---
    render_welcome_header(user, api_client)
    render_action_cards(user)
    render_suggestions_grid()

    # --- HISTORIAL DE CHAT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes anteriores
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:  # Assistant
            # --- EXTRACT AND DISPLAY SUMMARY FIRST (OUTSIDE CHAT BUBBLE) ---
            if isinstance(msg["content"], list):
                summary = msg.get("summary", "")
                if summary:
                    st.info(summary, icon="📊")
                    st.divider()
            
            with st.chat_message("assistant"):
                # Si es lista (Visual Package), renderizamos con el motor
                if isinstance(msg["content"], list):
                    Visualizer.render(msg["content"], key_prefix=f"msg_{idx}")
                else:
                    st.markdown(msg["content"])

    # --- INPUT DEL USUARIO ---
    if prompt := st.chat_input("Escribe tu consulta aquí..."):
        # Limpiar estado de Debugger anterior
        if "last_api_response" in st.session_state:
            st.session_state.last_api_response = {}
        # Agregar mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Renderizar feedback inmediato
        with st.chat_message("user"):
            st.markdown(prompt)
        
    # --- LÓGICA DE RESPUESTA CENTRALIZADA ---
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        _handle_backend_response(st.session_state.messages[-1]["content"], user, api_client)

    # --- DEBUGGER UI ---
    if SHOW_DEBUG_UI and st.session_state.get("show_debugger", False):
        _render_debugger()

def _handle_backend_response(prompt_content, user, api_client):
    """Maneja la llamada al backend y el procesamiento de la respuesta."""
    with st.status("🧠 **Analizando...**", expanded=True) as status:
        st.write("📡 Conectando con Nexus AI...")
        response_data = api_client.send_chat(prompt_content, user)
        
        if response_data:
            status.update(label="✅ **Respuesta Recibida**", state="complete", expanded=False)
        else:
            status.update(label="❌ **Error de Conexión**", state="error", expanded=False)

    if response_data:
        _process_response_data(response_data)
        st.rerun()

def _process_response_data(response_data):
    """Procesa la respuesta raw del backend (alertas, visuales, texto)."""
    # 1. Detección de Anomalías
    anomalia = response_data.get("anomalia_detectada", False)
    insight = response_data.get("insight_ejecutivo", "")
    
    if anomalia:
        st.error("🚨 **ALERTA DE GESTIÓN DE TALENTO DETECTADA**", icon="🔥")
        with st.container():
            st.markdown(f"""
            <div style="border-left: 5px solid #EF3340; padding: 10px; background-color: #f8f9fa; margin-bottom: 20px;">
                <span style="font-size: 1.1em; color: #333;">{insight}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()

    # 2. Parsing de Contenido (Visual vs Texto)
    is_visual = False
    content_payload = []
    
    if response_data.get("response_type") == "visual_package":
        is_visual = True
        content_payload = response_data.get("content", [])
    elif "content" in response_data and isinstance(response_data["content"], list):
        is_visual = True
        content_payload = response_data["content"]
    elif "response" in response_data:
        # Fallback JSON parsing
        text_response = str(response_data["response"])
        matches = re.search(r"(\{.*?\})", text_response, re.DOTALL)
        if matches:
            try:
                parsed = json.loads(matches.group(1))
                if isinstance(parsed, dict) and "content" in parsed:
                    is_visual = True
                    content_payload = parsed["content"]
                elif isinstance(parsed, dict) and "visual_package" in parsed:
                    vp = parsed["visual_package"]
                    is_visual = True
                    content_payload = vp if isinstance(vp, list) else [{"type": "text", "payload": vp.get("text", str(vp))}]
            except json.JSONDecodeError:
                pass

    # 3. Guardar en Historial
    if is_visual:
        # --- EXTRACT ALERT/SUMMARY HIGHLIGHT ---
        # Prioritize explicit 'alert_highlight' or 'summary' keys for the Blue Banner.
        # We do NOT fallback to 'response' locally to avoid duplication.
        summary = response_data.get("alert_highlight") or response_data.get("summary", "")
        
        # --- DEBUG: TRACE SUMMARY ---
        # print(f"🔍 DEBUG SUMMARY: Extracted summary = '{summary[:100]}...'")
        # ---------------------------
        
        # --- DISPLAY SUMMARY IMMEDIATELY (OUTSIDE CHAT BUBBLE) ---
        if summary:
            st.info(summary, icon="📊")
            st.divider()
        # ------------------------------------------------
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": content_payload,
            "summary": summary
        })
    else:
        ai_text = response_data.get("response") or str(response_data)
        if ai_text.startswith("```json"):
            ai_text = ai_text.replace("```json", "").replace("```", "").strip()
        st.session_state.messages.append({"role": "assistant", "content": ai_text})

def _render_debugger():
    st.divider()
    with st.expander("🛠️ Debugger: Comunicación con Backend", expanded=True):
        if "last_api_response" in st.session_state:
            res = st.session_state.last_api_response or {}
            
            telemetry = res.get("telemetry", {})
            if telemetry:
                c1, c2, c3 = st.columns(3)
                c1.metric("Model Turns", telemetry.get("model_turns", 0))
                c2.metric("Tools Llamadas", len(telemetry.get("tools_executed", [])))
                c3.metric("Req. Totales (est)", telemetry.get("api_invocations_est", 0))
                
                if telemetry.get("tools_executed"):
                    st.write(f"🔧 **Herramientas usadas:** `{', '.join(telemetry['tools_executed'])}`")
            
            st.write("📄 **Raw JSON Response:**")
            st.json(res)
            
            st.divider()
            st.write("📤 **Contexto Enviado (Payload):**")
            if "last_request_payload" in st.session_state:
                st.code(json.dumps(st.session_state.last_request_payload, indent=2), language="json")
        else:
            st.info("Esperando la primera consulta para mostrar datos de debug.")
