import streamlit as st
import pandas as pd
from src.core.database import get_db, init_db

st.set_page_config(page_title="SecOps Assistido - Painel Executivo", layout="wide")

init_db()

st.title("🛡️ SecOps Assistido v2 - Painel Executivo")
st.markdown("Monitorização em tempo real de anomalias, métricas de segurança e indicadores de desempenho.")

# 1. Obter dados da base de dados
@st.cache_data(ttl=5)
def load_logs():
    with get_db() as conn:
        df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC", conn)
    return df

df_logs = load_logs()

# 2. Métricas de KPIs
col1, col2, col3 = st.columns(3)
total_logs = len(df_logs)
sources_count = df_logs['source'].nunique() if not df_logs.empty else 0

col1.metric("Total de Registos / Alertas", total_logs)
col2.metric("Fontes de Origem Ativas", sources_count)
col3.metric("Estado do Sistema", "Operacional", "Normal")

st.divider()

# 3. Visão de Dados e Séries Temporais
st.subheader("📊 Distribuição de Eventos por Origem")
if not df_logs.empty:
    source_counts = df_logs['source'].value_counts()
    st.bar_chart(source_counts)

    st.subheader("📋 Registos Recentes")
    st.dataframe(df_logs.head(20), use_container_width=True)
else:
    st.info("Ainda não existem registos na base de dados. Execute o pipeline para gerar dados.")
