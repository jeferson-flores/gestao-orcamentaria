import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Painel de Simulação Orçamentária - UFSM",
    page_icon="🏛️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. SISTEMA DE SEGURANÇA E AUTENTICAÇÃO (SENHA)
# -----------------------------------------------------------------------------
SENHA_CORRETA = "ufsm2026"  # <--- ALTERE AQUI A SENHA DE ACESSO DO PAINEL

def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🏛️ Sistema de Gestão Orçamentária - PRA/UFSM")
        st.subheader("Área Restrita à Alta Gestão")
        
        senha_digitada = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("Entrar"):
            if senha_digitada == SENHA_CORRETA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta. Acesso negado.")
        return False
    return True

if verificar_senha():

    # -----------------------------------------------------------------------------
    # 3. INTERFACE PRINCIPAL DO PAINEL
    # -----------------------------------------------------------------------------
    st.title("🏛️ Painel de Gestão e Simulação Orçamentária")
    st.caption("Pró-Reitoria de Administração (PRA) - Universidade Federal de Santa Maria")

    # CARGA DE DADOS DEMONSTRATIVOS DO TESOURO GERENCIAL
    @st.cache_data
    def carregar_dados_exemplo():
        dados = {
            "Acao_Cod": ["20RK", "20RK", "20RK", "2082", "2082", "8282"],
            "Acao_Nome": [
                "Funcionamento de IFES (Custeio)",
                "Funcionamento de IFES (Custeio)",
                "Funcionamento de IFES (Investimento)",
                "Assistência Estudantil",
                "Assistência Estudantil",
                "Reestruturação e Expansão"
            ],
            "Grupo_Despesa": [
                "Outras Despesas Correntes", "Outras Despesas Correntes", 
                "Investimentos", "Outras Despesas Correntes", 
                "Outras Despesas Correntes", "Investimentos"
            ],
            "Elemento_Despesa": [
                "Energia Elétrica", "Contratos de Terceirização", 
                "Equipamentos", "Bolsas Estudantis", 
                "Restaurante Universitário", "Obras em Andamento"
            ],
            "Dotacao_Atualizada": [15000000.0, 22000000.0, 3000000.0, 12000000.0, 8000000.0, 5000000.0],
            "Empenhado": [14200000.0, 21500000.0, 1800000.0, 11800000.0, 7900000.0, 3200000.0],
            "Liquidado": [13800000.0, 19500000.0, 1200000.0, 11000000.0, 7500000.0, 2100000.0]
        }
        return pd.DataFrame(dados)

    # BARRA LATERAL: UPLOAD E SLIDERS
    st.sidebar.header("📁 Carga de Dados (TG)")
    arquivo = st.sidebar.file_uploader("Upload de relatório do Tesouro Gerencial (.xlsx ou .csv)", type=["csv", "xlsx"])

    if arquivo is not None:
        try:
            if arquivo.name.endswith(".csv"):
                df_base = pd.read_csv(arquivo)
            else:
                df_base = pd.read_excel(arquivo)
            st.sidebar.success("Arquivo do TG carregado com sucesso!")
        except Exception as e:
            st.sidebar.error("Erro ao ler arquivo. Exibindo dados de teste.")
            df_base = carregar_dados_exemplo()
    else:
        df_base = carregar_dados_exemplo()
        st.sidebar.info("Exibindo dados demonstrativos.")

    # SLIDERS DE SIMULAÇÃO
    st.sidebar.markdown("---")
    st.sidebar.header("🎛️ Simulador Orçamentário")
    
    fator_custeio = st.sidebar.slider(
        "Ajuste no Custeio Geral (%)",
        min_value=-30.0, max_value=30.0, value=0.0, step=1.0
    )

    fator_investimento = st.sidebar.slider(
        "Ajuste em Investimentos (%)",
        min_value=-50.0, max_value=50.0, value=0.0, step=5.0
    )

    # APLICAÇÃO DA SIMULAÇÃO
    df_simulado = df_base.copy()
    def calcular_simulacao(row):
        dotacao = row["Dotacao_Atualizada"]
        if row["Grupo_Despesa"] == "Outras Despesas Correntes":
            return dotacao * (1 + (fator_custeio / 100))
        elif row["Grupo_Despesa"] == "Investimentos":
            return dotacao * (1 + (fator_investimento / 100))
        return dotacao

    df_simulado["Dotacao_Simulada"] = df_simulado.apply(calcular_simulacao, axis=1)

    # INDICADORES PRINCIPAIS (KPIS)
    dot_orig = df_simulado["Dotacao_Atualizada"].sum()
    dot_sim = df_simulado["Dotacao_Simulada"].sum()
    emp_tot = df_simulado["Empenhado"].sum()
    dif_orc = dot_sim - dot_orig

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dotação Atual", f"R$ {dot_orig:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("Dotação Simulada", f"R$ {dot_sim:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta=f"R$ {dif_orc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Total Empenhado", f"R$ {emp_tot:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c4.metric("Execução Atual", f"{(emp_tot / dot_orig) * 100:.1f}%")

    st.markdown("---")

    # GRÁFICOS
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Cenário Original vs. Simulado por Ação")
        df_agrup = df_simulado.groupby("Acao_Nome")[["Dotacao_Atualizada", "Dotacao_Simulada"]].sum().reset_index()
        fig_barras = px.bar(
            df_agrup, x="Acao_Nome", y=["Dotacao_Atualizada", "Dotacao_Simulada"],
            barmode="group", labels={"value": "R$", "variable": "Cenário", "Acao_Nome": "Ação"}
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    with col_g2:
        st.subheader("Distribuição do Orçamento Simulado")
        fig_pizza = px.pie(df_simulado, names="Elemento_Despesa", values="Dotacao_Simulada", hole=0.4)
        st.plotly_chart(fig_pizza, use_container_width=True)

    # TABELA DE DADOS
    st.subheader("📋 Tabela Detalhada de Execução e Simulação")
    st.dataframe(df_simulado, use_container_width=True)
