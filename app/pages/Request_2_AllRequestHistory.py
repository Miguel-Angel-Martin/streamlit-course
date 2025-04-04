import streamlit as st
import pandas as pd

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import filter_dataframe
from lib.streamlit_common import merge_materials_data_to_request_lines_df

from lib.queries import get_request_by_id_with_transaction_date_and_time
from lib.queries import get_request_lines_by_request_id
from lib.queries import get_transactions_notes

# ----- Initialization -----
PAGE_NAME = "Request_2_AllRequestHistory"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----

# Interfaz de requests atendidas
def previous_requests_ui():
    
    # Consulta de requests atendidas con la fecha y hora en la que se transaccionaron
    previous_requests_df = get_request_by_id_with_transaction_date_and_time()

    if previous_requests_df.empty:
        no_results_message("You have not any attended request yet")
    else:

        # - Mostrar requests atendidas -
        st.subheader("📚 Request History", help = (
            "Here are all the requests that have been previously processed. They might have been either accepted or denied.\n\n"
            "Select a request to view the details of its request lines and the transaction associated with that request line."
        ))

        # Elegir orden y columnas a mostrar
        columns_to_show = ["Id", "UserRequester", "Status", "Type", "Posting_date", "Time", "Transaction_Posting_Date", "Transaction_Time", 
                           "WarehouseNotes", "Feedback_To_Requester", "Receiver", "Manufacturing_Destination", "Project_Id"]
        previous_requests_df = previous_requests_df[columns_to_show]

        # Renombrar las columnas que se quiera
        previous_requests_df = previous_requests_df.rename(columns = {
            "Id": "Request id",
            "UserRequester": "Requester",
            "Type": "Type of request",
            "Posting_date": "Posting date",
            "Time": "Posting time",
            "Transaction_Posting_Date": "Transaction date",
            "Transaction_Time": "Transaction time",
            "WarehouseNotes": "Requester Notes",
            "Feedback_To_Requester" : "Logistics Notes",
            "Manufacturing_Destination": "Destination",
            "Project_Id": "Project id"
        })

        filtered_df = filter_dataframe(previous_requests_df, "Previous requests")

        # Mostrar requests atendidas
        selected_request = st.dataframe(
            filtered_df,
            height = 250,
            use_container_width = True,
            hide_index = True,
            on_select = "rerun",
            selection_mode = "single-row"
        )

        # Mostrar las request lines de una request pendiente seleccionada
        selected_index = selected_request.selection.rows
        if selected_index:
            selected_row = filtered_df.iloc[selected_index[0]]
            request_id = int(selected_row['Request id'])
            request_lines_df = get_request_lines_by_request_id(request_id)

            # Mostrar las request lines
            st.text("Request lines")
            request_lines_with_material_data_df = merge_materials_data_to_request_lines_df(request_lines_df)

            # Juntar el campo de notas de la transaccion de la request line porque es relevante en algunos casos
            transactions_df = get_transactions_notes()

            request_lines_with_material_data_df = pd.merge(request_lines_with_material_data_df, transactions_df, how='left', on='Transaction id')

            st.dataframe(
                data = request_lines_with_material_data_df,
                use_container_width=True,
                hide_index=True
            )

previous_requests_ui()