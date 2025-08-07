import streamlit as st
import pandas as pd
def dataframes():
    st.title("Dataframes")
    
    # Create a sample DataFrame
    data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"]
    }
    df = pd.DataFrame(data)
    
    # Display the DataFrame as a table
    st.table(df)