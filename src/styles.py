import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        /* Import Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --rimac-red: #EF3340;
            --rimac-dark: #1A202C;
            --rimac-gray: #F7F9FC;
            --text-primary: #2D3748;
            --text-secondary: #718096;
        }

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
        }

        /* --- Global Background --- */
        .stApp {
            background-color: #FFFFFF;
        }

        /* --- Header & Sidebar --- */
        [data-testid="stSidebar"] {
            background-color: #FAFAFA;
            border-right: 1px solid #E2E8F0;
        }
        
        [data-testid="stSidebar"] hr {
            border-color: #E2E8F0;
        }

        /* --- Inputs --- */
        /* Target the outer container of the input to ensure border surrounds everything (incl. eye icon) */
        div[data-baseweb="input"] {
            border-radius: 8px;
            border: 1px solid #E2E8F0;
            background-color: #FFFFFF;
        }

        /* Ensure inner styling doesn't create double borders or weird backgrounds */
        div[data-baseweb="input"] > div {
            border: none;
            background-color: transparent !important;
        }
        
        div[data-baseweb="input"]:hover {
            border-color: #CBD5E0;
        }

        div[data-baseweb="input"]:focus-within {
            border-color: var(--rimac-red) !important;
            box-shadow: 0 0 0 1px var(--rimac-red) !important;
        }

        /* --- Buttons --- */
        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1.5rem;
            transition: all 0.2s;
            border: none;
            width: 100%;
        }

        /* Primary Button (Use specific key or class if possible, otherwise generic overrides) */
        div.stButton > button:active, div.stButton > button:focus, div.stButton > button:hover {
            border-color: transparent;
            color: inherit;
        }

        /* --- Metric Cards --- */
        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid #E2E8F0;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2.25rem !important;
            font-weight: 700;
            color: var(--rimac-dark);
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.875rem !important;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* --- Chat UI --- */
        [data-testid="stChatMessage"] {
            background-color: #FFFFFF;
            border: 1px solid #EDF2F7;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02);
        }

        [data-testid="stChatMessage"][data-testid="user"] {
            background-color: #F8FAFC;
        }

        /* --- Login Split Layout Helpers --- */
        .login-container {
            display: flex;
            height: 100vh;
        }
        
        .login-hero {
            flex: 1;
            background-color: var(--rimac-red);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        .login-form {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 4rem;
            background-color: #FFFFFF;
        }

        /* --- New Central Card Style --- */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .login-card-container {
            background-color: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            border: 1px solid #E2E8F0;
            animation: fadeIn 0.6s ease-out forwards;
            text-align: center;
        }
        
        .login-header {
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .login-subtitle {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 0.5rem;
        }

    </style>
    """, unsafe_allow_html=True)
