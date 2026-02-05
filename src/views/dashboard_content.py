# src/views/dashboard_content.py

# --- TEXTOS DE BIENVENIDA ---
WELCOME_TITLE = "¡Hola, {name}! 👋"
WELCOME_SUBTITLE = "Bienvenido a tu <b>Centro de Comando de Talento</b>. ¿Qué insights descubriremos hoy?"

# --- TARJETAS DE ACCIÓN RÁPIDA ---
ACTION_CARDS = [
    {
        "key": "rotacion",
        "title": "📉 Rotación y Fugas",
        "caption": "Analiza tendencias de salida y retención.",
        "button_label": "Ver Análisis de Rotación ➔",
        "prompt": "Analiza mes a mes la rotación voluntaria e involuntaria del año 2024 y 2025 por cada división (uo2), mostrar el top 5 de divisiones con mayor rotación.",
        "role_required": None # None = Public
    },
    {
        "key": "talento",
        "title": "⭐ Talento Clave",
        "caption": "Identifica a tus HiPos y Riesgos.",
        "button_label": "Ver Top Talent ➔",
        "prompt": "Muestra las fugas de talento clave (Hiper/Hipo) registradas en el último mes cerrado.",
        "role_required": ["admin", "hr_bp"]
    },
    {
        "key": "alertas",
        "title": "🚨 Alertas Activas",
        "caption": "Focos rojos que requieren atención.",
        "button_label": "Ver Alertas ➔",
        "prompt": "¿Qué divisiones (UO2) tienen la mayor tasa de renuncia acumulada en el año 2025?",
        "role_required": ["admin", "hr_bp"]
    }
]

# --- SUGERENCIAS ---
SUGGESTIONS_HEADER = "##### 💡 ¿No sabes por dónde empezar? Prueba estas consultas:"

SUGGESTIONS_COLUMNS = [
    {
        "title": "📊 Tendencias y Evolución",
        "items": [
            {
                "label": "•  Curva de rotación mensual 2025",
                "prompt": "Muestra la tendencia mensual de rotación voluntaria e involuntaria del 2025 a nivel de toda la empresa."
            },
            {
                "label": "•  Comparativo 2024 vs 2025",
                "prompt": "Genera un gráfico comparativo de la rotación acumulada entre el año 2024 y 2025."
            }
        ]
    },
    {
        "title": "🔍 Focos y Segmentos",
        "items": [
            {
                "label": "•  Ranking de Divisiones (UO2)",
                "prompt": "¿Cuáles son las 5 divisiones (UO2) con mayor cantidad de renuncias en lo que va del año?"
            },
            {
                "label": "•  FFVV vs Administrativos",
                "prompt": "Compara la tasa de rotación entre el segmento Fuerza de Ventas y Administrativos para el año 2025."
            }
        ]
    },
    {
        "title": "🧠 Insights Profundos",
        "items": [
             {
                "label": "•  Motivos de Salida",
                "prompt": "¿Cuáles son los principales motivos de renuncia registrados en el último trimestre de 2025 a nivel de toda la empresa?"
            },
            {
                "label": "•  Listado de Bajas Recientes",
                "prompt": "Dame un listado detallado de las personas que cesaron el último mes cerrado del año 2025 a nivel de toda la empresa."
            }
        ]
    }
]
