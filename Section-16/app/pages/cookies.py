import streamlit as st
from streamlitextras.cookiemanager import get_cookie_manager
from datetime import datetime, timedelta

# Inicializar CookieManager
cookie_manager = get_cookie_manager()
cookie_manager.delayed_init()  # Asegura que CookieManager se mantenga en st.session_state

# Título de la aplicación
st.title("Gestión Avanzada de Cookies con CookieManager")

# Mostrar todas las cookies almacenadas
st.subheader("Todas las cookies:")
cookies = cookie_manager.get_all()
st.write(cookies)

# Entrada de texto para el nombre y valor de la cookie
cookie_name = st.text_input("Nombre de la cookie", "mi_cookie")
cookie_value = st.text_input("Valor de la cookie", "valor_inicial")

# Configuración avanzada de la cookie
expires_at = st.date_input("Fecha de expiración", datetime.now() + timedelta(days=1))
secure = st.checkbox("Secure (HTTPS)")
path = st.text_input("Ruta de la cookie", "/")
same_site = st.selectbox("SameSite", ["strict", "lax", "none"])

# Botones para establecer, obtener y eliminar cookies
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Establecer cookie"):
        cookie_manager.set(
            cookie_name,
            cookie_value,
            expires_at=datetime.combine(expires_at, datetime.min.time()),
            secure=secure,
            path=path,
            same_site=same_site,
        )
        st.success(f"Cookie '{cookie_name}' establecida.")
        st.rerun() 
with col2:
    if st.button("Obtener cookie"):
        value = cookie_manager.get(cookie_name)
        if value:
            st.info(f"Valor de '{cookie_name}': {value}")
        else:
            st.warning(f"No se encontró la cookie '{cookie_name}'.")

with col3:
    if st.button("Eliminar cookie"):
        cookie_manager.delete(cookie_name)
        st.warning(f"Cookie '{cookie_name}' eliminada.")

# Mostrar el valor actual de la cookie
st.subheader(f"Valor actual de '{cookie_name}':")
st.write(cookie_manager.get(cookie_name))
