import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Salud Interactivo",
    page_icon="🩺",
    layout="wide"
)

# --- TÍTULO PRINCIPAL ---
st.title("🩺 Dashboard Interactivo de Datos de Salud")
st.markdown("Utiliza los filtros en la barra lateral para explorar los datos de los pacientes.")

# --- GENERACIÓN DE DATOS ---
@st.cache_data
def generar_datos(n_records=1000):
    """Genera un DataFrame con datos de salud aleatorios."""
    np.random.seed(42) # Semilla para reproducibilidad
    ciudades = ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena']
    generos = ['Masculino', 'Femenino']
    
    data = {
        'Edad': np.random.randint(18, 85, size=n_records),
        'Genero': np.random.choice(generos, size=n_records),
        'Ciudad': np.random.choice(ciudades, size=n_records),
        'Presion_Sistolica': np.random.randint(90, 180, size=n_records),
        'Presion_Diastolica': np.random.randint(60, 110, size=n_records),
        'Colesterol_Total': np.random.randint(150, 300, size=n_records),
        'Glucosa': np.random.randint(70, 200, size=n_records),
        'IMC': np.random.uniform(18.5, 40, size=n_records).round(1),
        'Fumador': np.random.choice([True, False], size=n_records, p=[0.25, 0.75]),
        'Actividad_Fisica_Horas': np.random.randint(0, 15, size=n_records)
    }
    df = pd.DataFrame(data)
    return df

df_original = generar_datos()
df = df_original.copy()

# --- BARRA LATERAL DE FILTROS ---
st.sidebar.header("Filtros del Dashboard")

# Filtro por Ciudad
ciudades_seleccionadas = st.sidebar.multiselect(
    "Selecciona la Ciudad:",
    options=df['Ciudad'].unique(),
    default=df['Ciudad'].unique()
)

# Filtro por Rango de Edad
rango_edad = st.sidebar.slider(
    "Selecciona el Rango de Edad:",
    min_value=int(df['Edad'].min()),
    max_value=int(df['Edad'].max()),
    value=(int(df['Edad'].min()), int(df['Edad'].max()))
)

# Filtro por Género
genero_seleccionado = st.sidebar.multiselect(
    "Selecciona el Género:",
    options=df['Genero'].unique(),
    default=df['Genero'].unique()
)

# Filtro por Fumador (con checkbox)
solo_fumadores = st.sidebar.checkbox("Mostrar solo fumadores")

# --- APLICACIÓN DE FILTROS ---
df_filtrado = df[
    (df['Ciudad'].isin(ciudades_seleccionadas)) &
    (df['Edad'].between(rango_edad[0], rango_edad[1])) &
    (df['Genero'].isin(genero_seleccionado))
]

if solo_fumadores:
    df_filtrado = df_filtrado[df_filtrado['Fumador'] == True]


# --- CONTENIDO PRINCIPAL DEL DASHBOARD ---

# Métricas Clave (KPIs)
st.subheader("Métricas Clave")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Total Pacientes", value=f"{df_filtrado.shape[0]:,}")

with kpi2:
    st.metric(label="Edad Promedio", value=f"{df_filtrado['Edad'].mean():.1f} años")

with kpi3:
    st.metric(label="Colesterol Promedio", value=f"{df_filtrado['Colesterol_Total'].mean():.0f} mg/dL")

with kpi4:
    st.metric(label="IMC Promedio", value=f"{df_filtrado['IMC'].mean():.1f}")

st.markdown("---")

# --- VISUALIZACIONES DINÁMICAS ---
st.subheader("Visualizaciones Interactivas")

# Dividir el layout en dos columnas para los gráficos
col1, col2 = st.columns(2)

with col1:
    # Gráfico de Distribución (Histograma)
    st.markdown("#### Distribución de una Variable")
    numeric_cols = df_filtrado.select_dtypes(include=np.number).columns.tolist()
    var_dist = st.selectbox("Selecciona una variable numérica:", options=numeric_cols, index=numeric_cols.index('IMC'))
    
    fig_hist = px.histogram(
        df_filtrado,
        x=var_dist,
        color='Genero',
        marginal="box", # Añade un boxplot en el margen
        title=f'Distribución de {var_dist}',
        template='plotly_white'
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    # Gráfico de Correlación (Scatter Plot)
    st.markdown("#### Relación entre dos Variables")
    x_axis = st.selectbox("Variable para el Eje X:", options=numeric_cols, index=numeric_cols.index('Edad'))
    y_axis = st.selectbox("Variable para el Eje Y:", options=numeric_cols, index=numeric_cols.index('Presion_Sistolica'))
    
    fig_scatter = px.scatter(
        df_filtrado,
        x=x_axis,
        y=y_axis,
        color='Fumador',
        title=f'Relación entre {x_axis} y {y_axis}',
        hover_name='Ciudad',
        template='plotly_white'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --- VISTA DE DATOS FILTRADOS ---
st.subheader("Datos Filtrados")
st.write(f"Mostrando {df_filtrado.shape[0]} de {df_original.shape[0]} registros.")
st.dataframe(df_filtrado)
