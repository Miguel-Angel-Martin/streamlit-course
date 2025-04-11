import streamlit as st
import pandas as pd

from lib.streamlit_common import common_page_initialization
from lib.streamlit_common import no_results_message
from lib.streamlit_common import rerun_with_success
from lib.streamlit_common import rerun_with_error
from lib.streamlit_common import add_keyword
from lib.streamlit_common import remove_keyword
from lib.streamlit_common import update_user_role

from lib.queries import get_keywords_values
from lib.queries import get_all_users

from lib.types import UserRole

# ----- Initialization -----
PAGE_NAME = "Settings"
common_page_initialization(f"{PAGE_NAME}.py")

# ----- Interfaz -----
        
def settings_default_ui():

    st.subheader("🧰 Settings", help=(
        "From here, you can view all users who are admins, as well as the keywords used to filter GR files "
        "in the 'Document Header Text' field.\n\n"
        "- You can type a new keyword and click the 'Add keyword' button to add it.\n"
        "- You can also select an existing keyword and click 'Remove keyword' to remove it."
    ))


    col1, col2 = st.columns([1, 1])

    with col1:
        # Mostrar las palabras clave en un filtro (lista)
        st.write("##### List of Keywords")
        keywords_df = get_keywords_values()

        keywords_df = keywords_df.sort_values(by='Value', ascending=True)
        keyword_list = keywords_df['Value'].tolist()

        if keywords_df.empty:
            st.warning("No keywords")
        else:
            st.dataframe(
                data = keywords_df,
                hide_index = True,
                use_container_width = True,
                height = 384
            )

        col3, col4 = st.columns([1, 1])
        with col3:
            keyword = st.text_input(
                label = "Write a new keyword:"
            )

            add_keyword_button = st.button(
                label = "Add keyword",
                use_container_width = True,
                disabled = (keyword == '')
            )

            if add_keyword_button and keyword != '':
                if add_keyword(keyword):
                    rerun_with_success(f"Keyword '{keyword}' saved")
                else:
                    rerun_with_error(f"Keyword '{keyword}' already exists")

        with col4:
            selected_keyword = st.selectbox(
                options = keyword_list,
                label = "Select a keyword to remove:"
            )

            remove_keyword_button = st.button(
                label = "Remove keyword",
                use_container_width = True,
                disabled = (keywords_df.empty)
            )

            if remove_keyword_button and selected_keyword:
                if remove_keyword(selected_keyword):
                    rerun_with_success(f"Keyword '{selected_keyword}' removed")
                else:
                    rerun_with_error(f"Keyword '{selected_keyword}' does not exist")

    with col2:
        # Filtrar la tabla de usuarios para mostrar solo aquellos con rol 'admin'
        users_df = get_all_users()
        columns_to_show = ["UserKey", "Email", "Role"]

        st.write("##### Users")
        if users_df.empty:
            no_results_message("No users")
        else:
            users_df = users_df[columns_to_show]
            selected_user = st.dataframe(
                data = users_df,
                hide_index = True,
                use_container_width = True,
                on_select = "rerun",
                selection_mode = "single-row",
                height = 384
            )

            selected_index = selected_user.selection.rows
            if selected_index:
                selected_row = users_df.iloc[selected_index[0]]
                user = str(selected_row['UserKey'])
                email = str(selected_row['Email'])
                role = str(selected_row['Role'])
                
                available_roles = [role.value for role in UserRole]

                if st.session_state.user['email'] == email:
                    available_roles.remove(UserRole.REQUESTER.value)
                available_roles.remove(role)
                    
                selected_role = st.selectbox(
                    label = f"Select new role for '{user}' ({email})",
                    options = available_roles
                )

                change_role_button = st.button(
                    label = "Change rol",
                    use_container_width = True
                )

                if change_role_button:
                    if update_user_role(user, selected_role):
                        rerun_with_success(f"User '{user}' changed role to {selected_role}")
                    else:
                        rerun_with_error(f"There was a problem trying to change the rol of '{user}' to {selected_role}")



settings_default_ui()
