import streamlit as st
import pandas as pd
def tables():
    st.title("Tables")
    
    # Create a sample DataFrame
    file = st.file_uploader("Upload a CSV file", type=["csv"])
    if file is not None:
        df = pd.read_csv(file)
        st.subheader("Data Preview")
        # Display the DataFrame as a table
        st.table(df)
    else:
        st.write("Please upload a CSV file to display its contents.")