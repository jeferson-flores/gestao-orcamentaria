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
# 2. SISTEMA DE SEGURANÇA E AUTENTICAÇÃO
# -----------------------------------------------------------------------------
SENHA_CORRETA = "ufsm2026"  # Defina sua senha aqui

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

    st.title("🏛️ Painel de Gestão e Simulação Orçamentária")
    st.caption("Pró-Reitoria de Administração (PRA) - Universidade Federal de Santa Maria")

    # Funcao para tratar valores do Tesouro Gerencial (ex: "1.500.000,00" -> 1500000.00)
    def converter_para_numero(val):
        if pd.isna(val):
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).strip().replace(".", "").replace(",", ".")
        try:
            return float(val_str)
        except ValueError:
            return 0.0

    # -----------------------------------------------------------------------------
    # 3. CARGA E MAPEAMENTO DE DADOS (TESOURO GERENCIAL)
    # -----------------------------------------------------------------------------
    st.sidebar.header("📁 Carga de Dados (TG)")
    arquivo = st.sidebar.file_uploader("Upload do relatório (.xlsx ou .csv)", type=["csv", "xlsx"])

    if arquivo is not None:
        try:
            if arquivo.name.endswith(".csv"):
                # Tenta ler CSV com separadores comuns no Brasil
                try:
                    df_raw = pd.read_csv(arquivo, sep=";", encoding="latin1")
                    if len(df_raw.columns) <= 1:
                        arquivo.seek(0)
                        df_raw = pd.read_csv(arquivo, sep=",")
                except:
                    arquivo.seek(0)
                    df_raw = pd.read_csv(arquivo)
            else:
                df_raw = pd.read_excel(arquivo)
            
            st.sidebar.success("Arquivo carregado com sucesso!")

            # EXPANDER PARA MAPEAMENTO FLEXÍVEL DE COLUNAS
            with st.expander("🛠️ Mapeamento de Colunas do Tesouro Gerencial", expanded=True):
                st.write("Confirme ou selecione quais colunas da sua planilha correspondem aos campos do sistema:")
                
                colunas_disponiveis = list(df_raw.columns)
                
                # Mapeamento automático inteligente tentando adivinhar pelos nomes comuns do TG
                idx_acao = next((i for i, c in enumerate(colunas_disponiveis) if "ação" in c.lower() or "acao" in c.lower() or "programa" in c.lower()), 0)
                idx_desp = next((i for i, c in enumerate(colunas_disponiveis) if "gnd" in c.lower() or "grupo" in c.lower() or "despesa" in c.lower() or "elemento" in c.lower()), 0)
                idx_dot = next((i for i, c in enumerate(colunas_disponiveis) if "dotação" in c.lower() or "dotacao" in c.lower() or "autorizado" in c.lower() or "credito" in c.lower()), 0)
                idx_emp = next((i for i, c in enumerate(colunas_disponiveis) if "empenhado" in c.lower() or "empenho" in c.lower()), 0)

                c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                col_acao = c_m1.selectbox("Coluna da Ação / Projeto:", colunas_disponiveis, index=idx_acao)
                col_despesa = c_m2.selectbox("Coluna do Grupo/Categoria:", colunas_disponiveis, index=idx_desp)
                col_dotacao = c_m3.selectbox("Coluna da Dotação Atualizada:", colunas_disponiveis, index=idx_dot)
                col_empenhado = c_m4.selectbox("Coluna do Valor Empenhado:", colunas_disponiveis, index=idx_emp)

            # Padroniza o dataframe com as colunas selecionadas
            df_base = pd.DataFrame({
                "Acao": df_raw[col_acao].astype(str),
                "Categoria": df_raw[col_despesa].astype(str),
                "Dotacao_Atualizada": df_raw[col_dotacao].apply(converter_para_numero),
                "Empenhado": df_raw[col_empenhado].apply(converter_para_numero)
            })

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
            st.stop()
    else:
        # Dados de exemplo se nenhum arquivo for carregado
        st.sidebar.info("Nenhum arquivo enviado. Exibindo dados de exemplo.")
        df_base = pd.DataFrame({
            "Acao": ["20RK - Funcionamento", "20RK - Funcionamento", "2082 - Assistência Estudantil"],
            "Categoria": ["Custeio", "Investimento", "Custeio"],
            "Dotacao_Atualizada": [15000000.0, 3000000.0, 8000000.0],
            "Empenhado": [14200000.0, 1800000.0, 7900000.0]
        })

    # -----------------------------------------------------------------------------
    # 4. SIMULADOR E REGRAS DE CÁLCULO
    # -----------------------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.header("🎛️ Simulador Orçamentário")
    
    fator_geral = st.sidebar.slider(
        "Ajuste Linear Geral no Orçamento (%)",
        min_value=-30.0, max_value=30.0, value=0.0, step=1.0
    )

    df_simulado = df_base.copy()
    df_simulado["Dotacao_Simulada"] = df_simulado["Dotacao_Atualizada"] * (1 + (fator_geral / 100))

    # -----------------------------------------------------------------------------
    # 5. DASHBOARD E INDICADORES (KPIS)
    # -----------------------------------------------------------------------------
    dot_orig = df_simulado["Dotacao_Atualizada"].sum()
    dot_sim = df_simulado["Dotacao_Simulada"].sum()
    emp_tot = df_simulado["Empenhado"].sum()
    dif_orc = dot_sim - dot_orig

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dotação Atual Total", f"R$ {dot_orig:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("Dotação Simulada", f"R$ {dot_sim:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta=f"R$ {dif_orc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Total Empenhado", f"R$ {emp_tot:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c4.metric("Execução Atual", f"{(emp_tot / dot_orig * 100) if dot_orig > 0 else 0:.1f}%")

    st.markdown("---")

    # -----------------------------------------------------------------------------
    # 6. VISUALIZAÇÕES GRÁFICAS E TABELAS
    # -----------------------------------------------------------------------------
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Cenário Original vs. Simulado por Ação")
        df_agrup = df_simulado.groupby("Acao")[["Dotacao_Atualizada", "Dotacao_Simulada"]].sum().reset_index()
        fig_barras = px.bar(
            df_agrup, x="Acao", y=["Dotacao_Atualizada", "Dotacao_Simulada"],
            barmode="group", labels={"value": "R$", "variable": "Cenário", "Acao": "Ação Orçamentária"}
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    with col_g2:
        st.subheader("Distribuição do Orçamento Simulado por Categoria")
        df_cat = df_simulado.groupby("Categoria")["Dotacao_Simulada"].sum().reset_index()
        fig_pizza = px.pie(df_cat, names="Categoria", values="Dotacao_Simulada", hole=0.4)
        st.plotly_chart(fig_pizza, use_container_width=True)

    st.subheader("📋 Tabela Detalhada de Execução e Simulação")
    st.dataframe(df_simulado, use_container_width=True)
