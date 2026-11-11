import streamlit as st
import pandas as pd
from src.core.database import get_db, init_db

st.set_page_config(page_title="SecOps Assistido - Painel de Investigação", layout="wide")

init_db()

st.title("🛡️ SecOps Assistido v2 - Painel de Investigação de Alertas")
st.markdown("Ferramenta de análise detalhada de anomalias, filtragem por origem e inspeção de payloads.")

@st.cache_data(ttl=5)
def load_logs():
    with get_db() as conn:
        df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC", conn)
    return df

df_logs = load_logs()

if not df_logs.empty:
    st.sidebar.header("🔍 Filtros de Investigação")
    sources = ["Todos"] + list(df_logs['source'].unique())
    selected_source = st.sidebar.selectbox("Filtrar por Origem", sources)
    
    search_term = st.sidebar.text_input("Procurar no Conteúdo / Dados")

    filtered_df = df_logs.copy()
    if selected_source != "Todos":
        filtered_df = filtered_df[filtered_df['source'] == selected_source]
    if search_term:
        filtered_df = filtered_df[filtered_df['raw_data'].str.contains(search_term, case=False, na=False)]

    st.subheader(f"Resultados Filtrados ({len(filtered_df)} registos)")
    st.dataframe(filtered_df, use_container_width=True)

    st.divider()
    st.subheader("🔎 Inspecionar Detalhes do Registo")
    if not filtered_df.empty:
        selected_id = st.selectbox("Selecione o ID do Registo", filtered_df['id'].tolist())
        row = filtered_df[filtered_df['id'] == selected_id].iloc[0]
        
        col1, col2 = st.columns(2)
        col1.write(f"**ID:** {row['id']}")
        col1.write(f"**Origem (Source):** {row['source']}")
        col2.write(f"**Evento:** {row['event_name']}")
        col2.write(f"**Timestamp:** {row['timestamp']}")
        
        st.markdown("**Dados Brutos / Detalhes (Payload):**")
        st.code(row['raw_data'], language="json")
    else:
        st.warning("Nenhum registo corresponde aos filtros aplicados.")
else:
    st.info("Ainda não existem registos na base de dados. Execute o pipeline para gerar dados.")
