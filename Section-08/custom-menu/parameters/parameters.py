import streamlit as st

st.title("Parameters Section")

if st.button("Parameters1"):
    st.switch_page("parameters/parameters1.py")
st.write("This section demonstrates how to use parameters in Streamlit.")

sendId= st.text_input("Send ID", placeholder="Enter ID to send")

submit = st.button("Submit ID")
if submit:
    st.write(f"ID {sendId} submitted successfully!")
    st.session_state.sendId = sendId
    st.switch_page("parameters/parameters1.py")