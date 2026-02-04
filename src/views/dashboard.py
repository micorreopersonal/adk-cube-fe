# src/views/dashboard.py
# Includes CSS hacks for button alignment
import streamlit as st
import os
from src.state import get_user, logout
from src.security.auth import AuthService

from src.services.api_client import ApiClient
from src.components.sidebar import render_sidebar

def render_dashboard():
    user = get_user()
    auth = AuthService()
    api_client = ApiClient() 
    
    # --- Sidebar ---
    render_sidebar()

    # --- UI Principal ---
    # Títulos neutrales para producción
    
    # Header de Bienvenida con Estilo
    # Header de Bienvenida con Botón de Reinicio
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        st.markdown(f"""
            <h1 style='color: #1A202C; font-size: 2.2rem;'>¡Hola, {user.name.split(' ')[0]}! 👋</h1>
            <p style='color: #718096; font-size: 1.1rem;'>
                Bienvenido a tu <b>Centro de Comando de Talento</b>. ¿Qué insights descubriremos hoy?
            </p>
        """, unsafe_allow_html=True)
    
    with h_col2:
        # Alineación y botón de reset
        st.write("") 
        st.write("")
        if st.button("🗑️ Reiniciar", help="Borrar memoria del agente y limpiar chat", use_container_width=True):
             if api_client.reset_session(user):
                 st.session_state.messages = []
                 st.session_state.last_api_response = None # Limpiar también el último debug
                 st.toast("Memoria del agente borrada.", icon="🧹")
                 st.rerun()
             else:
                 st.toast("Error al reiniciar sesión.", icon="❌")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Tarjetas de Acción Rápida (Solo si NO hay historial de chat para no saturar)
    if not st.session_state.get("messages"):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            with st.container(border=True):
                st.markdown("### 📉 Rotación y Fugas")
                st.caption("Analiza tendencias de salida y retención.")
                if st.button("Ver Análisis de Rotación ➔", key="btn_rotacion"):
                     # Prompt Específico: Periodo, Comparativa y Dimensión (Divisiones = UO2)
                     st.session_state.messages.append({"role": "user", "content": "Analiza la rotación voluntaria del año 2024 y 2025 comparada por divisiones."})
                     st.rerun()

        # RBAC Check
        is_privileged = user.role in ['admin', 'hr_bp']

        with c2:
            with st.container(border=True):
                st.markdown("### ⭐ Talento Clave")
                st.caption("Identifica a tus HiPos y Riesgos.")
                
                if is_privileged:
                    if st.button("Ver Top Talent ➔", key="btn_talento"):
                         st.session_state.messages.append({"role": "user", "content": "Muestra las fugas de talento clave (Hiper/Hipo) registradas en el último mes cerrado."})
                         st.rerun()
                else:
                    st.button("🔒 Top Talent", key="btn_talento_disabled", disabled=True, help="Requiere rol HR_BP o ADMIN")

        with c3:
            with st.container(border=True):
                st.markdown("### 🚨 Alertas Activas")
                st.caption("Focos rojos que requieren atención.")
                
                if is_privileged:
                    if st.button("Ver Alertas ➔", key="btn_alertas"):
                         st.session_state.messages.append({"role": "user", "content": "¿Qué divisiones (UO2) tienen la mayor tasa de renuncia acumulada en el año 2025?"})
                         st.rerun()
                else:
                    st.button("🔒 Alertas", key="btn_alertas_disabled", disabled=True, help="Requiere rol HR_BP o ADMIN")
        
        # --- SUGGESTIONS / BRAINSTORMING BLOCK ---
        st.divider()
        st.markdown("##### 💡 ¿No sabes por dónde empezar? Prueba estas consultas:")
        
        # CSS HACK: Alinear texto de botones a la izquierda para parecer lista
        # CSS HACK: Alinear texto de botones a la izquierda para parecer lista
        st.markdown("""
            <style>
            /* Force left alignment for buttons in columns (Suggestions) */
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

        # Grid de sugerencias
        s_col1, s_col2, s_col3 = st.columns(3)
        
        with s_col1:
            st.markdown("**📊 Tendencias y Evolución**")
            # Usar espacios NO rompibles para separar el bullet
            if st.button("•  Curva de rotación mensual 2025", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Muestra la tendencia mensual de rotación voluntaria e involuntaria del 2025 a nivel de toda la empresa."})
                st.rerun()
            if st.button("•  Comparativo 2024 vs 2025", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Genera un gráfico comparativo de la rotación acumulada entre el año 2024 y 2025."})
                st.rerun()

        with s_col2:
            st.markdown("**🔍 Focos y Segmentos**")
            if st.button("•  Ranking de Divisiones (UO2)", use_container_width=True):
                 st.session_state.messages.append({"role": "user", "content": "¿Cuáles son las 5 divisiones (UO2) con mayor cantidad de renuncias en lo que va del año?"})
                 st.rerun()
            if st.button("•  FFVV vs Administrativos", use_container_width=True):
                 st.session_state.messages.append({"role": "user", "content": "Compara la tasa de rotación entre el segmento Fuerza de Ventas y Administrativos para el año 2025."})
                 st.rerun()

        with s_col3:
            st.markdown("**🧠 Insights Profundos**")
            if st.button("•  Motivos de Salida", use_container_width=True):
                 st.session_state.messages.append({"role": "user", "content": "¿Cuáles son los principales motivos de renuncia registrados en el último trimestre de 2025 a nivel de toda la empresa?"})
                 st.rerun()
            if st.button("•  Listado de Bajas Recientes", use_container_width=True):
                 st.session_state.messages.append({"role": "user", "content": "Dame un listado detallado de las personas que cesaron el último mes cerrado del año 2025 a nivel de toda la empresa."})
                 st.rerun()
    

    # --- HISTORIAL DE CHAT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # El historial inicia vacío para mostrar las Tarjetas de Acción


    # Mostrar mensajes anteriores
    from src.components.visualizer import Visualizer
    
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:  # Assistant
            # --- EXTRACT AND DISPLAY SUMMARY FIRST (OUTSIDE CHAT BUBBLE) ---
            if isinstance(msg["content"], list):
                summary = msg.get("summary", "")
                if summary:
                    st.markdown(f"### 📊 {summary}")
                    st.divider()
            
            with st.chat_message("assistant"):
                # Si es lista (Visual Package), renderizamos con el motor
                if isinstance(msg["content"], list):
                    # Render visual blocks
                    Visualizer.render(msg["content"], key_prefix=f"msg_{idx}")
                else:
                    # Mensaje de texto plano
                    st.markdown(msg["content"])

    # --- INPUT DEL USUARIO ---
    # Placeholder genérico
    # --- INPUT DEL USUARIO ---
    # Placeholder genérico
    if prompt := st.chat_input("Escribe tu consulta aquí..."):
        # 0. Limpiar estado de Debugger anterior para evitar "Ghosts"
        if "last_api_response" in st.session_state:
            st.session_state.last_api_response = {}
        # 1. Agregar mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Renderizar INMEDIATAMENTE para feedback visual (Solo en input manual)
        with st.chat_message("user"):
            st.markdown(prompt)
        
    # --- LÓGICA DE RESPUESTA CENTRALIZADA ---
    # Si el último mensaje es del usuario (venga del Input o de los Botones), generamos respuesta
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        
        # Recuperar el último prompt
        prompt_content = st.session_state.messages[-1]["content"]

        # NOTA: No renderizamos el mensaje del usuario AQUÍ.
        # - Si vino de chat_input, ya se renderizó arriba.
        # - Si vino de botón + rerun, ya se renderizó en el bucle de historial al principio.
        # Esto soluciona el bug de duplicidad.

        # 2. LLAMADA AL BACKEND REAL (Async UI Pattern)
        with st.status("🧠 **Analizando...**", expanded=True) as status:
            st.write("📡 Conectando con Nexus AI...")
            # El backend recibirá el rol del usuario y decidirá qué tools usar internamente
            response_data = api_client.send_chat(prompt_content, user)
            
            if response_data:
                status.update(label="✅ **Respuesta Recibida**", state="complete", expanded=False)
            else:
                status.update(label="❌ **Error de Conexión**", state="error", expanded=False)

        # 3. Mostrar respuesta AI
        if response_data:
            # --- DETECCIÓN DE ANOMALÍAS (EXECUTIVE REPORTING) ---
            anomalia = response_data.get("anomalia_detectada", False)
            insight = response_data.get("insight_ejecutivo", "")
            data_reporte = response_data.get("data_reporte", {})
            
            if anomalia:
                # Contenedor de Alerta Roja (Estilo RIMAC / Crítico)
                st.error("🚨 **ALERTA DE GESTIÓN DE TALENTO DETECTADA**", icon="🔥")
                
                with st.container():
                    st.markdown(f"""
                    <div style="border-left: 5px solid #EF3340; padding: 10px; background-color: #f8f9fa; margin-bottom: 20px;">
                        <span style="font-size: 1.1em; color: #333;">{insight}</span>
                    </div>
                    """, unsafe_allow_html=True)

            
            st.divider()

            import json
            import re
            # Lógica de detección robusta de VisualDataPackage
            is_visual = False
            content_payload = []
            
            # Caso A: Protocolo correcto (response_type="visual_package")
            if response_data.get("response_type") == "visual_package":
                is_visual = True
                content_payload = response_data.get("content", [])

            # Caso B: Protocolo implícito (Falta response_type, pero existe "content" lista)
            elif "content" in response_data and isinstance(response_data["content"], list):
                is_visual = True
                content_payload = response_data["content"]
            
            # Caso C: JSON String dentro de "response" (El LLM devolvió JSON como texto)
            elif "response" in response_data:
                text_response = str(response_data["response"])
                # Intentamos "olfatear" si hay un JSON en el texto
                matches = re.search(r"(\{.*?\})", text_response, re.DOTALL)
                if matches:
                    try:
                        parsed = json.loads(matches.group(1))
                        # Si tiene content, lo usamos
                        if isinstance(parsed, dict) and "content" in parsed:
                            is_visual = True
                            content_payload = parsed["content"]
                        # Si tiene visual_package (el caso del error), lo extraemos
                        elif isinstance(parsed, dict) and "visual_package" in parsed:
                            vp = parsed["visual_package"]
                            is_visual = True
                            if isinstance(vp, list): content_payload = vp
                            elif isinstance(vp, dict): content_payload = [{"type": "text", "payload": vp.get("text", str(vp))}]
                    except json.JSONDecodeError:
                        pass # No era JSON válido, tratamos como texto normal
            
            # --- RENDERIZADO ---
            if is_visual:
                # Extract summary from response_data
                summary = response_data.get("summary", "")
                
                # Store summary WITH the message for proper historical rendering
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": content_payload,
                    "summary": summary  # Store summary alongside content
                })
                # No necesitamos renderizar aquí el componente visual complejo, 
                # porque st.rerun() lo hará en el bucle principal de historial.
                # Solo mostrar feedback inmediato si se desea, pero rerun es más limpio.
            else:
                # Fallback: Texto plano
                # Prioridad: 'response' > 'content' (si fuera string) > Error
                ai_text = response_data.get("response") or str(response_data)
                
                # Limpieza cosmética: A veces el backend manda artifacts de JSON en markdown
                if ai_text.startswith("```json"):
                    ai_text = ai_text.replace("```json", "").replace("```", "").strip()
                
                st.session_state.messages.append({"role": "assistant", "content": ai_text})

            # Forzar actualización para que el mensaje nuevo aparezca en el historial principal
            st.rerun()
            
            # --- VIEW JSON PAYLOAD (Added for Debug in Local Mode) ---
            if SHOW_DEBUG_UI:
                with st.expander("📄 Ver JSON Payload (Debug)"):
                     st.json(content_payload if is_visual else ai_text)
            
    # --- DEBUGGER UI (Solo si está activo) ---
    from src.config import SHOW_DEBUG_UI
    if SHOW_DEBUG_UI and st.session_state.get("show_debugger", False):
        st.divider()
        with st.expander("🛠️ Debugger: Comunicación con Backend", expanded=True):
            if "last_api_response" in st.session_state:
                res = st.session_state.last_api_response
                
                # Extraer Telemetría
                telemetry = res.get("telemetry", {})
                if telemetry:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Model Turns", telemetry.get("model_turns", 0))
                    with c2:
                        st.metric("Tools Llamadas", len(telemetry.get("tools_executed", [])))
                    with c3:
                        st.metric("Req. Totales (est)", telemetry.get("api_invocations_est", 0))
                    
                    if telemetry.get("tools_executed"):
                        st.write(f"🔧 **Herramientas usadas:** `{', '.join(telemetry['tools_executed'])}`")
                else:
                    st.info("No hay telemetría en esta respuesta (Legacy o Error).")
                
                # Raw JSON
                st.write("📄 **Raw JSON Response:**")
                st.json(res)
                
                # --- Context Copier ---
                st.divider()
                st.write("📤 **Contexto Enviado (Payload):**")
                st.caption("Copia esto para reproducir errores en Postman o Pytest.")
                import json
                if "last_request_payload" in st.session_state:
                    st.code(json.dumps(st.session_state.last_request_payload, indent=2), language="json")
                else:
                    st.info("No hay contexto previo capturado.")
            else:
                st.info("Esperando la primera consulta para mostrar datos de debug.")
