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
# 2. BANCO DE DADOS/ESTRUTURAS PADRÃO
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

UNIDADES_UFSM_PADRAO = [
    "PRA - Pró-Reitoria de Administração",
    "PROPLAN - Pró-Reitoria de Planejamento",
    "PROGRAD - Pró-Reitoria de Graduação",
    "PRPGP - Pró-Reitoria de Pós-Graduação e Pesquisa",
    "PRE - Pró-Reitoria de Extensão",
    "PRAE - Pró-Reitoria de Assuntos Estudantis",
    "PROINFRA - Pró-Reitoria de Infraestrutura",
    "PROGEP - Pró-Reitoria de Gestão de Pessoas",
    "INOVA - Pró-Reitoria de Inovação e Empreendedorismo",
    "CAL - Centro de Artes e Letras",
    "CCNE - Centro de Ciências Naturais e Exatas",
    "CCR - Centro de Ciências Rurais",
    "CCS - Centro de Ciências da Saúde",
    "CCSH - Centro de Ciências Sociais e Humanas",
    "CE - Centro de Educação",
    "CEFD - Centro de Educação Física e Desportos",
    "CT - Centro de Tecnologia",
    "Colégio Politécnico da UFSM",
    "CTISM - Colégio Técnico Industrial de Santa Maria",
    "Campus Frederico Westphalen",
    "Campus Palmeira das Missões",
    "Campus Cachoeira do Sul",
    "Campus Silveira Martins",
    "Reitoria e Gabinete do Reitor",
    "DGA - Diretoria de Gestão Ambiental",
    "DTI / CPD - Diretoria de TI / Processamento de Dados",
    "DRI - Diretoria de Relações Internacionais",
    "Hospital Veterinário / HVU",
    "Encargos Gerais da UFSM / Outros"
]

MAPA_UGS_PADRAO = {
    "REITORIA DA UFSM": "Reitoria e Gabinete do Reitor",
    "GABINETE DO REITOR": "Reitoria e Gabinete do Reitor",
    "AUDITORIA INTERNA": "Reitoria e Gabinete do Reitor",
    "CORREGEDORIA SETORIAL DA UFSM": "Reitoria e Gabinete do Reitor",
    "COORDENADORIA DE COMUNICACAO SOCIAL": "Reitoria e Gabinete do Reitor",
    "EDITORA UFSM": "Reitoria e Gabinete do Reitor",
    "PRO-REITORIA DE ADMINISTRACAO DA UFSM": "PRA - Pró-Reitoria de Administração",
    "ALMOXARIFADO CENTRAL DA UFSM": "PRA - Pró-Reitoria de Administração",
    "UFSM-DEPARTAMENTO DE MATERIAL E PATRIMONIO": "PRA - Pró-Reitoria de Administração",
    "DEPARTAMENTO DE CONTABILIDADE E FINANCAS": "PRA - Pró-Reitoria de Administração",
    "SERVICOS DE TRANSPORTES E OFICINAS/UFSM": "PRA - Pró-Reitoria de Administração",
    "SETOR DE IMPORTACAOES DA UFSM": "PRA - Pró-Reitoria de Administração",
    "PRO-REITORIA DE PLANEJAMENTO DA UFSM": "PROPLAN - Pró-Reitoria de Planejamento",
    "COORDENADORIA DE PLANEJAMENTO INFORMACIONAL": "PROPLAN - Pró-Reitoria de Planejamento",
    "PRO-REITORIA DE GRADUACAO DA UFSM": "PROGRAD - Pró-Reitoria de Graduação",
    "DEPARTAMENTO DE REGISTRO E CONTROLE ACADEMICO": "PROGRAD - Pró-Reitoria de Graduação",
    "PRO-REITORIA DE POS-GRADUACAO E PESQUISA-UFSM": "PRPGP - Pró-Reitoria de Pós-Graduação e Pesquisa",
    "PRO-REITORIA DE EXTENSAO DA UFSM": "PRE - Pró-Reitoria de Extensão",
    "PRO-REITORIA DE INOVACAO E EMPREENDEDORISMO": "INOVA - Pró-Reitoria de Inovação e Empreendedorismo",
    "AGENCIA DE INOVACAO E TRANSFERENCIA DE TECNOLOGIA": "INOVA - Pró-Reitoria de Inovação e Empreendedorismo",
    "PROGEP": "PROGEP - Pró-Reitoria de Gestão de Pessoas",
    "PRO REITORIA DE GESTAO DE PESSOAS": "PROGEP - Pró-Reitoria de Gestão de Pessoas",
    "PRO-REITORIA DE ASSUNTOS ESTUDANTIS DA UFSM": "PRAE - Pró-Reitoria de Assuntos Estudantis",
    "RESTAURANTE UNIVERSITARIO DA UFSM": "PRAE - Pró-Reitoria de Assuntos Estudantis",
    "RESTAURANTE UNIVERSITARIO - CAMPUS PM": "PRAE - Pró-Reitoria de Assuntos Estudantis",
    "RESTAURANTE UNIVERSITARIO - CAMPUS FW": "PRAE - Pró-Reitoria de Assuntos Estudantis",
    "RESTAURANTE UNIVERSITARIO - CAMPUS CACH.SUL": "PRAE - Pró-Reitoria de Assuntos Estudantis",
    "SECRET. APOIO ADMIN. - PRAE": "PRAE - Pró-Reitoria de Assuntos Estudantis",
    "COORDENADORIA DE ACOES EDUCACIONAIS DA UFSM": "PRAE - Pró-Reitoria de Assuntos Estudantis",
    "PRO-REITORIA DE INFRAESTRUTURA - UFSM": "PROINFRA - Pró-Reitoria de Infraestrutura",
    "PRO-REITORIA DE INFRAESTRUTURA - PROINFRA": "PROINFRA - Pró-Reitoria de Infraestrutura",
    "DIRETORIA DE GESTAO AMBIENTAL": "DGA - Diretoria de Gestão Ambiental",
    "CENTRO DE PROCESSAMENTO DE DADOS DA UFSM": "DTI / CPD - Diretoria de TI / Processamento de Dados",
    "LABORATORIO DE MANUTENCAO DE INFORMATICA UFSM": "DTI / CPD - Diretoria de TI / Processamento de Dados",
    "DIRETORIA DE TI": "DTI / CPD - Diretoria de TI / Processamento de Dados",
    "DIRETORIA DE RELACOES INTERNACIONAIS": "DRI - Diretoria de Relações Internacionais",
    "CENTRO DE ARTES E LETRAS DA UFSM": "CAL - Centro de Artes e Letras",
    "CENTRO DE CIENCIAS NATURAIS E EXATAS DA UFSM": "CCNE - Centro de Ciências Naturais e Exatas",
    "CENTRO DE CIENCIAS RURAIS DA UFSM": "CCR - Centro de Ciências Rurais",
    "CENTRO DE CIENCIAS DA SAUDE DA UFSM": "CCS - Centro de Ciências da Saúde",
    "CENTRO DE CIENCIAS SOCIAIS E HUMANAS DA UFSM": "CCSH - Centro de Ciências Sociais e Humanas",
    "CENTRO EDUCACAO DA UFSM": "CE - Centro de Educação",
    "CENTRO DE EDUCACAO FISICA E DESPORTOS DA UFSM": "CEFD - Centro de Educação Física e Desportos",
    "CENTRO DE TECNOLOGIA DA UFSM": "CT - Centro de Tecnologia",
    "COLEGIO POLITECNICO DA UFSM": "Colégio Politécnico da UFSM",
    "COLEGIO TECNICO INDUSTRIAL DA UFSM": "CTISM - Colégio Técnico Industrial de Santa Maria",
    "CAMPUS DA UFSM EM FREDERICO WESTPHALEN": "Campus Frederico Westphalen",
    "CAMPUS DA UFSM EM PALMEIRAS DAS MISSOES": "Campus Palmeira das Missões",
    "CAMPUS DA UFSM EM CACHOEIRA DO SUL": "Campus Cachoeira do Sul",
    "ESPACO MULTIDISC. PESQ E EXTENS SILV MARTINS": "Campus Silveira Martins",
    "HOSPITAL DE CLINICAS VETERINARIAS DA UFSM": "Hospital Veterinário / HVU",
    "FAZENDA ESCOLA DA UFSM": "CCR - Centro de Ciências Rurais",
    "ENCARGOS GERAIS DA UFSM": "Encargos Gerais da UFSM / Outros"
}

# Inicialização da Memória do Sistema
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "carga"

if "contas_gerenciais" not in st.session_state:
    st.session_state.contas_gerenciais = PLANO_CONTAS_PADRAO.copy()

if "unidades_consolidadas" not in st.session_state:
    st.session_state.unidades_consolidadas = UNIDADES_UFSM_PADRAO.copy()

if "mapa_ugs" not in st.session_state:
    st.session_state.mapa_ugs = MAPA_UGS_PADRAO.copy()

if "dicionario_pis" not in st.session_state:
    st.session_state.dicionario_pis = {}

if "dados_tg_raw" not in st.session_state:
    st.session_state.dados_tg_raw = None

# Controle de edição inline
if "editando_unidade" not in st.session_state:
    st.session_state.editando_unidade = None

if "editando_conta" not in st.session_state:
    st.session_state.editando_conta = None

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
    # 4. MENU LATERAL POR BOTÕES COM LOGO DA UFSM
    # -----------------------------------------------------------------------------
    
    # URL da logomarca oficial da UFSM em alta definição
    LOGO_UFSM_URL = "https://upload.wikimedia.org/wikipedia/commons/e/eb/Brasao-ufsm.png"

    # Exibe a logo no topo do menu lateral (esquerda)
    st.sidebar.image(LOGO_UFSM_URL, use_container_width=True)
    
    st.sidebar.title("🏛️ PRA / UFSM")
    st.sidebar.caption("Gestão Orçamentária Executiva")
    st.sidebar.markdown("---")

    if st.sidebar.button("📁 1. Carga da Planilha", use_container_width=True, type="primary" if st.session_state.pagina_atual == "carga" else "secondary"):
        st.session_state.pagina_atual = "carga"
        st.rerun()

    if st.sidebar.button("🏛️ 2. Cadastro de Unidades & UGs", use_container_width=True, type="primary" if st.session_state.pagina_atual == "unidades" else "secondary"):
        st.session_state.pagina_atual = "unidades"
        st.rerun()

    if st.sidebar.button("🏷️ 3. Plano de Contas", use_container_width=True, type="primary" if st.session_state.pagina_atual == "contas" else "secondary"):
        st.session_state.pagina_atual = "contas"
        st.rerun()

    if st.sidebar.button("📖 4. Dicionário de PIs", use_container_width=True, type="primary" if st.session_state.pagina_atual == "dicionario" else "secondary"):
        st.session_state.pagina_atual = "dicionario"
        st.rerun()

    if st.sidebar.button("📊 5. Relatório Executivo", use_container_width=True, type="primary" if st.session_state.pagina_atual == "relatorio" else "secondary"):
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
        st.write("Faça o upload da planilha líquida/executada do Tesouro Gerencial (.xlsx ou .csv).")

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
    # PÁGINA 2: CADASTRO DE UNIDADES E MAPEAMENTO DE UGs
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "unidades":
        st.header("🏛️ Cadastro de Unidades Organizacionais & Mapeamento de UGs")
        st.write("Gestão das Unidades Institucionais e alocação de UGs da planilha.")

        tab1, tab2 = st.tabs(["📌 Cadastro de Unidades Consolidadas", "🔗 Mapeamento de UGs (Colunas F/G)"])

        with tab1:
            col_u1, col_u2 = st.columns([1, 2])
            
            with col_u1:
                st.subheader("Adicionar Nova Unidade")
                nova_u = st.text_input("Nome da Unidade Consolidada:")
                if st.button("➕ Adicionar Unidade", use_container_width=True):
                    if nova_u and nova_u not in st.session_state.unidades_consolidadas:
                        st.session_state.unidades_consolidadas.append(nova_u)
                        st.success(f"Unidade '{nova_u}' cadastrada!")
                        st.rerun()

            with col_u2:
                st.subheader(f"Unidades Cadastradas ({len(st.session_state.unidades_consolidadas)})")
                
                for idx, unidade in enumerate(st.session_state.unidades_consolidadas):
                    c_txt, c_btn_edit, c_btn_del = st.columns([5, 1, 1])
                    c_txt.write(f"• **{unidade}**")
                    
                    if c_btn_edit.button("✏️", key=f"edit_u_{idx}", help="Alterar nome da Unidade"):
                        st.session_state.editando_unidade = unidade
                        st.rerun()

                    if c_btn_del.button("🗑️", key=f"del_u_{idx}", help="Excluir Unidade"):
                        st.session_state.unidades_consolidadas.remove(unidade)
                        # Remove dos mapeamentos
                        for ug_k, val in list(st.session_state.mapa_ugs.items()):
                            if val == unidade:
                                st.session_state.mapa_ugs[ug_k] = "Encargos Gerais da UFSM / Outros"
                        st.rerun()

                    # Caixa Inline para Alteração de Nome
                    if st.session_state.editando_unidade == unidade:
                        with st.container():
                            c_in, c_save, c_canc = st.columns([4, 1, 1])
                            novo_nome_u = c_in.text_input("Novo nome:", value=unidade, key=f"inp_u_{idx}")
                            if c_save.button("Salvar", key=f"save_u_{idx}"):
                                if novo_nome_u and novo_nome_u != unidade:
                                    # 1. Atualiza na lista de Unidades
                                    st.session_state.unidades_consolidadas[idx] = novo_nome_u
                                    # 2. Atualiza em cascata o Mapeamento de UGs
                                    for ug_k, val in st.session_state.mapa_ugs.items():
                                        if val == unidade:
                                            st.session_state.mapa_ugs[ug_k] = novo_nome_u
                                    st.success("Unidade alterada com sucesso!")
                                st.session_state.editando_unidade = None
                                st.rerun()

                            if c_canc.button("Cancelar", key=f"canc_u_{idx}"):
                                st.session_state.editando_unidade = None
                                st.rerun()

        with tab2:
            st.subheader("Alocação de Unidades Gestoras (UGs SIAFI -> Unidade Consolidada)")
            
            ugs_para_mapear = set(st.session_state.mapa_ugs.keys())

            if st.session_state.dados_tg_raw is not None:
                df_raw = st.session_state.dados_tg_raw
                cols = list(df_raw.columns)
                col_ug_nom = cols[6] if len(cols) > 6 else cols[0]
                ugs_planilha = df_raw[col_ug_nom].dropna().unique()
                for ug_p in ugs_planilha:
                    ugs_para_mapear.add(str(ug_p).strip())

            st.write(f"**Total de UGs identificadas:** {len(ugs_para_mapear)}")

            col_b1, col_b2 = st.columns([2, 1])
            with col_b1:
                st.caption("Associe cada UG do SIAFI/Tesouro Gerencial a uma das Unidades Consolidadas:")
            with col_b2:
                if st.button("Restaurar Mapeamento Padrão"):
                    st.session_state.mapa_ugs = MAPA_UGS_PADRAO.copy()
                    st.success("Mapeamento restaurado!")
                    st.rerun()

            for ug_item in sorted(list(ugs_para_mapear)):
                c_ug, c_sel = st.columns([2, 2])
                c_ug.write(f"🏢 **{ug_item}**")
                
                def_val = st.session_state.mapa_ugs.get(ug_item, "Encargos Gerais da UFSM / Outros")
                if def_val not in st.session_state.unidades_consolidadas:
                    st.session_state.unidades_consolidadas.append(def_val)

                idx_u = st.session_state.unidades_consolidadas.index(def_val)

                nova_aloc = c_sel.selectbox(
                    "Alocar para:",
                    st.session_state.unidades_consolidadas,
                    index=idx_u,
                    key=f"ug_map_{ug_item}"
                )
                st.session_state.mapa_ugs[ug_item] = nova_aloc

    # -----------------------------------------------------------------------------
    # PÁGINA 3: PLANO DE CONTAS CONTÁBEIS
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "contas":
        st.header("🏷️ Estrutura do Plano de Contas Gerenciais")
        st.write("Plano de contas gerenciais para apresentação à Alta Gestão.")

        col_add, col_list = st.columns([1, 2])

        with col_add:
            st.subheader("Adicionar Nova Conta")
            nova_conta = st.text_input("Nome/Código da Conta:")
            if st.button("➕ Adicionar Conta", use_container_width=True):
                if nova_conta and nova_conta not in st.session_state.contas_gerenciais:
                    st.session_state.contas_gerenciais.append(nova_conta)
                    st.success(f"Conta '{nova_conta}' adicionada!")
                    st.rerun()

        with col_list:
            st.subheader(f"Plano de Contas Ativo ({len(st.session_state.contas_gerenciais)})")
            
            for idx, conta in enumerate(st.session_state.contas_gerenciais):
                c_nome, c_edit, c_del = st.columns([5, 1, 1])
                c_nome.write(f"• **{conta}**")
                
                if c_edit.button("✏️", key=f"edit_c_{idx}", help="Alterar nome da Conta"):
                    st.session_state.editando_conta = conta
                    st.rerun()

                if c_del.button("🗑️", key=f"del_c_{idx}", help="Excluir Conta"):
                    st.session_state.contas_gerenciais.remove(conta)
                    # Remove dos mapeamentos do dicionário de PIs
                    for pi_k, val in list(st.session_state.dicionario_pis.items()):
                        if val == conta:
                            st.session_state.dicionario_pis[pi_k] = "Sem Classificação"
                    st.rerun()

                # Caixa Inline para Alteração de Nome
                if st.session_state.editando_conta == conta:
                    with st.container():
                        c_in, c_save, c_canc = st.columns([4, 1, 1])
                        novo_nome_c = c_in.text_input("Novo nome:", value=conta, key=f"inp_c_{idx}")
                        if c_save.button("Salvar", key=f"save_c_{idx}"):
                            if novo_nome_c and novo_nome_c != conta:
                                # 1. Atualiza na lista de contas
                                st.session_state.contas_gerenciais[idx] = novo_nome_c
                                # 2. Atualiza em cascata no Dicionário de PIs
                                for pi_k, val in st.session_state.dicionario_pis.items():
                                    if val == conta:
                                        st.session_state.dicionario_pis[pi_k] = novo_nome_c
                                st.success("Conta alterada com sucesso!")
                            st.session_state.editando_conta = None
                            st.rerun()

                        if c_canc.button("Cancelar", key=f"canc_c_{idx}"):
                            st.session_state.editando_conta = None
                            st.rerun()

    # -----------------------------------------------------------------------------
    # PÁGINA 4: DICIONÁRIO DE PIs
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "dicionario":
        st.header("📖 Dicionário de Mapeamento dos PIs")
        st.write("Mapeamento automático e manual de Planos Internos (SIAFI) para as Contas Gerenciais.")

        if st.session_state.dados_tg_raw is None:
            st.warning("⚠️ Carregue a planilha na aba '1. Carga da Planilha' para listar os PIs do relatório.")
        else:
            df = st.session_state.dados_tg_raw
            colunas = list(df.columns)
            
            col_pi_cod = colunas[11] if len(colunas) > 11 else colunas[0]
            col_pi_nome = colunas[12] if len(colunas) > 12 else col_pi_cod

            df_pis = df[[col_pi_cod, col_pi_nome]].drop_duplicates().dropna()
            df_pis["PI_Completo"] = df_pis[col_pi_cod].astype(str).str.strip() + " - " + df_pis[col_pi_nome].astype(str).str.strip()
            lista_pis = sorted(df_pis["PI_Completo"].unique())

            st.write(f"**Total de PIs únicos identificados na planilha:** {len(lista_pis)}")

            for pi_item in lista_pis:
                col_lbl, col_sel = st.columns([2, 2])
                col_lbl.write(f"📌 **{pi_item}**")
                
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
    # PÁGINA 5: RELATÓRIO EXECUTIVO
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "relatorio":
        st.header("📊 Relatório Executivo de Despesas Discricionárias")

        if st.session_state.dados_tg_raw is None:
            st.info("👋 Por favor, faça a carga do arquivo na aba **'1. Carga da Planilha'** para acessar os relatórios.")
        else:
            df = st.session_state.dados_tg_raw
            colunas = list(df.columns)

            col_resultado_lei = colunas[2] if len(colunas) > 2 else colunas[0]   # Coluna C
            col_ug_nome = colunas[6] if len(colunas) > 6 else colunas[0]         # Coluna G
            col_pi_cod = colunas[11] if len(colunas) > 11 else colunas[0]        # Coluna L
            col_pi_nome = colunas[12] if len(colunas) > 12 else col_pi_cod      # Coluna M
            col_valor = colunas[19] if len(colunas) > 19 else colunas[-1]       # Coluna T

            # 1. Filtro: Recursos Discricionários (Coluna C contém "2")
            df_disc = df[df[col_resultado_lei].astype(str).str.contains("2", na=False)].copy()

            # 2. Tratamento e Mapeamento
            df_disc["Valor_Tratado"] = df_disc[col_valor].apply(converter_valor)
            
            # Normalização e busca na tabela de mapeamentos
            df_disc["Unidade_Consolidada"] = df_disc[col_ug_nome].astype(str).map(
                lambda x: st.session_state.mapa_ugs.get(x.strip(), "Encargos Gerais da UFSM / Outros")
            )

            # 3. Tradução dos PIs
            df_disc["PI_Completo"] = df_disc[col_pi_cod].astype(str).str.strip() + " - " + df_disc[col_pi_nome].astype(str).str.strip()
            df_disc["Conta_Gerencial"] = df_disc["PI_Completo"].map(
                lambda x: st.session_state.dicionario_pis.get(x, "Sem Classificação")
            )

            # 4. CARREGAMENTO DO SELETOR COM TODAS AS UNIDADES CADASTRADAS NO SISTEMA
            lista_unidades_select = ["--- TOTAL DA UFSM ---"] + sorted(st.session_state.unidades_consolidadas)
            unidade_selecionada = st.selectbox("🏛️ Selecione a Unidade para Análise:", lista_unidades_select)

            if unidade_selecionada != "--- TOTAL DA UFSM ---":
                df_relatorio = df_disc[df_disc["Unidade_Consolidada"] == unidade_selecionada].copy()
            else:
                df_relatorio = df_disc.copy()

            val_total = df_relatorio["Valor_Tratado"].sum()
            qtd_pis = df_relatorio["PI_Completo"].nunique()

            k1, k2, k3 = st.columns(3)
            k1.metric("Visão Selecionada", unidade_selecionada)
            k2.metric("Total Executado (Discricionário)", f"R$ {val_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            k3.metric("Planos Internos (PIs) Ativos", qtd_pis if val_total > 0 else 0)

            st.markdown("---")

            if df_relatorio.empty or val_total == 0:
                st.info(f"Nenhum valor ou lançamento financeiro foi encontrado para a unidade **'{unidade_selecionada}'** na planilha do Tesouro Gerencial fornecida.")
            else:
                col_g, col_t = st.columns([1, 1])

                df_exec = df_relatorio.groupby("Conta_Gerencial")["Valor_Tratado"].sum().reset_index()
                df_exec.columns = ["Conta Gerencial", "Valor Total (R$)"]
                df_exec = df_exec[df_exec["Valor Total (R$)"] > 0].sort_values(by="Valor Total (R$)", ascending=False)

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
                df_det = df_det[df_det["Valor (R$)"] > 0].sort_values(by="Valor (R$)", ascending=False)
                st.dataframe(df_det.style.format({"Valor (R$)": "R$ {:,.2f}"}), use_container_width=True)
