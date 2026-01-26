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
        url = f"{BACKEND_URL}/token" # Endpoint estándar OAuth2
        
        # FastAPI OAuth2PasswordBearer espera 'username' y 'password' como form-data
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json() # Esperamos {"access_token": "...", "token_type": "bearer", "user": {...}}
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Error de Conexión: No se encuentra el Backend en {BACKEND_URL}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error HTTP: {e}")
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
        
        headers = {
            "Authorization": f"Bearer {user.token}", 
            "Content-Type": "application/json"
        }

        try:
            # Enviamos la petición POST
            response = requests.post(url, json=payload, headers=headers)
            
            # Si el backend responde 401/403/500, lanzamos error aquí
            response.raise_for_status() 
            
            # Retornamos la respuesta en JSON
            return response.json()
            
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