# Visor de Cuadernos con Chat RAG

A Streamlit-based application that combines PDF viewing capabilities with an intelligent chat interface powered by Retrieval-Augmented Generation (RAG). This app allows you to study PDF notebooks while interacting with an AI assistant that can answer questions based on the document content.

## Features

- **PDF Viewing**: View PDF documents directly in the browser using Google Drive integration
- **RAG-Powered Chat**: Ask questions about your notebooks and get answers based on the actual content
- **Multiple LLM Support**: Choose between Google's Gemini and OpenAI's GPT models
- **Smart Document Processing**: Automatic chunking and vectorization of PDF content
- **Session Management**: Maintains separate chat histories for different notebooks
- **Cached Resources**: Efficient caching strategy for fast loading and reduced API calls

## Architecture

### Core Components

1. **Document Processing Pipeline**
   - PDF loading via `PyPDFLoader`
   - Document chunking using `RecursiveCharacterTextSplitter` (chunk_size=1000, chunk_overlap=150)
   - Vector embeddings via Google's `text-embedding-004` model
   - Vector storage in ChromaDB (in-memory)

2. **RAG Chain**
   - Retrieval using Chroma's retriever (k=4 documents)
   - Response generation via `RetrievalQA` chain with "stuff" chain type
   - Support for multiple LLM backends

3. **Caching Strategy**
   - `@st.cache_resource`: LLM models, embeddings, ChromaDB instances, and RAG chains
   - `@st.cache_data`: PDF loading and splitting operations
   - Unique ChromaDB collections per PDF to avoid conflicts

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

1. **Select a Notebook** (Tab 1):
   - Choose a notebook from the dropdown menu
   - Click "Cargar Cuaderno" to load it

2. **View and Chat** (Tab 2):
   - Left panel: View the PDF notebook
   - Right panel: Chat interface
   - Select your preferred LLM model (Google or OpenAI)
   - Ask questions about the notebook content

## Configuration

### Adding New Notebooks

Edit the `CUADERNOS` dictionary in [app.py](app.py):

```python
CUADERNOS = {
    "Your Notebook Title": {
        "gdrive_id": "google_drive_file_id",  # For PDF preview (optional)
        "local_path": "path/to/your/notebook.pdf"  # Required for RAG
    }
}
```

- `gdrive_id`: Google Drive file ID for PDF preview iframe (can be `None`)
- `local_path`: Path to local PDF file (required for RAG functionality)

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

### Chat Reset Behavior

When a new notebook is selected, the chat history (`st.session_state.messages`) is automatically cleared to prevent confusion between different document contexts.

## Project Structure

```
proyecto_PLN/
├── app.py                          # Main application file
├── requirements.txt                # Python dependencies
├── CLAUDE.md                       # Developer instructions for Claude Code
├── README.md                       # This file
├── .streamlit/
│   └── secrets.toml               # API keys (not in version control)
└── [Your PDF files]               # Notebook PDFs
```

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

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]
