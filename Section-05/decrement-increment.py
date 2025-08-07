import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")

st.divider()


def increment_counter():
    if "counter" not in st.session_state:
        st.session_state.counter = 0
    st.session_state.counter += 1

    
def decrement_counter():
    if "counter" not in st.session_state:
        st.session_state.counter = 0
    st.session_state.counter -= 1


st.button("Increment", on_click=increment_counter, key="increment")
st.button("Decrement", on_click=decrement_counter, key="decrement")

st.write("#", st.session_state.counter)