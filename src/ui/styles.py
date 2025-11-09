"""Custom CSS styling for the application."""

import streamlit as st


def apply_custom_styles():
    """Apply custom CSS styling to the Streamlit application."""
    st.markdown("""
        <style>
        /* Main title styling */
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(120deg, #2563eb, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            color: #6b7280;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 12px 24px;
            font-weight: 500;
        }

        /* Info boxes */
        .stAlert {
            border-radius: 8px;
        }

        /* Chat container */
        .stChatMessage {
            padding: 1rem;
            border-radius: 8px;
        }

        /* Selectbox */
        .stSelectbox {
            margin-bottom: 1rem;
        }

        /* Expander */
        .streamlit-expanderHeader {
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the application header."""
    st.markdown('<h1 class="main-title">AI Study Assistant</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Intelligent companion for studying technical documents with advanced RAG technology</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")
