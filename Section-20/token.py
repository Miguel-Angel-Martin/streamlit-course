import os
from huggingface_hub import InferenceClient
import streamlit as st

client = InferenceClient(
    provider="hf-inference",
    api_key=st.secrets["HF_TOKEN"],
)
st.title("Huggin Face (Token Classification)")

usr_prompt = st.text_area("Write your felling")

if st.button("Send"):
    if not usr_prompt.strip():
        st.warning("Please enter a question")

    else:
        with st.spinner("Generating response..."):
            try:
                result = client.token_classification(
                usr_prompt,
                model="FacebookAI/xlm-roberta-large-finetuned-conll03-english",
                )
                for r in result:
                    st.info(f"Label: {r["word"]}")
            except Exception as e:
                st.error(f"Error: {e}")
                st.warning(e)