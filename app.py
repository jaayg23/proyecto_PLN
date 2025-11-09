import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

# --- Configuración de la Página ---
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        font-weight: 500;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 8px;
    }

    /* Chat container */
    .stChatMessage {
        padding: 1rem;
        border-radius: 8px;
    }

    /* Selectbox */
    .stSelectbox {
        margin-bottom: 1rem;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">AI Study Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Intelligent companion for studying technical documents with advanced RAG technology</p>', unsafe_allow_html=True)

# --- Configuración de API Keys ---
# Carga las claves desde los secretos de Streamlit (archivo .streamlit/secrets.toml)
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("No se encontró GOOGLE_API_KEY en los secretos. El modelo de Google y los embeddings no funcionarán.")

try:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("No se encontró OPENAI_API_KEY en los secretos. El modelo de OpenAI no funcionará.")

# --- Base de Datos de Cuadernos ---
# IMPORTANTE:
# Debes tener estos archivos PDF en la misma carpeta que tu 'app.py'
# o actualizar la ruta en 'local_path' a donde sea que estén.

CUADERNOS = {
    "Apuntes de Análisis Real": {
        "gdrive_id": "1_hMB2nws4_meusxc077FlbQjwlMhqcKS",
        "local_path": "Analisis_Real.pdf"
    },
    "Lógica Computacional": {
        "gdrive_id": "1tNRQNf6WE6zc2bAO08SSTxlWQaH2s8s3",
        "local_path": "Lógica_Computacional.pdf"
    },
    "Disposiciones Generales (Ejemplo)": {
        "gdrive_id": None, # Este no tiene visor de GDrive
        "local_path": "2._Libro_1___Disposiciones_Generales.pdf"
    }
}

# --- Definición de Pestañas ---
st.markdown("---")
tab1, tab2 = st.tabs(["Document Viewer", "AI Chat Assistant"])
# --- Funciones Cacheadas de LangChain ---

@st.cache_resource(show_spinner="Loading LLM model...")
def load_llm(name):
    """Carga el modelo LLM especificado."""
    try:
        if name == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                st.error("No se puede cargar el modelo de OpenAI. Falta OPENAI_API_KEY.")
                return None
            return ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
        else:
            if not os.getenv("GOOGLE_API_KEY"):
                st.error("No se puede cargar el modelo de Google. Falta GOOGLE_API_KEY.")
                return None
            return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    except Exception as e:
        st.error(f"Error al cargar el modelo {name}: {e}")
        return None

@st.cache_resource(show_spinner="Loading embeddings model...")
def load_embeddings():
    """Carga el modelo de embeddings de Google."""
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("No se puede cargar el modelo de embeddings. Falta GOOGLE_API_KEY.")
        return None
    try:
        return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    except Exception as e:
        st.error(f"Error al cargar embeddings: {e}")
        return None

@st.cache_data(show_spinner="Loading and processing PDF...")
def load_and_split_pdf(file_path):
    """Carga un PDF y lo divide en chunks."""
    try:
        loader = PyPDFLoader(file_path=file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        split_docs = text_splitter.split_documents(docs)
        return split_docs
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo PDF en la ruta: {file_path}")
        return None
    except Exception as e:
        st.error(f"Error al cargar el PDF: {e}")
        return None

@st.cache_resource(show_spinner="Creating vector database...")
def create_chroma_db(_file_path):
    """Crea la base de datos Chroma a partir de los documentos spliteados."""
    # 1. Cargar embeddings
    embeddings = load_embeddings()
    if embeddings is None:
        return None

    # 2. Cargar y splitear docs
    split_docs = load_and_split_pdf(_file_path)
    if split_docs is None:
        return None

    # 3. Crear ChromaDB
    # Usamos un nombre de colección único basado en el nombre del archivo
    collection_name = f"doc_{os.path.basename(_file_path).replace('.', '_')}"

    try:
        # Chroma.from_documents se encarga de generar los embeddings y guardarlos
        chroma_db = Chroma.from_documents(
            split_docs,
            embeddings,
            collection_name=collection_name
        )
        return chroma_db
    except Exception as e:
        st.error(f"Error al crear ChromaDB: {e}")
        return None

@st.cache_resource(show_spinner="Loading RAG chain...")
def get_rag_chain(_llm, _chroma_db):
    """Crea la cadena de RetrievalQA (RAG)."""
    if _llm is None or _chroma_db is None:
        return None

    try:
        # Crear el retriever desde la base de datos
        # Corregido: search_kwargs (en lugar de search_kwaargs) y {"k": 4} (dict)
        retriever = _chroma_db.as_retriever(search_kwargs={"k": 4})

        rag_chain = RetrievalQA.from_chain_type(
            llm=_llm,
            chain_type="stuff",
            retriever=retriever
        )
        return rag_chain
    except Exception as e:
        st.error(f"Error al crear la cadena RAG: {e}")
        return None

# --- Funciones para Multi-Agent RAG ---

@st.cache_resource(show_spinner="Creating retrievers for all documents...")
def create_all_retrievers():
    """Crea retrievers para todos los cuadernos configurados."""
    embeddings = load_embeddings()
    if embeddings is None:
        return None

    retrievers = {}
    for notebook_name, notebook_info in CUADERNOS.items():
        local_path = notebook_info.get("local_path")
        if local_path and os.path.exists(local_path):
            try:
                chroma_db = create_chroma_db(local_path)
                if chroma_db:
                    retriever = chroma_db.as_retriever(search_kwargs={"k": 4})
                    retrievers[notebook_name] = retriever
            except Exception as e:
                st.warning(f"No se pudo crear retriever para '{notebook_name}': {e}")

    return retrievers

def create_retriever_tool(notebook_name, retriever):
    """Crea una herramienta (Tool) para un cuaderno específico."""

    def search_notebook(query: str) -> str:
        """Busca información en el cuaderno y retorna contexto relevante."""
        try:
            docs = retriever.get_relevant_documents(query)
            if not docs:
                return f"No se encontró información relevante en '{notebook_name}'."

            results = []
            for doc in docs:
                page = doc.metadata.get("page", "desconocida")
                content = doc.page_content.strip()
                results.append(f"[Página {page}] {content}")

            return "\n\n".join(results)
        except Exception as e:
            return f"Error al buscar en '{notebook_name}': {str(e)}"

    # Descripción del cuaderno para ayudar al agente a decidir
    descriptions = {
        "Apuntes de Análisis Real": "Usa esta herramienta para buscar información sobre Análisis Real, matemáticas, límites, continuidad, derivadas, integrales y teoremas matemáticos.",
        "Lógica Computacional": "Usa esta herramienta para buscar información sobre Lógica Computacional, lógica proposicional, lógica de predicados, cálculo lógico, teoremas de computación.",
        "Disposiciones Generales (Ejemplo)": "Usa esta herramienta para buscar información sobre disposiciones generales, definiciones y explicaciones del RETIE (Reglamento Técnico de Instalaciones Eléctricas)."
    }

    description = descriptions.get(notebook_name, f"Busca información en el cuaderno '{notebook_name}'.")

    return Tool(
        name=f"Buscador_{notebook_name.replace(' ', '_')}",
        func=search_notebook,
        description=description
    )

@st.cache_resource(show_spinner="Initializing multi-RAG agent...")
def create_multi_rag_agent(_llm, _retrievers):
    """Crea un agente que puede elegir entre múltiples cuadernos."""
    if _llm is None or not _retrievers:
        return None

    try:
        # Crear herramientas para cada retriever
        tools = []
        for notebook_name, retriever in _retrievers.items():
            tool = create_retriever_tool(notebook_name, retriever)
            tools.append(tool)

        # Inicializar el agente con las herramientas
        agent = initialize_agent(
            tools=tools,
            llm=_llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True
        )

        return agent
    except Exception as e:
        st.error(f"Error al crear el agente multi-RAG: {e}")
        return None

# --- Inicialización del Estado de Sesión ---
if "selected_notebook" not in st.session_state:
    st.session_state.selected_notebook = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "llm_model_name" not in st.session_state:
    st.session_state.llm_model_name = "google"

# --- Pestaña 1: Visor de Cuadernos ---
with tab1:
    st.header("Document Viewer")
    st.markdown("Select and view your PDF documents.")

    cuaderno_seleccionado = st.selectbox(
        "Select a document to view:",
        list(CUADERNOS.keys()),
        index=None,
        placeholder="Choose from available documents..."
    )

    if cuaderno_seleccionado:
        st.session_state.selected_notebook = cuaderno_seleccionado
        notebook_info = CUADERNOS[cuaderno_seleccionado]
        file_id = notebook_info.get("gdrive_id")

        st.subheader(f"{cuaderno_seleccionado}")

        if file_id:
            embed_url = f"https://drive.google.com/file/d/{file_id}/preview"
            st.components.v1.iframe(embed_url, height=800, scrolling=True)
        else:
            st.info(f"This document does not have a Google Drive ID configured for preview.")
            st.markdown("**Note:** You can still query this document in the AI Chat Assistant.")
    else:
        st.info("Select a document from the dropdown menu to view it.")

# --- Pestaña 2: Chat Multi-RAG ---
with tab2:
    st.header("AI Chat Assistant")
    st.markdown("Ask questions about **any document**. The assistant will automatically choose the most relevant document to answer from.")

    # Selector de modelo LLM
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("The agent can search across multiple documents and select the most relevant one.")
    with col2:
        model_name = st.selectbox(
            "Model:",
            ("google", "openai"),
            key="llm_model_name"
        )

    # --- Cargar componentes del Multi-Agent RAG ---
    llm = load_llm(st.session_state.llm_model_name)
    retrievers = create_all_retrievers()
    agent = create_multi_rag_agent(llm, retrievers)
    # --- Fin de la carga de componentes ---

    # Mostrar cuadernos disponibles
    with st.expander("Available documents for querying"):
        if retrievers:
            for notebook_name in retrievers.keys():
                st.markdown(f"• **{notebook_name}**")
        else:
            st.warning("Could not load documents.")

    # Contenedor para el historial del chat
    chat_container = st.container(height=600, border=True)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Manejar nueva entrada del usuario
    if prompt := st.chat_input("Ask about any topic from your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Generar respuesta usando el agente multi-RAG
        with chat_container:
            with st.chat_message("assistant"):
                response = ""
                if agent is not None:
                    with st.spinner("Analyzing your documents..."):
                        try:
                            # El agente decide qué herramienta (cuaderno) usar
                            result = agent.run(prompt)
                            response = result
                        except Exception as e:
                            response = f"Error generating response: {e}"
                            st.error(response)
                else:
                    response = "Error: The agent could not be initialized. Please check API keys and PDF availability."

                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})