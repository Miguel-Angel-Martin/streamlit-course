import streamlit as st
from config.supabase import supabase_config
import re

def check_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


st.markdown("<center><h1>Supabot: Supabse and Genimi AI</h1></center>", unsafe_allow_html=True)

_, col, _ = st.columns([3,3,3])

with col:
    with st.form("Register", clear_on_submit=True):
        supabase = supabase_config()
        st.subheader("Create Account")
        user = st.text_input("user", placeholder="user name", autocomplete="off")
        email = st.text_input("email", placeholder="user email", autocomplete="off")
        password = st.text_input("password", placeholder="user password", type="password")
        c1, c2, c3 = st.columns([2,1,2])
        with c2:
            submit = st.form_submit_button("Register", icon=":material/send:", type="primary")
        if submit:
            if check_email(email):
              try:
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                if response.user.id:
                  user_id = response.user.id
                  data = {"id": user_id, "user": user, "email": response.user.email}
                  supabase.table("users").insert(data).execute()
                  st.success("Account created successfully! Please check your email to verify your account.")
                  st.switch_page("main.py")
                else:
                  st.error(f"Error creating account: {response}")
              except Exception as e:
                st.error(f"Login error: {e}")
            else:
                st.error("Invalid email")

        