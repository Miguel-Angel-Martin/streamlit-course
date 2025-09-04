import streamlit as st
def conversor():
    st.subheader("Conversor de unidades")
    
    def conversor_unidades(valor, origen, destino):
        conversion_unidades={
            "milimetros": 0.1,
            "centimetros": 1,
            "metros": 100,
            "Kilómetros": 100000            
        }
        valor_centimetros = valor * conversion_unidades[origen]
        result = valor_centimetros / conversion_unidades[destino]
        return result
    unidades = [
        "milimetros", 
        "centimetros",
        "metros",
        "Kilómetros"
    ]
    col1, col2, col3 = st.columns(3)
    valor = col1.number_input("Introduce el valor a convertir", min_value=0.0, value=1.0)
    origen = col2.selectbox("unidades de origen", options=unidades)
    destino = col3.selectbox("unidades de destino", options=unidades)
    
    if st.button("Convertir"):
        result = conversor_unidades(valor, origen, destino)
        st.subheader(f"{valor} {origen} son equivalentes a {result} {destino}")
        
        