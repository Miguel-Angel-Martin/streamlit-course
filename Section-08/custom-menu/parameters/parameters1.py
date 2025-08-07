import streamlit as st

st.title("Parameters Section 1")
if st.button("Parameters"):
    st.switch_page("parameters/parameters.py")

if "sendId" in st.session_state:
    st.write(f"Received ID: {st.session_state.sendId}")
else:
    st.write("No ID received yet.")