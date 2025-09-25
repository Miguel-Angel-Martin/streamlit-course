import streamlit as st
from ollama import Client
import pandas as pd
from sidebar_utils import sidebar
import io



def clean():
    st.session_state.message = []

# Selecciona el tipo de archivo que se permitirá cargar
allowed_files = {'xlsx', 'txt', 'csv'}
selected_model = sidebar(clean_callback=clean, current_page="main", uploaded_file="")
st.title(f"File Analisis: {selected_model}")
st.markdown("<hr>", unsafe_allow_html=True)
# Crea un uploader para seleccionar archivos
uploaded_file = st.file_uploader("Carga tus archivos para análisis", type=allowed_files)

# Variable para almacenar el contenido del archivo
file_content = ""
file_info = ""


if uploaded_file is not None:
    size_mb = uploaded_file.size / (1024 * 1024)
    file_info = f"📄 File uploaded: {uploaded_file.name} ({size_mb:.2f} MB)"
    st.info(file_info)
    
    try:
        if uploaded_file.name.endswith('.xlsx'):
            # Leer archivo Excel
            df = pd.read_excel(uploaded_file)
            st.write("Vista previa del archivo:")
            st.dataframe(df.head(10))  # Muestra primeras 10 filas
            
            # Convertir a texto para enviar a Ollama
            file_content = f"""
                ARCHIVO EXCEL: {uploaded_file.name}
                Dimensiones: {df.shape[0]} filas, {df.shape[1]} columnas
                Columnas: {', '.join(df.columns.tolist())}

                PRIMERAS 10 FILAS:
                {df.head(10).to_string()}

                INFORMACIÓN ESTADÍSTICA:
                {df.describe().to_string() if len(df.select_dtypes(include=['number']).columns) > 0 else 'No hay columnas numéricas'}
            """
            
        elif uploaded_file.name.endswith('.csv'):
            # Leer archivo CSV
            df = pd.read_csv(uploaded_file)
            st.write("Vista previa del archivo:")
            st.dataframe(df.head(10))
            
            # Convertir a texto para enviar a Ollama
            file_content = f"""
                ARCHIVO CSV: {uploaded_file.name}
                Dimensiones: {df.shape[0]} filas, {df.shape[1]} columnas
                Columnas: {', '.join(df.columns.tolist())}

                PRIMERAS 10 FILAS:
                {df.head(10).to_string()}

                INFORMACIÓN ESTADÍSTICA:
                {df.describe().to_string() if len(df.select_dtypes(include=['number']).columns) > 0 else 'No hay columnas numéricas'}
                """
            
        elif uploaded_file.name.endswith('.txt'):
            # Leer archivo de texto
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            st.write("Vista previa del archivo:")
            st.text_area("Contenido", content[:1000] + "..." if len(content) > 1000 else content, height=200)
            
            file_content = f"""
                ARCHIVO DE TEXTO: {uploaded_file.name}
                Longitud: {len(content)} caracteres

                CONTENIDO:
                {content}
                """
            
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")

# Inicializar mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Haz una pregunta sobre el archivo cargado o cualquier otra consulta"):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Preparar el prompt para Ollama
    if uploaded_file is not None and file_content:
        # Si hay un archivo cargado, incluir su contenido en el prompt
        full_prompt = f"""
Tienes acceso a un archivo que el usuario ha cargado. Aquí está la información del archivo:

{file_content}

PREGUNTA DEL USUARIO: {prompt}

Por favor, analiza el archivo y responde a la pregunta del usuario basándote en el contenido del archivo cuando sea relevante.
"""
    else:
        # Si no hay archivo, usar solo el prompt del usuario
        full_prompt = prompt
    
    # Generar respuesta con Ollama
    with st.spinner("Analizando y generando respuesta..."):
        try:
            client = Client()
            response = client.chat(
                model=selected_model, 
                messages=[{"role": "user", "content": full_prompt}]
            )
            response_txt = response["message"]["content"]
        except Exception as e:
            response_txt = f"Error al conectar con Ollama: {str(e)}"
    
    # Agregar respuesta del asistente
    st.session_state.messages.append({"role": "assistant", "content": response_txt})
    with st.chat_message("assistant"):
        st.markdown(response_txt)
