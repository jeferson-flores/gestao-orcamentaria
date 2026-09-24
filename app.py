import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO E ESTILO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistema de Gestão Orçamentária - UFSM",
    page_icon="🏛️",
    layout="wide"
)

# Inicialização da Memória da Aplicação (Session State) para Cadastros
if "contas_gerenciais" not in st.session_state:
    # Contas iniciais de exemplo (você pode alterar/adicionar na interface)
    st.session_state.contas_gerenciais = ["Manutenção & Concessionárias", "Assistência e Bolsas", "Obras & Infraestrutura", "Insumos de Laboratório", "Sem Classificação"]

if "dicionario_pis" not in st.session_state:
    # Mapeamento inicial vazio {PI: Conta}
    st.session_state.dicionario_pis = {}

if "dados_tg_raw" not in st.session_state:
    st.session_state.dados_tg_raw = None

# -----------------------------------------------------------------------------
# 2. SEGURANÇA E AUTENTICAÇÃO
# -----------------------------------------------------------------------------
SENHA_CORRETA = "ufsm2026"

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
    # 3. MENU LATERAL DE NAVEGAÇÃO
    # -----------------------------------------------------------------------------
    st.sidebar.title("🏛️ PRA / UFSM")
    st.sidebar.caption("Gestão Orçamentária Executiva")
    
    opcao_menu = st.sidebar.radio(
        "Navegação",
        [
            "📊 Relatório Principal",
            "📖 Dicionário de PIs",
            "🏷️ Cadastro de Contas",
            "📁 Carga do Tesouro Gerencial"
        ]
    )

    # -----------------------------------------------------------------------------
    # FUNÇÃO AUXILIAR: TRATAMENTO DE VALORES NUMÉRICOS
    # -----------------------------------------------------------------------------
    def converter_valor(val):
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
    # PÁGINA 1: CARGA DE DADOS
    # -----------------------------------------------------------------------------
    if opcao_menu == "📁 Carga do Tesouro Gerencial":
        st.header("📁 Carga do Relatório do Tesouro Gerencial")
        st.write("Faça o upload do arquivo brutos (.xlsx ou .csv) extraído do Tesouro Gerencial.")

        arquivo = st.file_uploader("Selecione a planilha do TG", type=["csv", "xlsx"])

        if arquivo is not None:
            try:
                if arquivo.name.endswith(".csv"):
                    try:
                        df = pd.read_csv(arquivo, sep=";", encoding="latin1")
                        if len(df.columns) <= 1:
                            arquivo.seek(0)
                            df = pd.read_csv(arquivo, sep=",")
                    except:
                        arquivo.seek(0)
                        df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)
                
                st.session_state.dados_tg_raw = df
                st.success(f"Arquivo carregado com sucesso! {len(df)} linhas encontradas.")
                st.dataframe(df.head(5), use_container_width=True)

            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}")

        elif st.session_state.dados_tg_raw is not None:
            st.info("Já existe um arquivo carregado na memória.")
            if st.button("Remover Arquivo Atual"):
                st.session_state.dados_tg_raw = None
                st.rerun()

    # -----------------------------------------------------------------------------
    # PÁGINA 2: CADASTRO DE CONTAS GERENCIAIS
    # -----------------------------------------------------------------------------
    elif opcao_menu == "🏷️ Cadastro de Contas":
        st.header("🏷️ Cadastro de Contas Gerenciais")
        st.write("Crie os nomes amigáveis e estruturados que serão apresentados à Reitoria.")

        col_add, col_list = st.columns([1, 2])

        with col_add:
            st.subheader("Nova Conta")
            nova_conta = st.text_input("Nome da Conta Gerencial:")
            if st.button("Adicionar Conta"):
                if nova_conta and nova_conta not in st.session_state.contas_gerenciais:
                    st.session_state.contas_gerenciais.append(nova_conta)
                    st.success(f"Conta '{nova_conta}' criada com sucesso!")
                    st.rerun()

        with col_list:
            st.subheader("Contas Cadastradas")
            for idx, conta in enumerate(st.session_state.contas_gerenciais):
                c_nome, c_del = st.columns([3, 1])
                c_nome.write(f"• **{conta}**")
                if c_del.button("Excluir", key=f"del_{idx}"):
                    st.session_state.contas_gerenciais.remove(conta)
                    st.rerun()

    # -----------------------------------------------------------------------------
    # PÁGINA 3: DICIONÁRIO DE PIs (PLANO INTERNO)
    # -----------------------------------------------------------------------------
    elif opcao_menu == "📖 Dicionário de PIs":
        st.header("📖 Dicionário e Tradução de PIs (Planos Internos)")
        st.write("Associe cada código de PI (SIAFI) a uma Conta Gerencial compreensível.")

        if st.session_state.dados_tg_raw is None:
            st.warning("⚠️ Faça o upload do arquivo do Tesouro Gerencial na aba 'Carga do Tesouro Gerencial' para listar os PIs.")
        else:
            df = st.session_state.dados_tg_raw
            
            # Identificação das colunas do TG conforme especificado (L/M para PI)
            colunas = list(df.columns)
            col_pi_cod = colunas[11] if len(colunas) > 11 else colunas[0]  # Coluna L (índice 11)
            col_pi_nome = colunas[12] if len(colunas) > 12 else col_pi_cod # Coluna M (índice 12)

            # Extrai PIs únicos
            df_pis = df[[col_pi_cod, col_pi_nome]].drop_duplicates().dropna()
            df_pis["PI_Completo"] = df_pis[col_pi_cod].astype(str) + " - " + df_pis[col_pi_nome].astype(str)
            
            lista_pis = sorted(df_pis["PI_Completo"].unique())

            st.write(f"**Total de PIs identificados no arquivo:** {len(lista_pis)}")

            # Formulário de Associação
            for pi_item in lista_pis:
                col_pi_lbl, col_sel = st.columns([2, 2])
                col_pi_lbl.write(f"📌 **{pi_item}**")
                
                # Valor atual mapeado
                conta_atual = st.session_state.dicionario_pis.get(pi_item, "Sem Classificação")
                idx_def = st.session_state.contas_gerenciais.index(conta_atual) if conta_atual in st.session_state.contas_gerenciais else 0

                nova_associoacao = col_sel.selectbox(
                    "Vincular à Conta:",
                    st.session_state.contas_gerenciais,
                    index=idx_def,
                    key=f"sel_{pi_item}"
                )
                
                st.session_state.dicionario_pis[pi_item] = nova_associoacao

    # -----------------------------------------------------------------------------
    # PÁGINA 4: RELATÓRIO PRINCIPAL (ALTA GESTÃO)
    # -----------------------------------------------------------------------------
    elif opcao_menu == "📊 Relatório Principal":
        st.header("📊 Relatório de Recursos Discricionários por Conta Gerencial")

        if st.session_state.dados_tg_raw is None:
            st.info("👋 Bem-vindo! Para visualizar o relatório executivo, faça o upload da planilha na aba **'Carga do Tesouro Gerencial'** no menu à esquerda.")
        else:
            df = st.session_state.dados_tg_raw
            colunas = list(df.columns)

            # Mapeamento pelas posições exatas indicadas:
            # Coluna C (índice 2): "Resultado Lei Nome"
            # Coluna L/M (índices 11 e 12): PI Código e Nome
            # Coluna T (índice 19): Valores
            col_resultado_lei = colunas[2] if len(colunas) > 2 else colunas[0]
            col_pi_cod = colunas[11] if len(colunas) > 11 else colunas[0]
            col_pi_nome = colunas[12] if len(colunas) > 12 else col_pi_cod
            col_valor = colunas[19] if len(colunas) > 19 else colunas[-1]

            # 1. Filtro: Recursos Discricionários (Coluna C com código 2)
            df_filtrado = df[df[col_resultado_lei].astype(str).str.contains("2", na=False)].copy()

            # 2. Tratamento do Valor (Coluna T)
            df_filtrado["Valor_Tratado"] = df_filtrado[col_valor].apply(converter_valor)

            # 3. Criação da Identificação Única do PI
            df_filtrado["PI_Completo"] = df_filtrado[col_pi_cod].astype(str) + " - " + df_filtrado[col_pi_nome].astype(str)

            # 4. Aplicação do Dicionário para Tradução para Conta Gerencial
            df_filtrado["Conta_Gerencial"] = df_filtrado["PI_Completo"].map(
                lambda x: st.session_state.dicionario_pis.get(x, "Sem Classificação")
            )

            # --- APRESENTAÇÃO DOS RESULTADOS ---
            total_discricionario = df_filtrado["Valor_Tratado"].sum()
            
            m1, m2 = st.columns(2)
            m1.metric("Total de Recursos Discricionários", f"R$ {total_discricionario:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            m2.metric("PIs Processados", len(df_filtrado["PI_Completo"].unique()))

            st.markdown("---")

            # Consolidação por Conta Gerencial
            df_executivo = df_filtrado.groupby("Conta_Gerencial")["Valor_Tratado"].sum().reset_index()
            df_executivo.columns = ["Conta Gerencial", "Valor Total (R$)"]
            df_executivo = df_executivo.sort_values(by="Valor Total (R$)", ascending=False)

            col_g, col_t = st.columns([1, 1])

            with col_g:
                st.subheader("Visão por Conta Gerencial")
                fig = px.pie(
                    df_executivo, 
                    names="Conta Gerencial", 
                    values="Valor Total (R$)", 
                    hole=0.4,
                    title="Distribuição das Despesas Discricionárias"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_t:
                st.subheader("Resumo de Valores")
                st.dataframe(
                    df_executivo.style.format({"Valor Total (R$)": "R$ {:,.2f}"}),
                    use_container_width=True
                )

            st.markdown("---")
            st.subheader("🔍 Detalhamento por PI")
            df_detalhado = df_filtrado.groupby(["Conta_Gerencial", "PI_Completo"])["Valor_Tratado"].sum().reset_index()
            df_detalhado.columns = ["Conta Gerencial", "Plano Interno (PI)", "Valor (R$)"]
            st.dataframe(df_detalhado.style.format({"Valor (R$)": "R$ {:,.2f}"}), use_container_width=True)
