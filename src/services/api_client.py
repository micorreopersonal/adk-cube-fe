# adk-frontend/src/services/api_client.py

import requests
import streamlit as st
from src.config import BACKEND_URL
from src.security.models import UserProfile

class ApiClient:
    def login(self, username, password):
        """
        Obtiene el token JWT del backend
        """
        url = f"{BACKEND_URL}/token" # Endpoint estándar OAuth2 sin prefijo /api
        
        # --- MOCK LOGIN FOR DEMO/DEV ---
        # Permite entrar sin backend si se usan estas credenciales
        # if username.lower() == "admin" and password == "p014654":
        #     return {
        #         "access_token": "mock-token-admin-001", 
        #         "token_type": "bearer",
        #         "user": {
        #             "username": "admin",
        #             "role": "admin",
        #             "name": "Admin User"
        #         }
        #     }
        
        # if username.lower() == "paul" and password == "admin123":
        #      return {
        #         "access_token": "mock-token-paul-002", 
        #         "token_type": "bearer",
        #         "user": {
        #             "username": "paul",
        #             "role": "admin",
        #             "name": "Paul"
        #         }
        #     }
        # -------------------------------
        
        # FastAPI OAuth2PasswordBearer espera 'username' y 'password' como form-data
        data = {
            "username": username,
            "password": password
        }
        
        try:
            print(f"🔑 DEBUG LOGIN: Attempting login to {url} with user '{username}'")
            response = requests.post(url, data=data)
            print(f"🔑 DEBUG LOGIN: Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"🔑 DEBUG LOGIN: Error Response: {response.text}")
                
            response.raise_for_status()
            return response.json() # Esperamos {"access_token": "...", "token_type": "bearer", "user": {...}}
            
        except requests.exceptions.ConnectionError:
            print(f"❌ DEBUG LOGIN: Error de Conexión: No se encuentra el Backend en {BACKEND_URL}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ DEBUG LOGIN: Error HTTP: {e}")
            return None

    def send_chat(self, message: str, user: UserProfile):
        """
        Envía el mensaje al backend usando el TOKEN REAL del usuario.
        """
        url = f"{BACKEND_URL}/chat"
        
        payload = {
            "message": message,
            "session_id": f"session-{user.username}", 
            # "context_profile": user.role # El backend probablemente lo saca del token ahora, pero lo dejamos si es requerido explícitamente por el agente
            # En arquitecturas seguras, el rol se decodifica del JWT, pero por compatibilidad con tu código actual de agente lo enviamos.
            "context_profile": user.role 
        }
        
        # --- TELEMETRY: Capture Request Context (Context Copier) ---
        st.session_state.last_request_payload = payload
        
        headers = {
            "Authorization": f"Bearer {user.token}", 
            "Content-Type": "application/json"
        }

        # --- DEBUG: TOKEN VISIBILITY ---
        # print(f"🔑 DEBUG: Headers being sent to {url}:")
        # -------------------------------

        try:
            # Enviamos la petición POST
            response = requests.post(url, json=payload, headers=headers)
            
            # Si el backend responde 401/403/500, lanzamos error aquí
            response.raise_for_status() 
            
            # Retornamos la respuesta en JSON
            res_json = response.json()
            st.session_state.last_api_response = res_json
            return res_json
            
        except requests.exceptions.ConnectionError:
            st.error("❌ Error de Conexión: No se encuentra el Backend.")
            return None
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ El Backend rechazó la conexión: {e}")
            try:
                st.write(response.json())
            except:
                pass
            return None

    def reset_session(self, user: UserProfile):
        """
        Llama al endpoint /session/reset para borrar la memoria del agente.
        """
        url = f"{BACKEND_URL}/api/session/reset"
        session_id = f"session-{user.username}"
        
        payload = {
            "session_id": session_id
        }
        
        headers = {
            "Authorization": f"Bearer {user.token}", 
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"Error resetting session: {e}")
            return False

