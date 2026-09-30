import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from supabase import create_client, Client

# Inicializa o cliente do Supabase
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# Inicializa a Engine do SQLAlchemy para consultas pesadas via Pandas
@st.cache_resource
def get_db_engine():
    db_url = st.secrets["DATABASE_URL"]
    return create_engine(db_url)

# Função para carregar DataFrames para o Supabase
def carregar_dados_para_supabase(df: pd.DataFrame, nome_tabela: str):
    engine = get_db_engine()
    df.to_sql(nome_tabela, con=engine, if_exists="append", index=False, chunksize=2000)

# Função para realizar consultas SQL e retornar DataFrames
def executar_consulta_sql(query: str) -> pd.DataFrame:
    engine = get_db_engine()
    return pd.read_sql_query(query, con=engine)
