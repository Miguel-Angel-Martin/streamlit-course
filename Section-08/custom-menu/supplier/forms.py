import streamlit as st
import pandas as pd 
from datetime import datetime


st.divider()
st.subheader("Forms Section")
with st.form("my_form"):
    st.write("This is a form with various input components.")
    text_input = st.text_input("Enter some text", key="text_input", placeholder="Type here...", type="default")
    pass_input = st.text_input("Enter your password", key="pass_input", placeholder="Enter your password", type="password", max_chars=20)
    number_input = st.number_input("Enter a number", min_value=0, max_value=100, value=10, step=1, key="number_input")
    options = ["Option 1", "Option 2", "Option 3"]
    selectbox = st.selectbox("Choose an option", options, key="selectbox")
    multiselect = st.multiselect("Select multiple options", options, default=["Option 1"], key="multiselect")
    slider = st.slider("Select a range", min_value=0, max_value=100, value=(20, 80), key="slider")
    min_date = pd.to_datetime("1900-01-01")
    max_date = pd.to_datetime("2050-12-31")
    date_input = st.date_input("Select a date", value=pd.to_datetime("2023-10-01"), min_value=min_date, max_value=max_date, key="date_input")
    time_input = st.time_input("Select a time", value=pd.to_datetime("12:00").time(), step=60, key="time_input")
    submit_button = st.form_submit_button(label="Submit")
    if submit_button:
        if not text_input or not pass_input:
            st.error("Please fill in all required fields.")
        else:
            # Process the form data
            st.write("Form submitted with the following data:")
            st.write("Text Input:", text_input)
            st.write("Password Input:", pass_input)
            st.write("Number Input:", number_input)
            st.write("Selectbox:", selectbox)
            st.write("Multiselect:", multiselect)
            st.write("Slider:", slider)
            st.write("Date Input:", date_input)
            st.write("Time Input:", time_input)