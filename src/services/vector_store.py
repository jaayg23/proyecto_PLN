"""Vector store service for managing ChromaDB operations."""

import os
import streamlit as st
from typing import Optional, Dict
from langchain_community.vectorstores import Chroma
from langchain.schema.vectorstore import VectorStoreRetriever

from ..config.settings import Settings
from .llm_service import LLMService
from .document_service import DocumentService


class VectorStoreService:
    """Service for managing vector databases and retrievers."""

    @staticmethod
    @st.cache_resource(show_spinner="Creating vector database...")
    def create_chroma_db(file_path: str):
        """
        Create ChromaDB instance from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            ChromaDB instance or None if creation fails
        """
        # Load embeddings
        embeddings = LLMService.load_embeddings()
        if embeddings is None:
            return None

        # Load and split documents
        split_docs = DocumentService.load_and_split_pdf(file_path)
        if split_docs is None:
            return None

        # Create unique collection name based on filename
        collection_name = f"doc_{os.path.basename(file_path).replace('.', '_').replace(' ', '_')}"

        try:
            # Create ChromaDB with embeddings
            chroma_db = Chroma.from_documents(
                documents=split_docs,
                embedding=embeddings,
                collection_name=collection_name
            )
            return chroma_db
        except Exception as e:
            st.error(f"❌ Error creating ChromaDB: {e}")
            return None

    @staticmethod
    def create_retriever(
        chroma_db,
        k: Optional[int] = None
    ) -> Optional[VectorStoreRetriever]:
        """
        Create retriever from ChromaDB instance.

        Args:
            chroma_db: ChromaDB instance
            k: Number of documents to retrieve (default from Settings)

        Returns:
            Retriever instance or None if creation fails
        """
        if chroma_db is None:
            return None

        k = k or Settings.RETRIEVER_K

        try:
            retriever = chroma_db.as_retriever(search_kwargs={"k": k})
            return retriever
        except Exception as e:
            st.error(f"❌ Error creating retriever: {e}")
            return None

    @staticmethod
    @st.cache_resource(show_spinner="Creating retrievers for all documents...")
    def create_all_retrievers(notebooks: dict) -> Optional[Dict[str, VectorStoreRetriever]]:
        """
        Create retrievers for all configured notebooks.

        Args:
            notebooks: Dictionary of notebook configurations

        Returns:
            Dictionary mapping notebook names to retrievers
        """
        embeddings = LLMService.load_embeddings()
        if embeddings is None:
            return None

        retrievers = {}

        for notebook_name, notebook_config in notebooks.items():
            local_path = notebook_config.local_path

            if local_path and os.path.exists(local_path):
                try:
                    chroma_db = VectorStoreService.create_chroma_db(local_path)
                    if chroma_db:
                        retriever = VectorStoreService.create_retriever(chroma_db)
                        if retriever:
                            retrievers[notebook_name] = retriever
                except Exception as e:
                    st.warning(f"⚠️ Could not create retriever for '{notebook_name}': {e}")
            else:
                st.warning(f"⚠️ PDF file not found for '{notebook_name}': {local_path}")

        return retrievers if retrievers else None

    @staticmethod
    def get_collection_name(file_path: str) -> str:
        """
        Generate ChromaDB collection name from file path.

        Args:
            file_path: Path to file

        Returns:
            Sanitized collection name
        """
        return f"doc_{os.path.basename(file_path).replace('.', '_').replace(' ', '_')}"
