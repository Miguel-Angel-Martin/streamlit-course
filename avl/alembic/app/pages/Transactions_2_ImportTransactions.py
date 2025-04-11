import streamlit as st
import pandas as pd

from sqlalchemy import Date
from datetime import datetime

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import rerun_with_success
from lib.streamlit_common import rerun_with_error
from lib.streamlit_common import clean_GR_html
from lib.streamlit_common import is_gr_file_registered
from lib.streamlit_common import save_gr_lines_data
from lib.streamlit_common import filter_dataframe

# ----- Initialization -----
PAGE_NAME = "Transactions_2_ImportTransactions"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----

# Interfaz para permitir realizar multiples transacciones mediante un GR file
def make_multiple_transactions_ui():
    
    st.subheader("🚚 Import transactions", help=(
        "From here, you can import a GR file to display its transactions and select the ones you want to make. \n\n"
        "Steps to follow:\n"
        "- Upload a GR file.\n"
        "- Select the transactions you want to register and click the 'Make transactions' button.\n"
        "- Confirm the transactions.\n\n"
        "Once confirmed, the new materials will be registered with the quantities specified in the transactions, "
        "or the stock of materials that were already registered will be updated."
    ))

    # Key del file uploader
    if "gr_file_uploader_key" not in st.session_state:
        st.session_state["gr_file_uploader_key"] = 0

    # Ficheros del file uploader con la key subidos
    if "gr_uploaded_files" not in st.session_state:
        st.session_state["gr_uploaded_files"] = []

    # File uploader (con key) para realizar multiples transacciones
    GR_file = st.file_uploader(
        label = "Add GR file to make multiple transactions",
        type = ["htm"],
        key = st.session_state["gr_file_uploader_key"],
    )

    st.divider()

    # Si se sube un ficehro
    if GR_file is not None:
        try:
            st.session_state["gr_uploaded_files"] = GR_file
            # Comprobar si el fichero tiene el formato adecuado (GR en su nombre)
            file_name = GR_file.name
            
            if "GR" not in file_name:
                st.error("The filename needs to contain 'GR'.")
            else:
                file_content = (GR_file.read())
                # Leer todas las tablas del fichero subido
                gr_file_data = clean_GR_html(file_content, False)
                new_transactions_date = datetime.strptime(gr_file_data[0], '%d.%m.%Y').date()
                gr_file_lines_df = gr_file_data[1]
                show_multiple_gr_lines_df_ui(gr_file_lines_df, new_transactions_date)

        except Exception as e:
            st.error(f"File processing error: {e}")

# Interfaz con las transacciones de un GR file
def show_multiple_gr_lines_df_ui(new_gr_lines_df: pd.DataFrame, new_transactions_date: Date):

    # Comprobar que el fichero no ha sido registrado
    if is_gr_file_registered(new_transactions_date):
        st.warning(f"The GR file of {new_transactions_date} has already been transacted.\n\n"
            "Make sure you are importing transactions that have not been previously recorded from this "
            "file to avoid registering material entries that have already been produced. \n\n"
            "Otherwise, it can be reversed through another transaction in the 'Transfer out' menu, "
            "specifying in the notes that it was a confusion, mistake, or similar.")


    # Mostrar transacciones
    st.subheader(f"{new_transactions_date} Transactions", help = (
        "These are the transactions that have been read from the GR file you have uploaded.\n\n"
        "Select the transactions you wish to process and press the 'Confirm' button located in the left menu."
    ))

    if new_gr_lines_df.empty:
        no_results_message("There are no valid requests in this GR file")

        # Boton de confirmacion
        confirm_button = st.button(
            label = "Register GR file anyway"
        )

        if confirm_button:
            if save_gr_lines_data(new_gr_lines_df, new_transactions_date):
                st.session_state["gr_file_uploader_key"] += 1 # Nuevo file uploader para no mostrar la informacion en pantalla del archivo subido
                rerun_with_success("GR file updated successfully")
            else:
                rerun_with_error("An error occurred while uploading the GR file")

    else:
        filtered_df = filter_dataframe(new_gr_lines_df, "New transactions")
        
        selected_gr_lines = st.dataframe(
            filtered_df,
            hide_index = True,
            use_container_width = True,
            on_select = "rerun",
            selection_mode = "multi-row",
            height = 390
        )

        # Boton de confirmacion
        make_transactions_button = st.button(
            label = "Make transactions"
        )

        if make_transactions_button:
            selected_indexes = selected_gr_lines.selection.rows
            if selected_indexes:
                selected_gr_lines_df = filtered_df.iloc[selected_indexes]
                confirm_multiple_transactions_ui(selected_gr_lines_df, new_transactions_date)
            else:
                st.error("You have to select at least one transaction")

@st.dialog(title="Confirm transactions", width="large")
def confirm_multiple_transactions_ui(selected_gr_lines_df: pd.DataFrame, gr_date: Date):
    
    # Aviso en forma de quote
    st.subheader(f"{gr_date} Transactions")
    st.dataframe(
        data = selected_gr_lines_df,
        hide_index = True,
        use_container_width = True
    )

    # Confirmación
    confirm_button = st.button(
        label = "Yes, make transactions",
        use_container_width = True
    )
    
    if confirm_button:
        if save_gr_lines_data(selected_gr_lines_df, gr_date):
            st.session_state["gr_file_uploader_key"] += 1 # Nuevo file uploader para no mostrar la informacion en pantalla del archivo subido
            rerun_with_success("Transactions completed successfully")
        else:
            rerun_with_error("An error occurred while importing the transactions")

make_multiple_transactions_ui()