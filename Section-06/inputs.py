import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.divider()

st.title("Inputs Section")

st.write("This section demonstrates various input components in Streamlit.")

st.divider()
st.write("### Text Input")
text_input = st.text_input("Enter some text", key="text_input", placeholder="Type here...", type="default")
st.write("You entered:", text_input)
pass_input = st.text_input("Enter your password", key="pass_input", placeholder="Enter your password",type="password", max_chars=20)
st.write("You entered:", pass_input)
st.divider()

st.write("### Number Input")
number_input = st.number_input("Enter a number", min_value=0, max_value=100, value=10, step=1, key="number_input")
st.write("You entered:", number_input)
st.divider()
st.text_area("Enter some text", key="text_area", placeholder="Type here...", height=100)
st.divider()
st.write("### Selectbox")
options = ["Option 1", "Option 2", "Option 3"]
selectbox = st.selectbox("Choose an option", options, key="selectbox")
st.write("You selected:", selectbox)
st.divider()
st.write("### Multiselect")
multiselect = st.multiselect("Select multiple options", options, default=["Option 1"], key="multiselect")
st.write("You selected:", multiselect)
st.divider()
st.write("### Slider")
slider = st.slider("Select a range", min_value=0, max_value=100, value=(20, 80), key="slider")
st.write("You selected:", slider)
st.divider()
st.write("### Date Input")
min_date = pd.to_datetime("1900-01-01")
max_date = pd.to_datetime("2050-12-31")
date_input = st.date_input("Select a date", value=pd.to_datetime("2023-10-01"), min_value=min_date, max_value=max_date, key="date_input")
st.write("You selected:", date_input)
st.divider()
st.write("### Time Input")
time_input = st.time_input("Select a time", value=pd.to_datetime("12:00").time(), step=60, key="time_input")
st.write("You selected:", time_input)
st.divider()
st.write("### File Uploader")
uploaded_file = st.file_uploader("Upload a file", type=["csv", "txt", "jpg", "png"], key="file_uploader")
if uploaded_file is not None:
    if uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
        st.write("DataFrame from CSV:")
        st.dataframe(df)
    elif uploaded_file.type in ["text/plain", "text"]:
        text_data = uploaded_file.read().decode("utf-8")
        st.write("Text data:")
        st.text(text_data)
    elif uploaded_file.type.startswith("image/"):
        image = uploaded_file.read()
        st.image(image, caption="Uploaded Image", use_column_width=True)
    else:
        st.write("Unsupported file type.")        
st.divider()    