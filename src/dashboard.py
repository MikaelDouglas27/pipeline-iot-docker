"""Dashboard interativo das leituras de temperatura IoT."""
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Dashboard IoT", page_icon="🌡️", layout="wide")
@st.cache_resource
def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER','iot_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD','troque_esta_senha')}@"
        f"{os.getenv('POSTGRES_HOST','localhost')}:{os.getenv('POSTGRES_PORT','5432')}/"
        f"{os.getenv('POSTGRES_DB','iot_db')}"
    )
def load_data(view):
    # Nomes das views são constantes definidas no projeto, não entradas do usuário.
    return pd.read_sql(f"SELECT * FROM {view}", get_engine())

st.title("🌡️ Dashboard de Temperaturas IoT")
st.caption("Análise de leituras de sensores internos e externos — conjunto público do Kaggle.")
try:
    resumo = pd.read_sql(
        "SELECT COUNT(*) AS leituras, ROUND(AVG(temperature)::numeric,2) AS media, "
        "ROUND(MIN(temperature)::numeric,2) AS minima, "
        "ROUND(MAX(temperature)::numeric,2) AS maxima FROM temperature_readings",
        get_engine()
    ).iloc[0]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Leituras", f"{int(resumo.leituras):,}".replace(",", "."))
    c2.metric("Temperatura média", f"{resumo.media} °C")
    c3.metric("Mínima", f"{resumo.minima} °C")
    c4.metric("Máxima", f"{resumo.maxima} °C")

    st.subheader("Temperatura média por ambiente")
    df = load_data("avg_temp_por_local")
    st.plotly_chart(px.bar(df, x="location", y="avg_temp", color="location",
                           hover_data=["total_leituras"], labels={"location":"Ambiente","avg_temp":"Média (°C)"}),
                    use_container_width=True)

    st.subheader("Quantidade de leituras por hora")
    horas = load_data("leituras_por_hora")
    st.plotly_chart(px.line(horas, x="hora", y="contagem", markers=True,
                            labels={"hora":"Hora do dia","contagem":"Leituras"}),
                    use_container_width=True)

    st.subheader("Temperaturas máximas e mínimas por dia")
    diario = load_data("temp_max_min_por_dia")
    fig = px.line(diario, x="data", y=["temp_max","temp_min"],
                  labels={"value":"Temperatura (°C)","data":"Data","variable":"Métrica"})
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Dados diários")
    st.dataframe(diario, use_container_width=True)
except Exception as exc:
    st.error("Não foi possível consultar o banco. Confira se o Docker está ativo e se o pipeline já foi executado.")
    st.exception(exc)
