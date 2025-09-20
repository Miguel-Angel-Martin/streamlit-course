import streamlit as st
from config.supabase import supabase_config
import re

st.set_page_config("SupaBot Gemini", page_icon=":material/robot_2:", layout="wide")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
    
if st.session_state.authenticated:
    st.success(f"Already logged in as {st.session_state.user_email}")
    if st.button("Go to Dashboard"):
        st.switch_page("dashboard.py")  # o tu página principal
    st.stop()
    
    
def check_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


st.markdown("<center><h1>Supabot: Supabse and Genimi AI</h1></center>", unsafe_allow_html=True)
_, col, _ = st.columns([3,3,3])

with col:
    with st.container(border=True):
        supabase = supabase_config()
        st.subheader("Sign In")
        email = st.text_input("email", placeholder="user email", autocomplete="off")
        password = st.text_input("password", placeholder="user password", type="password")
        c1, c2, c3 = st.columns([2,1,2])
        with c1:
            submit = st.button("Login", icon=":material/send:", type="primary")
        if submit:
            if check_email(email):
              try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                if response.user.id:
                  user_id = response.user.id                  
                  st.session_state.authenticated = True
                  st.session_state.user_email = email
                  st.success("Login successful!")
                  st.switch_page("pages/home.py") 
                elif response.error:
                  st.error(f"Login error: {response.error}")
                else:
                  st.error(f"Error creating account: {response}")
              except Exception as e:
                st.error(f"Login error: {e}")
            else:
                st.error("Invalid email")
        with c3:
          if st.button("Register", icon=":material/person_add:", type="tertiary"):
                st.switch_page("pages/register.py")

