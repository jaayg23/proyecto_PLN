"""Application settings and configuration management."""

import os
import streamlit as st
from typing import Optional


class Settings:
    """Centralized configuration management for the application."""

    # LLM Model Configuration
    GOOGLE_MODEL_NAME = "gemini-2.5-flash"
    GOOGLE_MAX_OUTPUT_TOKENS = 1536
    OPENAI_MODEL_NAME = "gpt-4o-mini"
    OPENAI_MAX_TOKENS = 900
    OLLAMA_MODEL_NAME = "llama3.2"  # Modelo llama3.2 (3B) - buen balance
    OLLAMA_BASE_URL = "http://localhost:11434"  # URL de tu servidor Ollama
    OLLAMA_CONTEXT_WINDOW = 4096
    EMBEDDINGS_MODEL_NAME = "models/text-embedding-004"
    OLLAMA_EMBEDDINGS_MODEL = "nomic-embed-text"  # Modelo de embeddings de Ollama
    LLM_TEMPERATURE = 0.6

    # Document Processing Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150
    RETRIEVER_K = 6

    # Embedding Configuration
    EMBEDDING_BATCH_SIZE = 10  # Process embeddings in small batches to avoid timeouts
    EMBEDDING_REQUEST_TIMEOUT = 60  # Timeout in seconds for embedding requests
    EMBEDDING_MAX_RETRIES = 3  # Maximum number of retries for failed batches
    EMBEDDING_RETRY_DELAY = 2  # Initial delay between retries (will use exponential backoff)

    # Agent Configuration
    AGENT_MAX_ITERATIONS = 8
    AGENT_VERBOSE = False

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
