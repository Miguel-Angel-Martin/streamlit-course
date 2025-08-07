import streamlit as st
from tables import tables
from dataframes import dataframes
import charts
import pandas as pd

if "menu_state" not in st.session_state:
    st.session_state.menu_state = "Dataframes"


with st.sidebar:
    st.header("Navigation")
    st.write("Use the sidebar to navigate through the sections.")
    st.session_state.menu_state = st.selectbox("Menu", ["Dataframes", "Tables", "Charts"])
    
    
st.title("Section 09: Dataframes, Tables, and Charts")
if st.session_state.menu_state == "Dataframes":
    dataframes()
elif st.session_state.menu_state == "Tables":
    tables()    
elif st.session_state.menu_state == "Charts":
    charts.charts()