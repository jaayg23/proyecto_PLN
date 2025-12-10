"""Custom CSS styling for the application."""

import streamlit as st


def apply_custom_styles():
    """Apply custom CSS styling to the Streamlit application."""
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Main container - Dark theme */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            background-color: #0f172a;
        }
        
        .main {
            background-color: #0f172a;
        }
        
        /* Main title styling */
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f0abfc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
            text-align: center;
            animation: fadeInDown 0.6s ease-out;
        }

        .subtitle {
            color: #94a3b8;
            font-size: 1.15rem;
            margin-bottom: 2.5rem;
            text-align: center;
            font-weight: 400;
            line-height: 1.6;
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* Animations */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Tab styling - Dark theme */
        .stTabs {
            background-color: #1e293b;
            border-radius: 16px;
            padding: 0.5rem;
            margin-bottom: 2rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 14px 28px;
            font-weight: 600;
            font-size: 0.95rem;
            background-color: #0f172a;
            border-radius: 12px;
            color: #94a3b8;
            transition: all 0.3s ease;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #1e293b;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
            color: #cbd5e1;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%) !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(129, 140, 248, 0.5) !important;
        }

        /* Info boxes - Dark theme */
        .stAlert {
            border-radius: 12px;
            border: 1px solid #334155;
            padding: 1rem 1.25rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            animation: fadeInUp 0.4s ease-out;
            background-color: #1e293b !important;
            color: #e2e8f0 !important;
        }
        
        [data-testid="stNotification"] {
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }

        /* Chat container - Dark theme */
        .stChatMessage {
            padding: 1.25rem;
            border-radius: 16px;
            margin-bottom: 1rem;
            animation: fadeInUp 0.3s ease-out;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .stChatMessage[data-testid="user-message"] {
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
            color: white;
        }
        
        .stChatMessage[data-testid="assistant-message"] {
            background-color: #1e293b;
            border: 1px solid #334155;
            color: #e2e8f0;
        }

        /* Selectbox - Dark theme */
        .stSelectbox {
            margin-bottom: 1.5rem;
        }
        
        .stSelectbox label {
            color: #e2e8f0 !important;
            font-weight: 600 !important;
        }
        
        .stSelectbox > div > div {
            border-radius: 10px;
            border: 2px solid #334155;
            transition: all 0.3s ease;
            background-color: #1e293b;
        }
        
        .stSelectbox > div > div:hover {
            border-color: #818cf8;
            box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2);
        }
        
        .stSelectbox > div > div:focus-within {
            border-color: #818cf8;
            box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.3);
        }
        
        /* Selectbox text color */
        .stSelectbox div[data-baseweb="select"] > div {
            color: #e2e8f0;
        }

        /* Headers and text - Dark theme */
        h1, h2, h3, h4, h5, h6 {
            color: #f1f5f9 !important;
        }
        
        .stMarkdown p {
            color: #cbd5e1;
        }
        
        /* Expander - Dark theme */
        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 1rem;
            background-color: #1e293b;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
            color: #e2e8f0;
            border: 1px solid #334155;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #334155;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .streamlit-expanderContent {
            color: #cbd5e1;
            background-color: #1e293b;
        }
        
        /* Input field - Dark theme */
        .stChatInputContainer {
            border-top: 1px solid #334155;
            padding-top: 1rem;
        }
        
        .stChatInput > div > div {
            border-radius: 12px;
            border: 2px solid #334155;
            transition: all 0.3s ease;
            background-color: #1e293b;
        }
        
        .stChatInput > div > div:focus-within {
            border-color: #818cf8;
            box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2);
        }
        
        .stChatInput input {
            color: #e2e8f0;
        }
        
        .stChatInput input::placeholder {
            color: #64748b;
        }
        
        /* Buttons - Dark theme */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.5rem 1.5rem;
            transition: all 0.3s ease;
            border: none;
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
            color: white;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(129, 140, 248, 0.5);
        }
        
        /* PDF Viewer - Dark theme */
        iframe {
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            transition: box-shadow 0.3s ease;
            border: 1px solid #334155;
        }
        
        iframe:hover {
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6);
        }
        
        /* Container with border - Dark theme */
        [data-testid="stVerticalBlock"] > div:has(> div.stChatMessage) {
            background-color: #0f172a;
            border-radius: 16px;
            padding: 1rem;
        }
        
        /* Spinner - Dark theme */
        .stSpinner > div {
            border-top-color: #818cf8 !important;
        }
        
        /* Divider - Dark theme */
        hr {
            margin: 2rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #334155, transparent);
        }
        
        /* Sidebar - Dark theme */
        [data-testid="stSidebar"] {
            background-color: #1e293b;
        }
        
        /* Text input - Dark theme */
        .stTextInput input {
            background-color: #1e293b;
            color: #e2e8f0;
            border: 2px solid #334155;
        }
        
        .stTextInput input:focus {
            border-color: #818cf8;
            box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2);
        }
        
        /* Welcome message styling */
        .welcome-message {
            text-align: center;
            padding: 100px 20px;
            color: #64748b;
        }
        
        .welcome-message h3 {
            color: #cbd5e1 !important;
        }
        </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the application header."""
    st.markdown('<h1 class="main-title">✨ AI Study Assistant</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">🚀 Your intelligent companion for exploring technical documents with cutting-edge RAG technology</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")
