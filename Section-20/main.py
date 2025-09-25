import streamlit as st

st.set_page_config("Hugging Face Chats")

pages = {
    "Text models": [
        st.Page("chat.py", title="Chat OpenAI"),
        st.Page("feelings.py", title="Feelings"),
    ],
    "Tokens and translations": [
        st.Page("translator.py", title="Translator"),
        st.Page("token.py", title="Token Classification"),
    ],
    "Summarization": [
        st.Page("summarization.py", title="Summarization"),
    ],
}

pg = st.navigation(pages)
pg.run()
