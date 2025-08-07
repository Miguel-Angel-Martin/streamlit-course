import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.divider()
st.write("This is the URL section of the app.")
st.link_button("Ir a google", url="https://www.google.com")

text_descargar = "Descargar archivo CSV"
st.download_button(
    label=text_descargar,
    data="col1,col2\n1,2\n3,4",
    file_name="archivo.csv",
    mime="text/csv",
    key="download_csv")
st.divider()
st.download_button(
    "Descargar archivo TXT",text_descargar)
st.divider()
with open("./assets/image.jpg", "rb") as file:
    st.download_button(
        label="Descargar imagen",
        data=file,
        file_name="imagen.jpg",
        mime="image/jpeg",
        key="download_image"
    )
