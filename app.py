import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Análisis Exploratorio de Datos",
    page_icon="📊",
    layout="wide"
)

# --- TÍTULO Y DESCRIPCIÓN ---
st.title("📊 Análisis Exploratorio de Datos (EDA)")
st.write("Esta aplicación genera datos aleatorios y realiza un análisis exploratorio básico con visualizaciones interactivas.")

# --- GENERACIÓN DE DATOS ---
# Usamos un caché para que los datos no se regeneren en cada interacción
@st.cache_data
def generar_datos():
    """Genera un DataFrame con datos aleatorios para el análisis."""
    np.random.seed(42) # Semilla para reproducibilidad
    fechas = pd.date_range(start="2023-01-01", periods=100, freq='D')
    categorias = ['A', 'B', 'C', 'D']
    
    data = {
        'Fecha': fechas,
        'Categoría': np.random.choice(categorias, size=100),
        'Ventas': np.random.randint(50, 500, size=100),
        'Visitantes': np.random.uniform(100, 1000, size=100).astype(int),
        'Tasa_Conversion': np.random.uniform(0.01, 0.1, size=100)
    }
    df = pd.DataFrame(data)
    return df

df = generar_datos()

# --- MOSTRAR DATOS CRUDOS Y ESTADÍSTICAS ---
st.header("1. Vista de los Datos")

# Expander para no ocupar mucho espacio
with st.expander("Ver tabla de datos completos"):
    st.dataframe(df)

st.subheader("Estadísticas Descriptivas")
st.write("Resumen estadístico de las columnas numéricas:")
st.write(df.describe())


# --- VISUALIZACIONES ---
st.header("2. Visualizaciones Interactivas")
st.write("Explora los datos a través de los siguientes gráficos.")

# Dividir el layout en dos columnas
col1, col2 = st.columns(2)

with col1:
    # --- GRÁFICO DE BARRAS ---
    st.subheader("📈 Total de Ventas por Categoría")
    
    # Agrupar datos para el gráfico
    ventas_por_categoria = df.groupby('Categoría')['Ventas'].sum().reset_index()
    
    # Crear la figura con Plotly Express
    fig_barras = px.bar(
        ventas_por_categoria,
        x='Categoría',
        y='Ventas',
        title='Suma de Ventas Totales por Categoría',
        labels={'Ventas': 'Total de Ventas ($)', 'Categoría': 'Categoría de Producto'},
        color='Categoría',
        template='plotly_white'
    )
    
    # Actualizar el layout para un mejor aspecto
    fig_barras.update_layout(
        xaxis_title="Categoría",
        yaxis_title="Total de Ventas ($)",
        showlegend=False
    )
    
    st.plotly_chart(fig_barras, use_container_width=True)

with col2:
    # --- GRÁFICO DE LÍNEAS ---
    st.subheader("📉 Evolución de Visitantes en el Tiempo")
    
    # Crear la figura con Plotly Express
    fig_lineas = px.line(
        df,
        x='Fecha',
        y='Visitantes',
        title='Número de Visitantes Diarios',
        labels={'Visitantes': 'Número de Visitantes', 'Fecha': 'Fecha'},
        template='plotly_white'
    )
    
    # Actualizar el layout
    fig_lineas.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Número de Visitantes"
    )
    
    st.plotly_chart(fig_lineas, use_container_width=True)

st.info("💡 Consejo: Puedes hacer clic y arrastrar en los gráficos para hacer zoom y pasar el cursor sobre los puntos para ver los valores exactos.")
