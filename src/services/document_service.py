"""Document processing and PDF handling service."""

import streamlit as st
from typing import Optional, List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from ..config.settings import Settings


class DocumentService:
    """Service for loading and processing PDF documents."""

    @staticmethod
    @st.cache_data(show_spinner="Loading and processing PDF...")
    def load_and_split_pdf(file_path: str) -> Optional[List[Document]]:
        """
        Load a PDF file and split it into chunks.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of document chunks or None if loading fails
        """
        try:
            # Load PDF
            loader = PyPDFLoader(file_path=file_path)
            docs = loader.load()

            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=Settings.CHUNK_SIZE,
                chunk_overlap=Settings.CHUNK_OVERLAP
            )
            split_docs = text_splitter.split_documents(docs)

            return split_docs

        except FileNotFoundError:
            st.error(f"❌ PDF file not found: {file_path}")
            return None
        except Exception as e:
            st.error(f"❌ Error loading PDF: {e}")
            return None

    @staticmethod
    def validate_pdf_exists(file_path: str) -> bool:
        """
        Check if PDF file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        import os
        return os.path.exists(file_path) and file_path.endswith('.pdf')

    @staticmethod
    def get_pdf_metadata(file_path: str) -> dict:
        """
        Extract metadata from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary with metadata (pages, size, etc.)
        """
        import os

        metadata = {
            "exists": False,
            "path": file_path,
            "size_bytes": 0,
            "size_mb": 0.0
        }

        if os.path.exists(file_path):
            metadata["exists"] = True
            size_bytes = os.path.getsize(file_path)
            metadata["size_bytes"] = size_bytes
            metadata["size_mb"] = round(size_bytes / (1024 * 1024), 2)

        return metadata
