import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

# 1. Configurações de Identidade Visual (Cores Senac/HerzBier)
st.set_page_config(page_title="HerzBier Tech Monitor", layout="wide", page_icon="🍺")

# CSS para Estilização Profissional
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    [data-testid="stMetricValue"] { color: #004587 !important; font-weight: 800; }
    .stAlert { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# 2. Ligação Segura à Base de Dados (Cloud Secrets)
def conectar_bd():
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        database=st.secrets["postgres"]["dbname"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        port=st.secrets["postgres"]["port"]
    )

# 3. Lógica de Negócio (Faixas Térmicas do seu Código API)
FAIXAS = {
    "mostura": {"min": 62, "max": 72},
    "fervura": {"min": 95, "max": 100},
    "fermentacao": {"min": 18, "max": 24},
    "maturacao": {"min": 0, "max": 5}
}

# 4. Título e Branding
st.title("🍺 HerzBier | Dashboard de Engenharia IoT")
st.caption("Projeto Ciência e Tecnologia Aplicada I - Senac Nações Unidas")

try:
    conn = conectar_bd()
    
    # Busca Leituras (Últimas 100)
    df = pd.read_sql("SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 100", conn)
    
    # Busca Alertas (Últimos 5)
    df_alertas = pd.read_sql("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 5", conn)
    
    conn.close()

    if not df.empty:
        # Processamento de Dados
        ultima = df.iloc[0]
        etapa_atual = ultima['etapa'].lower()
        faixa = FAIXAS.get(etapa_atual, {"min": 0, "max": 100})
        
        # --- LINHA 1: KPIs EM TEMPO REAL ---
        c1, c2, c3, c4 = st.columns(4)
        
        c1.metric("Temp. Líquido", f"{ultima['temp_liq']} °C")
        c2.metric("Temp. Ambiente", f"{ultima['temp_amb']} °C")
        c3.metric("Humidade", f"{ultima['umidade']} %")
        
        # Status de Conformidade
        dentro_faixa = faixa['min'] <= ultima['temp_liq'] <= faixa['max']
        if dentro_faixa:
            c4.success(f"ETAPA: {etapa_atual.upper()}")
        else:
            c4.error(f"ALERTA: FORA DA FAIXA ({etapa_atual})")

        st.divider()

        # --- LINHA 2: GRÁFICO TÉCNICO E ALERTAS ---
        col_graf, col_alert = st.columns([2, 1])

        with col_graf:
            st.subheader("📊 Curva de Temperatura e Setpoints")
            
            fig = px.line(df, x='timestamp', y=['temp_liq', 'temp_amb'],
                         labels={'value': '°C', 'timestamp': 'Tempo'},
                         color_discrete_map={'temp_liq': '#004587', 'temp_amb': '#FFC107'})
            
            # Adiciona as linhas de limite (Setpoints)
            fig.add_hline(y=faixa['min'], line_dash="dash", line_color="green", annotation_text="Mín")
            fig.add_hline(y=faixa['max'], line_dash="dash", line_color="red", annotation_text="Máx")
            
            st.plotly_chart(fig, use_container_width=True)

        with col_alert:
            st.subheader("⚠️ Log de Alertas (ADO)")
            if not df_alertas.empty:
                for index, row in df_alertas.iterrows():
                    cor = "error" if row['severidade'] == "CRITICAL" else "warning"
                    st.write(f"**{row['severidade']}** | {row['mensagem']}")
                    st.caption(f"Valor: {row['valor']}°C | Limites: {row['threshold']}")
            else:
                st.info("Nenhum alerta crítico registado no sistema.")

        # --- LINHA 3: ANÁLISE CIENTÍFICA ---
        with st.expander("🔬 Análise de Conformidade e Dados Brutos"):
            total = len(df)
            conformidade = (df['temp_liq'].between(faixa['min'], faixa['max'])).sum() / total * 100
            st.write(f"**Índice de Conformidade Térmica (Últimas 100 leituras):** {conformidade:.1f}%")
            st.dataframe(df.head(10), use_container_width=True)

    else:
        st.warning("⚠️ Ligação estabelecida, mas a aguardar dados do ESP32...")

except Exception as e:
    st.error(f"❌ Erro de Ligação: Verifique se os 'Secrets' do Postgres estão configurados corretamente.")
    st.info("O sistema procura as tabelas 'sensor_readings' e 'alerts' na base de dados 'ByteBier'.")
