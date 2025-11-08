import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma

# --- Configuración de la Página ---
st.set_page_config(layout="wide")
st.title("Visor de Cuadernos con Chat RAG 🚀")

# --- Configuración de API Keys ---
# Carga las claves desde los secretos de Streamlit (archivo .streamlit/secrets.toml)
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("⚠️ No se encontró GOOGLE_API_KEY en los secretos. El modelo de Google y los embeddings no funcionarán.")

try:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ No se encontró OPENAI_API_KEY en los secretos. El modelo de OpenAI no funcionará.")

# --- Base de Datos de Cuadernos ---
# IMPORTANTE:
# Debes tener estos archivos PDF en la misma carpeta que tu 'app.py'
# o actualizar la ruta en 'local_path' a donde sea que estén.

CUADERNOS = {
    "Apuntes de Análisis Real": {
        "gdrive_id": "1_hMB2nws4_meusxc077FlbQjwlMhqcKS",
        "local_path": "Apuntes_de_Análisis_Real.pdf"
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
tab1, tab2 = st.tabs(["1. Selección de Cuaderno", "2. Ver Apuntes y Chatear"])
# --- Funciones Cacheadas de LangChain ---

@st.cache_resource(show_spinner="Cargando modelo LLM... 🤖")
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

@st.cache_resource(show_spinner="Cargando modelo de embeddings... 🧬")
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

@st.cache_data(show_spinner="Cargando y dividiendo PDF... 🧠")
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

@st.cache_resource(show_spinner="Creando base de datos vectorial (ChromaDB)... 🗄️")
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

@st.cache_resource(show_spinner="Cargando cadena RAG... 🔗")
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

# --- Inicialización del Estado de Sesión ---
if "selected_notebook" not in st.session_state:
    st.session_state.selected_notebook = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "llm_model_name" not in st.session_state:
    st.session_state.llm_model_name = "google"

# --- Pestaña 1: Selección ---
with tab1:
    st.header("Elige tus apuntes")
    st.markdown("Selecciona el cuaderno que te gustaría estudiar hoy.")

    cuaderno_seleccionado = st.selectbox(
        "Selecciona un cuaderno:",
        list(CUADERNOS.keys()),
        index=None,
        placeholder="Haz clic para ver las opciones..."
    )

    if st.button("Cargar Cuaderno", use_container_width=True, type="primary"):
        if cuaderno_seleccionado:
            st.session_state.selected_notebook = cuaderno_seleccionado
            st.session_state.messages = [] # Limpiar chat anterior
            st.success(f"¡{cuaderno_seleccionado} cargado! 🎉")
            st.info("Haz clic en la pestaña '2. Ver Apuntes y Chatear' para comenzar.")
        else:
            st.error("¡Debes seleccionar un cuaderno primero!")

# --- Pestaña 2: Visor y Chat ---
with tab2:
    if not st.session_state.selected_notebook:
        st.warning("⬅️ Por favor, selecciona un cuaderno en la pestaña '1. Selección de Cuaderno' primero.")
    else:
        # Recuperamos la información del cuaderno
        notebook_name = st.session_state.selected_notebook
        notebook_info = CUADERNOS[notebook_name]
        file_id = notebook_info.get("gdrive_id")
        local_path = notebook_info.get("local_path")

        st.header(f"Estudiando: {notebook_name}")

        col1, col2 = st.columns([3, 2])

        # Columna 1: Visor de Apuntes
        with col1:
            st.subheader("Apuntes 📝")
            if file_id:
                embed_url = f"https://drive.google.com/file/d/{file_id}/preview"
                st.components.v1.iframe(embed_url, height=700, scrolling=True)
            else:
                st.info(f"Este cuaderno ('{notebook_name}') no tiene un ID de Google Drive para visualización.")

        # Columna 2: Chat
        with col2:
            st.subheader("Chat de Estudio (con RAG) 🤖")

            # Selector de modelo LLM
            model_name = st.selectbox(
                "Elige el modelo de IA:",
                ("google", "openai"),
                key="llm_model_name"
            )

            # --- Cargar todos los componentes del RAG ---
            llm = load_llm(st.session_state.llm_model_name)
            
            chroma_db = None
            if local_path:
                chroma_db = create_chroma_db(local_path)
            else:
                st.error(f"No hay 'local_path' configurado para '{notebook_name}'. El chat RAG no puede funcionar.")
            
            rag_chain = get_rag_chain(llm, chroma_db)
            # --- Fin de la carga de componentes ---

            # Contenedor para el historial del chat
            chat_container = st.container(height=550, border=True)

            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Manejar nueva entrada del usuario
            if prompt := st.chat_input(f"Pregunta sobre {notebook_name}..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                # Generar respuesta del RAG
                with chat_container:
                    with st.chat_message("assistant"):
                        response = ""
                        if rag_chain is not None:
                            with st.spinner("Buscando en los apuntes y pensando..."):
                                try:
                                    # Invocamos la cadena RAG con la 'query'
                                    result = rag_chain.invoke({"query": prompt})
                                    # La respuesta está en la clave 'result'
                                    response = result["result"]
                                except Exception as e:
                                    response = f"Error al generar la respuesta RAG: {e}"
                        else:
                            response = "Error: La cadena RAG no pudo ser inicializada. Revisa las API keys o la ruta del archivo PDF."
                        
                        st.markdown(response)

                st.session_state.messages.append({"role": "assistant", "content": response})