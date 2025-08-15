import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Comercial de Salud",
    page_icon="📈",
    layout="wide"
)

# --- TÍTULO PRINCIPAL ---
st.title("📈 Dashboard Comercial para Equipo de Ventas")
st.markdown("Análisis de comportamiento de compras y generación de prospectos para médicos.")

# --- GENERACIÓN DE DATOS SIMULADOS ---
@st.cache_data
def generar_datos(n_medicos=200, n_compras=2000):
    """Genera un DataFrame simulado de médicos y sus compras."""
    np.random.seed(42)
    
    # Datos de Médicos
    especialidades = ['Cardiología', 'Dermatología', 'Pediatría', 'Oncología', 'General']
    ciudades = ['Bogotá', 'Medellín', 'Cali', 'Barranquilla']
    medicos_df = pd.DataFrame({
        'ID_Medico': range(1, n_medicos + 1),
        'Nombre_Medico': [f'Dr. Apellido{i}' for i in range(1, n_medicos + 1)],
        'Especialidad': np.random.choice(especialidades, n_medicos),
        'Ciudad': np.random.choice(ciudades, n_medicos)
    })

    # Datos de Compras
    productos = ['Producto A', 'Producto B', 'Producto C', 'Producto D', 'Producto E']
    fechas_compra = [datetime.now() - timedelta(days=np.random.randint(1, 730)) for _ in range(n_compras)]
    compras_df = pd.DataFrame({
        'ID_Medico': np.random.randint(1, n_medicos + 1, n_compras),
        'Fecha_Compra': fechas_compra,
        'Producto': np.random.choice(productos, n_compras),
        'Monto_Compra': np.random.uniform(100, 1500, n_compras).round(2)
    })

    # Unir los dataframes
    df_completo = pd.merge(compras_df, medicos_df, on='ID_Medico')
    return df_completo.sort_values(by='Fecha_Compra', ascending=False)

# --- FEATURE ENGINEERING PARA EL MODELO ---
def crear_features(df):
    """Crea características de Recencia, Frecuencia y Monetario (RFM)."""
    hoy = datetime.now()
    features_df = df.groupby('ID_Medico').agg(
        Recencia=('Fecha_Compra', lambda date: (hoy - date.max()).days),
        Frecuencia=('ID_Medico', 'count'),
        Monetario=('Monto_Compra', 'sum')
    ).reset_index()
    
    # Crear un target sintético para el modelo (ej: compró en los últimos 90 días)
    df_ultima_compra = df.groupby('ID_Medico')['Fecha_Compra'].max().reset_index()
    df_ultima_compra['Target'] = (hoy - df_ultima_compra['Fecha_Compra']).dt.days < 90
    
    features_df = pd.merge(features_df, df_ultima_compra[['ID_Medico', 'Target']], on='ID_Medico')
    return features_df

# --- ENTRENAMIENTO DEL MODELO PREDICTIVO ---
def entrenar_modelo(features_df):
    """Entrena un modelo de clasificación para predecir la probabilidad de compra."""
    X = features_df[['Recencia', 'Frecuencia', 'Monetario']]
    y = features_df['Target']
    
    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Entrenar modelo
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    
    return model

# Cargar datos (solo se hace una vez gracias al caché)
df_original = generar_datos()

# --- BARRA LATERAL DE FILTROS ---
st.sidebar.header("Filtros del Dashboard")
especialidad_seleccionada = st.sidebar.multoselect(
    "Filtrar por Especialidad:",
    options=df_original['Especialidad'].unique(),
    default=df_original['Especialidad'].unique()
)
ciudad_seleccionada = st.sidebar.multoselect(
    "Filtrar por Ciudad:",
    options=df_original['Ciudad'].unique(),
    default=df_original['Ciudad'].unique()
)
df_filtrado = df_original[
    (df_original['Especialidad'].isin(especialidad_seleccionada)) &
    (df_original['Ciudad'].isin(ciudad_seleccionada))
]

# --- DASHBOARD DE ANÁLISIS COMERCIAL ---
st.subheader("Análisis de Comportamiento de Compras")
col1, col2 = st.columns(2)

with col1:
    # Ventas a lo largo del tiempo
    ventas_por_mes = df_filtrado.set_index('Fecha_Compra').groupby(pd.Grouper(freq='ME'))['Monto_Compra'].sum().reset_index()
    fig_line = px.line(ventas_por_mes, x='Fecha_Compra', y='Monto_Compra', title='Evolución de Ventas Mensuales', markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    # Top productos por monto
    top_productos = df_filtrado.groupby('Producto')['Monto_Compra'].sum().nlargest(5).reset_index()
    fig_bar = px.bar(top_productos, x='Producto', y='Monto_Compra', title='Top 5 Productos por Monto de Venta', color='Producto')
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# --- SECCIÓN DE PREDICCIÓN Y GENERACIÓN DE PROSPECTOS ---
st.subheader("🤖 Generador de Prospectos con IA")

# Controles para la generación de prospectos
st.sidebar.header("Generador de Prospectos")
dias_sin_compra = st.sidebar.slider(
    "Médicos que no han comprado en los últimos (días):",
    min_value=30, max_value=365, value=90, step=15
)
comercial_seleccionado = st.sidebar.selectbox(
    "Seleccionar Comercial:",
    ('Camila', 'Andrea')
)

if st.sidebar.button("✨ Generar Prospectos"):
    with st.spinner('Reentrenando modelo y generando prospectos...'):
        # 1. Recrear features y reentrenar el modelo CADA VEZ que se presiona el botón
        df_features = crear_features(df_original)
        modelo = entrenar_modelo(df_features)

        # 2. Identificar médicos inactivos
        medicos_activos_recientemente = df_original[df_original['Fecha_Compra'] >= (datetime.now() - timedelta(days=dias_sin_compra))]['ID_Medico'].unique()
        prospectos_df = df_features[~df_features['ID_Medico'].isin(medicos_activos_recientemente)]

        if prospectos_df.empty:
            st.warning(f"No se encontraron médicos que no hayan comprado en los últimos {dias_sin_compra} días.")
        else:
            # 3. Predecir probabilidad de compra con el nuevo modelo
            X_prospectos = prospectos_df[['Recencia', 'Frecuencia', 'Monetario']]
            probabilidades = modelo.predict_proba(X_prospectos)[:, 1]
            prospectos_df['Probabilidad_Compra'] = probabilidades

            # 4. Asignar a comerciales
            prospectos_df = prospectos_df.sort_values(by='Probabilidad_Compra', ascending=False)
            
            if comercial_seleccionado == 'Camila':
                prospectos_finales = prospectos_df[prospectos_df['ID_Medico'] % 2 == 0].head(3)
            else: # Andrea
                prospectos_finales = prospectos_df[prospectos_df['ID_Medico'] % 2 != 0].head(3)
            
            # 5. Mostrar resultados
            st.success(f"Top 3 Prospectos asignados a **{comercial_seleccionado}**:")
            
            if prospectos_finales.empty:
                st.info(f"No hay suficientes prospectos para asignar a {comercial_seleccionado} con los criterios actuales.")
            else:
                prospectos_finales = pd.merge(prospectos_finales, df_original.drop_duplicates('ID_Medico'), on='ID_Medico')
                
                for index, row in prospectos_finales.iterrows():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 10px;">
                        <h4>👨‍⚕️ {row['Nombre_Medico']}</h4>
                        <ul>
                            <li><strong>Especialidad:</strong> {row['Especialidad']}</li>
                            <li><strong>Ciudad:</strong> {row['Ciudad']}</li>
                            <li><strong>Última Compra Hace:</strong> {row['Recencia']} días</li>
                            <li><strong>Probabilidad de Compra:</strong> <span style="color: green; font-weight: bold;">{row['Probabilidad_Compra']:.2%}</span></li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
else:
    st.info("Ajusta los filtros en la barra lateral y haz clic en 'Generar Prospectos' para ver las recomendaciones.")


