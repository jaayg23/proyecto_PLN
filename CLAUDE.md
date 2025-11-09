# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based Multi-Agent RAG (Retrieval-Augmented Generation) application that allows users to view PDF notebooks and chat with their content using AI. The app features:
- **Tab 1 - PDF Viewer**: View and browse through your PDF notebooks
- **Tab 2 - Multi-Agent Chat**: Ask questions about any notebook, and an intelligent agent will automatically choose the most relevant notebook(s) to answer from

The app uses LangChain's agent framework with tools, where each notebook becomes a searchable tool. The LLM agent intelligently routes queries to the appropriate document(s).

## Key Commands

### Running the Application
```bash
streamlit run app.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Core Components

The application is structured as a single-file Streamlit app (`app.py`) with the following key architectural components:

1. **Multi-Agent RAG System**: The app implements an intelligent multi-document RAG workflow:
   - PDF loading via `PyPDFLoader`
   - Document chunking using `RecursiveCharacterTextSplitter` (chunk_size=1000, chunk_overlap=150)
   - Vector embeddings via Google's `text-embedding-004` model
   - Vector storage in ChromaDB (in-memory, one collection per notebook)
   - **Agent with Tools**: Each notebook becomes a LangChain Tool with:
     - Retriever (k=4 documents per notebook)
     - Descriptive metadata for agent decision-making
     - Page-number annotated results
   - **Zero-Shot ReAct Agent**: Uses `AgentType.ZERO_SHOT_REACT_DESCRIPTION` to intelligently select which notebook(s) to query
   - The agent can reason about which tool (notebook) is most relevant for each query

2. **Caching Strategy**: Heavy use of Streamlit's caching decorators:
   - `@st.cache_resource`: For LLM models, embeddings, ChromaDB instances, retrievers, and agent (shared across sessions)
   - `@st.cache_data`: For PDF loading and splitting (data transformations)
   - Each ChromaDB collection has a unique name based on the PDF filename to avoid conflicts
   - All retrievers are loaded once at startup for optimal performance

3. **State Management**: Session state tracks:
   - `selected_notebook`: Currently viewed notebook in Tab 1 (for PDF viewer only)
   - `messages`: Chat history for the multi-agent chat (persistent across notebook switches)
   - `llm_model_name`: Selected LLM model ("google" or "openai")

### Supported LLM Models

- **Google**: `gemini-2.5-flash` (default)
- **OpenAI**: `gpt-4o-mini`

Both models use temperature=0.1 for more deterministic responses.

## Configuration

### API Keys

The application requires API keys stored in `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your_google_api_key"
OPENAI_API_KEY = "your_openai_api_key"
```

The app will function with only one API key, but both LLM options require their respective keys.

### Adding New Notebooks

Edit the `CUADERNOS` dictionary in `app.py`:

```python
CUADERNOS = {
    "Notebook Title": {
        "gdrive_id": "google_drive_file_id",  # For PDF preview (optional)
        "local_path": "path_to_local_pdf.pdf"  # Required for RAG
    }
}
```

- `gdrive_id`: Used for Google Drive PDF preview iframe (can be None)
- `local_path`: Path to local PDF file (required for RAG functionality)

## Important Technical Details

### ChromaDB Collection Naming

Collections are named dynamically: `doc_{filename_with_underscores}`. This ensures each PDF gets its own vector store and prevents conflicts when switching between notebooks.

### Error Handling

The app gracefully handles missing API keys and file paths, displaying informative error messages to users rather than crashing. Each major component (LLM loading, embeddings, ChromaDB creation, RAG chain) has try-catch blocks.

### Agent Tool Selection

The agent uses descriptive tool metadata to decide which notebook to query. Each tool includes:
- A descriptive name (e.g., `Buscador_Apuntes_de_Análisis_Real`)
- A detailed description of the notebook's content and when to use it
- This allows the LLM to intelligently route questions like "What is a derivative?" to the math notebook and "What is RETIE?" to the electrical regulations notebook

### Chat Persistence

Unlike the previous version, the chat history in Tab 2 is **persistent** and doesn't clear when switching between notebooks in Tab 1. This allows users to have a continuous conversation about multiple notebooks.
