import streamlit as st
from models.customer_model import CustomerModel

@st.cache_data(ttl=60)
def fetch_all_customers():
    return CustomerModel.get_all_customers()

def add_customers():
    st.title("Add customers")
    ss = st.session_state
    if "customers" not in ss:
        ss["customers"] = None
    
    ss.customers = fetch_all_customers()
    
    if ss.customers is not None and not ss.customers.empty:
        for _, item in ss.customers.iterrows():
            with st.container(border=True):
                cc1, cc2, cc3, cc4, cc5, cc6, cc7 = st.columns(7)
                with cc1: st.write(item['customer_id'])
                with cc2: st.write(item['name'])
                with cc3: st.write(item['surname'])
                with cc4: st.write(item['telephone'])
                with cc5: st.write(item['project'])
                with cc6: st.write(item['date'])
                with cc7: st.button("edit / delete", key=item['customer_id'])
    else:
        st.caption("No customers found in the database.")
