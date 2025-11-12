"""Application settings and configuration management."""

import os
import streamlit as st
from typing import Optional


class Settings:
    """Centralized configuration management for the application."""

    # LLM Model Configuration
    GOOGLE_MODEL_NAME = "gemini-2.5-flash"
    OPENAI_MODEL_NAME = "gpt-4o-mini"
    EMBEDDINGS_MODEL_NAME = "models/text-embedding-004"
    LLM_TEMPERATURE = 0.1

    # Document Processing Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150
    RETRIEVER_K = 4

    # Embedding Configuration
    EMBEDDING_BATCH_SIZE = 10  # Process embeddings in small batches to avoid timeouts
    EMBEDDING_REQUEST_TIMEOUT = 60  # Timeout in seconds for embedding requests
    EMBEDDING_MAX_RETRIES = 3  # Maximum number of retries for failed batches
    EMBEDDING_RETRY_DELAY = 2  # Initial delay between retries (will use exponential backoff)

    # Agent Configuration
    AGENT_MAX_ITERATIONS = 3
    AGENT_VERBOSE = True

    # UI Configuration
    PAGE_TITLE = "AI Study Assistant"
    PAGE_ICON = "📚"
    LAYOUT = "wide"

    @staticmethod
    def load_api_keys() -> tuple[Optional[str], Optional[str]]:
        """
        Load API keys from Streamlit secrets.

        Returns:
            tuple: (google_api_key, openai_api_key)
        """
        google_key = None
        openai_key = None

        try:
            google_key = st.secrets["GOOGLE_API_KEY"]
            os.environ["GOOGLE_API_KEY"] = google_key
        except KeyError:
            st.error("⚠️ GOOGLE_API_KEY not found in secrets. Google models and embeddings will not work.")

        try:
            openai_key = st.secrets["OPENAI_API_KEY"]
            os.environ["OPENAI_API_KEY"] = openai_key
        except KeyError:
            st.error("⚠️ OPENAI_API_KEY not found in secrets. OpenAI models will not work.")

        return google_key, openai_key

    @staticmethod
    def get_google_api_key() -> Optional[str]:
        """Get Google API key from environment."""
        return os.getenv("GOOGLE_API_KEY")

    @staticmethod
    def get_openai_api_key() -> Optional[str]:
        """Get OpenAI API key from environment."""
        return os.getenv("OPENAI_API_KEY")
