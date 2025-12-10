"""Agent service for managing RAG agents and tools."""

import streamlit as st
from typing import Optional, Dict
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.schema.vectorstore import VectorStoreRetriever

from ..config.settings import Settings
from ..config.notebooks import NotebookConfig


class AgentService:
    """Service for creating and managing LangChain agents and tools."""

    @staticmethod
    def create_retriever_tool(
        notebook_name: str,
        retriever: VectorStoreRetriever,
        notebook_config: NotebookConfig
    ) -> Tool:
        """
        Create a LangChain Tool from a retriever.

        Args:
            notebook_name: Name of the notebook
            retriever: Vector store retriever
            notebook_config: Notebook configuration with description

        Returns:
            LangChain Tool instance
        """
        def search_notebook(query: str) -> str:
            """Search for information in the notebook and return relevant context."""
            try:
                docs = retriever.get_relevant_documents(query)

                if not docs:
                    return f"No relevant information found in '{notebook_name}'."

                results = []
                for doc in docs:
                    page = doc.metadata.get("page", "unknown")
                    content = doc.page_content.strip()
                    results.append(f"[Page {page}] {content}")

                return "\n\n".join(results)

            except Exception as e:
                return f"Error searching in '{notebook_name}': {str(e)}"

        # Use description from notebook configuration
        description = notebook_config.description

        return Tool(
            name=f"Search_{notebook_name.replace(' ', '_')}",
            func=search_notebook,
            description=description
        )

    @staticmethod
    def create_multi_rag_agent(
        _llm,
        _retrievers: Dict[str, VectorStoreRetriever],
        notebooks: dict
    ):
        """
        Create an agent that can choose between multiple notebooks.

        Args:
            _llm: Language model instance
            _retrievers: Dictionary mapping notebook names to retrievers
            notebooks: Dictionary of notebook configurations

        Returns:
            Initialized agent or None if creation fails
        """
        if _llm is None or not _retrievers:
            return None

        try:
            # Create tools for each retriever
            tools = []
            for notebook_name, retriever in _retrievers.items():
                notebook_config = notebooks.get(notebook_name)
                if notebook_config:
                    tool = AgentService.create_retriever_tool(
                        notebook_name,
                        retriever,
                        notebook_config
                    )
                    tools.append(tool)

            # Initialize agent with tools - sin límites
            agent = initialize_agent(
                tools=tools,
                llm=_llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=Settings.AGENT_VERBOSE,
                handle_parsing_errors=True,
                return_intermediate_steps=False,
                early_stopping_method="generate",
                max_iterations=Settings.AGENT_MAX_ITERATIONS,
                agent_kwargs={
                    "system_message": (
                        "You are a focused document analysis assistant. "
                        "Always consult the provided tools to gather evidence from the user's documents "
                        "before answering. Cite page numbers when possible and admit when the documents "
                        "do not contain the requested information."
                    )
                }
            )

            return agent

        except Exception as e:
            st.error(f"❌ Error creating multi-RAG agent: {e}")
            return None

    @staticmethod
    def run_agent(agent, query: str) -> str:
        """
        Run agent with a query.

        Args:
            agent: Initialized agent
            query: User query

        Returns:
            Agent response or error message
        """
        if agent is None:
            return "Error: Agent not initialized. Please check API keys and PDF availability."

        try:
            result = agent.run(query)
            return result
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            st.error(f"❌ {error_msg}")
            return error_msg
