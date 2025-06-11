import streamlit as st

st.title("Widgets")

st.subheader("Select-box")

opcion = st.selectbox("Escoge un color", ["Rojo","Amarillo","Verde","Azul"])
st.write(opcion)
st.subheader("Multiselect")
options = st.multiselect(
    "Elige varias opciones",
    ["Rojo","Amarillo","Verde","Azul"]
)
st.write(options)

st.subheader("Radio")
radio = st.radio(
    "Elige una opcion",
    ["Rojo","Amarillo","Verde","Azul"],
    captions= [
        "Opcion 1",
        "Opcion 2",
        "Opcion 3",
        "Opcion 4",
    ]
)

st.subheader("Checkbox, toggle y status")

acepto = st.checkbox("Aceptar terminos y condiciones de uso")
if acepto:
    st.success("Terminos aceptados", icon="✅")

rechazo = st.toggle("No acepto los terminos")
if rechazo:
    st.error("No acepto", icon="❌")

st.subheader("Colorpicker")
color = st.color_picker("Escoge un color","#c021d6")
st.write(color)

st.subheader("Sliders")
edad = st.slider("Cual es tu edad?", 0,120,18)
st.write("Tu edad es: ", edad)

rango = st.slider("Rango", value=(100, 200))
st.write(rango)


color_slider = st.select_slider(
    "Seleciona tu color",
    options= [
        "Rojo",
        "Amarillo",
        "Azul",
        "Rosa"
    ]
)
st.write("Tu color ", color_slider)