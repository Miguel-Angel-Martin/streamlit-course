import streamlit as st
import pandas as pd

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import filter_dataframe
from lib.streamlit_common import merge_materials_data_to_request_lines_df

from lib.queries import get_pendig_request_by_requester
from lib.queries import get_request_lines_by_request_id

# ----- Initialization -----
PAGE_NAME = "Request_4_OwnPendingRequests"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----

# Interfaz de requests pendientes
def pending_requests_ui():

    # Consulta de requests pendientes
    requester = st.session_state.user['email']
    pending_requests_df = get_pendig_request_by_requester(requester)
    
    if pending_requests_df.empty:
        no_results_message("You have not made any request yet")
    else:
        # - Mostrar requests pendientes -
        st.subheader("📬 My pending requests", help = (
            "From here, you can view all the requests you have made that are pending action by another privileged user.\n\n"
            "Select a request to view the details of its request lines and the transaction associated with that request line."
        ))

        # Elegir orden y columnas a mostrar
        columns_to_show = ["Id", "UserRequester", "Type", "Posting_date", "Time", "WarehouseNotes", "Project_Id"]
        pending_requests_df = pending_requests_df[columns_to_show]

        # Renombrar las columnas que se quiera
        pending_requests_df = pending_requests_df.rename(columns = {
            "Id": "Request id",
            "UserRequester": "Requester",
            "Type": "Type of request",
            "Posting_date": "Posting date",
            "Time": "Posting time",
            "WarehouseNotes": "Notes",
            "Project_Id": "Project id"
        })

        filtered_df = filter_dataframe(pending_requests_df, "Pending requests")
        
        # Mostrar requests pendientes
        selected_pending_request = st.dataframe(
            filtered_df,
            height = 250,
            use_container_width = True,
            hide_index = True,
            on_select = "rerun",
            selection_mode = "single-row"
        )

        # Mostrar los materiales de una request pendiente seleccionada
        selected_index = selected_pending_request.selection.rows
        if selected_index:
            selected_row = filtered_df.iloc[selected_index[0]]
            request_id = int(selected_row['Request id'])
            request_lines_df = get_request_lines_by_request_id(request_id)

            # Mostrar las request lines
            st.text("Request lines")
            request_lines_with_material_data_df = merge_materials_data_to_request_lines_df(request_lines_df)
            st.dataframe(
                data = request_lines_with_material_data_df,
                use_container_width=True,
                hide_index=True
            )

pending_requests_ui()