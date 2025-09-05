import streamlit as st
from shortener import shortener
from scrapper import scrapper

def main():
    st.set_page_config("Utilities",page_icon=":material/service_toolbox:",layout="wide")
    st.title("Utilities")
    tab1, tab2 = st.tabs(["Shortener", "Scrapper"])
    with tab1:
        shortener()
    with tab2:
        scrapper()

if __name__ == "__main__":
    main()