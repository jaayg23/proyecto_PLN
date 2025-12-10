"""LLM and embeddings service layer."""

import streamlit as st
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings

from ..config.settings import Settings


class LLMService:
    """Service for managing LLM models and embeddings."""

    @staticmethod
    @st.cache_resource(show_spinner="Loading LLM model...")
    def load_llm(model_name: str):
        """
        Load the specified LLM model.

        Args:
            model_name: Either "openai", "google", or "ollama"

        Returns:
            Initialized LLM model or None if loading fails
        """
        try:
            if model_name == "openai":
                if not Settings.get_openai_api_key():
                    st.error("❌ Cannot load OpenAI model. Missing OPENAI_API_KEY.")
                    return None
                return ChatOpenAI(
                    model_name=Settings.OPENAI_MODEL_NAME,
                    temperature=Settings.LLM_TEMPERATURE
                )
            elif model_name == "ollama":
                return ChatOllama(
                    model=Settings.OLLAMA_MODEL_NAME,
                    base_url=Settings.OLLAMA_BASE_URL,
                    temperature=Settings.LLM_TEMPERATURE
                )
            else:  # google
                if not Settings.get_google_api_key():
                    st.error("❌ Cannot load Google model. Missing GOOGLE_API_KEY.")
                    return None
                return ChatGoogleGenerativeAI(
                    model=Settings.GOOGLE_MODEL_NAME,
                    temperature=Settings.LLM_TEMPERATURE
                )
        except Exception as e:
            st.error(f"❌ Error loading {model_name} model: {e}")
            return None

    @staticmethod
    @st.cache_resource(show_spinner="Loading embeddings model...")
    def load_embeddings(use_ollama: bool = False):
        """
        Load embeddings model (Google or Ollama).

        Args:
            use_ollama: If True, use Ollama embeddings. Otherwise use Google embeddings.

        Returns:
            Initialized embeddings model or None if loading fails
        """
        try:
            if use_ollama:
                # Usar embeddings de Ollama
                return OllamaEmbeddings(
                    model=Settings.OLLAMA_EMBEDDINGS_MODEL,
                    base_url=Settings.OLLAMA_BASE_URL
                )
            else:
                # Usar embeddings de Google
                if not Settings.get_google_api_key():
                    st.error("❌ Cannot load Google embeddings model. Missing GOOGLE_API_KEY.")
                    return None
                return GoogleGenerativeAIEmbeddings(
                    model=Settings.EMBEDDINGS_MODEL_NAME,
                    request_options={"timeout": Settings.EMBEDDING_REQUEST_TIMEOUT}
                )
        except Exception as e:
            st.error(f"❌ Error loading embeddings: {e}")
            return None

    @staticmethod
    def get_available_models() -> list[str]:
        """
        Get list of available LLM models based on configured API keys.

        Returns:
            List of available model names
        """
        available = []
        # Ollama siempre está disponible si está corriendo localmente
        available.append("ollama")
        if Settings.get_google_api_key():
            available.append("google")
        if Settings.get_openai_api_key():
            available.append("openai")
        return available

    @staticmethod
    def validate_model_availability(model_name: str) -> bool:
        """
        Check if a specific model is available.

        Args:
            model_name: Model name to validate

        Returns:
            True if model is available, False otherwise
        """
        return model_name in LLMService.get_available_models()
