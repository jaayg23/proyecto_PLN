"""Vector store service for managing ChromaDB operations."""

import os
import time
import streamlit as st
from typing import Optional, Dict, List
from langchain_community.vectorstores import Chroma
from langchain.schema.vectorstore import VectorStoreRetriever
from langchain.schema import Document

from ..config.settings import Settings
from .llm_service import LLMService
from .document_service import DocumentService


class VectorStoreService:
    """Service for managing vector databases and retrievers."""

    @staticmethod
    def _create_chroma_in_batches(
        split_docs: List[Document],
        embeddings,
        collection_name: str
    ) -> Optional[Chroma]:
        """
        Create ChromaDB by processing documents in batches with retry logic.

        Args:
            split_docs: List of document chunks
            embeddings: Embeddings model
            collection_name: Name for the ChromaDB collection

        Returns:
            ChromaDB instance or None if creation fails
        """
        batch_size = Settings.EMBEDDING_BATCH_SIZE
        max_retries = Settings.EMBEDDING_MAX_RETRIES
        retry_delay = Settings.EMBEDDING_RETRY_DELAY

        total_docs = len(split_docs)
        chroma_db = None

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Process documents in batches
            for i in range(0, total_docs, batch_size):
                batch = split_docs[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_docs + batch_size - 1) // batch_size

                status_text.text(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)...")

                # Retry logic for each batch
                for attempt in range(max_retries):
                    try:
                        if chroma_db is None:
                            # Create initial ChromaDB with first batch
                            chroma_db = Chroma.from_documents(
                                documents=batch,
                                embedding=embeddings,
                                collection_name=collection_name
                            )
                        else:
                            # Add subsequent batches to existing ChromaDB
                            chroma_db.add_documents(documents=batch)

                        # Update progress
                        progress = min((i + len(batch)) / total_docs, 1.0)
                        progress_bar.progress(progress)
                        break  # Success, exit retry loop

                    except Exception as e:
                        if "504" in str(e) or "deadline" in str(e).lower():
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                                status_text.warning(
                                    f"⚠️ Timeout on batch {batch_num} (attempt {attempt + 1}/{max_retries}). "
                                    f"Retrying in {wait_time}s..."
                                )
                                time.sleep(wait_time)
                            else:
                                status_text.error(
                                    f"❌ Failed to process batch {batch_num} after {max_retries} attempts. "
                                    f"Error: {e}"
                                )
                                raise
                        else:
                            # Non-timeout error, raise immediately
                            raise

                # Small delay between batches to avoid rate limiting
                if i + batch_size < total_docs:
                    time.sleep(0.5)

            progress_bar.progress(1.0)
            status_text.success(f"✅ Successfully processed {total_docs} documents in {total_batches} batches!")
            time.sleep(1)  # Brief pause to show success message

            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()

            return chroma_db

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Error creating ChromaDB: {e}")
            return None

    @staticmethod
    @st.cache_resource(show_spinner="Creating vector database...")
    def create_chroma_db(file_path: str):
        """
        Create ChromaDB instance from PDF file using batch processing.

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

        # Create ChromaDB using batch processing with retry logic
        return VectorStoreService._create_chroma_in_batches(
            split_docs=split_docs,
            embeddings=embeddings,
            collection_name=collection_name
        )

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
