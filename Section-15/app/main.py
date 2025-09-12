import streamlit as st
from db_manager import DBManager

st.title("🚀 Streamlit + MySQL con Docker y clase DBManager")

# Inicialización de la base de datos y tabla customer
db = DBManager()
db.init_db()

# Mostrar datos de customer
df_customer = db.fetch_customers()
st.dataframe(df_customer)
