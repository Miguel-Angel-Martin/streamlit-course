import streamlit as st
from faker import Faker
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Faker data", layout="wide")
st.title(":orange[FAKER DATA GENERATOR]")
st.divider()
df= pd.DataFrame()
with st.sidebar:
    st.subheader("Configura tu faker Data.")
    localization = st.selectbox("Idioma", options=["en_US","es_MX", "es_ES", "fr_FR", "it_IT","pt_BR"])
    num_fields = st.number_input("Cantidad de campos", min_value=1, max_value=7, step=1)
    num_rows= st.number_input("Cantidad de filas", min_value=1, max_value=1000, step=1)
    
    fake = Faker(localization)
    
    faker_options= {
        "Name": fake.name,
        "Email": fake.email,
        "Address": fake.address,
        "Phone Number": fake.phone_number,
        "Job": fake.job,
        "Company": fake.company,
        "Birth": fake.date_of_birth     
    }
    
    fields_selection=[]
    st.write("Select the fields")
    
    for i in range(num_fields):
        field = st.selectbox(f"Field {i+1}", list(faker_options.keys()), key=f"field_{i}")
        fields_selection.append(field)

if st.button("Generate Data"):
    data = {field: [faker_options[field]() for _ in range(num_rows)] for field in fields_selection}
    data["id"]= range(1, num_rows+1)
    df = pd.DataFrame(data)
    column_order= ["id"] + [col for col in df.columns if col != "id"]
    df= df[column_order]    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, flex=1)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=100)
    grid_options = gb.build()
    AgGrid(df, gridOptions=grid_options, height=500, theme="streamlit")

if df.empty == False:
    col1, col2, _ = st.columns([1,1,8])
    with col1:        
        csv= df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="faker_data.csv",
            mime="text/csv"
        )
    with col2:
        json= df.to_json(orient="records", indent=4, force_ascii=False).encode("utf-8")
        st.download_button(
            label="Download json",
            data=json,
            file_name="faker_data.json",
            mime="application/json"
        )
    st.divider()