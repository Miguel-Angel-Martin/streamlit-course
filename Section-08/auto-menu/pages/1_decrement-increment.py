import streamlit as st
import pandas as pd


st.divider()

# Initialize counter in session state
if "counter" not in st.session_state:
    st.session_state.counter = 0

def increment_counter():
    st.session_state.counter += 1

def decrement_counter():
    st.session_state.counter -= 1

st.button("Increment", on_click=increment_counter, key="increment")
st.button("Decrement", on_click=decrement_counter, key="decrement")

# Safely access st.session_state.counter
counter = st.session_state.get("counter", 0)
st.write("#", counter)