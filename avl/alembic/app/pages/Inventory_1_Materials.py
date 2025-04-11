import streamlit as st
import pandas as pd

from sqlalchemy import select, func

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import change_id_of_vendors_by_name
from lib.streamlit_common import filter_dataframe
from lib.queries import get_materials_total_received_quantity
from lib.queries import get_materials_pending_requests
from lib.queries import get_all_materials

# ----- Initialization -----
PAGE_NAME = "Inventory_1_Materials"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----

# Interfaz por defecto de la pagina
def inventory_default_ui():
    
    # Leer materiales
    materials_df = get_all_materials()

    if materials_df.empty:
        no_results_message("There are no registered materials at the moment")
    else:
        st.subheader("🗂️ Materials", help=(
            "Here you can view information about all materials registered through a transaction, "
            "including the total amount to receive, the total ordered quantity, and the number of current requests "
            "asking for stock of the material.\n\n"
            " - Materials can only be added through 'Import transactions' or 'Transfer in' menues.\n\n"
            " - The total requested amount is updated from 'Update materials'."
        ))

        total_received_quantity = get_materials_total_received_quantity()

        pending_requests_df = get_materials_pending_requests()

        # Realizar el merge para agregar las columnas con informacion adicional sobre el material
        materials_df = pd.merge(materials_df, pending_requests_df, on='PO_PO_Item', how='left')
        materials_df = pd.merge(materials_df, total_received_quantity, on='PO_PO_Item', how='left')

        # Cantidad total por recibir = toda la solicitada - la que ha llegado
        materials_df['PendingQtyToReceiveFinal'] = materials_df['Pending_QTY_To_Receive'] - materials_df['TotalReceivedQuantity'].fillna(0)

        # Elegir orden y columnas a mostrar
        columns_to_show = ["PO_PO_Item", "Vendor_Number", "Short_Description", "Long_Text", "Project_Id", "WBS", "Stock", "PendingQtyToReceiveFinal", "Pending_QTY_To_Receive", "PendingRequestsCount"]
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
            "Pending_QTY_To_Receive": "Total ordered quantity",
            "PendingRequestsCount": "Amount of pending Requests",
            "PendingQtyToReceiveFinal": "Pending quantity to reveive"
        })

        filtered_df = filter_dataframe(materials_df, "Materials")

        # Mostrar dataframe de materiales
        st.dataframe(
            data = filtered_df,
            hide_index = True,
            use_container_width = True,
            height = 900
        )

inventory_default_ui()
