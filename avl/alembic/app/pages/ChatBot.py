import streamlit as st
import os
import json
import pydantic # data validation
# import the lateral menu.
from lib.streamlit_common import common_page_initialization
from lib.rag import RAG, Chunk
# first line, first call.
DATABASE_PATH=os.path.dirname(__file__)+"/../database/AvlMaterialTracker.db"
BOT_NAME="AVL bot"
BOT_AVATAR=os.path.dirname(__file__) + "/../resources/AvlLogo.png"

common_page_initialization("ChatBoy.py")


def create_user_message():
    return st.chat_message(name="user")
def create_bot_message():
    return st.chat_message(name=BOT_NAME, avatar=BOT_AVATAR)

def print_chat(messages: list[dict[str,str]]):
    for msg in messages:
        if msg["author"]== "user":
            create_user_message().write(msg["content"])
        else:
            container = create_bot_message()
            container.write(msg["content"])
            with container.expander(label="Sources"):
                st.code(msg["sources"][0].content)


if "rag" not in st.session_state:
    st.session_state.rag = RAG(json.load(open( os.path.dirname(__file__) + "/../resources/rag.json")))

prompt = st.chat_input("Ask something")


if prompt:
    create_user_message().write(prompt)
    stream= st.session_state.rag.begin_sql_stream(
        prompt,
        json.load(open(os.path.dirname(__file__)+"/../resources/database.json")) | {"path": DATABASE_PATH}
    )
    botMessage = create_bot_message()
    response = create_bot_message().write_stream(stream)
    chunks = st.session_state.rag.end_stream(response)
    if "history" not in st.session_state:
        st.session_state.history=[]

    with botMessage.expander(label="Sources"):
        st.code(chunks[0].content)

    st.session_state.history.append({
        "author": "bot",

    })