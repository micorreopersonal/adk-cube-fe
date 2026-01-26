# src/security/models.py
from dataclasses import dataclass

@dataclass
class UserProfile:
    """Modelo inmutable del usuario en sesión"""
    username: str
    name: str
    role: str  # 'admin', 'analyst', 'viewer'
    token: str # JWT Token real
    
    @property
    def is_admin(self):
        return self.role == "admin"