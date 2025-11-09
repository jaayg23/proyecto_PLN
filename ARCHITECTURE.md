# Architecture Documentation - AI Study Assistant v2.0

## Overview

This document describes the modular architecture implemented in version 2.0 of the AI Study Assistant application.

## Architecture Comparison

### Before (v1.0) - Monolithic
```
proyecto_PLN/
├── app.py                  # 393 lines - ALL logic in one file
├── requirements.txt
└── PDFs...
```

**Problems**:
- Single responsibility violation
- Difficult to test individual components
- Hard to maintain and extend
- Tight coupling between layers
- Configuration mixed with business logic

### After (v2.0) - Modular
```
proyecto_PLN/
├── app.py                          # 50 lines - Entry point only
├── src/
│   ├── config/                     # Configuration layer
│   │   ├── __init__.py
│   │   ├── settings.py            # Application settings
│   │   └── notebooks.py           # Document database
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── llm_service.py         # LLM management
│   │   ├── document_service.py    # PDF processing
│   │   ├── vector_store.py        # ChromaDB operations
│   │   └── agent_service.py       # Multi-agent RAG
│   ├── ui/                         # Presentation layer
│   │   ├── __init__.py
│   │   ├── styles.py              # CSS styling
│   │   ├── components.py          # Reusable components
│   │   └── pages.py               # Tab content
│   └── utils/                      # Utility layer
│       ├── __init__.py
│       └── helpers.py             # Session state
├── app_old.py                      # Backup of v1.0
├── requirements.txt
└── README.md
```

**Benefits**:
- Clear separation of concerns
- Easy to test and maintain
- Scalable and extensible
- Type-safe configuration
- Reusable components

## Layer Descriptions

### 1. Configuration Layer (`src/config/`)

**Purpose**: Centralized configuration and constants

#### `settings.py`
- Application-wide settings
- API key management
- Model configurations
- Document processing parameters
- Agent settings

**Key Classes**:
```python
class Settings:
    GOOGLE_MODEL_NAME = "gemini-2.5-flash"
    OPENAI_MODEL_NAME = "gpt-4o-mini"
    CHUNK_SIZE = 1000
    RETRIEVER_K = 4
    # ... etc
```

#### `notebooks.py`
- Document database with metadata
- Type-safe `NotebookConfig` dataclass
- Helper functions for querying notebooks

**Key Classes**:
```python
@dataclass
class NotebookConfig:
    name: str
    gdrive_id: Optional[str]
    local_path: str
    description: str
    category: str
```

### 2. Service Layer (`src/services/`)

**Purpose**: Business logic and external service integration

#### `llm_service.py` - LLM Management
- Load and cache LLM models (Google, OpenAI)
- Load and cache embedding models
- Model availability validation
- Streamlit caching integration

**Key Methods**:
- `load_llm(model_name)`: Load specific LLM
- `load_embeddings()`: Load embedding model
- `get_available_models()`: List available models
- `validate_model_availability(model_name)`: Check model availability

#### `document_service.py` - PDF Processing
- Load PDFs using PyPDFLoader
- Split documents into chunks
- PDF validation and metadata extraction

**Key Methods**:
- `load_and_split_pdf(file_path)`: Load and chunk PDF
- `validate_pdf_exists(file_path)`: Check PDF existence
- `get_pdf_metadata(file_path)`: Extract PDF metadata

#### `vector_store.py` - Vector Database
- Create ChromaDB instances
- Generate retrievers for semantic search
- Manage multiple vector stores

**Key Methods**:
- `create_chroma_db(file_path)`: Create vector DB from PDF
- `create_retriever(chroma_db, k)`: Create retriever
- `create_all_retrievers(notebooks)`: Create retrievers for all docs
- `get_collection_name(file_path)`: Generate collection name

#### `agent_service.py` - Multi-Agent RAG
- Create LangChain Tools from retrievers
- Initialize Zero-Shot ReAct agents
- Tool-based document routing
- Agent execution and error handling

**Key Methods**:
- `create_retriever_tool(notebook_name, retriever, config)`: Create tool
- `create_multi_rag_agent(llm, retrievers, notebooks)`: Create agent
- `run_agent(agent, query)`: Execute agent query

### 3. UI Layer (`src/ui/`)

**Purpose**: User interface and presentation logic

#### `styles.py` - Styling
- Custom CSS for the application
- Gradient title styling
- Professional color scheme
- `apply_custom_styles()`: Apply CSS
- `render_header()`: Render app header

#### `components.py` - Reusable Components
- UI components library
- Model selector
- Document selector
- PDF viewer
- Chat message renderer
- Alert/notification helpers

**Key Methods**:
- `render_model_selector(available_models, default)`: Model dropdown
- `render_notebook_selector(notebooks, default_index)`: Document dropdown
- `render_pdf_viewer(notebook_name, gdrive_id)`: PDF iframe
- `render_available_documents(retrievers)`: Document list
- `render_chat_message(role, content)`: Single message
- `render_chat_history(messages)`: Full chat history

#### `pages.py` - Page Content
- Tab content and page logic
- Integration with service layer

**Key Classes**:
- `DocumentViewerPage`: PDF viewing tab
- `ChatAssistantPage`: Multi-agent chat tab

### 4. Utility Layer (`src/utils/`)

**Purpose**: Cross-cutting concerns and helpers

#### `helpers.py` - Session State Management
- Streamlit session state management
- Getters and setters for state variables
- Message history management

**Key Methods**:
- `initialize()`: Initialize session state
- `get_selected_notebook()`: Get current notebook
- `set_selected_notebook(name)`: Set current notebook
- `get_messages()`: Get chat messages
- `add_message(role, content)`: Add chat message
- `clear_messages()`: Clear chat history

## Data Flow

### Document Loading Flow
```
User selects document
    ↓
UI Layer (pages.py)
    ↓
Configuration (notebooks.py) → Get NotebookConfig
    ↓
Service Layer (document_service.py) → Load PDF
    ↓
Service Layer (vector_store.py) → Create ChromaDB
    ↓
UI Layer (components.py) → Display PDF
```

### Chat Query Flow
```
User enters query
    ↓
UI Layer (pages.py)
    ↓
Service Layer (llm_service.py) → Get LLM model
    ↓
Service Layer (vector_store.py) → Get retrievers
    ↓
Service Layer (agent_service.py) → Create agent
    ↓
Agent selects relevant tool(s)
    ↓
Retriever gets relevant documents
    ↓
LLM generates response
    ↓
UI Layer (components.py) → Display response
```

## Caching Strategy

### Resource Caching (`@st.cache_resource`)
Used for stateful objects that should persist across sessions:
- LLM models
- Embedding models
- ChromaDB instances
- Retrievers
- Agents

### Data Caching (`@st.cache_data`)
Used for data transformations:
- PDF loading and splitting
- Document processing

## Type Safety

The architecture uses Python type hints throughout:

```python
def load_llm(model_name: str) -> Optional[ChatOpenAI | ChatGoogleGenerativeAI]
def create_retriever(chroma_db, k: Optional[int] = None) -> Optional[VectorStoreRetriever]
def render_chat_message(role: str, content: str) -> None
```

Dataclasses provide type-safe configuration:
```python
@dataclass
class NotebookConfig:
    name: str
    gdrive_id: Optional[str]
    local_path: str
    description: str
    category: str = "general"
```

## Extension Points

### Adding a New LLM Provider

1. Edit `src/services/llm_service.py`:
```python
def load_llm(model_name: str):
    if model_name == "new_provider":
        return NewProviderChat(...)
```

2. Edit `src/config/settings.py`:
```python
class Settings:
    NEW_PROVIDER_MODEL_NAME = "model-name"
```

### Adding a New Document

Edit `src/config/notebooks.py`:
```python
NOTEBOOKS["New Document"] = NotebookConfig(
    name="New Document",
    gdrive_id="...",
    local_path="path/to/doc.pdf",
    description="Use this tool when...",
    category="category_name"
)
```

### Adding a New UI Component

Edit `src/ui/components.py`:
```python
class UIComponents:
    @staticmethod
    def render_new_component(param: str) -> None:
        # Component logic
        pass
```

### Adding Custom Settings

Edit `src/config/settings.py`:
```python
class Settings:
    NEW_FEATURE_ENABLED = True
    NEW_FEATURE_PARAM = 42
```

## Testing Strategy

The modular architecture enables comprehensive testing:

### Unit Tests
```python
# Test individual services
def test_load_llm():
    llm = LLMService.load_llm("google")
    assert llm is not None

def test_notebook_config():
    config = NotebookConfig(
        name="Test",
        gdrive_id=None,
        local_path="test.pdf",
        description="Test notebook",
        category="test"
    )
    assert config.name == "Test"
```

### Integration Tests
```python
# Test service interactions
def test_create_rag_chain():
    llm = LLMService.load_llm("google")
    embeddings = LLMService.load_embeddings()
    chroma_db = VectorStoreService.create_chroma_db("test.pdf")
    assert chroma_db is not None
```

### UI Tests
```python
# Test component rendering (can mock services)
def test_render_model_selector():
    available = ["google", "openai"]
    # Mock Streamlit and test rendering
    pass
```

## Performance Considerations

1. **Caching**: Aggressive use of Streamlit caching reduces API calls and loading time
2. **Lazy Loading**: Components only load when needed
3. **Efficient Retrievers**: ChromaDB with optimized k value (4 documents)
4. **Streaming**: Can be added to LLM responses for better UX

## Security Considerations

1. **API Keys**: Stored in `.streamlit/secrets.toml` (gitignored)
2. **Input Validation**: PDF paths validated before loading
3. **Error Handling**: Comprehensive error handling prevents crashes
4. **Type Safety**: Dataclasses prevent invalid configurations

## Migration Guide

### From v1.0 to v2.0

1. **Backup**: Old `app.py` saved as `app_old.py`
2. **Configuration**: Move notebook definitions to `src/config/notebooks.py`
3. **Custom Settings**: Move to `src/config/settings.py`
4. **Run**: No changes to user-facing functionality

### Code Mapping

| v1.0 Location | v2.0 Location |
|---------------|---------------|
| `app.py` lines 112-128 (load_llm) | `src/services/llm_service.py` |
| `app.py` lines 130-140 (load_embeddings) | `src/services/llm_service.py` |
| `app.py` lines 142-156 (load_and_split_pdf) | `src/services/document_service.py` |
| `app.py` lines 158-185 (create_chroma_db) | `src/services/vector_store.py` |
| `app.py` lines 208-292 (agent functions) | `src/services/agent_service.py` |
| `app.py` lines 21-70 (CSS) | `src/ui/styles.py` |
| `app.py` lines 302-393 (UI) | `src/ui/pages.py` |
| `app.py` lines 92-105 (CUADERNOS) | `src/config/notebooks.py` |

## Conclusion

The v2.0 architecture provides:
- ✅ Clear separation of concerns
- ✅ Improved maintainability
- ✅ Better testability
- ✅ Type safety
- ✅ Scalability
- ✅ Reusable components
- ✅ Professional code organization

This makes the codebase production-ready and easy to extend with new features.
