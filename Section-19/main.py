import streamlit as st
from ollama import Client
from sidebar_utils import sidebar


def clean():
    st.session_state.message = []


if "message" not in st.session_state:
    st.session_state.message = []

selected_model = sidebar(clean_callback=clean, current_page="main")
st.title(f"Chat {selected_model}")
st.markdown("<hr>", unsafe_allow_html=True)
for message in st.session_state.message:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
if prompt := st.chat_input("Question"):
    st.session_state.message.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Validating data..."):
        try:
            client = Client()
            response = client.chat(model=selected_model, messages=[{"role": "user", "content": prompt}])
            response_txt = response["message"]["content"]         
        except Exception as e:
            response_txt= f"Error: {str(e)}"
            
    st.session_state.message.append({"role": "assistant", "content": response_txt})
    with st.chat_message("assistant"):
        st.markdown(response_txt)