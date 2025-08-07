import streamlit as st
import pandas as pd
st.set_page_config(page_title="Section 08: Streamlit App", layout="wide", page_icon=":rocket:")

st.title("Section 08: Streamlit App Custom Menu")
st.sidebar.header("Your Sidebar Header")  # This will be above any widgets you manually add
pages = {
            "Customer Menu": [
                st.Page("./customer/decrement-increment.py", title="Decrement/Increment",icon=":material/cached:"),
                st.Page("./customer/buttoms.py", title="Buttoms",icon=":material/radio_button_checked:"),            
            ],
            "Supplier Menu": [
                st.Page("./supplier/forms.py", title="Forms",icon=":material/dynamic_form:"),
            ],
            "Parameters Menu": [
                st.Page("./parameters/parameters.py", title="Parameters",icon=":material/settings:"),
                st.Page("./parameters/parameters1.py", title="Parameters 1",icon=":material/settings_applications:"),
            ],
        }      

pg= st.navigation(pages, position="sidebar", expanded=True)
pg.run()
