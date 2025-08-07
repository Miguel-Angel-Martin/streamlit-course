import streamlit as st
import pandas as pd

def charts():
    st.title("Charts")
    
    # Create a sample DataFrame
    data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"]
    }
    df = pd.DataFrame(data)
    
    # Display the DataFrame as a chart
    st.bar_chart(df.set_index("Name")["Age"])  # Bar chart of ages by name