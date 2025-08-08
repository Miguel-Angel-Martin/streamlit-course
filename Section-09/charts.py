import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def plot_bar_chart(data, title, color="blue",x_label="x_label", y_label="y_label"):
    start, end = st.slider("Range", 0, len(data)-1, (0, min(10, len(data)-1)))

    # Filtrar datos
    filtered_data = data.iloc[start:end+1]
    # Crear figura y ejes
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(filtered_data.index, filtered_data.values, color=color )
            
    # Añadir etiquetas encima de las barras
    ax.bar_label(bars, label_type='edge', padding=3)    
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xticks(range(len(filtered_data.index)))
    ax.set_xticklabels(filtered_data.index, rotation=45)    
    st.pyplot(fig)
def charts():
    st.title("Charts")
    file = st.file_uploader("Upload a CSV file", type=["csv"])
    if file is not None:
        df = pd.read_csv(file)
        st.subheader("Data Preview")
        st.write(f"Displaying {len(df)} rows and {len(df.columns)} columns")
        if 'color' in df.columns:
            st.subheader("Car count by color")
            color_counts = df['color'].value_counts()
            plot_bar_chart(color_counts, "Car Count by Color", color="green", x_label="Color", y_label="Count")
        else:
            st.warning("La columna color no está presente en el archivo.")
            
        if 'model' in df.columns:
            st.subheader("Car count by models")
            model_counts = df['model'].value_counts().sort_index()
            plot_bar_chart(model_counts, "Car Count by Model", color="orange", x_label="Model", y_label="Count")     
        else:
            st.warning("La columna model no está presente en el archivo.")
        
        if 'year' in df.columns:
            st.subheader("Car count by year (Pie)")
            plt.figure()
            car = st.selectbox("Select a car", df['car'].unique())
            car_data = df[df['car'] == car]
            car_counts = car_data['model'].value_counts().sort_index()
            car_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            plt.title(f"Car Count by model for {car} ({car_data.shape[0]} cars)")
            plt.ylabel("")
            st.pyplot(plt)
            
            
    else:
        st.write("Please upload a CSV file to display its contents.")
        

