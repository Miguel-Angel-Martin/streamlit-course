from openai import OpenAI
import streamlit as st
import os

st.title("Huggin Face (Chat OpenAI)")
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=st.secrets["HF_TOKEN"],
)

usr_prompt= st.text_area("Write your question")

if st.button("Send"):
    if not usr_prompt.strip():
        st.warning("Please enter a question")
        
    else:
        with st.spinner("Generating response..."):
            try:
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b:fireworks-ai",
                    messages=[
                        {
                            "role": "user",
                            "content": usr_prompt
                        }
                    ],
                )
            except Exception as e:
                st.error(f"Error: {e}")
                response= e
            response= completion.choices[0].message.content
            
            
    st.markdown(response)

