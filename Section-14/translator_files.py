import streamlit as st
from deep_translator import GoogleTranslator  # 5000 characteres max as each time.
import pyperclip
from docx import Document
from PyPDF2 import PdfReader
import pandas as pd
from functools import partial

st.title("File translator")

def copy_text(text):
    pyperclip.copy(text)
    st.toast("Text copy to clipboard ✅")

languages = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Alemán": "de",
    "Italiano": "it",
}
selected_language = st.selectbox("Select language", options=list(languages.keys()))

file = st.file_uploader("Upload a file (.docx, .pdf, .txt, .csv)", type=["docx", "pdf", "txt", "csv"])

if file is not None:
    text_content =""
    try:
        if file.name.endswith(".txt"):
            text_content = file.read().decode("utf-8")
        elif file.name.endswith(".docx"):
            doc = Document(file)
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
        elif file.name.endswith(".pdf"):
            pdf_reader = PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                text_content += pdf_reader.pages[page_num].extract_text() + "\n"
        elif file.name.endswith(".csv"):
            df = pd.read_csv(file)
            text_content = df.to_string()
        st.text_area("Text to translate", text_content, height=300)
        if st.button("Translate"):
            if not text_content:
                st.warning("Please enter text to translate.")
            else:
                try:
                    translator = GoogleTranslator(
                        source="auto", 
                        target=languages[selected_language]
                    )
                    translated_text = translator.translate(text_content)
                    st.text_area("Translated text", translated_text, height=300)
                    copy_callback = partial(copy_text, translated_text)
                    st.button("Copy to clipboard", on_click=copy_callback, icon=":material/file_copy:", type="primary")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    except Exception as e:
        st.error(f"An error occurred proccessing file: {e}")