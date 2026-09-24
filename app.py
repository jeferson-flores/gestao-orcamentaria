import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistema de Gestão Orçamentária - UFSM",
    page_icon="🏛️",
    layout="wide"
)

# Customização CSS para o menu por botões
st.markdown("""
    <style>
    div[data-testid="stSidebar"] button {
        width: 100%;
        border-radius: 6px;
        height: 2.8em;
        font-weight: bold;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BANCO DE DADOS/ESTRUTURAS PADRÃO (SISTEMA DE CONTAS E UNIDADES)
# -----------------------------------------------------------------------------
PLANO_CONTAS_PADRAO = [
    "1.1. Obras, Reformas e Adequações",
    "1.2. Concessionárias (Energia, Água, Gás)",
    "1.3. Manutenção Predial e Conservação",
    "1.4. Conservação de Áreas Verdes e Limpeza Urbana",
    "2.1. Serviços de Vigilância e Portaria",
    "2.2. Serviços de Limpeza e Higienização",
    "2.3. Apoio Administrativo e Motoristas",
    "2.4. Recepção e Serviços Gerais",
    "3.1. Equipamentos e Infraestrutura de TI",
    "3.2. Licenças de Software, Sistemas e Nuvem",
    "3.3. Conectividade, Redes e Telefonia",
    "4.1. Restaurante Universitário (RU) - Insumos e Operação",
    "4.2. Bolsas de Assistência Estudantil e Permanência",
    "4.3. Moradia Estudantil e Apoio ao Estudante",
    "5.1. Bolsas de Graduação, Pós e Extensão",
    "5.2. Material Didático, de Laboratório e Insumos de Pesquisa",
    "5.3. Fomento a Projetos de Pesquisa, Extensão e Inovação",
    "5.4. Unidades Especializadas (HVU, Fazenda, Colégios)",
    "6.1. Passagens e Diárias (Nacionais e Internacionais)",
    "6.2. Eventos Acadêmicos, Culturais e Congressos",
    "6.3. Capacitação e Desenvolvimento de Servidores",
    "7.1. Aquisição de Equipamentos e Mobiliário",
    "7.2. Biblioteca (Livros, Periódicos e Bases Científicas)",
    "7.3. Frota e Combustíveis",
    "8.1. Material de Expediente e Suprimentos",
    "8.2. Encargos Institucionais e Impostos",
    "8.3. Outras Despesas Operacionais",
    "Sem Classificação"
]

# Dicionário de Mapeamento de Unidades (SIAFI -> Unidade Consolidada)
MAPA_UNIDADES = {
    "REITORIA DA UFSM": "Reitoria e Gabinete",
    "GABINETE DO REITOR": "Reitoria e Gabinete",
    "AUDITORIA INTERNA": "Reitoria e Gabinete",
    "CORREGEDORIA SETORIAL DA UFSM": "Reitoria e Gabinete",
    "COORDENADORIA DE COMUNICACAO SOCIAL": "Reitoria e Gabinete",
    "DIRETORIA DE RELACOES INTERNACIONAIS": "Reitoria e Gabinete",
    
    "PRO-REITORIA DE ADMINISTRACAO DA UFSM": "PRA - Pró-Reitoria de Administração",
    "ALMOXARIFADO CENTRAL DA UFSM": "PRA - Pró-Reitoria de Administração",
    "UFSM-DEPARTAMENTO DE MATERIAL E PATRIMONIO": "PRA - Pró-Reitoria de Administração",
    "DEPARTAMENTO DE CONTABILIDADE E FINANCAS": "PRA - Pró-Reitoria de Administração",
    "SERVICOS DE TRANSPORTES E OFICINAS/UFSM": "PRA - Pró-Reitoria de Administração",
    "SETOR DE IMPORTACAOES DA UFSM": "PRA - Pró-Reitoria de Administração",

    "PRO-REITORIA DE PLANEJAMENTO DA UFSM": "PROPLAN - Pró-Reitoria de Planejamento",
    "PRO-REITORIA DE GRADUACAO DA UFSM": "PROGRAD - Pró-Reitoria de Graduação",
    "PRO-REITORIA DE POS-GRADUACAO E PESQUISA-UFSM": "PRPGP - Pesquisa e Pós-Graduação",
    "PRO-REITORIA DE EXTENSAO DA UFSM": "PRE - Pró-Reitoria de Extensão",
    "PRO-REITORIA DE INOVACAO E EMPREENDEDORISMO": "INOVA - Inovação e Empreendedorismo",
    "PROGEP": "PROGEP - Gestão de Pessoas",
    "PRO REITORIA DE GESTAO DE PESSOAS": "PROGEP - Gestão de Pessoas",
    
    "PRO-REITORIA DE ASSUNTOS ESTUDANTIS DA UFSM": "PRAE - Assuntos Estudantis",
    "RESTAURANTE UNIVERSITARIO DA UFSM": "PRAE - Assuntos Estudantis",
    "RESTAURANTE UNIVERSITARIO - CAMPUS PM": "PRAE - Assuntos Estudantis",
    "RESTAURANTE UNIVERSITARIO - CAMPUS FW": "PRAE - Assuntos Estudantis",
    "RESTAURANTE UNIVERSITARIO - CAMPUS CACH.SUL": "PRAE - Assuntos Estudantis",
    "SECRET. APOIO ADMIN. - PRAE": "PRAE - Assuntos Estudantis",
    "COORDENADORIA DE ACOES EDUCACIONAIS DA UFSM": "PRAE - Assuntos Estudantis",

    "PRO-REITORIA DE INFRAESTRUTURA - UFSM": "PROINFRA - Infraestrutura",
    "PRO-REITORIA DE INFRAESTRUTURA - PROINFRA": "PROINFRA - Infraestrutura",

    "CENTRO DE ARTES E LETRAS DA UFSM": "CAL - Centro de Artes e Letras",
    "CENTRO DE CIENCIAS NATURAIS E EXATAS DA UFSM": "CCNE - Ciências Naturais e Exatas",
    "CENTRO DE CIENCIAS RURAIS DA UFSM": "CCR - Centro de Ciências Rurais",
    "CENTRO DE CIENCIAS DA SAUDE DA UFSM": "CCS - Centro de Ciências da Saúde",
    "CENTRO DE CIENCIAS SOCIAIS E HUMANAS DA UFSM": "CCSH - Ciências Sociais e Humanas",
    "CENTRO EDUCACAO DA UFSM": "CE - Centro de Educação",
    "CENTRO DE EDUCACAO FISICA E DESPORTOS DA UFSM": "CEFD - Educação Física e Desportos",
    "CENTRO DE TECNOLOGIA DA UFSM": "CT - Centro de Tecnologia",

    "COLEGIO POLITECNICO DA UFSM": "Colégio Politécnico",
    "COLEGIO TECNICO INDUSTRIAL DA UFSM": "CTISM - Colégio Técnico Industrial",
    "CAMPUS DA UFSM EM FREDERICO WESTPHALEN": "Campus Frederico Westphalen",
    "CAMPUS DA UFSM EM PALMEIRAS DAS MISSOES": "Campus Palmeira das Missões",
    "CAMPUS DA UFSM EM CACHOEIRA DO SUL": "Campus Cachoeira do Sul",
    "ESPACO MULTIDISC. PESQ E EXTENS SILV MARTINS": "Campus Silveira Martins",

    "CENTRO DE PROCESSAMENTO DE DADOS DA UFSM": "CPD - Processamento de Dados",
    "LABORATORIO DE MANUTENCAO DE INFORMATICA UFSM": "CPD - Processamento de Dados",
    "DIRETORIA DE GESTAO AMBIENTAL": "DGA - Diretoria de Gestão Ambiental",
    "HOSPITAL DE CLINICAS VETERINARIAS DA UFSM": "Hospital Veterinário / HVU",
    "ENCARGOS GERAIS DA UFSM": "Encargos Gerais da UFSM"
}

# Inicialização da Memória do Sistema
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "carga"

if "contas_gerenciais" not in st.session_state:
    st.session_state.contas_gerenciais = PLANO_CONTAS_PADRAO

if "dicionario_pis" not in st.session_state:
    st.session_state.dicionario_pis = {}

if "dados_tg_raw" not in st.session_state:
    st.session_state.dados_tg_raw = None

# -----------------------------------------------------------------------------
# 3. AUTENTICAÇÃO
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
                st.error("Senha incorreta.")
        return False
    return True

if verificar_senha():

    # -----------------------------------------------------------------------------
    # 4. MENU LATERAL POR BOTÕES
    # -----------------------------------------------------------------------------
    st.sidebar.title("🏛️ PRA / UFSM")
    st.sidebar.caption("Gestão Orçamentária Executiva")
    st.sidebar.markdown("---")

    if st.sidebar.button("📁 1. Carga da Planilha", use_container_width=True, type="primary" if st.session_state.pagina_atual == "carga" else "secondary"):
        st.session_state.pagina_atual = "carga"
        st.rerun()

    if st.sidebar.button("🏷️ 2. Plano de Contas", use_container_width=True, type="primary" if st.session_state.pagina_atual == "contas" else "secondary"):
        st.session_state.pagina_atual = "contas"
        st.rerun()

    if st.sidebar.button("📖 3. Dicionário de PIs", use_container_width=True, type="primary" if st.session_state.pagina_atual == "dicionario" else "secondary"):
        st.session_state.pagina_atual = "dicionario"
        st.rerun()

    if st.sidebar.button("📊 4. Relatório Executivo", use_container_width=True, type="primary" if st.session_state.pagina_atual == "relatorio" else "secondary"):
        st.session_state.pagina_atual = "relatorio"
        st.rerun()

    st.sidebar.markdown("---")

    def converter_valor(val):
        if pd.isna(val): return 0.0
        if isinstance(val, (int, float)): return float(val)
        val_str = str(val).strip().replace(".", "").replace(",", ".")
        try: return float(val_str)
        except: return 0.0

    # -----------------------------------------------------------------------------
    # PÁGINA 1: CARGA DA PLANILHA
    # -----------------------------------------------------------------------------
    if st.session_state.pagina_atual == "carga":
        st.header("📁 Carga do Relatório do Tesouro Gerencial")
        st.write("Faça o upload da planilha liquida/executada do Tesouro Gerencial (.xlsx ou .csv).")

        arquivo = st.file_uploader("Selecione o arquivo da UFSM", type=["csv", "xlsx"])

        if arquivo is not None:
            try:
                if arquivo.name.endswith(".csv"):
                    try: df = pd.read_csv(arquivo, sep=";", encoding="latin1")
                    except: df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)
                
                st.session_state.dados_tg_raw = df
                st.success(f"Arquivo carregado com sucesso! {len(df):,} linhas identificadas.")
                st.dataframe(df.head(5), use_container_width=True)

            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}")

        elif st.session_state.dados_tg_raw is not None:
            st.info("Já existe uma planilha carregada na memória do sistema.")
            if st.button("Remover e Enviar Nova Planilha"):
                st.session_state.dados_tg_raw = None
                st.rerun()

    # -----------------------------------------------------------------------------
    # PÁGINA 2: PLANO DE CONTAS CONTÁBEIS
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "contas":
        st.header("🏷️ Estrutura do Plano de Contas Gerenciais")
        st.write("Plano de contas padronizado em linguagem amigável para apresentação à Alta Gestão.")

        col_add, col_list = st.columns([1, 2])

        with col_add:
            st.subheader("Adicionar Nova Conta")
            nova_conta = st.text_input("Nome/Código da Conta:")
            if st.button("Adicionar"):
                if nova_conta and nova_conta not in st.session_state.contas_gerenciais:
                    st.session_state.contas_gerenciais.append(nova_conta)
                    st.success(f"Conta '{nova_conta}' adicionada!")
                    st.rerun()

        with col_list:
            st.subheader("Plano de Contas Ativo")
            for idx, conta in enumerate(st.session_state.contas_gerenciais):
                c_nome, c_del = st.columns([4, 1])
                c_nome.write(f"• **{conta}**")
                if c_del.button("Excluir", key=f"del_c_{idx}"):
                    st.session_state.contas_gerenciais.remove(conta)
                    st.rerun()

    # -----------------------------------------------------------------------------
    # PÁGINA 3: DICIONÁRIO DE PIs
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "dicionario":
        st.header("📖 Dicionário de Mapeamento dos PIs")
        st.write("Mapeamento automático e manual de Planos Internos (SIAFI) para as Contas Gerenciais.")

        if st.session_state.dados_tg_raw is None:
            st.warning("⚠️ Carregue a planilha na aba '1. Carga da Planilha' para listar os PIs do relatório.")
        else:
            df = st.session_state.dados_tg_raw
            colunas = list(df.columns)
            
            # Posições das Colunas: L (11) e M (12)
            col_pi_cod = colunas[11] if len(colunas) > 11 else colunas[0]
            col_pi_nome = colunas[12] if len(colunas) > 12 else col_pi_cod

            df_pis = df[[col_pi_cod, col_pi_nome]].drop_duplicates().dropna()
            df_pis["PI_Completo"] = df_pis[col_pi_cod].astype(str) + " - " + df_pis[col_pi_nome].astype(str)
            lista_pis = sorted(df_pis["PI_Completo"].unique())

            st.write(f"**Total de PIs únicos identificados na planilha:** {len(lista_pis)}")

            # Sugestão Automática de Mapeamento com base nas palavras-chave do PI Nome
            for pi_item in lista_pis:
                col_lbl, col_sel = st.columns([2, 2])
                col_lbl.write(f"📌 **{pi_item}**")
                
                # Regra simples de autoselect se não mapeado
                conta_sugerida = st.session_state.dicionario_pis.get(pi_item, "Sem Classificação")
                if conta_sugerida == "Sem Classificação":
                    p_up = pi_item.upper()
                    if "RU" in p_up or "RESTAURANTE" in p_up or "ALIMENT" in p_up:
                        conta_sugerida = "4.1. Restaurante Universitário (RU) - Insumos e Operação"
                    elif "BOLSA" in p_up or "ASSIST" in p_up:
                        conta_sugerida = "4.2. Bolsas de Assistência Estudantil e Permanência"
                    elif "ENERGIA" in p_up or "AGUA" in p_up or "GAS" in p_up:
                        conta_sugerida = "1.2. Concessionárias (Energia, Água, Gás)"
                    elif "OBRA" in p_up or "REFORMA" in p_up:
                        conta_sugerida = "1.1. Obras, Reformas e Adequações"
                    elif "TIC" in p_up or "INFORMATICA" in p_up:
                        conta_sugerida = "3.1. Equipamentos e Infraestrutura de TI"

                idx_def = st.session_state.contas_gerenciais.index(conta_sugerida) if conta_sugerida in st.session_state.contas_gerenciais else 0

                nova_ass = col_sel.selectbox(
                    "Conta Gerencial:",
                    st.session_state.contas_gerenciais,
                    index=idx_def,
                    key=f"sel_pi_{pi_item}"
                )
                st.session_state.dicionario_pis[pi_item] = nova_ass

    # -----------------------------------------------------------------------------
    # PÁGINA 4: RELATÓRIO EXECUTIVO (COM SELETOR DE UNIDADES)
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "relatorio":
        st.header("📊 Relatório Executivo de Despesas Discricionárias")

        if st.session_state.dados_tg_raw is None:
            st.info("👋 Por favor, faça a carga do arquivo na aba **'1. Carga da Planilha'** para acessar os relatórios.")
        else:
            df = st.session_state.dados_tg_raw
            colunas = list(df.columns)

            # Mapeamento pelas posições solicitadas
            col_resultado_lei = colunas[2] if len(colunas) > 2 else colunas[0]   # Coluna C
            col_ug_nome = colunas[6] if len(colunas) > 6 else colunas[0]         # Coluna G (UG Responsável Nome)
            col_pi_cod = colunas[11] if len(colunas) > 11 else colunas[0]        # Coluna L
            col_pi_nome = colunas[12] if len(colunas) > 12 else col_pi_cod      # Coluna M
            col_valor = colunas[19] if len(colunas) > 19 else colunas[-1]       # Coluna T

            # 1. Filtro: Recursos Discricionários (Coluna C contém "2")
            df_disc = df[df[col_resultado_lei].astype(str).str.contains("2", na=False)].copy()

            # 2. Tratamento e Mapeamento de Unidades
            df_disc["Valor_Tratado"] = df_disc[col_valor].apply(converter_valor)
            df_disc["Unidade_Consolidada"] = df_disc[col_ug_nome].astype(str).map(
                lambda x: MAPA_UNIDADES.get(x.strip(), "Outras Unidades / Administrativo")
            )

            # 3. Tradução dos PIs
            df_disc["PI_Completo"] = df_disc[col_pi_cod].astype(str) + " - " + df_disc[col_pi_nome].astype(str)
            df_disc["Conta_Gerencial"] = df_disc["PI_Completo"].map(
                lambda x: st.session_state.dicionario_pis.get(x, "Sem Classificação")
            )

            # SELETOR DE UNIDADE NO TOPO DO RELATÓRIO
            unidades_disponiveis = ["--- TOTAL DA UFSM ---"] + sorted(list(df_disc["Unidade_Consolidada"].unique()))
            unidade_selecionada = st.selectbox("🏛️ Selecione a Unidade para Análise:", unidades_disponiveis)

            # Aplicação do Filtro de Unidade
            if unidade_selecionada != "--- TOTAL DA UFSM ---":
                df_relatorio = df_disc[df_disc["Unidade_Consolidada"] == unidade_selecionada].copy()
            else:
                df_relatorio = df_disc.copy()

            # RESUMO E KPIS
            val_total = df_relatorio["Valor_Tratado"].sum()
            qtd_pis = df_relatorio["PI_Completo"].nunique()

            k1, k2, k3 = st.columns(3)
            k1.metric("Visão Selecionada", unidade_selecionada)
            k2.metric("Total Executado (Discricionário)", f"R$ {val_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            k3.metric("Planos Internos (PIs) Ativos", qtd_pis)

            st.markdown("---")

            # VISUALIZAÇÕES
            col_g, col_t = st.columns([1, 1])

            df_exec = df_relatorio.groupby("Conta_Gerencial")["Valor_Tratado"].sum().reset_index()
            df_exec.columns = ["Conta Gerencial", "Valor Total (R$)"]
            df_exec = df_exec.sort_values(by="Valor Total (R$)", ascending=False)

            with col_g:
                st.subheader("Distribuição por Conta Gerencial")
                fig = px.pie(
                    df_exec, 
                    names="Conta Gerencial", 
                    values="Valor Total (R$)", 
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_t:
                st.subheader("Resumo de Valores por Conta")
                st.dataframe(
                    df_exec.style.format({"Valor Total (R$)": "R$ {:,.2f}"}),
                    use_container_width=True,
                    height=380
                )

            st.markdown("---")
            st.subheader("🔍 Detalhamento por Plano Interno (PI)")
            df_det = df_relatorio.groupby(["Conta_Gerencial", "PI_Completo"])["Valor_Tratado"].sum().reset_index()
            df_det.columns = ["Conta Gerencial", "Plano Interno (PI)", "Valor (R$)"]
            st.dataframe(df_det.style.format({"Valor (R$)": "R$ {:,.2f}"}), use_container_width=True)
