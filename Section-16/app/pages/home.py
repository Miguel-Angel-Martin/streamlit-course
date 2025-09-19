import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from config.supabase import supabase_config

supabase = supabase_config()

cookies = EncryptedCookieManager(
    prefix="supabot",
    password=st.secrets["client"]["COOKIES_PASSWORD"]
)

if not cookies.ready():
    st.write("Starting cookie manager... reload the page if its not starts.")
    st.spinner()
    st.stop()

session_id = cookies.get("session")
if not session_id:
  st.warning("Please login to continue")
  st.switch_page("main.py")
  st.stop()


st.subheader(f"Welcome {session_id}")
with st.sidebar:
    if st.button("Logout", icon=":material/exit_to_app:", type="tertiary"):
        try:
            response = supabase.auth.sign_out()
        except Exception as e:
            st.error(f"Error logging out supabase: {e}")
        try:
            del cookies['a-session']
            st.switch_page("main.py")
        except Exception as e:
            st.error(f"Error logging out cookies: {e}")

    
