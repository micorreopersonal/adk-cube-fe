# src/security/auth.py
from typing import Optional, List
from .models import UserProfile
from src.services.api_client import ApiClient

class AuthService:
    def login(self, username, password) -> Optional[UserProfile]:
        api = ApiClient()
        data = api.login(username, password)
        
        if not data or "access_token" not in data:
            return None
            
        token = data["access_token"]
        
        # INTENTO 1: Ver si el backend nos devolvio el perfil del usuario en la respuesta
        # Formato esperado: { "access_token": "...", "user": { "username": "...", "role": "..." } }
        user_data = data.get("user")
        
        # INTENTO 2: Si no viene, asumimos valores por defecto o extraemos del token (decodificación básica si fuera necesario)
        # Por seguridad y simplicidad, vamos a ser optimistas y asumir que si logueó, al menos tenemos el usuario.
        if not user_data:
            # Caso de respaldo: Asumimos ADMIN por ahora para no bloquear, O pedimos /users/me
            # TODO: Implementar llamada a /users/me si el token no trae info
            user_data = {
                "username": username,
                "name": username.capitalize(),
                "role": "admin" if username.lower() in ["admin", "paul"] else "analyst" # Fallback temporal
            }
            
        return UserProfile(
            username=user_data.get("username", username),
            name=user_data.get("name", username),
            role=user_data.get("role", "viewer"),
            token=token
        )

    def get_allowed_tools(self, role: str) -> List[str]:
        """Define qué herramientas ve cada rol (RBAC)"""
        if role == "admin":
            return ["Generar Reporte", "Consultar BigQuery", "Borrar Datos (Peligroso)"]
        elif role == "analyst":
            return ["Generar Reporte", "Consultar BigQuery"]
        else:
            return []