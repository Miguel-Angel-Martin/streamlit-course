import streamlit as st
import pyshorteners as pysh
import pyperclip
def shortener():
    st.subheader("Shortener")
    shortener = pysh.Shortener()

    # Inicializar el estado si no existe
    if "url_to_shorten" not in st.session_state:
        st.session_state["url_to_shorten"] = ""
    if "shortened_url" not in st.session_state:
        st.session_state["shortened_url"] = ""

    # Función para limpiar
    def clean():
        st.session_state["url_to_shorten"] = ""
        st.session_state["shortened_url"] = ""

    with st.container(border=True):
        c1, c2, c3 = st.columns([7, 1, 1], vertical_alignment="bottom")
        with c1:
            url = st.text_input(
                "", 
                placeholder="URL here: https://www.google.com", 
                key="url_to_shorten", 
                autocomplete="off"
            )
        with c2:
            cancel = st.button("Cancel", icon=":material/cancel:", on_click=clean)
        with c3:
            submit = st.button("Short", type="primary")


    if submit and url:
        try:
            shortened = shortener.tinyurl.short(url)
            st.session_state["shortened_url"] = shortened
        except Exception as e:
            st.error(f"Error al acortar la URL: {e}")

    # Mostrar resultado si existe
    if st.session_state["shortened_url"]:
        st.success(f"URL acortada: {st.session_state['shortened_url']}")
        st.button("Copiar al portapapeles", on_click=lambda: pyperclip.copy(st.session_state["shortened_url"]))
