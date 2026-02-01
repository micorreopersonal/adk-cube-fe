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
        st.markdown("## 🛡️ RIMAC Seguros") 
        st.caption("People Analytics & AI") 
        
        st.info(f"Usuario: **{user.name}**")
        st.caption(f"Rol: {user.role.upper()}")
        
        if st.button("Cerrar Sesión"):
            logout()
            
    # --- UI Principal ---
    # Títulos neutrales para producción
    st.title("🔴 Asistente de Gestión del Talento")
    st.markdown(f"Bienvenido/a **{user.name}**. Aquí tienes tu centro de comando para People Analytics.")
    


    # --- HISTORIAL DE CHAT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Agregar saludo inicial SOLO si el historial está vacío al inicio de sesión
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Hola **{user.name}**. Estoy listo para ayudarte con tus tareas de People Analytics."
        })

    # Mostrar mensajes anteriores
    from src.components.visualizer import Visualizer
    
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            # Soporte híbrido: Texto plano (Legacy) o Estructura Visual
            content = msg["content"]
            if isinstance(content, str):
                st.markdown(content)
            elif isinstance(content, list):
                Visualizer.render(content, key_prefix=str(idx))

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
            # ... (Resto de la lógica de visualizer)
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
                st.session_state.messages.append({"role": "assistant", "content": content_payload})
                new_msg_idx = len(st.session_state.messages) - 1
                with st.chat_message("assistant"):
                    Visualizer.render(content_payload, key_prefix=str(new_msg_idx))
            else:
                # Fallback: Texto plano
                # Prioridad: 'response' > 'content' (si fuera string) > Error
                ai_text = response_data.get("response") or str(response_data)
                
                # Limpieza cosmética: A veces el backend manda artifacts de JSON en markdown
                if ai_text.startswith("```json"):
                    ai_text = ai_text.replace("```json", "").replace("```", "").strip()
                
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
                with st.chat_message("assistant"):
                    st.markdown(ai_text)
            
    # --- DEBUGGER UI (Solo si está activo) ---
    if st.session_state.get("show_debugger", False):
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
            else:
                st.info("Esperando la primera consulta para mostrar datos de debug.")
