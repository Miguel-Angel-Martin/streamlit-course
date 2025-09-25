import os
from huggingface_hub import InferenceClient
import streamlit as st

client = InferenceClient(
    provider="hf-inference",
    api_key=st.secrets["HF_TOKEN"],
)


usr_prompt = st.text_area("Write your felling")

if st.button("Send"):
    if not usr_prompt.strip():
        st.warning("Please enter a question")

    else:
        with st.spinner("Generating response..."):
            try:
                result = client.text_classification(
                    "I love Real Madrid",
                    model="tabularisai/multilingual-sentiment-analysis",
                )
                for r in result:
                    st.info(f"Label: {r.label}, Score: {r.score:.2f}")
            except Exception as e:
                st.error(f"Error: {e}")
                st.warning(e)
            