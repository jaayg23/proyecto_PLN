# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based RAG (Retrieval-Augmented Generation) application that allows users to view PDF notebooks and chat with their content using AI. The app combines PDF viewing capabilities with an intelligent chat interface powered by LangChain.

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

1. **LangChain RAG Pipeline**: The app implements a complete RAG workflow:
   - PDF loading via `PyPDFLoader`
   - Document chunking using `RecursiveCharacterTextSplitter` (chunk_size=1000, chunk_overlap=150)
   - Vector embeddings via Google's `text-embedding-004` model
   - Vector storage in ChromaDB (in-memory)
   - Retrieval using Chroma's retriever (k=4 documents)
   - Response generation via `RetrievalQA` chain with "stuff" chain type

2. **Caching Strategy**: Heavy use of Streamlit's caching decorators:
   - `@st.cache_resource`: For LLM models, embeddings, ChromaDB instances, and RAG chains (shared across sessions)
   - `@st.cache_data`: For PDF loading and splitting (data transformations)
   - Each ChromaDB collection has a unique name based on the PDF filename to avoid conflicts

3. **State Management**: Session state tracks:
   - `selected_notebook`: Currently loaded notebook
   - `messages`: Chat history for the current session
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

### Chat Reset Behavior

When a new notebook is selected, the chat history (`st.session_state.messages`) is cleared to prevent confusion between different document contexts.
