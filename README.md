# AI Study Assistant - Multi-Agent RAG System

A modular, production-ready Streamlit application that combines PDF viewing capabilities with an intelligent Multi-Agent RAG (Retrieval-Augmented Generation) chat interface. Ask questions about any document, and the AI agent will automatically select and query the most relevant source.

## Features

- **📖 PDF Document Viewer**: View PDF documents directly in the browser from local files
- **🤖 Multi-Agent RAG Chat**: Intelligent agent that routes queries to the most relevant document(s)
- **🔄 Multiple LLM Support**: Switch between Google Gemini and OpenAI GPT models
- **📊 Smart Document Processing**: Automatic chunking and vectorization of PDF content
- **💾 Efficient Caching**: Resource caching strategy for fast loading and reduced API calls
- **🏗️ Modular Architecture**: Clean separation of concerns for maintainability and scalability

## Architecture

### Overview

The application follows a **layered, modular architecture** with clear separation of concerns:

```
proyecto_PLN/
├── app.py                          # Main entry point (minimal orchestration)
├── src/
│   ├── config/                     # Configuration layer
│   │   ├── settings.py            # App settings and API key management
│   │   └── notebooks.py           # Document definitions and metadata
│   ├── services/                   # Business logic layer
│   │   ├── llm_service.py         # LLM and embeddings management
│   │   ├── document_service.py    # PDF processing pipeline
│   │   ├── vector_store.py        # ChromaDB operations
│   │   └── agent_service.py       # Multi-agent RAG logic
│   ├── ui/                         # Presentation layer
│   │   ├── styles.py              # CSS and styling
│   │   ├── components.py          # Reusable UI components
│   │   └── pages.py               # Tab/page content
│   └── utils/                      # Utility layer
│       └── helpers.py             # Session state management
├── requirements.txt
└── README.md
```

### Architecture Layers

#### 1. Configuration Layer (`src/config/`)
- **settings.py**: Centralized application settings, API keys, model configurations
- **notebooks.py**: Type-safe document database with metadata and descriptions

#### 2. Service Layer (`src/services/`)
- **llm_service.py**: LLM and embeddings loading with caching
- **document_service.py**: PDF processing pipeline
- **vector_store.py**: ChromaDB vector database operations
- **agent_service.py**: Multi-agent RAG orchestration and tool creation

#### 3. UI Layer (`src/ui/`)
- **styles.py**: Custom CSS styling
- **components.py**: Reusable UI components
- **pages.py**: Tab content (Document Viewer, Chat Assistant)

#### 4. Utility Layer (`src/utils/`)
- **helpers.py**: Session state management

### Multi-Agent RAG System

1. **Document Processing**: PDFs → Chunks → Embeddings → ChromaDB
2. **Tool Creation**: Each document becomes a LangChain Tool with descriptive metadata
3. **Agent Routing**: Zero-Shot ReAct agent intelligently selects relevant document(s)
4. **Response Generation**: Context retrieved with page numbers, LLM generates answer

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Steps

1. Clone the repository:
```bash
git clone https://github.com/jaayg23/proyecto_PLN.git
cd proyecto_PLN
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys by creating `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "your_google_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
```

**Note**: The app can function with only one API key, but you'll need the respective key for each LLM you want to use.

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the App

#### Document Viewer Tab

1. Select a document from the dropdown menu
2. View the PDF directly from your local files (embedded in the browser)
3. Selected document is stored in session state

#### AI Chat Assistant Tab

1. Select your preferred LLM model (Google or OpenAI)
2. View available documents in the expander
3. Type your question in the chat input
4. The agent will:
   - Analyze your query
   - Select the most relevant document(s)
   - Retrieve relevant context
   - Generate an answer with page references

**Example queries**:
- "What is a derivative?" → Routes to Math notebook
- "Explain RETIE regulations" → Routes to Regulations notebook
- "What is computational logic?" → Routes to Computer Science notebook

## Configuration

### Adding New Documents

Edit [src/config/notebooks.py](src/config/notebooks.py):

```python
from src.config.notebooks import NotebookConfig, NOTEBOOKS

NOTEBOOKS["Your New Document"] = NotebookConfig(
    name="Your New Document",
    local_path="path/to/your/document.pdf",  # Required - path to local PDF
    description="Use this tool to search for information about...",  # For agent routing
    category="your_category"  # For organization
)
```

### Customizing Settings

Edit [src/config/settings.py](src/config/settings.py):

```python
class Settings:
    # LLM Configuration
    GOOGLE_MODEL_NAME = "gemini-2.5-flash"
    OPENAI_MODEL_NAME = "gpt-4o-mini"
    LLM_TEMPERATURE = 0.1

    # Document Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150
    RETRIEVER_K = 4

    # Agent Configuration
    AGENT_MAX_ITERATIONS = 3
    AGENT_VERBOSE = True
```

### Supported LLM Models

- **Google Gemini**: `gemini-2.5-flash` (default)
- **OpenAI GPT**: `gpt-4o-mini`

Both models use temperature=0.1 for more deterministic responses.

## Dependencies

### Core Libraries
- `streamlit`: Web application framework
- `langchain`: LLM application framework
- `langchain-openai`: OpenAI integration
- `langchain-google-genai`: Google Generative AI integration
- `langchain-community`: Community integrations

### AI/ML Libraries
- `openai`: OpenAI API client
- `google-generativeai`: Google AI API client
- `chromadb`: Vector database

### Document Processing
- `pypdf`: PDF parsing and loading

### Data Handling
- `pandas`: Data manipulation (dependency of other libraries)

## Technical Details

### ChromaDB Collection Naming

Collections are named dynamically using the pattern: `doc_{filename_with_underscores}`. This ensures each PDF gets its own vector store and prevents conflicts when switching between notebooks.

### Error Handling

The application includes comprehensive error handling:
- Graceful handling of missing API keys
- File path validation
- Try-catch blocks around major components (LLM loading, embeddings, ChromaDB creation, RAG chain)
- Informative error messages displayed to users

### Chat Persistence

Chat history in Tab 2 is **persistent** across:
- Document switches in Tab 1
- Model changes
- UI re-renders

This allows continuous multi-document conversations.

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `.streamlit/secrets.toml` exists with valid API keys
   - Check that the keys have proper permissions

2. **PDF Not Found**
   - Verify the `local_path` in the `CUADERNOS` dictionary
   - Ensure PDF files are in the correct location

3. **Embedding Errors**
   - Google API key is required for embeddings (used for all LLM models)
   - Check internet connection for API calls

4. **Slow Initial Load**
   - First-time loading processes the entire PDF and creates embeddings
   - Subsequent loads use cached resources for faster performance

5. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+)

## Development

### Project Benefits

The modular architecture makes it easy to:
- **Add new features**: Extend service classes
- **Change UI**: Modify components and pages
- **Swap dependencies**: Replace LLM or vector store implementations
- **Test components**: Unit test individual modules
- **Scale the application**: Add more documents, models, or features

### Best Practices

1. **Configuration**: Add settings to `Settings` class, not hardcoded
2. **New documents**: Use `NotebookConfig` dataclass for type safety
3. **Services**: Keep business logic in service layer
4. **UI components**: Create reusable components in `components.py`
5. **Caching**: Use appropriate Streamlit cache decorators

## Migration from v1.0

If you're upgrading from the monolithic version:

1. Your old `app.py` is backed up as `app_old.py`
2. Update any custom notebook configurations in `src/config/notebooks.py`
3. Migrate any custom settings to `src/config/settings.py`
4. The API and functionality remain the same

## Contributing

Contributions are welcome! The modular architecture makes it easy to:
- Add new LLM providers
- Implement new vector stores
- Create additional UI components
- Enhance agent capabilities

## License

[Add your license information here]

## Contact

- **Repository**: https://github.com/jaayg23/proyecto_PLN
- **Issues**: https://github.com/jaayg23/proyecto_PLN/issues

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/)
- [LangChain](https://langchain.com/)
- [Google Generative AI](https://ai.google.dev/)
- [OpenAI](https://openai.com/)
- [ChromaDB](https://www.trychroma.com/)
