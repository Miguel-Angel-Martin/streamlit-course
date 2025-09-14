import streamlit as st

from views.add_customers import add_customers
from views.show_customers import show_customers

st.set_page_config("🚀 Streamlit + MySQL con Docker y clase DBManager", layout="wide")

tab1, tab2 = st.tabs(["Add customers", "Show customers"])

with tab1:
    add_customers()

with tab2:
    show_customers()


# Inicialización de la base de datos y tabla customer
#db = DBManager()
#db.init_db()
#
## Mostrar datos de customer
#df_customer = db.fetch_customers()
#st.dataframe(df_customer)
