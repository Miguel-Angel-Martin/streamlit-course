import streamlit as st
from models.customer_model import CustomerModel
import pandas as pd
import time

def show_customers():
    st.title("Show customers")

    ss = st.session_state

    # --- Inicializar DataFrame ---
    if "df_customers" not in ss:
        customers = CustomerModel.get_all_customers()
        ss.df_customers = pd.DataFrame(customers)
        ss.df_customers["Delete"] = False
        
    if "close_dialog" not in ss:
            ss.close_dialog = False
    # --- Función para refrescar datos ---
    def refresh_customers():
        customers = CustomerModel.get_all_customers()
        ss.df_customers = pd.DataFrame(customers)
        ss.df_customers["Delete"] = False

    # --- Editor de datos ---
    data = st.data_editor(ss.df_customers, num_rows="dynamic")

    rc1, rc2, _ = st.columns([1, 1, 12])

    # --- Editar clientes ---
    with rc1:
        if st.button("Edit", icon=":material/edit:"):
            for _, row in data.iterrows():
                CustomerModel.update_customer(
                    customer_id=row['customer_id'],
                    name=row['name'],
                    surname=row['surname'],
                    telephone=row['telephone'],
                    project=row['project'],
                    date=row['date']
                )
            st.toast("Customers updated.")
            refresh_customers()

    # --- Eliminar clientes ---
    with rc2:
        @st.dialog("Delete customers")
        def delete_customers():
            st.error("Are you sure you want to delete the selected customers?")
            col1, _, col2 = st.columns([1,3,1])
            with col1:
                if st.button("Confirm"):
                    rows_to_delete = data[data["Delete"]]
                    if not rows_to_delete.empty:
                        for _, row in rows_to_delete.iterrows():
                            CustomerModel.delete_customer(row['customer_id'])
                        st.toast("Customers deleted.")
                        refresh_customers()
                    else:
                        st.toast("No customers selected for deletion.")
                    ss.close_dialog = True
            with col2:
                if st.button("Cancel"):
                    st.toast("Operation cancelled.")
                    ss.close_dialog = True

            if ss.close_dialog:
                ss.close_dialog = False
                time.sleep(1)
                st.rerun()
        if st.button("Delete", icon=":material/delete:"):
            delete_customers()
