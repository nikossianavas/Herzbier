import streamlit as st
import pandas as pd
import psycopg2 # Necessário para ligar ao PostgreSQL
import time

# Configurações do Dashboard
st.set_page_config(page_title="HerzBier Tech Dashboard", layout="wide")

st.title("🍺 HerzBier: Painel Técnico de Engenharia")
st.markdown("---")

# Função para ligar à base de dados (Conforme o seu esquema SQL)
def load_data():
    # Substitua pelos dados da sua base de dados local/nuvem
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="SUA_PASSWORD"
    )
    query = "SELECT timestamp, temp_liq, temp_amb, umidade, etapa FROM sensor_readings ORDER BY timestamp DESC LIMIT 50"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Layout de Colunas para KPIs
col1, col2, col3 = st.columns(3)

try:
    df = load_data()
    latest = df.iloc[0]

    with col1:
        st.metric("Temperatura do Líquido", f"{latest['temp_liq']} °C", delta="Estável")
    with col2:
        st.metric("Humidade Ambiente", f"{latest['umidade']} %")
    with col3:
        st.metric("Etapa Atual", latest['etapa'].upper())

    # Gráfico de histórico
    st.subheader("Curva de Temperatura (Últimas 50 leituras)")
    st.line_chart(df.set_index('timestamp')[['temp_liq', 'temp_amb']])

except:
    st.warning("A aguardar ligação com a base de dados PostgreSQL...")

# Auto-refresh a cada 5 segundos
time.sleep(5)
st.rerun()