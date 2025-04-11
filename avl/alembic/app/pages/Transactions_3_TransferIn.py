import streamlit as st
import pandas as pd

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import rerun_with_success
from lib.streamlit_common import rerun_with_error
from lib.streamlit_common import save_transfer_in

from lib.queries import get_all_warehouses
from lib.queries import get_all_projects
from lib.queries import get_all_vendors
from lib.queries import get_vendor_by_name
from lib.queries import get_material_by_id

from lib.types import TransactionType

# ----- Initialization -----
PAGE_NAME = "Transactions_3_TransferIn"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----

# Interfaz con el formulario para crear una transaccion de entrada a mano
def make_delivery_transaction_ui():

    warehouses_df = get_all_warehouses()

    if warehouses_df.empty:
        no_results_message("There are no registered warehouses to make a manual transaction")
    else:

        st.subheader("🚛 Transfer in", help = (
            "From here, you can perform a manual transaction in case the material enters without being registered in a GR file.\n\n"
            "To do this, simply fill in the fields with the relevant transaction and material information.\n\n"
            "Materials in the system are identified by the combination of PO and PO Item, so please enter one that "
            "is not yet registered in the system and that you believe will not interfere with the arrival of new materials in the future."
        ))

        with st.form("Transfer in form"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                product_order = st.text_input(
                    label = "Product order",
                    placeholder = "37XXXXXX"
                )

            with col2:
                product_order_item = st.text_input(
                    label = "Product order item",
                    placeholder = "01"
                )

            vendor_names = get_all_vendors()["Company"].tolist()
            vendor_names.sort()

            with col3:
                selected_vendor = st.selectbox(
                    label = "Vendor",
                    options = vendor_names
                )
                vendor_number = get_vendor_by_name(selected_vendor).at[0, "Number"]

            project_ids = get_all_projects()["Id"].tolist()
            project_ids.sort()

            with col4:
                selected_project_id = st.selectbox(
                    label = "Project Id",
                    options = project_ids
                )
            
            short_description = st.text_input(label = "Short description")
            long_description = st.text_area(label = "Long description", height = 150)

            #warehouse_name = st.selectbox(label = "Store material in...", options = warehouses)

            delivered_qty = st.number_input(
                label = f"Delivered quantity",
                min_value = 1,
                value = 1
            )
            
            make_delivery_transaction = st.form_submit_button(
                label = "Make delivery transaction"
            )

            # Realizar transaccion
            if make_delivery_transaction :
                # Comprobar que los campos son correctos
                if (product_order and product_order_item) == '':
                    st.error("'Product order', 'Product order item' fields are required")
                    return
                
                po_po_item = f"{product_order}.{product_order_item}"
                material = get_material_by_id(po_po_item)["PO_PO_Item"]
                
                if not material.empty:
                    st.error(f"The material {po_po_item} has been already transacted")
                    return
                
                # Crear la transaccion y el material
                new_transaction_data = {
                    "Type": TransactionType.DELIVERY.value,
                    "PO_PO_Item": po_po_item,
                    "User": st.session_state.user['id'],
                    "Transact_QTY": delivered_qty
                }
                    
                new_material_data = {
                    "PO_PO_Item": po_po_item,
                    "Stock": delivered_qty,
                    "Warehouse_Id": 1,
                    "Vendor_Number": vendor_number,
                    "Short_Description": short_description,
                    "Long_Text": long_description,
                    "Project_Id": selected_project_id,
                    "Pending_QTY_To_Receive": delivered_qty
                }

                confirm_delivery_transaction_ui(new_transaction_data, new_material_data)

# Ventana de confirmacion para crear una request a mano con su material
@st.dialog(title = "Confirm transaction", width = "large")
def confirm_delivery_transaction_ui(new_transaction_data, new_material_data):

    # Informacion de la transaccion
    new_transaction_df = pd.DataFrame([new_transaction_data])
    
    # Informacion del material
    new_material_df = pd.DataFrame([new_material_data])

    st.subheader("Transaction info")
    st.dataframe(
        data = new_transaction_df,
        hide_index = True,
        use_container_width = True
    )
    
    st.divider()
    
    st.subheader("Material Info")
    st.dataframe(
        data = new_material_df,
        hide_index = True,
        use_container_width = True
    )

    # Boton de confirmacion
    confirm = st.button(
        label="Confirm transaction",
        use_container_width=True
    )

    if confirm:
        # Lo tratamos como una linea de gr file y lo procesamos como tal
        if save_transfer_in(new_transaction_data, new_material_data):
            rerun_with_success("Transaction completed successfully")
        else:
            rerun_with_error("An error occurred while making the transaction")

make_delivery_transaction_ui()