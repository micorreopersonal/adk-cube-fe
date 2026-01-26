---
trigger: manual
---

# Especificación Técnica: Arquitectura Frontend Enterprise (ADK-Frontend)

**Rol:** Actúa como un Arquitecto de Software Senior experto en Python, Streamlit y Patrones de Diseño de Seguridad.

**Objetivo:**
Generar la estructura de código y los archivos iniciales para un proyecto frontend profesional llamado "adk-frontend". El objetivo es crear una interfaz de usuario escalable, modular y segura ("Enterprise-Ready") que se conecte a un backend FastAPI existente.

La arquitectura debe desacoplar la **Autenticación** (Login) de la **Autorización** (Roles/Permisos) para facilitar una futura migración a SSO (Google/Azure AD) sin reescribir la lógica de negocio.

---

### 1. Estructura de Directorios

Por favor, crea la siguiente estructura de carpetas y archivos vacíos (o con el código base que se detalla más abajo):

adk-frontend/
├── .env                  # Template: BACKEND_URL="http://127.0.0.1:8000"
├── .gitignore            # Ignorar .env, __pycache__, .venv
├── requirements.txt      # streamlit, requests, python-dotenv
├── main.py               # Entry Point & Router (Control de flujo principal)
└── src/
    ├── __init__.py
    ├── config.py         # Configuración y carga de variables de entorno
    ├── state.py          # Gestión centralizada de Session State (Singleton pattern)
    ├── security/         # NUEVO: Módulo de Seguridad y RBAC
    │   ├── __init__.py
    │   ├── models.py     # Definición de UserProfile y Roles
    │   └── auth_service.py # Lógica de Login y Filtrado de Herramientas (Provider Pattern)
    ├── services/
    │   ├── __init__.py
    │   └── api_client.py # Cliente HTTP para comunicar con el Backend
    ├── components/
    │   ├── __init__.py
    │   ├── sidebar.py    # Menú lateral con Info de Usuario y Logout
    │   └── debugger.py   # Visualizador JSON para desarrollo
    └── views/
        ├── __init__.py
        ├── login.py      # UI de Autenticación
        └── dashboard.py  # UI Principal (Chat y Herramientas)

---

### 2. Detalles de Implementación (Separation of Concerns)

Implementa el código necesario siguiendo estas directrices estrictas:

#### A. Configuración y Estado (`src/`)
1.  **`src/config.py`**:
    * Usa `python-dotenv` para cargar `BACKEND_URL`.
    * Define constantes para roles (ej: `ROLE_ADMIN = "admin"`, `ROLE_ANALYST = "analyst"`).
2.  **`src/state.py`**:
    * Gestiona `st.session_state`.
    * **Propiedades clave**:
        * `current_user`: (Optional[`UserProfile`]) - Objeto del usuario logueado.
        * `chat_history`: (List) - Historial de mensajes.
        * `last_api_response`: (Dict) - Para el debugger.
    * Métodos `init_state()` y `clear_session()`.

#### B. Seguridad y RBAC (`src/security/`)
3.  **`src/security/models.py`**:
    * Clase `UserProfile` (dataclass): Debe contener `username`, `full_name`, `role` (str).
4.  **`src/security/auth_service.py`**:
    * Clase `AuthService`.
    * **Método `login(username, password) -> Optional[UserProfile]`**:
        * Simula una base de datos local (Hardcoded dict) con usuarios de prueba:
            * User "admin" (Rol: Admin).
            * User "analyst" (Rol: Analyst).
        * Valida credenciales y retorna el objeto `UserProfile`.
    * **Método `get_allowed_tools(user: UserProfile) -> List[str]`**:
        * Implementa la lógica RBAC.
        * Si es Admin -> Retorna todas las tools.
        * Si es Analyst -> Retorna subset de tools (lectura).

#### C. Servicios y Componentes (`src/services/` & `src/components/`)
5.  **`src/services/api_client.py`**:
    * Clase `ApiClient`. Método `send_chat(message, user_context)` que hace POST al backend.
6.  **`src/components/sidebar.py`**:
    * Muestra el nombre del usuario (`current_user.full_name`) y su rol (`current_user.role`).
    * Botón de "Cerrar Sesión" que invoca `state.clear_session()` y `st.rerun()`.
7.  **`src/components/debugger.py`**:
    * Si se activa, muestra `st.json(last_api_response)` en un `st.expander`.

#### D. Vistas y Enrutamiento (`src/views/` & `main.py`)
8.  **`src/views/login.py`**:
    * Formulario limpio y profesional.
    * Usa `AuthService.login`. Si es exitoso, actualiza `state.current_user` y hace `st.rerun()`.
9.  **`src/views/dashboard.py`**:
    * Obtiene `current_user` del estado.
    * Usa `AuthService.get_allowed_tools(current_user)` para mostrar en pantalla qué herramientas están activas para este usuario (feedback visual).
    * Interfaz de chat (User/AI).
10. **`main.py`**:
    * Router Principal.
    * Verifica: `if not state.current_user`: renderiza `views.login`.
    * Caso contrario: renderiza `components.sidebar` + `views.dashboard`.

---

**Entregable:**
Genera el código completo de todos los archivos mencionados, listo para ejecutar `streamlit run main.py`. Asegúrate de que el código sea modular, limpio y tipado (Type Hints).