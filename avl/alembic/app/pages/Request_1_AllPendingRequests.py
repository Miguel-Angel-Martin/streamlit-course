import streamlit as st
import pandas as pd

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import filter_dataframe
from lib.streamlit_common import merge_materials_data_to_request_lines_df
from lib.streamlit_common import accept_request_by_id
from lib.streamlit_common import deny_request_by_id
from lib.streamlit_common import rerun_with_success
from lib.streamlit_common import rerun_with_error

from lib.queries import get_all_pending_requests
from lib.queries import get_request_lines_by_request_id
from lib.queries import get_request_by_id

# ----- Initialization -----
PAGE_NAME = "Request_1_AllPendingRequests"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----

# Interfaz para atender requests pendientes
def attend_requests_ui():

    # Consulta de requests pendientes
    pending_requests_df = get_all_pending_requests()

    if pending_requests_df.empty:
        no_results_message("There are not any pending request at the moment")
    else:
        # - Mostrar requests pendientes -
        st.subheader("📝 Pending requests", help = (
            "Here are all the requests that are pending and still need to be addressed.\n\n"
            "If you want to deny or attend a request, follow these steps:\n"
            "- Scroll through the list and select the one you want to deny\n"
            "- Click the 'Attend Request'/'Deny Request' button that appears in the menu on the left\n"
            "- Confirm the action, and you will be able to see the request in the 'Request History' menu, attended or denied."
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

        # Aplicar el filtro al DataFrame original para obtener el DataFrame filtrado
        filtered_df = filter_dataframe(pending_requests_df, "Pending requests")

        # Mostrar el DataFrame filtrado en Streamlit
        selected_pending_request = st.dataframe(
            filtered_df,
            height=400,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="Requested_requests"
        )

        # Obtener el índice de la fila seleccionada en el DataFrame filtrado
        selected_index = selected_pending_request.selection.rows

        if selected_index:
            # Acceder al valor del 'request_id' de la fila seleccionada en el DataFrame filtrado
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

            col1, col2 = st.columns(2)

            with col1:
                attend_request_button = st.button(
                    label = "Attend request",
                    use_container_width = True,
                )

            with col2:
                deny_request_button = st.button(
                    label = "Deny request",
                    use_container_width = True
                )

            if attend_request_button:
                confirm_request_ui(request_id, request_lines_with_material_data_df)

            if deny_request_button:
                deny_request_ui(request_id, request_lines_with_material_data_df)

@st.dialog(title="Attend request", width="large")
def confirm_request_ui(request_id, request_lines_with_material_data_df):

    request_df = get_request_by_id(request_id)
    

    st.text(f"Are you sure you want to accept this request?")

    st.dataframe(
        data = request_df,
        use_container_width = True,
        hide_index = True,
    )

    st.text("Request lines")
    st.dataframe(
        data = request_lines_with_material_data_df,
        use_container_width=True,
        hide_index=True
    )

    feedback_to_requester = st.text_area(
        label = "Feedback notes",
        height = 100
    )

    receiver = st.text_input(
        label = "Received by"
    )

    manufacturing_destination = st.text_input(
        label = "Manufacturing destination"
    )

    confirm_transaction = st.button(
        label = "Yes, attend request",
        use_container_width = True,
    )

    if confirm_transaction:
        if not receiver:
            st.error("The receiver data is required"); return
        if not manufacturing_destination:
            st.error("The manufacturing destination field is required"); return
        
        if accept_request_by_id(request_id, feedback_to_requester, receiver, manufacturing_destination):
            rerun_with_success("Transaction completed successfully")
        else:
            rerun_with_error(f"There is not enough material available to attend all the request lines")

# Confirmacion para denegar una request
@st.dialog(title="Deny Transaction", width="large")
def deny_request_ui(request_id: int, request_lines_with_material_data_df: pd.DataFrame):
    st.text(f"Are you sure you want to deny this request?")
    # Consulta de la request seleccionada
    request_df = get_request_by_id(request_id)

    st.dataframe(
        data = request_df,
        use_container_width = True,
        hide_index = True,
    )

    st.text("Request lines")
    st.dataframe(
        data = request_lines_with_material_data_df,
        use_container_width=True,
        hide_index=True
    )

    feedback_to_requester = st.text_area(
        label = "Feedback notes",
        height = 100
    )
    
    confirm_deny_button = st.button(
        label = "Yes, deny",
        use_container_width = True
    )

    if confirm_deny_button:
        if not feedback_to_requester:
            st.error("The feedback field is required"); return
        
        if deny_request_by_id(request_id, feedback_to_requester):
            rerun_with_success(f"Request with id {request_id} has been denied")
        else:
            rerun_with_error("An error occurred while denying the transaction")

attend_requests_ui()