import streamlit as st

st.set_page_config("Trasnsaltions")

pages = {
    "Translations": [
        st.Page("translator.py", title="Translator", icon=":material/translate:"),
        st.Page("translator_files.py", title="File translator", icon=":material/translate:")
    ]
}

pg = st.navigation(pages=pages, position="sidebar", expanded=True)
pg.run()



