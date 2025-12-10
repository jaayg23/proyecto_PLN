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
        st.markdown("## 📖 Document Viewer")
        st.markdown("Browse through your PDF document library with ease.")
        st.markdown("")

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
            st.info("👆 Select a document from the dropdown menu above to start viewing.")


class ChatAssistantPage:
    """AI Chat Assistant tab page."""

    @staticmethod
    def render(notebooks: dict):
        """
        Render the AI chat assistant page.

        Args:
            notebooks: Dictionary of notebook configurations
        """
        st.markdown("## 🤖 AI Chat Assistant")
        st.markdown(
            "Ask questions about **any topic** from your documents. "
            "The AI will intelligently search and select the most relevant sources to provide accurate answers."
        )
        st.markdown("")

        # Model selector in columns
        col1, col2 = st.columns([2, 1])

        with col1:
            st.info("💡 **Smart Multi-Document Search** — The AI agent automatically finds and uses the most relevant documents to answer your questions.")

        with col2:
            available_models = LLMService.get_available_models()
            selected_model = UIComponents.render_model_selector(
                available_models=available_models,
                default_model=available_models[0] if available_models else "ollama"
            )
            st.caption(f"Usando: **{selected_model}**")

        # Load LLM directamente con el modelo seleccionado
        llm = LLMService.load_llm(selected_model)
        
        if llm is None:
            st.error(f"❌ No se pudo cargar el modelo: {selected_model}")
            st.stop()
        
        # Validate LLM loaded successfully
        if llm is None:
            st.error("❌ Could not load the selected model. Please check:")
            st.markdown("- For **Ollama**: Make sure Ollama is running (check system tray)")
            st.markdown("- For **Google**: Check that GOOGLE_API_KEY is configured in secrets")
            st.markdown("- For **OpenAI**: Check that OPENAI_API_KEY is configured in secrets")
            st.stop()
        
        retrievers = VectorStoreService.create_all_retrievers(notebooks)
        
        # Validate retrievers loaded successfully
        if not retrievers:
            st.error("❌ Could not load documents. Please check that:")
            st.markdown("- PDF files exist in the configured paths")
            st.markdown("- GOOGLE_API_KEY is configured for embeddings")
            st.stop()
        
        agent = AgentService.create_multi_rag_agent(llm, retrievers, notebooks)

        # Show available documents
        UIComponents.render_available_documents(retrievers)
        
        st.markdown("")

        # Chat container
        chat_container = st.container(height=600, border=True)

        # Render chat history
        with chat_container:
            if not st.session_state.messages:
                st.markdown("""
                <div class='welcome-message'>
                    <h3>👋 Welcome to your AI Study Assistant!</h3>
                    <p style='font-size: 1.1rem; margin-top: 1rem;'>Start by asking a question about your documents below.</p>
                    <p style='margin-top: 0.5rem;'>💡 Example: "What are the main topics covered?"</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                UIComponents.render_chat_history(st.session_state.messages)

        # Handle user input
        if prompt := st.chat_input("💬 Ask me anything about your documents..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            with chat_container:
                UIComponents.render_chat_message("user", prompt)

            # Generate response
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("🔍 Searching through documents and generating response..."):
                        response = AgentService.run_agent(agent, prompt)
                        st.markdown(response)

            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": response})
