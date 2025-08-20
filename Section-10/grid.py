import streamlit as st
import pathlib
import pandas as pd
import numpy as np
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from faker import Faker
st.set_page_config(page_title="Section 10 - Grid", layout="wide")

def load_css(file_css):
    with open(css_file) as f:
        st.html(f"<style>{f.read()}</style>")

css_file = pathlib.Path(__file__).parent / "style.css"
load_css(css_file)

faker = Faker('es_ES')


st.title("Section 10 - Grid")

with st.container(border=True):
    st.subheader("Dashboard :violet[streamlit_extras]")
    c1, c2, c3 = st.columns(3, gap="large", vertical_alignment="top")
    with c1:
        st.success(faker.company())
        st.metric("Price", value=faker.pricetag(), delta=f"{faker.random_int(min=-100, max=100, step=1)} %")
    with c2:
        st.warning(faker.company())
        st.metric("Sales", value=faker.pricetag(), delta=f"{faker.random_int(min=-100, max=100, step=1)} %")
    with c3:
        st.info(faker.company())
        col1, col2 = st.columns(2)
        with col1:
            st.info(faker.company())
            st.metric("Price", value=faker.pricetag(), delta=f"{faker.random_int(min=-100, max=100, step=1)} %")
            st.metric("Sales", value=faker.pricetag(), delta=f"{faker.random_int(min=-100, max=100, step=1)} %")
        with col2:
            st.info(faker.company())
            st.metric("Price", value=faker.pricetag(), delta=f"{faker.random_int(min=-100, max=100, step=1)} %")
            st.metric("Sales", value=faker.pricetag(), delta=f"{faker.random_int(min=-100, max=100, step=1)} %")
    style_metric_cards(border_left_color="violet", border_size_px=2)
    
    column1, column2 = st.columns(2, gap="large", vertical_alignment="top")
    with column1:
        st.info("Balance")
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
        st.bar_chart(chart_data, use_container_width=True)
        
    with column2:
        st.info("Sales")
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
        st.line_chart(chart_data, use_container_width=True)
        
    data = {
        "col1": [faker.company() for _ in range(10)],
        "col2": [faker.pricetag() for _ in range(10)],
        "col3": [faker.pricetag() for _ in range(10)],
        "col4": [faker.pricetag() for _ in range(10)]
    }
    st.success("Data Table")
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)