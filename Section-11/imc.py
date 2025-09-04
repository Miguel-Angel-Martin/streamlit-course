import streamlit as st
import pandas as pd
def imc():
    st.subheader("Índice de masa corporal")
    st.latex(r"\text{imc}=\frac{\text{Peso (kg)}}{\text{Altura (m)}^2}")
    st.markdown("**Tabla del IMC según la OMS**")
    
    datos_imc= {
        "Categoria": [
            "Peso insuficiente",
            "Peso normal",
            "Sobrepeso",
            "Obesidad grado 1",
            "Obesidad grado 2",
            "Obesidad grado 3 (morbida)"
        ],
        "Min": [0, 18.5, 25, 30, 35, 40],
        "Max": [18.5, 24.9, 29.9, 34.9, 39.9, 100]
    }
    tabla_imc = pd.DataFrame({
        "Categoría": datos_imc["Categoria"],
        "Rango IMC": [f"{min} - {max}" for min, max in zip(datos_imc["Min"], datos_imc["Max"])]
    })
    st.table(tabla_imc)
    
    c1, c2 = st.columns(2)
    peso = c1.number_input("Peso")
    altura =c2.number_input("Altura")
    def obtener_categoria(imc_valor):
        for categoria, min_val, max_val in zip(datos_imc["Categoria"], datos_imc["Min"], datos_imc["Max"]):
            if min_val <= imc_valor < max_val:
                return categoria
        return "Fuera de rango"
    def imc_calc(peso, altura):
        if altura <= 0 or peso <= 0:
            return None, "La altura y el peso deben ser mayores a cero."
        else:
            imc_res = peso / (altura ** 2)
            return imc_res, f"Tu IMC es: {imc_res:.2f}"
        
    if st.button("Calcular", type="primary"):
        imc_valor, mensaje = imc_calc(peso, altura)
        st.title(f":green[{mensaje}]")
        if imc_valor:
            categoria = obtener_categoria(imc_valor)
            st.subheader(f"Categoría según la OMS: :orange[{categoria}]")