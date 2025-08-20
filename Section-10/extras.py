import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards

# Header coloreado
colored_header(
    label="Section 10",
    description="Streamlit Extras",
    color_name="red-70"
)

# Métricas normales de Streamlit
col1, col2 = st.columns(2)
with col1:
    st.metric("Temperature", "70 °F", "1.2 °F")
with col2:
    st.metric("Humidity", "86%", "4%")

# Aplica estilos de "cards" a todas las métricas de la página
style_metric_cards()


# Métricas nativas de Streamlit
st.metric("Temperature", "70 °F", "1.2 °F")
st.metric("Humidity", "86%", "4%")

