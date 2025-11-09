# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **modular, production-ready** Streamlit-based Multi-Agent RAG (Retrieval-Augmented Generation) application that allows users to view PDF notebooks and chat with their content using AI.

### Key Features
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

## Architecture Overview

**Version 2.0** introduces a **modular, layered architecture** with clean separation of concerns:

```
proyecto_PLN/
├── app.py                          # Main entry point (minimal, ~50 lines)
├── src/
│   ├── config/                     # Configuration layer
│   │   ├── settings.py            # Application settings
│   │   └── notebooks.py           # Document database
│   ├── services/                   # Business logic layer
│   │   ├── llm_service.py         # LLM management
│   │   ├── document_service.py    # PDF processing
│   │   ├── vector_store.py        # ChromaDB operations
│   │   └── agent_service.py       # Multi-agent RAG
│   ├── ui/                         # Presentation layer
│   │   ├── styles.py              # CSS styling
│   │   ├── components.py          # Reusable components
│   │   └── pages.py               # Tab content
│   └── utils/                      # Utility layer
│       └── helpers.py             # Session state
├── app_old.py                      # Backup of monolithic version
└── requirements.txt
```

### Architecture Principles

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Modularity**: Components can be developed, tested, and modified independently
3. **Type Safety**: Uses dataclasses for configuration (e.g., `NotebookConfig`)
4. **Maintainability**: Clear structure makes it easy to locate and modify code
5. **Scalability**: Easy to add new features, models, or documents

## Core Components

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

**New in v2.0**: Edit `src/config/notebooks.py`:

```python
from src.config.notebooks import NotebookConfig

NOTEBOOKS["Notebook Title"] = NotebookConfig(
    name="Notebook Title",
    gdrive_id="google_drive_file_id",  # For PDF preview (optional)
    local_path="path_to_local_pdf.pdf",  # Required for RAG
    description="Use this tool to search for information about...",  # For agent routing
    category="subject_area"  # For organization
)
```

**Key fields**:
- `name`: Display name of the notebook
- `gdrive_id`: Used for Google Drive PDF preview iframe (can be None)
- `local_path`: Path to local PDF file (required for RAG functionality)
- `description`: Detailed description used by the agent to decide when to use this notebook
- `category`: Category for organization (e.g., "mathematics", "computer_science", "regulations")

### Customizing Application Settings

Edit `src/config/settings.py`:

```python
class Settings:
    # LLM Model Configuration
    GOOGLE_MODEL_NAME = "gemini-2.5-flash"
    OPENAI_MODEL_NAME = "gpt-4o-mini"
    LLM_TEMPERATURE = 0.1

    # Document Processing Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150
    RETRIEVER_K = 4

    # Agent Configuration
    AGENT_MAX_ITERATIONS = 3
    AGENT_VERBOSE = True
```

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

The chat history in Tab 2 is **persistent** and doesn't clear when switching between notebooks in Tab 1. This allows users to have a continuous conversation about multiple notebooks.

## Development Guidelines

### Adding New Features

1. **New LLM Provider**: Extend `LLMService` in `src/services/llm_service.py`
2. **New UI Component**: Add to `UIComponents` in `src/ui/components.py`
3. **New Configuration**: Add to `Settings` in `src/config/settings.py`
4. **New Service**: Create new file in `src/services/` and follow existing patterns

### Code Organization Best Practices

1. **Configuration Layer** (`src/config/`):
   - All constants and settings
   - No business logic or UI code
   - Use dataclasses for type safety

2. **Service Layer** (`src/services/`):
   - Business logic only
   - No direct UI interactions (use Streamlit caching, not display functions)
   - Return data or objects, let UI layer handle display

3. **UI Layer** (`src/ui/`):
   - Presentation logic only
   - Call service layer for data
   - Reusable components in `components.py`
   - Page-specific logic in `pages.py`

4. **Main Entry Point** (`app.py`):
   - Keep minimal (orchestration only)
   - Just configure and render pages
   - No business logic

### Testing Strategy

The modular architecture makes testing easier:

- **Unit tests**: Test individual services independently
- **Integration tests**: Test service interactions
- **UI tests**: Test component rendering (can mock services)

### Migration from v1.0

The old monolithic `app.py` (393 lines) has been refactored into:
- `app.py`: 50 lines (entry point)
- `src/config/`: 100 lines (configuration)
- `src/services/`: 300 lines (business logic)
- `src/ui/`: 200 lines (presentation)
- `src/utils/`: 50 lines (utilities)

**Total**: ~700 lines (well-organized and modular vs. 393 lines monolithic)

The old version is backed up as `app_old.py` for reference.
