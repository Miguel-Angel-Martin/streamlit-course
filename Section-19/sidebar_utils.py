# sidebar_utils.py
import streamlit as st
import subprocess


def get_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        st.error(f"Error al listar los modelos: {e}")
        return []

    models = []
    lines = output.splitlines()
    for line in lines[1:]:
        line = line.strip()
        if line:
            models.append(line.split()[0])
    return models

def sidebar(clean_callback, current_page="main", uploaded_file:str=""):
    models = get_models()
    with st.sidebar: 
        st.title("Ollama chats")
        st.button("New chat", icon=":material/add_box:", on_click=clean_callback, use_container_width=True)
        selected_model = st.selectbox("Select model", models, key="selected_model", on_change=clean_callback)
        st.header("📋 Información")
        if current_page == "main":
            st.write("**Modelo:** " + selected_model)
        elif current_page == "files":
            st.write("**Modelo:** " + selected_model)
            if uploaded_file:
                st.write("**Archivo actual:** " + uploaded_file.name)
                st.write("**Tipos soportados:** xlsx, csv, txt")
            else:
                st.write("**Estado:** Sin archivo cargado")
                st.write("**Tipos soportados:** xlsx, csv, txt")
    return selected_model