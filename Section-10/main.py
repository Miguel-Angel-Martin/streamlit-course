import streamlit as st
import pathlib

def load_css(file_css):
    with open(css_file) as f:
        st.html(f"<style>{f.read()}</style>")

css_file = pathlib.Path(__file__).parent / "style.css"
load_css(css_file)

with st.sidebar:
    st.subheader("Sidebar Menu")


st.title("Section 10: Advanced Topics in Streamlit")
st.button("Click Me primary!", type="primary")
st.button("Click Me secondary!", type="secondary")
st.button("Click Me! tertiary", type="tertiary")
st.button("Click Me Css!", key="success")
st.button("Click Me Css!", key="info")
st.slider("Slider", 0, 100, 50)
st.text_input("Text Input", "Type here...")
st.text_area("Text Area", "Type here...")

with st.container(border=True):
    st.subheader("Container Section")
    st.write("This is a container section where you can add more content.")
    st.button("Container Button")