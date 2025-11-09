"""Helper functions and utilities."""

import streamlit as st


class SessionStateManager:
    """Manage Streamlit session state."""

    @staticmethod
    def initialize():
        """Initialize session state variables."""
        if "selected_notebook" not in st.session_state:
            st.session_state.selected_notebook = None

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "llm_model_name" not in st.session_state:
            st.session_state.llm_model_name = "google"

    @staticmethod
    def get_selected_notebook():
        """Get currently selected notebook."""
        return st.session_state.get("selected_notebook")

    @staticmethod
    def set_selected_notebook(notebook_name: str):
        """Set selected notebook."""
        st.session_state.selected_notebook = notebook_name

    @staticmethod
    def get_messages():
        """Get chat messages."""
        return st.session_state.get("messages", [])

    @staticmethod
    def add_message(role: str, content: str):
        """Add a message to chat history."""
        st.session_state.messages.append({"role": role, "content": content})

    @staticmethod
    def clear_messages():
        """Clear chat history."""
        st.session_state.messages = []

    @staticmethod
    def get_llm_model_name():
        """Get selected LLM model name."""
        return st.session_state.get("llm_model_name", "google")

    @staticmethod
    def set_llm_model_name(model_name: str):
        """Set LLM model name."""
        st.session_state.llm_model_name = model_name
