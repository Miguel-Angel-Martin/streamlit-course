import streamlit as st
from deep_translator import GoogleTranslator  # 5000 characteres max as each time.
import pyperclip
from functools import partial

st.title("Translator")


def copy_text(text):
    pyperclip.copy(text)
    st.toast("Text copy to clipboard ✅")


text_to_translate = st.text_area("Text to translate")
languages = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Alemán": "de",
    "Italiano": "it",
}
selected_language = st.selectbox("Select language", options=list(languages.keys()))

if st.button("Translate"):
    if not text_to_translate:
        st.warning("Please enter text to translate.")
    else:
        try:
            translator = GoogleTranslator(
                source="auto", target=languages[selected_language]
            )
            translated_text = translator.translate(text_to_translate)
            st.success(translated_text)
            copy_callback = partial(copy_text, translated_text)
            st.button("Copiar al portapapeles", on_click=copy_callback, icon=":material/file_copy:", type="primary")
        except Exception as e:
            st.error(f"An error occurred: {e}")
