import streamlit as st
import pandas as pd

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import get_all_PO_quantities_to_update
from lib.streamlit_common import update_quantities_to_receive
from lib.streamlit_common import rerun_with_success
from lib.streamlit_common import rerun_with_error

# ----- Initialization -----
PAGE_NAME = "Inventory_2_Update_Materials"
common_page_initialization(F"{PAGE_NAME}.py")

# ----- Interfaz -----

def inventory_update_materials_default_ui():

    st.subheader("🔄 Update materials", help=(
        "From here, you can upload a PO file to update the total ordered quantity of the materials.\n\n"
        " - ONLY materials that are already registered will be updated.\n\n"
        " - Other entries in the file will be ignored.\n\n"
    ))

    # Key del file uploader
    if "po_file_uploader_key" not in st.session_state:
        st.session_state["po_file_uploader_key"] = 0

    # Ficheros del file uploader con la key subidos
    if "po_uploaded_files" not in st.session_state:
        st.session_state["po_uploaded_files"] = []

    # Opcion de subir un fichero para realizar multiples actualizaciones de cantidades a recibir
    uploaderFilesPO = st.file_uploader(
        label = "Add PO file to update the quantities to receive of a group of materials",
        type = ["htm"],
        key = st.session_state["po_file_uploader_key"],
    )

    st.divider()

    # Si se sube un ficehro
    if uploaderFilesPO is not None:
        try:
            # Comprobar si el fichero es adecuado
            file_name = uploaderFilesPO.name
            if "PO" not in file_name:
                st.error("The filename needs to contain 'PO'.")
            else:
                file_content = uploaderFilesPO.read()
                # Leer todos los datagramas del fichero
                dataframes = pd.read_html(file_content)
                # Mostrar interfaz para actualizar cantidades
                inventory_update_materials_ui(dataframes)

        except Exception as e:
            st.error(f"File processing error: {e}")
            
# Interfaz para actualizar las cantidades pensdientes de un material
def inventory_update_materials_ui(dataframes: list[pd.DataFrame]):
    
    materials_to_update = get_all_PO_quantities_to_update(dataframes)

    if materials_to_update.empty:
        no_results_message("There are no entries in the file that match with the registered materials")
    else:
        
        st.subheader("Update quantities to receive", help=(
            "This table shows the materials to be updated.\n\n"
            "- Only pending quantities to receive will be updated.\n"
            "- The pending quantity will be replaced with the value shown in the table below after the update.\n"
            "- No other material data will be modified."
        ))

        st.dataframe(
            data = materials_to_update,
            hide_index = True,
            use_container_width = True,
            height = 390
        )
        
        confirm_updates_button = st.button(
            label = "Confirm Updates"
        )
        
        if confirm_updates_button:
            confirm_updates_ui(materials_to_update)

@st.dialog(title = "Confirm updates", width = "large")
def confirm_updates_ui(materials_to_update):
    st.write("Are you sure you want no upload the materials with te following data?")
    
    st.dataframe(
        data = materials_to_update,
        hide_index = True,
        use_container_width = True,
        height = 300
    )
    
    confirm_updates_button = st.button(
        label = "Yes, update materials",
        use_container_width = True
    )
    
    if confirm_updates_button:
        if update_quantities_to_receive(materials_to_update):
            st.session_state["po_file_uploader_key"] += 1 # Nuevo file uploader para no mostrar la informacion en pantalla del archivo subido
            rerun_with_success("Update completed successfully")
        else:
            rerun_with_error("An error occurred while updating the materials")

inventory_update_materials_default_ui()