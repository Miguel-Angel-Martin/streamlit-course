import streamlit as st
import pandas as pd

from sqlalchemy import select

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import rerun_with_success
from lib.streamlit_common import rerun_with_error
from lib.streamlit_common import change_id_of_vendors_by_name
from lib.streamlit_common import filter_dataframe
from lib.streamlit_common import save_transfer_out

from lib.queries import get_all_available_materials

from database.Database_Model import engine, Material

# ----- Initialization -----
PAGE_NAME = "Transactions_4_TransferOut"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----

def transfer_material_out_ui():

    # Mostrar materiales disponibles
    materials_df = get_all_available_materials()

    columns_to_show = ["PO_PO_Item", "Stock", "Pending_QTY_To_Receive", "Vendor_Number", "Short_Description", "Long_Text", "Project_Id", "WBS"]
    materials_df = materials_df[columns_to_show]

    # En vez de los numeros del vendor, se muestran los nombres asociados a ese numero 
    materials_df = change_id_of_vendors_by_name(materials_df)
    
    # Renombrar las columnas que se quiera
    materials_df = materials_df.rename(columns = {
        "PO_PO_Item": "PO.PO Item",
        "Vendor_Number": "Vendor",
        "Short_Description": "Short description",
        "Long_Text": "Long description",
        "Project_Id": "Project Id",
        "Pending_QTY_To_Receive": "Total ordered quantity"
    })

    if materials_df.empty:
        no_results_message("There are no available materials in the inventory at the moment")
    else:
        st.subheader("📦 Transfer out", help=(
            "From here, you can discard a material through a transaction. "
            "Follow these steps:\n"
            "- Select the material you want to discard and specify the quantity to discard.\n"
            "- Specify the reason for discarding the material (e.g., mistake when entering the material, wear and tear, etc.).\n"
            "- Click the 'Discard material' button and confirm the action.\n\n"
            "Once confirmed, the material's stock will be discounted."
        ))
        
        filtered_df = filter_dataframe(materials_df, "Materials")
        
        selected_material = st.dataframe(
            filtered_df,
            height = 500,
            hide_index = True,
            use_container_width = True,
            on_select = "rerun",
            selection_mode = "single-row"
        )

        selected_index = selected_material.selection.rows
        if selected_index:
            selected_row = filtered_df.iloc[selected_index[0]]
            material_po_po_item = str(selected_row['PO.PO Item'])
            material_stock = selected_row['Stock']

            col1, col2 = st.columns([1,4])

            with col1:
                transaccion_qty = st.number_input(
                    label = f"Quantity to transfer out",
                    min_value = 1,
                    max_value = int(material_stock),
                    value = 1
                )

            notes = st.text_area(
                label = "Notes (Reason for the transaction)",
                height = 100
            )

            make_broken_material_transaction_button = st.button(
                label = "Discard material"
            )
            
            if make_broken_material_transaction_button:
                if not notes.strip():
                    st.error("Notes are required to proceed with the transaction.")
                else:
                    make_broken_material_transaction(material_po_po_item, int(transaccion_qty), notes)

@st.dialog(title="Discard material", width="large")
def make_broken_material_transaction(material_po_po_item: str, transaccion_qty: int, notes: str):

    st.subheader(f"Are you sure you want to discard {transaccion_qty} units of this material?")
    
    # Mostrar informacion del material seleccionado
    material_df = pd.read_sql(
        select(Material)
        .where(Material.PO_PO_Item == material_po_po_item)
    , engine)

    st.dataframe(
        data = material_df,
        use_container_width = True,
        hide_index = True,
    )

    st.write(f"Units after transaction: {int(material_df.at[0, 'Stock']) - transaccion_qty}")
    
    confirm_discard = st.button(
        label = "Yes, discard material",
        use_container_width = True,
    )

    if confirm_discard:
        if save_transfer_out(material_po_po_item, transaccion_qty, notes):
            rerun_with_success("Transaction completed successfully")
        else:
            rerun_with_error("An error occurred while making the transaction")
   
transfer_material_out_ui()