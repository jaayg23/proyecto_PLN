"""Page components for tabs."""

import streamlit as st
from typing import Optional

from .components import UIComponents
from ..services import LLMService, VectorStoreService, AgentService


class DocumentViewerPage:
    """Document viewer tab page."""

    @staticmethod
    def render(notebooks: dict):
        """
        Render the document viewer page.

        Args:
            notebooks: Dictionary of notebook configurations
        """
        st.header("📖 Document Viewer")
        st.markdown("Select and view your PDF documents.")

        # Notebook selector
        selected_notebook = UIComponents.render_notebook_selector(notebooks)

        if selected_notebook:
            # Store in session state
            st.session_state.selected_notebook = selected_notebook

            # Get notebook configuration
            notebook_config = notebooks[selected_notebook]

            # Render PDF viewer from local file
            UIComponents.render_pdf_viewer(
                notebook_name=selected_notebook,
                local_path=notebook_config.local_path
            )
        else:
            UIComponents.show_info_message("Select a document from the dropdown menu to view it.")


class ChatAssistantPage:
    """AI Chat Assistant tab page."""

    @staticmethod
    def render(notebooks: dict):
        """
        Render the AI chat assistant page.

        Args:
            notebooks: Dictionary of notebook configurations
        """
        st.header("🤖 AI Chat Assistant")
        st.markdown(
            "Ask questions about **any document**. "
            "The assistant will automatically choose the most relevant document to answer from."
        )

        # Model selector in columns
        col1, col2 = st.columns([3, 1])

        with col1:
            st.info("💡 The agent can search across multiple documents and select the most relevant one.")

        with col2:
            available_models = LLMService.get_available_models()
            model_name = UIComponents.render_model_selector(
                available_models=available_models,
                default_model=st.session_state.get("llm_model_name", "google")
            )

        # Load components
        llm = LLMService.load_llm(st.session_state.llm_model_name)
        retrievers = VectorStoreService.create_all_retrievers(notebooks)
        agent = AgentService.create_multi_rag_agent(llm, retrievers, notebooks)

        # Show available documents
        UIComponents.render_available_documents(retrievers)

        # Chat container
        chat_container = st.container(height=600, border=True)

        # Render chat history
        with chat_container:
            UIComponents.render_chat_history(st.session_state.messages)

        # Handle user input
        if prompt := st.chat_input("Ask about any topic from your documents..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            with chat_container:
                UIComponents.render_chat_message("user", prompt)

            # Generate response
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("🔍 Analyzing your documents..."):
                        response = AgentService.run_agent(agent, prompt)
                        st.markdown(response)

            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": response})
