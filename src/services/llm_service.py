"""LLM and embeddings service layer."""

import streamlit as st
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from ..config.settings import Settings


class LLMService:
    """Service for managing LLM models and embeddings."""

    @staticmethod
    @st.cache_resource(show_spinner="Loading LLM model...")
    def load_llm(model_name: str):
        """
        Load the specified LLM model.

        Args:
            model_name: Either "openai" or "google"

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
    def load_embeddings() -> Optional[GoogleGenerativeAIEmbeddings]:
        """
        Load Google embeddings model with timeout configuration.

        Returns:
            Initialized embeddings model or None if loading fails
        """
        if not Settings.get_google_api_key():
            st.error("❌ Cannot load embeddings model. Missing GOOGLE_API_KEY.")
            return None

        try:
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
