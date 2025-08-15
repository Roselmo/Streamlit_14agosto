import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Agente con Llama3 y Groq",
    page_icon="🤖",
    layout="centered"
)

# --- TÍTULO Y DESCRIPCIÓN ---
st.title("🤖 Agente Inteligente con Llama3")
st.markdown("Este agente utiliza el poder de Llama3 a través de la API de Groq para responder a tus preguntas. Escribe tu consulta a continuación.")

# --- VALIDACIÓN DE LA API KEY ---
try:
    # Intenta acceder a la clave de API desde los secretos de Streamlit
    groq_api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("🚨 No se encontró la GROQ_API_KEY en los secretos de Streamlit.")
    st.info("Por favor, asegúrate de haber creado un archivo .streamlit/secrets.toml con tu clave. Mira las instrucciones en el archivo README.")
    st.stop() # Detiene la ejecución si la clave no se encuentra

# --- INICIALIZACIÓN DEL MODELO Y LA CADENA ---
# Inicializa el modelo de lenguaje de Groq
# El modelo llama3-8b-8192 es rápido y eficiente
chat = ChatGroq(
    temperature=0.7,
    groq_api_key=groq_api_key,
    model_name="llama3-8b-8192"
)

# Define la plantilla del prompt para guiar al modelo
system_prompt = "Eres un asistente útil y conciso. Responde a las preguntas del usuario de la mejor manera posible."
human_prompt = "{text}"
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", human_prompt)
])

# Define el parser para obtener la respuesta como texto
output_parser = StrOutputParser()

# Crea la cadena (chain) que une los componentes
chain = prompt | chat | output_parser

# --- INTERFAZ DE USUARIO ---
user_input = st.text_input("Escribe tu pregunta aquí:", key="user_input")

if user_input:
    with st.spinner("Pensando..."):
        try:
            # Invoca la cadena con la entrada del usuario
            response = chain.invoke({"text": user_input})
            st.write("### Respuesta del Agente:")
            st.markdown(response)
        except Exception as e:
            st.error(f"Ocurrió un error al contactar la API de Groq: {e}")

st.markdown("---")
st.write("Desarrollado con ❤️ usando Streamlit, LangChain y Groq.")




