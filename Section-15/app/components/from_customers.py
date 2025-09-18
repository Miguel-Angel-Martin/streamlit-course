import streamlit as st
from models.customer_model import CustomerModel
from datetime import date

def form_customers(id):
    st.write("Customers form.")
    ssf = st.session_state
    if "id" not in ssf:
        ssf.id=id
        ssf.name=""
        ssf.surname=""
        ssf.telephone=""
        ssf.project=""
        ssf.date=""
    item= CustomerModel.get_customer_by_id(id) if id else None
    
    with st.container(border=True):
        cc1, cc2, cc3, cc4 = st.columns(4)
        name = cc1.text_input("Name", autocomplete="off", key="name", value=item.get('name', '') if item else "")
        surname = cc2.text_input("Surname", autocomplete="off", key="surname", value=item.get('surname', '') if item else "")
        telephone = cc3.text_input("Telephone", autocomplete="off", key="telephone", value=item.get('telephone', '') if item else "")
        date_input = cc4.date_input("Date", key="date", value=item.get('date', date.today()) if item else date.today())
        project = st.text_area("Project", key="project",value=item.get('project', '') if item else "")

    def save():
        if name:
            CustomerModel.create_customer(name, surname, telephone, project, date_input)
            ssf.name=""
            ssf.surname=""
            ssf.telephone=""
            ssf.project=""
            ssf.date=date.today()
            st.toast("Customer saved.")
        else:
            st.warning("Customer name is required.")
            
    def edit():
        CustomerModel.update_customer(id, name, surname, telephone, project, date_input)
        ssf.id=""
        st.toast("Customer updated.")
    
    def delete(id):
        CustomerModel.delete_customer(id)
        ssf.id=""
        st.toast("Customer deleted.")
        st.rerun()
        
    def cancel():
        ssf.id=""
        ssf.name=""
        ssf.surname=""
        ssf.telephone=""
        ssf.project=""
        ssf.date=date.today()
    
    
    if id:
        b1,b2,b3,b4 = st.columns([1,1,1,5])
        with b1:
            b1.button("Edit", on_click=edit)
        with b2:
            b2.button("Cancel", on_click=cancel)
        with b3:
            toggle = b3.toggle("Delete")
            if toggle:
                b4.button("Delete", on_click=delete)
    else:
        st.button("Save", on_click=save)