import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        /* Import Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        /* Gradient Background for Header */
        header {
            background: linear-gradient(90deg, #FFFFFF 0%, #F5F7FA 100%);
            border-bottom: 1px solid #EAEAEA;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #FAFAFA;
            border-right: 1px solid #E0E0E0;
        }

        /* Chat Messages */
        [data-testid="stChatMessage"] {
            background-color: #FFFFFF;
            border: 1px solid #F0F0F0;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }

        [data-testid="stChatMessage"][data-testid="user"] {
            background-color: #F3F6FF;
            border-color: #DDE5FF;
        }

        /* Metric Cards */
        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid #EAEAEA;
            text-align: center;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 800;
            color: #2D3748;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            color: #718096;
            font-weight: 600;
        }

        /* Buttons */
        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        /* Titles */
        h1 {
            background: -webkit-linear-gradient(45deg, #1A202C, #2D3748);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -1px;
        }

    </style>
    """, unsafe_allow_html=True)
