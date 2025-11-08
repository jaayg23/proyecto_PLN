import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain

# --- Configuración de la Página ---
# Usamos "wide" para que el cuaderno y el chat tengan más espacio
st.set_page_config(layout="wide")
st.title("Visor de Cuadernos con Chat 🚀")

# --- Configuración de API Keys ---
# Carga las claves desde los secretos de Streamlit (archivo .streamlit/secrets.toml)
# Asegúrate de crear ese archivo con tu GOOGLE_API_KEY y OPENAI_API_KEY
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("⚠️ No se encontró GOOGLE_API_KEY en los secretos. El modelo de Google no funcionará.")

try:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ No se encontró OPENAI_API_KEY en los secretos. El modelo de OpenAI no funcionará.")


# --- Base de Datos de Cuadernos ---
# Modificamos el diccionario para incluir el ID de Google Drive (para el visor)
# y la RUTA LOCAL del archivo PDF (para LangChain).
#
# IMPORTANTE:
# Debes tener estos archivos PDF en la misma carpeta que tu 'app.py'
# o actualizar la ruta en 'local_path' a donde sea que estén.

CUADERNOS = {
    "Apuntes de Análisis Real": {
        "gdrive_id": "1_hMB2nws4_meusxc077FlbQjwlMhqcKS",
        "local_path": "Apuntes_de_Análisis_Real.pdf" # Ejemplo: asume que el PDF está en la misma carpeta
    },
    "Lógica Computacional": {
        "gdrive_id": "1tNRQNf6WE6zc2bAO08SSTxlWQaH2s8s3",
        "local_path": "Lógica_Computacional.pdf" # Ejemplo: asume que el PDF está en la misma carpeta
    },
    "Disposiciones Generales (Ejemplo)": {
        "gdrive_id": None, # Este no tiene visor de GDrive
        "local_path": "2._Libro_1___Disposiciones_Generales.pdf" # El PDF de tu ejemplo
    }
}

# --- Funciones Cacheadas de LangChain ---
# Usamos st.cache_data y st.cache_resource para no recargar
# los documentos y modelos con cada mensaje del chat.

@st.cache_data(show_spinner="Cargando y procesando PDF... 🧠")
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

@st.cache_resource(show_spinner="Cargando modelo LLM... 🤖")
def load_llm(name):
    """Carga el modelo LLM especificado."""
    try:
        if name == "openai":
            # Asegurarse que la API key esté disponible
            if not os.getenv("OPENAI_API_KEY"):
                st.error("No se puede cargar el modelo de OpenAI. Falta OPENAI_API_KEY.")
                return None
            return ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
        else:
            # Asegurarse que la API key esté disponible
            if not os.getenv("GOOGLE_API_KEY"):
                st.error("No se puede cargar el modelo de Google. Falta GOOGLE_API_KEY.")
                return None
            return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    except Exception as e:
        st.error(f"Error al cargar el modelo {name}: {e}")
        return None

@st.cache_resource(show_spinner="Cargando cadena de Q&A... 🔗")
def get_qa_chain(_llm):
    """Carga la cadena de Q&A de LangChain."""
    if _llm is None:
        return None
    return load_qa_chain(_llm, chain_type="stuff")

# --- Inicialización del Estado de Sesión ---
if "selected_notebook" not in st.session_state:
    st.session_state.selected_notebook = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "llm_model_name" not in st.session_state:
    st.session_state.llm_model_name = "google" # Default a Google

# --- Definición de Pestañas ---
tab1, tab2 = st.tabs(["1. Selección de Cuaderno", "2. Ver Apuntes y Chatear"])

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
        # Recuperamos la información del cuaderno desde el estado
        notebook_name = st.session_state.selected_notebook
        notebook_info = CUADERNOS[notebook_name]
        file_id = notebook_info.get("gdrive_id")
        local_path = notebook_info.get("local_path")

        st.header(f"Estudiando: {notebook_name}")

        # --- Definición de las Columnas ---
        col1, col2 = st.columns([3, 2]) # 60% PDF, 40% Chat

        # Columna 1: Visor de Apuntes (Izquierda)
        with col1:
            st.subheader("Apuntes 📝")
            if file_id:
                embed_url = f"https://drive.google.com/file/d/{file_id}/preview"
                st.components.v1.iframe(embed_url, height=700, scrolling=True)
            else:
                st.info(f"Este cuaderno ('{notebook_name}') no tiene un ID de Google Drive configurado para visualización. El chat seguirá funcionando si el archivo local existe.")

        # Columna 2: Chat (Derecha)
        with col2:
            st.subheader("Chat de Estudio 🤖")

            # Selector de modelo LLM
            model_name = st.selectbox(
                "Elige el modelo de IA:",
                ("google", "openai"),
                key="llm_model_name"
            )

            # Cargar el LLM y la cadena de Q&A
            llm = load_llm(st.session_state.llm_model_name)
            chain = get_qa_chain(llm)

            # Cargar y procesar el PDF
            split_docs = None
            if local_path:
                split_docs = load_and_split_pdf(local_path)
            else:
                st.error(f"No hay 'local_path' configurado para '{notebook_name}'. El chat no puede funcionar.")

            # Contenedor para el historial del chat
            chat_container = st.container(height=550, border=True)

            # 1. Mostrar historial de mensajes
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # 2. Manejar nueva entrada del usuario
            if prompt := st.chat_input(f"¿Dudas sobre {notebook_name}?"):
                # Añadir mensaje del usuario al historial y mostrarlo
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                # 3. Generar respuesta del LLM
                with chat_container:
                    with st.chat_message("assistant"):
                        response = ""
                        # Solo proceder si todo está cargado correctamente
                        if split_docs is not None and chain is not None:
                            with st.spinner("Pensando..."):
                                try:
                                    # Usamos .invoke en lugar de .run (moderno en LangChain)
                                    result = chain.invoke({"input_documents": split_docs, "question": prompt})
                                    response = result["output_text"]
                                except Exception as e:
                                    response = f"Error al generar la respuesta: {e}"
                        elif split_docs is None:
                            response = "Error: El documento PDF no pudo ser cargado. Revisa el 'local_path'."
                        else:
                            response = "Error: El modelo LLM o la cadena de Q&A no pudieron ser cargados. Revisa las API Keys en los secretos."

                        st.markdown(response)

                # Añadir respuesta del bot al historial
                st.session_state.messages.append({"role": "assistant", "content": response})