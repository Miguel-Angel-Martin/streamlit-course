import streamlit as st

from config.supabase import supabase_config
from datetime import datetime, timedelta
import time
supabase = supabase_config()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
    

st.subheader(f"Welcome {st.session_state.user_email}")
with st.sidebar:
    if st.button("Logout", icon=":material/exit_to_app:", type="tertiary"):
      try:
        # Cerrar sesión en Supabase
        response = supabase.auth.sign_out()
      except Exception as e:
        st.error(f"Error logging out supabase: {e}")
          
      # Limpiar session state
      st.session_state.authenticated = False
      st.session_state.user_email = None
      
      # Limpiar cachés
      st.cache_data.clear()
      st.cache_resource.clear()
      
      # Mostrar mensaje y redirigir
      st.success("Logout successful!")
      st.switch_page("main.py")

    
