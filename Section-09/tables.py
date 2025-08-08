import streamlit as st
import pandas as pd
def tables():
    st.title("Tables")
    
    # Create a sample DataFrame
    file = st.file_uploader("Upload a CSV file", type=["csv"])
    if file is not None:
        df = pd.read_csv(file)
        st.subheader("Data Preview")
        drop_columns = st.multiselect("Select columns to drop", df.columns.tolist())
        if drop_columns:
            df = df.drop(columns=drop_columns)
            # Display the DataFrame as a table
            limit = st.slider("Select number of rows to display", min_value=10, max_value=len(df), value=10)
            df = df.head(limit)
            st.write(f"Displaying the first {limit} rows of the uploaded CSV file: length {len(df)}")
            st.table(df)
        else:
            st.write("No columns selected to drop. Displaying the full DataFrame.")
            hide_columns = ["id","color"]
            df = df.drop(columns=hide_columns, errors='ignore')
            st.table(df.head(10))  # Display first 10 rows if no columns are dropped
    else:
        st.write("Please upload a CSV file to display its contents.")