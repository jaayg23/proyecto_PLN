"""Reusable UI components."""

import streamlit as st
from typing import Optional, List


class UIComponents:
    """Collection of reusable UI components."""

    @staticmethod
    def render_model_selector(
        available_models: List[str],
        default_model: str = "google"
    ) -> str:
        """
        Render LLM model selector.

        Args:
            available_models: List of available model names
            default_model: Default selected model

        Returns:
            Selected model name
        """
        if not available_models:
            st.error("❌ No LLM models available. Please configure API keys.")
            return default_model

        # Ensure default is in available models
        if default_model not in available_models:
            default_model = available_models[0]

        selected_model = st.selectbox(
            "🤖 AI Model:",
            available_models,
            index=available_models.index(default_model),
            key="llm_model_name",
            help="Select the AI model to use for generating responses"
        )

        return selected_model

    @staticmethod
    def render_notebook_selector(
        notebooks: dict,
        default_index: Optional[int] = None
    ) -> Optional[str]:
        """
        Render notebook/document selector.

        Args:
            notebooks: Dictionary of notebook configurations
            default_index: Default selected index

        Returns:
            Selected notebook name or None
        """
        notebook_names = list(notebooks.keys())

        selected = st.selectbox(
            "📚 Select a document to view:",
            notebook_names,
            index=default_index,
            placeholder="Choose from available documents...",
            help="Select a document from your library to view its content"
        )

        return selected

    @staticmethod
    def render_pdf_viewer(notebook_name: str, local_path: str):
        """
        Render PDF viewer from local file.

        Args:
            notebook_name: Name of the notebook
            local_path: Path to local PDF file
        """
        import base64
        import os

        st.markdown(f"### 📄 {notebook_name}")
        st.markdown("---")

        if not os.path.exists(local_path):
            st.error(f"❌ PDF file not found: `{local_path}`")
            st.info("💡 **Tip:** You can still query this document in the AI Chat Assistant if it was previously loaded.")
            return

        try:
            # Read PDF file
            with open(local_path, "rb") as f:
                pdf_bytes = f.read()

            # Encode to base64
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

            # Create PDF viewer with embedded data
            pdf_display = f'''
                <iframe
                    src="data:application/pdf;base64,{base64_pdf}"
                    width="100%"
                    height="800px"
                    type="application/pdf"
                    style="border: none;">
                </iframe>
            '''

            st.markdown(pdf_display, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error loading PDF: `{e}`")
            st.info("💡 **Tip:** You can still query this document in the AI Chat Assistant.")

    @staticmethod
    def render_available_documents(retrievers: dict):
        """
        Render expandable list of available documents.

        Args:
            retrievers: Dictionary of retrievers (keys are notebook names)
        """
        with st.expander("📚 **Available Documents** — Click to view", expanded=False):
            if retrievers:
                st.markdown("The AI can search across these documents:")
                st.markdown("")
                for idx, notebook_name in enumerate(retrievers.keys(), 1):
                    st.markdown(f"**{idx}.** 📖 {notebook_name}")
            else:
                st.warning("⚠️ Could not load documents.")

    @staticmethod
    def render_chat_message(role: str, content: str):
        """
        Render a chat message.

        Args:
            role: Message role (user/assistant)
            content: Message content
        """
        with st.chat_message(role):
            st.markdown(content)

    @staticmethod
    def render_chat_history(messages: List[dict]):
        """
        Render chat history.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
        """
        for message in messages:
            UIComponents.render_chat_message(
                role=message["role"],
                content=message["content"]
            )

    @staticmethod
    def show_info_message(message: str):
        """Show info message."""
        st.info(f"ℹ️ {message}")

    @staticmethod
    def show_error_message(message: str):
        """Show error message."""
        st.error(f"❌ {message}")

    @staticmethod
    def show_warning_message(message: str):
        """Show warning message."""
        st.warning(f"⚠️ {message}")

    @staticmethod
    def show_success_message(message: str):
        """Show success message."""
        st.success(f"✅ {message}")
