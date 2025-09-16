import streamlit as st

def form_customers():
    st.write("Customers form.")
    ssf = st.session_state
    ssf.id=id
    ssf.name=""
    ssf.surname=""
    ssf.telephone=""
    ssf.project=""
    ssf.date=""
    
    with st.container(border=True):
        cc1, cc2, cc3, cc4 = st.columns(3)
        name = cc1.text_input("Name", autocomplete="off", key="customer")
        surname = cc2.text_input("Surname", autocomplete="off", key="surname")
        telephone = cc3.text_input("Telephone", autocomplete="off", key="telephone")
        date = cc4.date_input("Date", key="date")
        project = st.text_area("Project", autocomplete="off", key="project")
        
    def save():
        if name:
            ssf.name=""
            ssf.surname=""
            ssf.telephone=""
            ssf.project=""
            ssf.date=date.today()
        else:
            st.warning("Customer name is required.")
                
        if id:
            pass
        else:
            st.button("Save", on_click=save)