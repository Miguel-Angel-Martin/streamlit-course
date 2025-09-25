import os
from huggingface_hub import InferenceClient
import streamlit as st

client = InferenceClient(
    provider="hf-inference",
    api_key=st.secrets["HF_TOKEN"],
)
st.title("Translator generation")


languages = {
    "Español": "es_XX",
    "Inglés": "en_XX",
    "Francés": "fr_XX",
    "Alemán": "de_XX",
    "Italiano": "it_IT",
}
main_container = st.container(
    border=True,
    horizontal=True,
    gap="medium",
    vertical_alignment="bottom",
    horizontal_alignment="center",
)
with main_container:
    

    source_language = st.selectbox("Select source language", options=list(languages.keys()), index=0, width=200)
    target_language = st.selectbox("Select target language", options=list(languages.keys()), index=1)

usr_prompt = st.text_area("Write your text")

with st.container(horizontal=True, border=True, vertical_alignment="bottom", gap="medium", horizontal_alignment="center"):
    
    if st.button("Translate", type="primary", width="stretch"):
        if not usr_prompt.strip():
            st.warning("Please enter text to translate.")
        else:
            source= languages[source_language]
            target= languages[target_language]
            if source == target:
                st.warning("Source language must be different from target language")
            else:
                with st.spinner("Generating transaltion..."):
                    try:
                        result = client.translation(
                            usr_prompt,
                            model="facebook/mbart-large-50-many-to-many-mmt",
                            src_lang=source,
                            tgt_lang=target,
                        )
                        st.subheader("Translation Result")
                        st.info(result["translation_text"])
                    except Exception as e:
                        st.error(f"Error: {e}")
    if st.button("Clean", type="secondary", width="stretch"):
        usr_prompt = ""