import os
from huggingface_hub import InferenceClient
import streamlit as st

client = InferenceClient(
    provider="hf-inference",
    api_key=st.secrets["HF_TOKEN"],
)
st.title("Summary generation")

usr_prompt = st.text_area("Write your text")

if st.button("Send"):
    if not usr_prompt.strip():
        st.warning("Please enter a question")

    else:
        with st.spinner("Generating response..."):
            try:
                result = client.summarization(
                    usr_prompt,
                    model="facebook/bart-large-cnn",
                )
                st.subheader("Summary Result")
                st.info(result["summary_text"])
            except Exception as e:
                st.error(f"Error: {e}")