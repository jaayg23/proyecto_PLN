"""
AI Study Assistant - Main Application Entry Point

A modular Streamlit application for viewing PDF documents and chatting with them
using Multi-Agent RAG (Retrieval-Augmented Generation) technology.
"""

import streamlit as st

from src.config import Settings, NOTEBOOKS
from src.ui import apply_custom_styles, render_header, DocumentViewerPage, ChatAssistantPage
from src.utils import SessionStateManager


def main():
    """Main application entry point."""
    # Configure page
    st.set_page_config(
        page_title=Settings.PAGE_TITLE,
        page_icon=Settings.PAGE_ICON,
        layout=Settings.LAYOUT,
        initial_sidebar_state="collapsed"
    )

    # Apply custom styling
    apply_custom_styles()

    # Render header
    render_header()

    # Load API keys
    Settings.load_api_keys()

    # Initialize session state
    SessionStateManager.initialize()

    # Create tabs
    tab1, tab2 = st.tabs(["📖 Document Viewer", "🤖 AI Chat Assistant"])

    # Render tabs
    with tab1:
        DocumentViewerPage.render(NOTEBOOKS)

    with tab2:
        ChatAssistantPage.render(NOTEBOOKS)


if __name__ == "__main__":
    main()
