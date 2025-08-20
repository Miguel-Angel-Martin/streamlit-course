import streamlit as st
import pathlib
from card import custom_card
def load_css(file_css):
    with open(css_file) as f:
        st.html(f"<style>{f.read()}</style>")

css_file = pathlib.Path(__file__).parent / "style.css"
load_css(css_file)


with st.sidebar:
    st.subheader("Sidebar Menu")


st.title("Section 10: Advanced Topics in Streamlit")
st.markdown("<h2 style='color:aqua'>Otro Titulo</h2>", unsafe_allow_html=True)
st.button("Click Me primary!", type="primary")
st.button("Click Me secondary!", type="secondary")
st.button("Click Me! tertiary", type="tertiary")
st.button("Click Me Css!", key="success")
st.button("Click Me Css!", key="info")
st.button(":red[Delete]", icon=":material/delete:")
st.slider("Slider", 0, 100, 50)
st.text_input("Text Input", "Type here...")
st.text_area("Text Area", "Type here...")

with st.container(border=True):
    st.subheader("Container :violet[Section]")
    st.write("This is a container section where you can add more content.")
    st.button("Container Button")
    
lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex."

custom_card("Card Title", lorem_ipsum, "Card Footer")