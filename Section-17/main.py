import streamlit as st
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_groq import ChatGroq

st.set_page_config("LLMs con DataFrames", layout="centered")
st.title("LLMs con DataFrames")


completion = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=st.secrets["groq"]["API_KEY"],
    temperature=0
)

if "messages" not in st.session_state:
    st.session_state.messages = []

def reLoadChat():
    st.session_state.messages = []

file = st.file_uploader("Select csv file", type="csv", on_change=reLoadChat())

if file is not None:
    df = pd.read_csv(file)
    agent = create_pandas_dataframe_agent(completion, df, verbose=True, allow_dangerous_code=True) 
    
if prompt := st.chat_input("Question"):
    prompt_final = f"Eres español con la siguiente pregunta {prompt} y cuando pida mas de un registro damelo en tabla o lista de markdonw"
    st.session_state.messages = []
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt_final})
        
    with st.spinner("Validating data..."):
        response = agent.invoke(st.session_state.messages)
        
    with st.chat_message("assistant"):
        st.markdown(response["output"])
    
    st.session_state.messages.append({"role": "assistant", "content": response})   