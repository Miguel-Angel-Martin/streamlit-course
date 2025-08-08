import streamlit as st
import pandas as pd
from io import BytesIO
def dataframes():
    st.title("Dataframes")
    
    # Create a sample DataFrame
    file = st.file_uploader("Upload a CSV file", type=["csv"])
    if file is not None:
        df = pd.read_csv(file)
        field= st.selectbox("Select a field to display", df.columns)
        search = st.text_input("", placeholder="Search for a value in the DataFrame", autocomplete="off")
        if search:
            #df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            df = df[df.apply(lambda row: search.lower() in str(row[field]).lower(), axis=1)]
        st.subheader("DataFrame Contents")
        st.write(f"Displaying {len(df)} rows and {len(df.columns)} columns")
        st.dataframe(df,
                    hide_index=True,
                    column_config={col: st.column_config.TextColumn(
                        label=col,
                        help=f"Column: {col}",
                        max_chars=1000 if df[col].dtype == 'object' else None
                    ) for col in df.columns},
                    use_container_width=True)
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        
        st.download_button("Download as Excel",
                            data=excel_buffer,
                            file_name="dataframe.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.write("Please upload a CSV file to display its contents.")
        