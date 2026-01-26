---
trigger: always_on
---

Actúa como un Arquitecto de Software Senior experto en Python y Streamlit. Tu tarea es generar la estructura de código y los archivos iniciales para un proyecto frontend profesional llamado "adk-frontend".

El objetivo es crear una interfaz de usuario escalable, modular y segura que se conecte a un backend FastAPI existente.

Por favor, crea la siguiente estructura de carpetas y archivos, e implementa el código base necesario en cada uno siguiendo los principios de "Separation of Concerns":

ESTRUCTURA DE DIRECTORIOS:
adk-frontend/
├── .env                  # (Crear con template: BACKEND_URL="http://127.0.0.1:8000")
├── .gitignore            # (Ignorar .env, __pycache__, .venv)
├── requirements.txt      # (streamlit, requests, python-dotenv)
├── main.py               # (Entry Point & Router)
└── src/
    ├── __init__.py
    ├── config.py         # (Carga de variables de entorno)
    ├── state.py          # (Gestión centralizada de Session State)
    ├── services/
    │   ├── __init__.py
    │   └── api_client.py # (Lógica de conexión HTTP con el Backend)
    ├── components/
    │   ├── __init__.py
    │   ├── sidebar.py    # (Menú lateral y botón de logout)
    │   └── debugger.py   # (Visualizador de JSON Raw de la respuesta del backend)
    └── views/
        ├── __init__.py
        ├── login.py      # (Vista de autenticación)
        └── dashboard.py  # (Vista principal del Chat)

DETALLES DE IMPLEMENTACIÓN:

1. src/config.py: Usa `python-dotenv` para cargar `BACKEND_URL`. Si no existe, lanza un error amigable.
2. src/state.py: Crea una clase o funciones para inicializar `st.session_state`. Debe manejar: `is_authenticated` (bool), `chat_history` (lista), `last_api_response` (dict/json para el debugger).
3. src/services/api_client.py: Crea una clase `ApiClient`.
   - Método `login(username, password)`: Retorna True/False (simulado por ahora o real si hay endpoint).
   - Método `send_chat(message)`: Hace POST al backend. Debe retornar la respuesta y guardar el JSON crudo para debug.
4. src/components/debugger.py: Un componente que, si se activa (ej. toggle en sidebar), muestra `st.json(last_api_response)` en un expander para inspeccionar la comunicación raw.
5. src/views/login.py: Formulario profesional. Al éxito, actualiza el estado `is_authenticated = True` y recarga.
6. src/views/dashboard.py: Interfaz de chat tipo espejo (User a la derecha, AI a la izquierda). Incluye el componente `debugger` al final o lateral.
7. main.py: Actúa como ROUTER.
   - Inicializa el estado.
   - Si `!is_authenticated` -> Renderiza `views.login`.
   - Si `is_authenticated` -> Renderiza `views.dashboard` + `components.sidebar`.

Genera el código completo y listo para ejecutar.