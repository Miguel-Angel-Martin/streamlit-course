import streamlit as st
import pandas as pd

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import filter_dataframe
from lib.streamlit_common import change_id_of_vendors_by_name
from lib.streamlit_common import save_request
from lib.streamlit_common import rerun_with_success
from lib.streamlit_common import rerun_with_error

from lib.queries import get_all_projects_with_available_materials
from lib.queries import get_project_by_name
from lib.queries import get_project_by_manager
from lib.queries import get_available_materials_from_project_id
from lib.queries import get_warehouse_by_id

from lib.types import RequestType

# ----- Initialization -----
PAGE_NAME = "Request_3_Make_Request"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----

# Interfaz para crear una request
def make_request_ui():
    st.subheader("🛒 Make Request", help = (
        "From here, you can create a request for multiple materials.\n\n"
        "A request can only be made for one project.\n\n"
        "To make a request:\n\n"
        " - Select the project that you want to make the request, and the available materials (with stock) for that project will be shown\n"
        " - For each material, indicate the quantity you want to request\n"
        " - Once you have selected all the materials you want to request, click the 'Make request' button and confirm the request\n"
    ))

    col1, col2 = st.columns([1,5])
    
    # Obtener proyectos con materiales disponibles
    projects_with_available_materials = get_all_projects_with_available_materials()
    
    project_ids_with_available_materials = projects_with_available_materials['Project_Id'].tolist()
    project_names_with_available_materials = projects_with_available_materials['Name'].tolist()
    project_names_with_available_materials = [i for i in project_names_with_available_materials if i != None]
    project_managers_with_available_materials = projects_with_available_materials['Manager'].tolist()
    project_managers_with_available_materials = [i for i in project_managers_with_available_materials if i != None]

    with col1:
        selected_filter = st.selectbox(
            label = "Search project by...",
            options = ['Id','Name','Manager']
        )
    
    with col2:
        if selected_filter == 'Id':
            selected_project_id = st.selectbox(
                label = "Project Id",
                options = project_ids_with_available_materials
            )

        if selected_filter == 'Name':
            selected_project_name = st.selectbox(
                label = "Project name",
                options = project_names_with_available_materials
            )
            selected_project_id = get_project_by_name(selected_project_name).at[0, 'Id']

        if selected_filter == 'Manager':

            col3, col4 = st.columns([1,1])

            with col3:
                selected_project_manager = st.selectbox(
                    label = "Project manager",
                    options = project_managers_with_available_materials
                )

            projects_of_manager = get_project_by_manager(selected_project_manager)

            filtered_projects = projects_of_manager[projects_of_manager['Id'].isin(projects_with_available_materials['Project_Id'])]
            
            with col4:
                selected_project_id = st.selectbox(
                    label="Select Project",
                    options=filtered_projects['Id'].tolist()
                )

    selected_warehouse_id = 1
    
    available_materials_df = get_available_materials_from_project_id(selected_project_id)

    if(available_materials_df.empty):
        no_results_message("There are not available materials at the moment")
    else:
        st.write("**Available materials**")

        columns_to_show = ["PO_PO_Item", "Stock", "Vendor_Number", "Short_Description", "Long_Text", "Project_Id", "WBS"]
        available_materials_df = available_materials_df[columns_to_show]

        available_materials_df = change_id_of_vendors_by_name(available_materials_df)
        available_materials_df = available_materials_df.rename(columns = {
            "PO_PO_Item": "PO.PO Item",
            "Vendor_Number": "Vendor",
            "Short_Description": "Short description",
            "Long_Text": "Long description",
            "Project_Id": "Project Id",
        })

        filtered_available_materials_df = filter_dataframe(available_materials_df, "Available materials")

        selected_materials_df = st.dataframe(
            filtered_available_materials_df,
            height = 310,
            use_container_width = True,
            hide_index = True,
            on_select = "rerun",
            selection_mode = "multi-row"
        )

        # Solicitar cantidades
        for selected_index in selected_materials_df.selection.rows:
            selected_row = filtered_available_materials_df.iloc[selected_index]
            material_part_1 = selected_row['Short description']
            material_part_2 = selected_row['Long description']
            material_name = selected_row['PO.PO Item']

            display_text = []
            if pd.notna(material_part_1):
                display_text.append(material_part_1)
            if pd.notna(material_part_2):
                display_text.append(material_part_2)
            if pd.notna(material_name):
                display_text.append(f"({material_name})")
            display_text_str = " ".join(display_text)
            
            col1, col2, col3 = st.columns([2, 1, 4])

            with col1:
                st.markdown(
                    f"<div style='text-align: left; padding-top: 35px;'>{display_text_str}</div>", 
                    unsafe_allow_html=True
                )

            with col2:
                st.number_input(
                    label = " ",
                    key = f"quantity_{selected_index}",
                    min_value = 1,
                    max_value = int(selected_row['Stock']),
                    value = int(selected_row['Stock'])
                )

        st.divider()

        # Tipo de request
        is_total_selected = st.checkbox(
            "If there are not enough materials, deliver only the available ones"
        )

        selected_type_of_request = RequestType.PARTIAL.value if is_total_selected else RequestType.TOTAL.value

        warehouse_notes_text = st.text_area(
            label = "Warehouse Notes",
            height = 150
        )

        make_request = st.button(
            label = "Make request",
        )

        if make_request:
            request_data = {
                'selected_project_id': selected_project_id,
                'selected_warehouse_id': selected_warehouse_id,
                'selected_type_of_request': selected_type_of_request,
                'available_materials_df': filtered_available_materials_df,
                'selected_materials_df': selected_materials_df,
                'materials_quantities': [st.session_state[f"quantity_{selected_index}"] for selected_index in selected_materials_df.selection.rows],
                'end_user': None,
                'warehouse_notes': warehouse_notes_text
            }

            if len(selected_materials_df.selection.rows) == 0:
                st.error("You need to select at least 1 material to make a request.")
            else:
                confirm_request_ui(request_data)

@st.dialog(title="Confirm your request", width="large")
def confirm_request_ui(request_data: dict):
    # Información del proyecto y almacen
    st.write(f"**Project ID:** {request_data['selected_project_id']}")
    warehouse_id = request_data['selected_warehouse_id']
    warehouse_name = get_warehouse_by_id(warehouse_id)['Name'].tolist()[0]
    st.write(f"**Warehouse:** {warehouse_name}")

    # Materiales seleccionados y cantidades
    st.write("**Materials to be requested:**")
    i = 0
    for index in request_data['selected_materials_df'].selection.rows:
        selected_row = request_data['available_materials_df'].iloc[index]
        material_part_1 = selected_row['Short description']
        material_part_2 = selected_row['Long description']
        material_name = selected_row['PO.PO Item']
        
        quantity = request_data['materials_quantities'][i]

        display_text = []
        if pd.notna(material_part_1):
            display_text.append(material_part_1)
        if pd.notna(material_part_2):
            display_text.append(material_part_2)
        if pd.notna(material_name):
            display_text.append(f"({material_name})")

        display_text_str = " ".join(display_text)
        st.write(f"- {display_text_str}: **{quantity}** units")
        i += 1
    
    # Tipo
    if request_data['selected_type_of_request'] == RequestType.TOTAL.value:
        st.write("**Treatment:** When the request is accepted, deliver all materials, or the request cannot be accepted.")
    else:
        st.write("**Treatment:** When the request is accepted, deliver only the available materials")

    # Notas almacen
    st.write(f"**Warehouse Notes:** {request_data['warehouse_notes']}")

    confirm_request_button = st.button(
        label = "Confirm request",
        use_container_width = True
    )

    if confirm_request_button:
        if save_request(request_data):
            rerun_with_success("Request created successfully")
        else:
            rerun_with_error("An error occurred while creating the request")

# Formulario para solicitar una request
make_request_ui()
