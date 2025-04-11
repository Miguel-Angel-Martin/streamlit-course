import streamlit as st
import pandas as pd

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import filter_dataframe

from lib.queries import get_all_transactions
from lib.queries import get_transactions_with_material_descriptions

# ----- Initialization -----
PAGE_NAME = "Transactions_1_TransactionsHistory"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----

# Interfaz para ver las transacciones hechas
def previous_transactions_ui():

    # Tabla de transacciones previas con filtro
    previous_transactions_df = get_all_transactions()

    if previous_transactions_df.empty:
        no_results_message("No transaction has been made yet")
    else:

        transactions_with_material_descriptions = get_transactions_with_material_descriptions()
        
        columns_to_show = ["Id", "Type", "PO_PO_Item", "Short_Description", "Long_Text", "SO_SO_Item", "Project_Id", "User", "Posting_date", "Time", "Transact_QTY", "Notes"]
        transactions_with_material_descriptions = transactions_with_material_descriptions[columns_to_show]
        transactions_with_material_descriptions = transactions_with_material_descriptions.rename(columns = {
            "PO_PO_Item": "Material PO.PO Item",
            "Project_Id": "Project Id",
            "Short_Description": "Short description",
            "Long_Text": "Long description",
            "SO_SO_Item": "SO.SO Item",
            "Posting_date": "Posting date",
            "Time": "Posting time",
            "Transact_QTY": "Transaction quantity"
        })

        col1, col2 = st.columns([3, 3])
        
        with col1:
            st.subheader("📜 Transactions History", help=(
                "Here, you can view the transaction history, including transactions from GR files, "
                "transactions made in the 'Transfer in' or 'Transfer out' menus, and attended or denied requests.\n\n"
                "The most recent transactions are shown first, and with the filter at "
                "the top right, you can narrow the view to only show transactions from a specific date onward."
            ))

        with col2:
            min_date = transactions_with_material_descriptions['Posting date'].min()
            max_date = transactions_with_material_descriptions['Posting date'].max()
            selected_date = st.date_input(
                label = "Transactions after",
                value = min_date,
                min_value = min_date,
                max_value = max_date
            )

        transactions_with_material_descriptions = transactions_with_material_descriptions[transactions_with_material_descriptions['Posting date'] >= selected_date]
        
        filtered_df_key = "Transactions with material descriptions"
        filtered_df = filter_dataframe(transactions_with_material_descriptions, filtered_df_key)

        # Ordenado para que aparezcan primero las mas recientes
        filtered_df = filtered_df.sort_values(by=['Posting date', 'Posting time'], ascending=[False, False])

        st.dataframe(
            filtered_df,
            hide_index = True,
            use_container_width = True,
            height = 700
        )

previous_transactions_ui()