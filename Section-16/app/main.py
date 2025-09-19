import streamlit as st
from config.supabase import supabase_config
from streamlit_cookies_manager import EncryptedCookieManager

import re
def check_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None



st.set_page_config("SupaBot Gemini", page_icon=":material/robot_2:", layout="wide")
cookies = EncryptedCookieManager(
    prefix="supabot",
    password=st.secrets["client"]["COOKIES_PASSWORD"]
)


session_id = cookies.get("session")
if "just_logged_in" in st.session_state and st.session_state.just_logged_in:
    st.session_state.just_logged_in = False
    st.switch_page("pages/home.py")

session_id = cookies.get("session")
if session_id and "just_logged_in" not in st.session_state:
    st.switch_page("pages/home.py")


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
                  cookies["session"]= user_id
                  st.session_state.just_logged_in = True
                  cookies.save()
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
        st.warning(session_id)
