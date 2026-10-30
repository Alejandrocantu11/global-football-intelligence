
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from urllib.parse import quote_plus

st.set_page_config(
    page_title="Global Football Intelligence",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Global Football Intelligence")
st.markdown("### Plataforma de análisis estadístico de fútbol")
st.divider()

# Configuración de PostgreSQL
# No guardamos la contraseña directamente en el código.
@st.cache_resource
def conectar_db():
    usuario = os.getenv("GFI_DB_USER", "postgres")
    password = os.environ["GFI_DB_PASSWORD"]
    host = os.getenv("GFI_DB_HOST", "localhost")
    puerto = os.getenv("GFI_DB_PORT", "5432")
    database = "global_football_db"

    url = (
        f"postgresql+psycopg2://{usuario}:"
        f"{quote_plus(password)}@{host}:{puerto}/{database}"
    )
    return create_engine(url)

@st.cache_data(ttl=60)
def cargar_datos():
    query = """
        SELECT liga, equipo, partidos, goles_totales,
               posesion_promedio, puntos_totales
        FROM estadisticas_equipos
    """
    return pd.read_sql(query, conectar_db())

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al conectar con PostgreSQL: {e}")
    st.stop()

# Filtros
st.sidebar.header("Filtros")

ligas = ["Todas"] + sorted(df["liga"].unique().tolist())
liga = st.sidebar.selectbox("Selecciona una liga", ligas)

if liga != "Todas":
    df = df[df["liga"] == liga]

equipos = ["Todos"] + sorted(df["equipo"].unique().tolist())
equipo = st.sidebar.selectbox("Selecciona un equipo", equipos)

if equipo != "Todos":
    df = df[df["equipo"] == equipo]

# Indicadores principales
c1, c2, c3, c4 = st.columns(4)

c1.metric("Equipos", len(df))
c2.metric("Partidos", f"{df['partidos'].sum():,}")
c3.metric("Goles", f"{df['goles_totales'].sum():,}")
c4.metric("Puntos", f"{df['puntos_totales'].sum():,}")

st.divider()

# Gráficas
col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        df.sort_values("goles_totales", ascending=False),
        x="equipo",
        y="goles_totales",
        color="liga",
        title="Goles por equipo"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        df.sort_values("puntos_totales", ascending=False),
        x="equipo",
        y="puntos_totales",
        color="liga",
        title="Puntos por equipo"
    )
    st.plotly_chart(fig, use_container_width=True)

fig = px.scatter(
    df,
    x="posesion_promedio",
    y="goles_totales",
    color="liga",
    hover_name="equipo",
    size="partidos",
    title="Relación entre posesión y goles"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Tabla de estadísticas")
st.dataframe(df, use_container_width=True)

st.caption(
    "Global Football Intelligence | "
    "Datos sintéticos procesados con Apache Spark"
)
