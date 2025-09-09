import streamlit as st
import requests
from bs4 import BeautifulSoup
from docx import Document
from io import BytesIO

def scrapper():
    st.subheader("Wikipedia web scrapper")
    
    search_term = st.text_input("", placeholder="Search in Wikipedia", autocomplete=False)
    language = "es"
    if search_term:
        url = f"https://{language}.wikipedia.org/wiki/{search_term.replace(' ', '_')}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
    
