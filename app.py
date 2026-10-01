import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine
from supabase import create_client, Client

# -----------------------------------------------------------------------------
# CONEXÃO E BANCO DE DADOS SUPABASE (SECRETS STREAMLIT)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

@st.cache_resource
def get_db_engine():
    db_url = st.secrets["DATABASE_URL"]
    return create_engine(db_url)

def carregar_dados_para_supabase(df: pd.DataFrame, nome_tabela: str = "tb_execucao_despesa"):
    engine = get_db_engine()
    df.to_sql(nome_tabela, con=engine, if_exists="append", index=False, chunksize=2000)

def executar_consulta_sql(query: str) -> pd.DataFrame:
    engine = get_db_engine()
    return pd.read_sql_query(query, con=engine)

def executar_comando_sql(query: str, params: dict = None):
    engine = get_db_engine()
    with engine.begin() as conn:
        if params:
            from sqlalchemy import text
            conn.execute(text(query), params)
        else:
            from sqlalchemy import text
            conn.execute(text(query))

# -----------------------------------------------------------------------------
# FUNÇÕES DE CRUD PARA A TABELA PUBLIC.TB_UGS
# -----------------------------------------------------------------------------
def buscar_ugs_banco():
    try:
        query = "SELECT codigo_ug, nome, sigla, ativo, criado_em FROM public.tb_ugs ORDER BY codigo_ug ASC;"
        return executar_consulta_sql(query)
    except Exception as e:
        st.error(f"Erro ao consultar tb_ugs no Supabase: {e}")
        return pd.DataFrame()

def inserir_ug_banco(codigo_ug: str, nome: str, sigla: str, ativo: bool):
    query = """
    INSERT INTO public.tb_ugs (codigo_ug, nome, sigla, ativo)
    VALUES (:codigo_ug, :nome, :sigla, :ativo);
    """
    executar_comando_sql(query, {"codigo_ug": codigo_ug, "nome": nome, "sigla": sigla, "ativo": ativo})

def atualizar_ug_banco(codigo_ug_orig: str, codigo_ug_novo: str, nome: str, sigla: str, ativo: bool):
    query = """
    UPDATE public.tb_ugs
    SET codigo_ug = :codigo_ug_novo, nome = :nome, sigla = :sigla, ativo = :ativo
    WHERE codigo_ug = :codigo_ug_orig;
    """
    executar_comando_sql(query, {
        "codigo_ug_orig": codigo_ug_orig,
        "codigo_ug_novo": codigo_ug_novo,
        "nome": nome,
        "sigla": sigla,
        "ativo": ativo
    })

def excluir_ug_banco(codigo_ug: str):
    query = "DELETE FROM public.tb_ugs WHERE codigo_ug = :codigo_ug;"
    executar_comando_sql(query, {"codigo_ug": codigo_ug})

# -----------------------------------------------------------------------------
# FUNÇÕES DE CRUD PARA PUBLIC.TB_NATUREZA_DESPESA_DETALHADA (CORRIGIDAS SEM "ID")
# -----------------------------------------------------------------------------
def buscar_ndd_banco():
    try:
        query = "SELECT codigo_ndd, descricao, grupo_despesa, ativo, criado_em FROM public.tb_natureza_despesa_detalhada ORDER BY codigo_ndd ASC;"
        return executar_consulta_sql(query)
    except Exception as e:
        st.error(f"Erro ao consultar tb_natureza_despesa_detalhada: {e}")
        return pd.DataFrame()

def inserir_ndd_banco(codigo_ndd: str, descricao: str, grupo_despesa: str, ativo: bool):
    query = """
    INSERT INTO public.tb_natureza_despesa_detalhada (codigo_ndd, descricao, grupo_despesa, ativo)
    VALUES (:codigo_ndd, :descricao, :grupo_despesa, :ativo);
    """
    executar_comando_sql(query, {"codigo_ndd": codigo_ndd, "descricao": descricao, "grupo_despesa": grupo_despesa, "ativo": ativo})

def atualizar_ndd_banco(codigo_ndd_orig: str, codigo_ndd_novo: str, descricao: str, grupo_despesa: str, ativo: bool):
    query = """
    UPDATE public.tb_natureza_despesa_detalhada
    SET codigo_ndd = :codigo_ndd_novo, descricao = :descricao, grupo_despesa = :grupo_despesa, ativo = :ativo
    WHERE codigo_ndd = :codigo_ndd_orig;
    """
    executar_comando_sql(query, {
        "codigo_ndd_orig": codigo_ndd_orig,
        "codigo_ndd_novo": codigo_ndd_novo,
        "descricao": descricao,
        "grupo_despesa": grupo_despesa,
        "ativo": ativo
    })

def excluir_ndd_banco(codigo_ndd: str):
    query = "DELETE FROM public.tb_natureza_despesa_detalhada WHERE codigo_ndd = :codigo_ndd;"
    executar_comando_sql(query, {"codigo_ndd": codigo_ndd})

# -----------------------------------------------------------------------------
# FUNÇÕES DE CRUD PARA PUBLIC.TB_CONTAS_GERENCIAIS
# -----------------------------------------------------------------------------
def buscar_contas_gerenciais_banco():
    try:
        query = """
        SELECT codigo_conta, nivel, nome_conta, codigo_ndd, ativo, criado_em
        FROM public.tb_contas_gerenciais
        ORDER BY codigo_conta ASC;
        """
        return executar_consulta_sql(query)
    except Exception as e:
        st.error(f"Erro ao consultar tb_contas_gerenciais: {e}")
        return pd.DataFrame()

def inserir_conta_gerencial_banco(codigo_conta: str, nome_conta: str, nivel: str, ativo: bool, codigo_ndd: str = None):
    query = """
    INSERT INTO public.tb_contas_gerenciais (codigo_conta, nome_conta, nivel, ativo, codigo_ndd)
    VALUES (:codigo_conta, :nome_conta, :nivel, :ativo, :codigo_ndd);
    """
    executar_comando_sql(query, {
        "codigo_conta": codigo_conta,
        "nome_conta": nome_conta,
        "nivel": nivel,
        "ativo": ativo,
        "codigo_ndd": codigo_ndd
    })

def atualizar_conta_gerencial_banco(codigo_conta_orig: str, codigo_conta_novo: str, nome_conta: str, nivel: str, ativo: bool, codigo_ndd: str = None):
    query = """
    UPDATE public.tb_contas_gerenciais
    SET codigo_conta = :codigo_conta_novo, nome_conta = :nome_conta, nivel = :nivel, ativo = :ativo, codigo_ndd = :codigo_ndd
    WHERE codigo_conta = :codigo_conta_orig;
    """
    executar_comando_sql(query, {
        "codigo_conta_orig": codigo_conta_orig,
        "codigo_conta_novo": codigo_conta_novo,
        "nome_conta": nome_conta,
        "nivel": nivel,
        "ativo": ativo,
        "codigo_ndd": codigo_ndd
    })

def excluir_conta_gerencial_banco(codigo_conta: str):
    query = "DELETE FROM public.tb_contas_gerenciais WHERE codigo_conta = :codigo_conta;"
    executar_comando_sql(query, {"codigo_conta": codigo_conta})

# -----------------------------------------------------------------------------
# 1. INICIALIZAÇÃO DA SESSÃO
# -----------------------------------------------------------------------------
if "logo_personalizada" not in st.session_state:
    st.session_state.logo_personalizada = None

icone_aba = st.session_state.logo_personalizada if st.session_state.logo_personalizada is not None else "🏛️"

st.set_page_config(
    page_title="SiGeO - Sistema de Gestão Orçamentária",
    page_icon=icone_aba,
    layout="wide"
)

# Customização CSS para impressão, menu lateral e botões do relatório
st.markdown("""
    <style>
    div[data-testid="stSidebar"] button {
        width: 100%;
        border-radius: 6px;
        height: 2.8em;
        font-weight: bold;
        margin-bottom: 4px;
    }

    div[data-testid="stColumn"] button[kind="secondary"] {
        padding: 0px !important;
        line-height: 1 !important;
    }

    @media print {
        [data-testid="stSidebar"], 
        header, 
        footer, 
        .stButton, 
        .stSelectbox,
        .no-print {
            display: none !important;
        }
        
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            width: 100% !important;
        }
        
        body {
            background-color: white !important;
            color: black !important;
        }
    }
    
    .cabecalho-impressao {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 2px solid #003366;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    .titulo-impressao h2 {
        margin: 0;
        color: #003366;
        font-size: 22px;
    }
    .titulo-impressao h4 {
        margin: 4px 0 0 0;
        color: #555555;
        font-size: 14px;
        font-weight: normal;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BANCO DE DADOS/ESTRUTURAS PADRÃO
# -----------------------------------------------------------------------------

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

USUARIOS_PADRAO = [
    {"usuario": "admin", "nome": "Administrador Geral", "senha": "ufsm2026", "perfil": "Administrador"},
    {"usuario": "pra_gestor", "nome": "Gestor PRA", "senha": "pra123", "perfil": "Gestor"},
]

# Inicialização da Memória do Sistema
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "carga"

if "unidades_consolidadas" not in st.session_state:
    st.session_state.unidades_consolidadas = UNIDADES_UFSM_PADRAO.copy()

if "mapa_ugs" not in st.session_state:
    st.session_state.mapa_ugs = MAPA_UGS_PADRAO.copy()

if "tabela_usuarios" not in st.session_state:
    st.session_state.tabela_usuarios = USUARIOS_PADRAO.copy()

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "dicionario_pis" not in st.session_state:
    st.session_state.dicionario_pis = {}

if "dados_tg_raw" not in st.session_state:
    st.session_state.dados_tg_raw = None

if "tot_expandidos_set" not in st.session_state:
    st.session_state.tot_expandidos_set = set()

if "editando_codigo_ug" not in st.session_state:
    st.session_state.editando_codigo_ug = None

if "editando_codigo_conta" not in st.session_state:
    st.session_state.editando_codigo_conta = None

if "editando_codigo_ndd" not in st.session_state:
    st.session_state.editando_codigo_ndd = None

# -----------------------------------------------------------------------------
# 3. AUTENTICAÇÃO
# -----------------------------------------------------------------------------
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("SiGeO - Sistema de Gestão Orçamentária")
        st.subheader("Acesso ao Sistema")
        
        c_user, c_pass = st.columns(2)
        usuario_input = c_user.text_input("Usuário:")
        senha_input = c_pass.text_input("Senha:", type="password")
        
        if st.button("Entrar", type="primary"):
            usuario_encontrado = None
            for u in st.session_state.tabela_usuarios:
                if u["usuario"].lower() == usuario_input.strip().lower() and u["senha"] == senha_input:
                    usuario_encontrado = u
                    break
            
            if usuario_encontrado:
                st.session_state.autenticado = True
                st.session_state.usuario_logado = usuario_encontrado
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        return False
    return True

if verificar_senha():

    # -----------------------------------------------------------------------------
    # 4. MENU LATERAL REORGANIZADO
    # -----------------------------------------------------------------------------
    
    if st.session_state.logo_personalizada is not None:
        st.sidebar.image(st.session_state.logo_personalizada, use_container_width=True)
    
    st.sidebar.title("SiGeO - Sistema de Gestão Orçamentária")
    st.sidebar.caption(f"Usuário: **{st.session_state.usuario_logado['nome']}** ({st.session_state.usuario_logado['perfil']})")
    
    if st.sidebar.button("🚪 Sair / Logout"):
        st.session_state.autenticado = False
        st.session_state.usuario_logado = None
        st.rerun()

    st.sidebar.markdown("---")

    if st.sidebar.button("📁 1. Carga da Planilha", use_container_width=True, type="primary" if st.session_state.pagina_atual == "carga" else "secondary"):
        st.session_state.pagina_atual = "carga"
        st.rerun()

    # Grupo Relatórios
    with st.sidebar.expander("📊 Relatórios", expanded=False):
        if st.button("📈 Execução Orçamentária", use_container_width=True, type="primary" if st.session_state.pagina_atual == "relatorio" else "secondary"):
            st.session_state.pagina_atual = "relatorio"
            st.rerun()

    # Grupo Configurações
    with st.sidebar.expander("⚙️ Configurações", expanded=False):
        if st.button("📌 Cadastro de Unidades Gestoras (UGs)", use_container_width=True, type="primary" if st.session_state.pagina_atual == "unidades_consolidadas" else "secondary"):
            st.session_state.pagina_atual = "unidades_consolidadas"
            st.rerun()

        if st.button("🔗 Mapeamento de UGs", use_container_width=True, type="primary" if st.session_state.pagina_atual == "mapeamento_ugs" else "secondary"):
            st.session_state.pagina_atual = "mapeamento_ugs"
            st.rerun()

        if st.button("🏷️ Contas Gerenciais", use_container_width=True, type="primary" if st.session_state.pagina_atual == "contas" else "secondary"):
            st.session_state.pagina_atual = "contas"
            st.rerun()

        if st.button("👤 Cadastro de Usuários", use_container_width=True, type="primary" if st.session_state.pagina_atual == "usuarios" else "secondary"):
            st.session_state.pagina_atual = "usuarios"
            st.rerun()

        if st.button("🎨 Configuração Visual", use_container_width=True, type="primary" if st.session_state.pagina_atual == "config" else "secondary"):
            st.session_state.pagina_atual = "config"
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
        st.header("📁 Carga do Relatório do Tesouro Gerencial e Gravação no Supabase")
        st.write("Faça o upload da planilha líquida/executada do Tesouro Gerencial (.xlsx ou .csv) para carregar na memória ou gravar na nuvem Supabase.")

        arquivo = st.file_uploader("Selecione o arquivo da UFSM", type=["csv", "xlsx"])

        if arquivo is not None:
            try:
                if arquivo.name.endswith(".csv"):
                    try: df = pd.read_csv(arquivo, sep=";", encoding="latin1")
                    except: df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)
                
                colunas = list(df.columns)

                def buscar_col(termos, default_idx):
                    for col in colunas:
                        for t in termos:
                            if t.lower() in str(col).lower():
                                return col
                    return colunas[default_idx] if len(colunas) > default_idx else colunas[0]

                col_ex = buscar_col(["exercício", "exercicio", "ano"], 0)
                col_mes = buscar_col(["mês", "mes", "competência", "periodo"], 1)
                col_ug = buscar_col(["ug", "unidade gestora"], 6 if len(colunas) > 6 else 0)
                col_nd = buscar_col(["natureza de despesa detalhada", "nd", "código nd", "codigo nd"], 11 if len(colunas) > 11 else 0)
                col_desc_nd = buscar_col(["descrição nd", "descricao nd", "nome nd"], 12 if len(colunas) > 12 else 0)
                col_val = buscar_col(["valor", "liquidado", "pago", "executado"], -1)

                df_tratado = pd.DataFrame()
                df_tratado["exercicio"] = pd.to_numeric(df[col_ex], errors="coerce").fillna(datetime.now().year).astype(int)
                df_tratado["mes_competencia"] = pd.to_datetime(df[col_mes].astype(str), errors="coerce").dt.month.fillna(1).astype(int)
                df_tratado["ug_responsavel"] = df[col_ug].astype(str).str.strip()
                df_tratado["natureza_despesa_detalhada"] = df[col_nd].astype(str).str.strip()
                df_tratado["descricao_nd"] = df[col_desc_nd].astype(str).str.strip()
                df_tratado["valor_liquidado"] = df[col_val].apply(converter_valor)

                st.session_state.dados_tg_raw = df
                st.success(f"Arquivo carregado e tratado com sucesso! {len(df_tratado):,} linhas identificadas na memória.")
                st.dataframe(df_tratado.head(5), use_container_width=True)

                st.markdown("---")
                st.subheader("🚀 PASSO 3: Exportação e Carga Massiva para o Supabase")
                st.caption("Grave esta planilha na tabela `tb_execucao_despesa` do seu banco de dados na nuvem Supabase.")

                if st.button("🚀 Gravar Dados no Supabase", type="primary"):
                    with st.spinner("Enviando lotes de dados para o Supabase..."):
                        carregar_dados_para_supabase(df_tratado, "tb_execucao_despesa")
                        st.success("🎉 Carga concluída com sucesso no banco de dados Supabase!")

            except Exception as e:
                st.error(f"Erro ao ler/enviar o arquivo: {e}")

        elif st.session_state.dados_tg_raw is not None:
            st.info("Já existe uma planilha carregada na memória local do sistema.")
            if st.button("Remover e Enviar Nova Planilha"):
                st.session_state.dados_tg_raw = None
                st.rerun()

    # -----------------------------------------------------------------------------
    # PÁGINA 2: RELATÓRIO DE EXECUÇÃO ORÇAMENTÁRIA
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "relatorio":
        c_head1, c_head2 = st.columns([1, 4])
        with c_head1:
            if st.session_state.logo_personalizada is not None:
                st.image(st.session_state.logo_personalizada, width=130)
            else:
                st.write("🏛️ **UFSM**")
        with c_head2:
            st.markdown(f"""
                <div class="titulo-impressao">
                    <h2>UNIVERSIDADE FEDERAL DE SANTA MARIA - UFSM</h2>
                    <h4>PRÓ-REITORIA DE ADMINISTRAÇÃO - EXECUÇÃO ORÇAMENTÁRIA</h4>
                    <p style="margin:2px 0 0 0; font-size:12px; color:#777;">Emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        fonte_dados = st.radio("📡 Fonte dos Dados do Relatório:", ["Banco de Dados Supabase (Nuvem / SQL)", "Planilha em Memória (Upload Local)"], horizontal=True)

        if fonte_dados == "Banco de Dados Supabase (Nuvem / SQL)":
            st.subheader("📊 Demonstrativo Financeiro Comparativo (Consulta SQL Directa do Supabase)")
            
            c_a1, c_a2 = st.columns(2)
            ano_atual_sel = c_a1.number_input("Ano Atual:", value=datetime.now().year, step=1)
            ano_ant_sel = c_a2.number_input("Ano Comparativo:", value=datetime.now().year - 1, step=1)

            if st.button("🔍 Executar Consulta SQL no Supabase", type="primary"):
                with st.spinner("Buscando e processando dados diretamente do Supabase..."):
                    try:
                        query_relatorio = f"""
                        SELECT 
                            COALESCE(cg.nivel, 'Nível 1') AS "Nível",
                            COALESCE(cg.codigo_conta, 'S/C') AS "Código",
                            COALESCE(cg.nome_conta, e.natureza_despesa_detalhada) AS "Conta Gerencial",
                            SUM(CASE WHEN e.exercicio = {ano_ant_sel} THEN e.valor_liquidado ELSE 0 END) AS "Ano Anterior",
                            SUM(CASE WHEN e.exercicio = {ano_atual_sel} THEN e.valor_liquidado ELSE 0 END) AS "Ano Atual"
                        FROM tb_execucao_despesa e
                        LEFT JOIN tb_natureza_despesa_detalhada ndd ON e.natureza_despesa_detalhada = ndd.codigo_ndd
                        LEFT JOIN tb_contas_gerenciais cg ON cg.codigo_ndd = ndd.codigo_ndd OR cg.codigo_conta = ndd.codigo_ndd
                        WHERE e.exercicio IN ({ano_ant_sel}, {ano_atual_sel})
                        GROUP BY "Nível", "Código", "Conta Gerencial"
                        ORDER BY "Código" ASC, "Conta Gerencial" ASC;
                        """
                        
                        df_relatorio_sql = executar_consulta_sql(query_relatorio)

                        if df_relatorio_sql.empty:
                            st.warning("Nenhum registro encontrado no Supabase para os anos selecionados.")
                        else:
                            df_relatorio_sql['Variação (%)'] = (
                                (df_relatorio_sql['Ano Atual'] - df_relatorio_sql['Ano Anterior']) 
                                / df_relatorio_sql['Ano Anterior'].replace(0, float('nan'))
                            ) * 100.0

                            st.dataframe(
                                df_relatorio_sql.style.format({
                                    'Ano Anterior': 'R$ {:,.2f}',
                                    'Ano Atual': 'R$ {:,.2f}',
                                    'Variação (%)': '{:+.2f}%'
                                }),
                                use_container_width=True
                            )

                    except Exception as e:
                        st.error(f"Erro ao consultar o Supabase: {e}")

        else:
            if st.session_state.dados_tg_raw is None:
                st.info("👋 Por favor, faça a carga do arquivo na aba **'1. Carga da Planilha'** para acessar os relatórios.")
            else:
                df = st.session_state.dados_tg_raw.copy()
                colunas = list(df.columns)

                def encontrar_coluna(termos_busca, indice_padrao):
                    for col in colunas:
                        for termo in termos_busca:
                            if termo.lower() in str(col).lower():
                                return col
                    return colunas[indice_padrao] if len(colunas) > indice_padrao else colunas[0]

                col_mes_ref = encontrar_coluna(["mês", "mes", "referencia", "referência", "período", "periodo"], 1)
                col_resultado_lei = encontrar_coluna(["resultado", "lei", "rp", "fonte"], 2)
                col_ug_nome = encontrar_coluna(["ug", "unidade gestora", "nome ug", "gestora"], 6 if len(colunas)>6 else 0)
                col_pi_cod = encontrar_coluna(["código pi", "codigo pi", "pi"], 11 if len(colunas)>11 else 0)
                col_pi_nome = me = encontrar_coluna(["nome pi", "descrição pi", "plano interno"], 12 if len(colunas)>12 else 0)
                col_valor = encontrar_coluna(["valor", "executado", "pago", "liquidado", "saldo"], -1)

                mascara_lei = df[col_resultado_lei].astype(str).str.contains("2", na=False)
                df_disc = df[mascara_lei].copy() if mascara_lei.sum() > 0 else df.copy()

                df_disc["Valor_Tratado"] = df_disc[col_valor].apply(converter_valor)
                
                df_disc["Unidade_Consolidada"] = df_disc[col_ug_nome].astype(str).str.strip().map(
                    lambda x: st.session_state.mapa_ugs.get(x, "CCSH - Centro de Ciências Sociais e Humanas" if "SOCIAL" in x or "HUMANA" in x else "Encargos Gerais da UFSM / Outros")
                )
                
                df_disc["PI_Completo"] = df_disc[col_pi_cod].astype(str).str.strip() + " - " + df_disc[col_pi_nome].astype(str).str.strip()
                
                df_disc["Conta_Gerencial"] = df_disc["PI_Completo"].map(
                    lambda x: st.session_state.dicionario_pis.get(x, "Outras Despesas Operacionais")
                )

                df_disc["Data_Ref"] = pd.to_datetime(df_disc[col_mes_ref], errors='coerce', dayfirst=True)
                if df_disc["Data_Ref"].isna().all():
                    df_disc["Data_Ref"] = pd.to_datetime(df_disc[col_mes_ref].astype(str), format='%m/%Y', errors='coerce')

                df_disc["Ano_Mes"] = df_disc["Data_Ref"].dt.to_period("M")

                meses_siglas = {
                    1: "JAN", 2: "FEV", 3: "MAR", 4: "ABR", 5: "MAI", 6: "JUN",
                    7: "JUL", 8: "AGO", 9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ"
                }
                
                def fmt_mmm_aaaa(periodo):
                    if pd.isna(periodo): return ""
                    return f"{meses_siglas[periodo.month]}/{periodo.year}"

                # CONTROLES DE FILTRO
                c_flag, c_unid, c_mes, c_imp = st.columns([1.5, 2, 2, 1])

                with c_flag:
                    tipo_visao = st.radio("📌 Visão do Relatório:", ["Mensal", "Anual"], horizontal=True)

                with c_unid:
                    lista_unidades_select = ["--- TOTAL DA UFSM ---"] + sorted(st.session_state.unidades_consolidadas)
                    unidade_selecionada = st.selectbox("🏛️ Unidade:", lista_unidades_select)

                df_filtrado_unidade = df_disc.copy()
                if unidade_selecionada != "--- TOTAL DA UFSM ---":
                    df_filtrado_unidade = df_filtrado_unidade[df_filtrado_unidade["Unidade_Consolidada"] == unidade_selecionada]

                periodos_disponiveis = sorted([p for p in df_filtrado_unidade["Ano_Mes"].dropna().unique()], reverse=True)
                
                with c_mes:
                    if periodos_disponiveis:
                        periodo_sel = st.selectbox(
                            "📅 Mês de Referência:", 
                            periodos_disponiveis, 
                            format_func=fmt_mmm_aaaa
                        )
                    else:
                        periodo_sel = None
                        st.warning("Nenhuma data válida encontrada na planilha.")

                with c_imp:
                    st.write(" ")
                    if st.button("🖨️ Imprimir / PDF", type="primary", use_container_width=True):
                        st.components.v1.html("<script>window.parent.print();</script>", height=0, width=0)

                st.markdown("---")

                if periodo_sel is not None:
                    # Busca a lista de contas diretamente da tabela no Supabase para montar a hierarquia
                    df_contas_cg = buscar_contas_gerenciais_banco()
                    
                    if not df_contas_cg.empty:
                        niveis_lista = sorted(df_contas_cg["nivel"].dropna().unique().tolist())
                    else:
                        niveis_lista = ["1", "2"]

                    if tipo_visao == "Mensal":
                        p0, p1, p2, p3 = periodo_sel, periodo_sel - 1, periodo_sel - 2, periodo_sel - 12
                        
                        lbl_0 = f"{fmt_mmm_aaaa(p0)} (R$)"
                        lbl_1 = f"{fmt_mmm_aaaa(p1)} (R$)"
                        var_1_str = f"Var. % ({fmt_mmm_aaaa(p0)} vs {fmt_mmm_aaaa(p1)})"
                        lbl_2 = f"{fmt_mmm_aaaa(p2)} (R$)"
                        var_2_str = f"Var. % ({fmt_mmm_aaaa(p1)} vs {fmt_mmm_aaaa(p2)})"
                        lbl_3 = f"{fmt_mmm_aaaa(p3)} (R$)"
                        var_3_str = f"Var. % ({fmt_mmm_aaaa(p0)} vs {fmt_mmm_aaaa(p3)})"

                        df0 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == p0]
                        df1 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == p1]
                        df2 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == p2]
                        df3 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == p3]

                        s0 = df0.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s1 = df1.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s2 = df2.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s3 = df3.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()

                        cols_valores = [lbl_0, lbl_1, lbl_2, lbl_3]
                        cols_cabecalho = ["Estrutura Gerencial / Nível", lbl_0, lbl_1, var_1_str, lbl_2, var_2_str, lbl_3, var_3_str]
                        larguras_colunas = [3.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2]
                        dict_somas = {lbl_0: s0, lbl_1: s1, lbl_2: s2, lbl_3: s3}
                        mapeamento_var = {var_1_str: (lbl_0, lbl_1), var_2_str: (lbl_1, lbl_2), var_3_str: (lbl_0, lbl_3)}

                    else:
                        ano_atual, mes_ref_num = periodo_sel.year, periodo_sel.month
                        ano_1, ano_2 = ano_atual - 1, ano_atual - 2
                        sigla_mes = meses_siglas[mes_ref_num]

                        lbl_0 = f"JAN-{sigla_mes}/{ano_atual} (R$)"
                        lbl_1 = f"JAN-{sigla_mes}/{ano_1} (R$)"
                        var_1_str = f"Var. % ({ano_atual} vs {ano_1})"
                        lbl_2 = f"JAN-{sigla_mes}/{ano_2} (R$)"
                        var_2_str = f"Var. % ({ano_1} vs {ano_2})"

                        df0 = df_filtrado_unidade[(df_filtrado_unidade["Ano_Mes"].dt.year == ano_atual) & (df_filtrado_unidade["Ano_Mes"].dt.month <= mes_ref_num)]
                        df1 = df_filtrado_unidade[(df_filtrado_unidade["Ano_Mes"].dt.year == ano_1) & (df_filtrado_unidade["Ano_Mes"].dt.month <= mes_ref_num)]
                        df2 = df_filtrado_unidade[(df_filtrado_unidade["Ano_Mes"].dt.year == ano_2) & (df_filtrado_unidade["Ano_Mes"].dt.month <= mes_ref_num)]

                        s0 = df0.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s1 = df1.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s2 = df2.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()

                        cols_valores = [lbl_0, lbl_1, lbl_2]
                        cols_cabecalho = ["Estrutura Gerencial / Nível", lbl_0, lbl_1, var_1_str, lbl_2, var_2_str]
                        larguras_colunas = [3.5, 1.5, 1.5, 1.5, 1.5, 1.5]
                        dict_somas = {lbl_0: s0, lbl_1: s1, lbl_2: s2}
                        mapeamento_var = {var_1_str: (lbl_0, lbl_1), var_2_str: (lbl_1, lbl_2)}

                    c_lbl_tit, c_btn_exp_all = st.columns([4, 1])
                    with c_lbl_tit:
                        st.subheader(f"📋 Execução Orçamentária Comparativa ({tipo_visao})")
                    with c_btn_exp_all:
                        if st.button("🔄 Expandir / Recolher Todos", use_container_width=True):
                            if len(st.session_state.tot_expandidos_set) > 0:
                                st.session_state.tot_expandidos_set.clear()
                            else:
                                st.session_state.tot_expandidos_set = set(niveis_lista)
                            st.rerun()

                    c_hd = st.columns(larguras_colunas)
                    for idx, col_nome in enumerate(cols_cabecalho):
                        align = "left" if idx == 0 else "right"
                        c_hd[idx].markdown(f"<div style='text-align: {align}; font-weight: bold; color: #475569; font-size: 13px;'>{col_nome}</div>", unsafe_allow_html=True)

                    st.markdown("<hr style='margin: 4px 0px 8px 0px;'>", unsafe_allow_html=True)

                    def fmt_moeda(v):
                        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    def fmt_percent_html(v):
                        if v == 0:
                            color = "#64748b"
                        elif v > 0:
                            color = "#dc2626"
                        else:
                            color = "#2563eb"
                        
                        val_str = f"{v:+.2f}%".replace(".", ",")
                        return f"<span style='color: {color}; font-weight: bold;'>{val_str}</span>"

                    somas_totais_gerais = {col: 0.0 for col in cols_valores}

                    for i_niv, nivel_val in enumerate(niveis_lista):
                        contas_do_nivel = []
                        if not df_contas_cg.empty:
                            contas_do_nivel = df_contas_cg[df_contas_cg["nivel"] == nivel_val]["nome_conta"].dropna().tolist()

                        is_expanded = nivel_val in st.session_state.tot_expandidos_set

                        val_tot_dict = {}
                        for col in cols_valores:
                            val_g = sum([dict_somas[col].get(c, 0.0) for c in contas_do_nivel])
                            val_tot_dict[col] = val_g
                            somas_totais_gerais[col] += val_g

                        vars_tot_dict = {}
                        for col_var, (v_atual, v_ant) in mapeamento_var.items():
                            base = val_tot_dict[v_ant]
                            vars_tot_dict[col_var] = ((val_tot_dict[v_atual] - base) / base * 100.0) if base > 0 else 0.0

                        cols_row = st.columns(larguras_colunas)
                        
                        c_btn, c_txt = cols_row[0].columns([0.35, 9.65])
                        btn_symbol = "➖" if is_expanded else "➕"
                        if c_btn.button(btn_symbol, key=f"btn_toggle_niv_{i_niv}", help=f"Expandir/Recolher Nível {nivel_val}"):
                            if is_expanded:
                                st.session_state.tot_expandidos_set.remove(nivel_val)
                            else:
                                st.session_state.tot_expandidos_set.add(nivel_val)
                            st.rerun()

                        c_txt.markdown(f"<div style='font-weight: bold; margin-top: 4px;'>Nível {nivel_val}</div>", unsafe_allow_html=True)

                        idx_col = 1
                        for col in cols_cabecalho[1:]:
                            if col in cols_valores:
                                val_str = fmt_moeda(val_tot_dict[col])
                            else:
                                val_str = fmt_percent_html(vars_tot_dict[col])
                            
                            cols_row[idx_col].markdown(f"<div style='text-align: right; font-weight: bold; margin-top: 4px;'>{val_str}</div>", unsafe_allow_html=True)
                            idx_col += 1

                        if is_expanded:
                            for conta in contas_do_nivel:
                                cols_sub = st.columns(larguras_colunas)
                                cols_sub[0].markdown(f"<div style='padding-left: 28px; color: #334155;'>↳ {conta}</div>", unsafe_allow_html=True)

                                val_sub_dict = {col: dict_somas[col].get(conta, 0.0) for col in cols_valores}
                                vars_sub_dict = {}
                                for col_var, (v_atual, v_ant) in mapeamento_var.items():
                                    base = val_sub_dict[v_ant]
                                    vars_sub_dict[col_var] = ((val_sub_dict[v_atual] - base) / base * 100.0) if base > 0 else 0.0

                                idx_col_sub = 1
                                for col in cols_cabecalho[1:]:
                                    if col in cols_valores:
                                        v_str = fmt_moeda(val_sub_dict[col])
                                    else:
                                        v_str = fmt_percent_html(vars_sub_dict[col])
                                    
                                    cols_sub[idx_col_sub].markdown(f"<div style='text-align: right; color: #475569;'>{v_str}</div>", unsafe_allow_html=True)
                                    idx_col_sub += 1

                        st.markdown("<div style='border-bottom: 1px solid #e2e8f0; margin: 2px 0;'></div>", unsafe_allow_html=True)

                    cols_tot_g = st.columns(larguras_colunas)
                    cols_tot_g[0].markdown("<div style='font-weight: bold; color: #003366; font-size: 15px;'>TOTAL GERAL DO RELATÓRIO</div>", unsafe_allow_html=True)

                    vars_gerais_dict = {}
                    for col_var, (v_atual, v_ant) in mapeamento_var.items():
                        base = somas_totais_gerais[v_ant]
                        vars_gerais_dict[col_var] = ((somas_totais_gerais[v_atual] - base) / base * 100.0) if base > 0 else 0.0

                    idx_col_g = 1
                    for col in cols_cabecalho[1:]:
                        if col in cols_valores:
                            v_g_str = fmt_moeda(somas_totais_gerais[col])
                        else:
                            v_g_str = fmt_percent_html(vars_gerais_dict[col])
                        
                        cols_tot_g[idx_col_g].markdown(f"<div style='text-align: right; font-weight: bold; color: #003366; font-size: 15px;'>{v_g_str}</div>", unsafe_allow_html=True)
                        idx_col_g += 1

    # -----------------------------------------------------------------------------
    # CADASTRO DE UNIDADES GESTORAS (PUBLIC.TB_UGS)
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "unidades_consolidadas":
        st.header("📌 Cadastro de Unidades Gestoras (UGs)")
        st.write("Gestão das Unidades cadastradas no banco de dados (`public.tb_ugs`).")

        df_ugs = buscar_ugs_banco()

        col_u1, col_u2 = st.columns([1, 2])
        
        with col_u1:
            st.subheader("➕ Adicionar Nova UG")
            with st.form("form_add_ug", clear_on_submit=True):
                codigo_input = st.text_input("Código da UG * (Único):", placeholder="Ex: 153164")
                nome_input = st.text_input("Nome da UG:", placeholder="Ex: Pró-Reitoria de Administração")
                sigla_input = st.text_input("Sigla:", placeholder="Ex: PRA")
                ativo_input = st.checkbox("UG Ativa", value=True)
                
                btn_salvar = st.form_submit_button("Salvar UG", use_container_width=True, type="primary")

                if btn_salvar:
                    if not codigo_input.strip():
                        st.error("O campo 'Código da UG' é obrigatório.")
                    else:
                        try:
                            inserir_ug_banco(
                                codigo_ug=codigo_input.strip(),
                                nome=nome_input.strip() if nome_input else None,
                                sigla=sigla_input.strip() if sigla_input else None,
                                ativo=ativo_input
                            )
                            rotulo_u = f"{sigla_input.strip()} - {nome_input.strip()}" if sigla_input and nome_input else nome_input or codigo_input
                            if rotulo_u not in st.session_state.unidades_consolidadas:
                                st.session_state.unidades_consolidadas.append(rotulo_u)
                            
                            st.success(f"UG '{codigo_input}' cadastrada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar UG (Verifique se o código é único): {e}")

        with col_u2:
            st.subheader(f"Unidades Cadastradas ({len(df_ugs)})")
            
            if df_ugs.empty:
                st.info("Nenhuma UG cadastrada na tabela `public.tb_ugs`.")
            else:
                for idx, row in df_ugs.iterrows():
                    ug_cod = row["codigo_ug"]
                    ug_nome = row["nome"] if pd.notna(row["nome"]) else ""
                    ug_sigla = row["sigla"] if pd.notna(row["sigla"]) else ""
                    ug_ativo = bool(row["ativo"]) if pd.notna(row["ativo"]) else True

                    status_str = "🟢" if ug_ativo else "🔴"
                    display_text = f"{status_str} **[{ug_cod}]** {ug_sigla} - {ug_nome}".strip(" -")

                    c_txt, c_btn_edit, c_btn_del = st.columns([5, 1, 1])
                    c_txt.markdown(display_text)
                    
                    if c_btn_edit.button("✏️", key=f"edit_ug_btn_{ug_cod}", help="Alterar dados da UG"):
                        st.session_state.editando_codigo_ug = ug_cod
                        st.rerun()

                    if c_btn_del.button("🗑️", key=f"del_ug_btn_{ug_cod}", help="Excluir UG"):
                        try:
                            excluir_ug_banco(ug_cod)
                            st.success(f"UG [{ug_cod}] excluída com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir UG: {e}")

                    if st.session_state.editando_codigo_ug == ug_cod:
                        with st.container():
                            st.markdown("---")
                            st.markdown(f"**Editando UG Cod: {ug_cod}**")
                            
                            edit_cod = st.text_input("Código UG:", value=str(ug_cod), key=f"edit_cod_{ug_cod}")
                            edit_nome = st.text_input("Nome:", value=ug_nome, key=f"edit_nome_{ug_cod}")
                            edit_sigla = st.text_input("Sigla:", value=ug_sigla, key=f"edit_sigla_{ug_cod}")
                            edit_ativo = st.checkbox("Ativo", value=ug_ativo, key=f"edit_ativo_{ug_cod}")

                            c_save, c_canc = st.columns(2)
                            if c_save.button("💾 Salvar Alterações", key=f"save_ug_btn_{ug_cod}", type="primary"):
                                try:
                                    atualizar_ug_banco(
                                        codigo_ug_orig=ug_cod,
                                        codigo_ug_novo=edit_cod.strip(),
                                        nome=edit_nome.strip() if edit_nome else None,
                                        sigla=edit_sigla.strip() if edit_sigla else None,
                                        ativo=edit_ativo
                                    )
                                    st.session_state.editando_codigo_ug = None
                                    st.success("Unidade alterada com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao atualizar UG: {e}")

                            if c_canc.button("Cancelar", key=f"canc_ug_btn_{ug_cod}"):
                                st.session_state.editando_codigo_ug = None
                                st.rerun()
                            st.markdown("---")

    # -----------------------------------------------------------------------------
    # MAPEAMENTO DE UGs
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "mapeamento_ugs":
        st.header("🔗 Mapeamento de UGs")
        st.write("Alocação de Unidades Gestoras (UGs SIAFI -> Unidade Consolidada).")

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
            
            def_val = st.session_state.mapa_ugs.get(ug_item, "CCSH - Centro de Ciências Sociais e Humanas" if "SOCIAL" in ug_item or "HUMANA" in ug_item else "Encargos Gerais da UFSM / Outros")
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
    # CONTAS GERENCIAIS E NATUREZA DE DESPESA DETALHADA
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "contas":
        st.header("⚙️ Gestão de Contas Gerenciais & NDD")
        st.write("Gerencie o cadastro de Contas Gerenciais, a estrutura por níveis e a hierarquia do plano de contas (`public.tb_contas_gerenciais`).")

        tab_cg, tab_ndd = st.tabs([
            "📌 Cadastro de Contas Gerenciais", 
            "🏷️ Natureza de Despesa Detalhada (NDD)"
        ])

        # Busca dados de NDD para popular opções de relacionamento
        df_ndd_opcoes = buscar_ndd_banco()
        opcoes_ndd = ["Nenhum (Sem vínculo)"]
        if not df_ndd_opcoes.empty:
            for _, r_ndd in df_ndd_opcoes.iterrows():
                desc = f" - {r_ndd['descricao']}" if pd.notna(r_ndd['descricao']) and r_ndd['descricao'] else ""
                opcoes_ndd.append(f"{r_ndd['codigo_ndd']}{desc}")

        # TAB 1: CONTAS GERENCIAIS
        with tab_cg:
            df_cg = buscar_contas_gerenciais_banco()

            col_add_cg, col_list_cg = st.columns([1, 2])

            with col_add_cg:
                st.subheader("➕ Nova Conta Gerencial")
                with st.form("form_add_cg", clear_on_submit=True):
                    codigo_conta_in = st.text_input("Código da Conta * (Ex: 1.0, 1.1):", placeholder="Ex: 1.1")
                    nome_conta_in = st.text_input("Nome da Conta *:", placeholder="Ex: Obras e Reformas")
                    nivel_in = st.text_input("Nível (Ex: 1, 2, 3 ou Nível 1):", value="1")
                    
                    ndd_sel = st.selectbox("Vincular a NDD (Opcional):", opcoes_ndd)
                    ativo_in = st.checkbox("Conta Ativa", value=True)
                    
                    btn_save_cg = st.form_submit_button("Salvar Conta Gerencial", use_container_width=True, type="primary")

                    if btn_save_cg:
                        if not codigo_conta_in.strip() or not nome_conta_in.strip():
                            st.error("Os campos 'Código da Conta' e 'Nome da Conta' são obrigatórios.")
                        else:
                            try:
                                codigo_ndd_val = None if ndd_sel == "Nenhum (Sem vínculo)" else ndd_sel.split(" - ")[0].strip()
                                inserir_conta_gerencial_banco(
                                    codigo_conta=codigo_conta_in.strip(),
                                    nome_conta=nome_conta_in.strip(),
                                    nivel=nivel_in.strip() if nivel_in else "1",
                                    ativo=ativo_in,
                                    codigo_ndd=codigo_ndd_val
                                )
                                st.success(f"Conta '{codigo_conta_in}' inserida com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao inserir conta gerencial: {e}")

            with col_list_cg:
                st.subheader(f"Contas Gerenciais Cadastradas ({len(df_cg)})")
                
                if df_cg.empty:
                    st.info("Nenhuma Conta Gerencial cadastrada na tabela `public.tb_contas_gerenciais`.")
                else:
                    for idx, row in df_cg.iterrows():
                        c_cod = row["codigo_conta"]
                        c_nome = row["nome_conta"] if pd.notna(row["nome_conta"]) else ""
                        c_niv = row["nivel"] if pd.notna(row["nivel"]) else "1"
                        c_ndd = row["codigo_ndd"] if "codigo_ndd" in row and pd.notna(row["codigo_ndd"]) else ""
                        c_ativo = bool(row["ativo"]) if pd.notna(row["ativo"]) else True

                        status_icon = "🟢" if c_ativo else "🔴"
                        
                        indent = "&nbsp;&nbsp;&nbsp;&nbsp;" if ("." in str(c_cod) or str(c_niv) != "1") else ""
                        ndd_str = f" | *NDD: {c_ndd}*" if c_ndd else ""
                        disp_str = f"{indent}{status_icon} **[{c_cod}]** {c_nome} *(Nível: {c_niv})*{ndd_str}"

                        c_txt, c_btn_edit, c_btn_del = st.columns([5, 1, 1])
                        c_txt.markdown(disp_str, unsafe_allow_html=True)

                        if c_btn_edit.button("✏️", key=f"edit_cg_btn_{c_cod}", help="Editar Conta"):
                            st.session_state.editando_codigo_conta = c_cod
                            st.rerun()

                        if c_btn_del.button("🗑️", key=f"del_cg_btn_{c_cod}", help="Excluir Conta"):
                            try:
                                excluir_conta_gerencial_banco(c_cod)
                                st.success(f"Conta [{c_cod}] excluída!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir conta: {e}")

                        if st.session_state.editando_codigo_conta == c_cod:
                            with st.container():
                                st.markdown("---")
                                st.markdown(f"**Editando Conta Gerencial: {c_cod}**")
                                
                                e_cod = st.text_input("Código da Conta:", value=str(c_cod), key=f"edit_cg_cod_{c_cod}")
                                e_nome = st.text_input("Nome da Conta:", value=c_nome, key=f"edit_cg_nome_{c_cod}")
                                e_niv = st.text_input("Nível:", value=str(c_niv), key=f"edit_cg_niv_{c_cod}")
                                
                                idx_ndd_def = 0
                                if c_ndd:
                                    for i_op, op in enumerate(opcoes_ndd):
                                        if op.startswith(str(c_ndd)):
                                            idx_ndd_def = i_op
                                            break
                                
                                e_ndd_sel = st.selectbox("Vincular a NDD:", opcoes_ndd, index=idx_ndd_def, key=f"edit_cg_ndd_{c_cod}")
                                e_ativo = st.checkbox("Ativo", value=c_ativo, key=f"edit_cg_ativo_{c_cod}")

                                c_save, c_canc = st.columns(2)
                                if c_save.button("💾 Salvar", key=f"save_cg_btn_{c_cod}", type="primary"):
                                    try:
                                        e_codigo_ndd_val = None if e_ndd_sel == "Nenhum (Sem vínculo)" else e_ndd_sel.split(" - ")[0].strip()
                                        atualizar_conta_gerencial_banco(
                                            codigo_conta_orig=c_cod,
                                            codigo_conta_novo=e_cod.strip(),
                                            nome_conta=e_nome.strip(),
                                            nivel=e_niv.strip() if e_niv else "1",
                                            ativo=e_ativo,
                                            codigo_ndd=e_codigo_ndd_val
                                        )
                                        st.session_state.editando_codigo_conta = None
                                        st.success("Conta Gerencial atualizada com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao atualizar conta: {e}")

                                if c_canc.button("Cancelar", key=f"canc_cg_btn_{c_cod}"):
                                    st.session_state.editando_codigo_conta = None
                                    st.rerun()
                                st.markdown("---")

        # TAB 2: NATUREZA DE DESPESA DETALHADA (NDD) - CORRIGIDA
        with tab_ndd:
            df_ndd = buscar_ndd_banco()

            col_add_ndd, col_list_ndd = st.columns([1, 2])

            with col_add_ndd:
                st.subheader("➕ Nova NDD")
                with st.form("form_add_ndd", clear_on_submit=True):
                    cod_ndd_in = st.text_input("Código NDD * (Único):", placeholder="Ex: 33903001")
                    desc_ndd_in = st.text_input("Descrição:", placeholder="Ex: Combustíveis e Lubrificantes")
                    grupo_despesa_in = st.text_input("Grupo de Despesa:", placeholder="Ex: Material de Consumo")
                    ativo_ndd_in = st.checkbox("NDD Ativa", value=True)

                    btn_save_ndd = st.form_submit_button("Salvar NDD", use_container_width=True, type="primary")

                    if btn_save_ndd:
                        if not cod_ndd_in.strip():
                            st.error("O campo 'Código NDD' é obrigatório.")
                        else:
                            try:
                                inserir_ndd_banco(
                                    codigo_ndd=cod_ndd_in.strip(),
                                    descricao=desc_ndd_in.strip(),
                                    grupo_despesa=grupo_despesa_in.strip() if grupo_despesa_in else None,
                                    ativo=ativo_ndd_in
                                )
                                st.success(f"NDD '{cod_ndd_in}' salva com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar NDD (Verifique se o código é único): {e}")

            with col_list_ndd:
                st.subheader(f"NDDs Cadastradas ({len(df_ndd)})")

                if df_ndd.empty:
                    st.info("Nenhuma Natureza de Despesa Detalhada cadastrada.")
                else:
                    for idx, row in df_ndd.iterrows():
                        n_cod = row["codigo_ndd"]
                        n_desc = row["descricao"] if pd.notna(row["descricao"]) else ""
                        n_grp = row["grupo_despesa"] if pd.notna(row["grupo_despesa"]) else ""
                        n_ativo = bool(row["ativo"]) if pd.notna(row["ativo"]) else True

                        status_ic = "🟢" if n_ativo else "🔴"
                        lbl_grp = f" *(Grupo: {n_grp})*" if n_grp else ""
                        disp_ndd = f"{status_ic} **[{n_cod}]** {n_desc}{lbl_grp}"

                        c_txt, c_btn_edit, c_btn_del = st.columns([5, 1, 1])
                        c_txt.markdown(disp_ndd)

                        if c_btn_edit.button("✏️", key=f"edit_ndd_btn_{n_cod}", help="Editar NDD"):
                            st.session_state.editando_codigo_ndd = n_cod
                            st.rerun()

                        if c_btn_del.button("🗑️", key=f"del_ndd_btn_{n_cod}", help="Excluir NDD"):
                            try:
                                excluir_ndd_banco(n_cod)
                                st.success("NDD excluída com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir NDD: {e}")

                        if st.session_state.editando_codigo_ndd == n_cod:
                            with st.container():
                                st.markdown("---")
                                st.markdown(f"**Editando NDD Cod: {n_cod}**")

                                e_ndd_cod = st.text_input("Código NDD:", value=str(n_cod), key=f"edit_ndd_cod_{n_cod}")
                                e_ndd_desc = st.text_input("Descrição:", value=n_desc, key=f"edit_ndd_desc_{n_cod}")
                                e_ndd_grp = st.text_input("Grupo de Despesa:", value=n_grp, key=f"edit_ndd_grp_{n_cod}")
                                e_ndd_ativo = st.checkbox("Ativo", value=n_ativo, key=f"edit_ndd_ativo_{n_cod}")

                                c_save, c_canc = st.columns(2)
                                if c_save.button("💾 Salvar", key=f"save_ndd_btn_{n_cod}", type="primary"):
                                    try:
                                        atualizar_ndd_banco(
                                            codigo_ndd_orig=n_cod,
                                            codigo_ndd_novo=e_ndd_cod.strip(),
                                            descricao=e_ndd_desc.strip(),
                                            grupo_despesa=e_ndd_grp.strip() if e_ndd_grp else None,
                                            ativo=e_ndd_ativo
                                        )
                                        st.session_state.editando_codigo_ndd = None
                                        st.success("NDD alterada com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao atualizar NDD: {e}")

                                if c_canc.button("Cancelar", key=f"canc_ndd_btn_{n_cod}"):
                                    st.session_state.editando_codigo_ndd = None
                                    st.rerun()
                                st.markdown("---")

    # -----------------------------------------------------------------------------
    # CADASTRO DE USUÁRIOS
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "usuarios":
        st.header("⚙️ Gestão de Usuários e Permissões")
        st.write("Cadastre e controle os usuários que possuem acesso ao sistema.")

        col_usr_add, col_usr_list = st.columns([1, 2])

        with col_usr_add:
            st.subheader("➕ Novo Usuário")
            novo_usr_id = st.text_input("Usuário (Login):")
            novo_usr_nome = st.text_input("Nome Completo:")
            novo_usr_pass = st.text_input("Senha:", type="password")
            novo_usr_perf = st.selectbox("Perfil:", ["Administrador", "Gestor", "Consulta"])

            if st.button("Cadastrar Usuário", use_container_width=True):
                if not novo_usr_id or not novo_usr_pass or not novo_usr_nome:
                    st.error("Preencha todos os campos obrigatórios.")
                elif any(u["usuario"].lower() == novo_usr_id.strip().lower() for u in st.session_state.tabela_usuarios):
                    st.error("Este nome de usuário já existe.")
                else:
                    st.session_state.tabela_usuarios.append({
                        "usuario": novo_usr_id.strip(),
                        "nome": novo_usr_nome.strip(),
                        "senha": novo_usr_pass,
                        "perfil": novo_usr_perf
                    })
                    st.success(f"Usuário '{novo_usr_id}' cadastrado com sucesso!")
                    st.rerun()

        with col_usr_list:
            st.subheader(f"Usuários Cadastrados ({len(st.session_state.tabela_usuarios)})")
            
            df_usr_view = pd.DataFrame(st.session_state.tabela_usuarios)[["usuario", "nome", "perfil"]]
            df_usr_view.columns = ["Login", "Nome Completo", "Perfil"]
            st.dataframe(df_usr_view, use_container_width=True)

            st.markdown("---")
            st.subheader("⚙️ Ações nos Usuários")
            
            usrs_existentes = [u["usuario"] for u in st.session_state.tabela_usuarios]
            usr_selecionado = st.selectbox("Selecione um usuário para editar/excluir:", usrs_existentes)
            
            if usr_selecionado:
                dados_usr = next(u for u in st.session_state.tabela_usuarios if u["usuario"] == usr_selecionado)
                c_edit_pass, c_del_usr = st.columns(2)
                
                with c_edit_pass:
                    nova_s = st.text_input(f"Nova senha para '{usr_selecionado}':", type="password", key="inp_nova_s")
                    if st.button("Alterar Senha"):
                        if nova_s:
                            dados_usr["senha"] = nova_s
                            st.success("Senha alterada com sucesso!")
                        else:
                            st.warning("Digite a nova senha.")

                with c_del_usr:
                    st.write("Excluir conta de acesso:")
                    if st.button(f"🗑️ Excluir '{usr_selecionado}'", type="primary"):
                        if len(st.session_state.tabela_usuarios) <= 1:
                            st.error("Não é possível remover o único usuário do sistema.")
                        else:
                            st.session_state.tabela_usuarios = [u for u in st.session_state.tabela_usuarios if u["usuario"] != usr_selecionado]
                            st.success(f"Usuário '{usr_selecionado}' removido com sucesso!")
                            st.rerun()

    # -----------------------------------------------------------------------------
    # CONFIGURAÇÕES VISUAIS
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "config":
        st.header("⚙️ Configuração Visuais e Logomarca")
        st.write("Carregue a imagem da logomarca oficial do seu computador. Ela será exibida no menu à esquerda, no cabeçalho do relatório e como ícone (favicon) na aba do navegador.")

        c_up, c_prev = st.columns([2, 1])

        with c_up:
            st.subheader("Fazer Upload da Logo")
            arquivo_logo = st.file_uploader("Selecione uma imagem (.png, .jpg, .jpeg):", type=["png", "jpg", "jpeg"])

            if arquivo_logo is not None:
                st.session_state.logo_personalizada = arquivo_logo.getvalue()
                st.success("Logomarca carregada com sucesso!")
                st.rerun()

            if st.session_state.logo_personalizada is not None:
                st.markdown("---")
                if st.button("🗑️ Remover Logomarca Atual"):
                    st.session_state.logo_personalizada = None
                    st.success("Logomarca removida com sucesso!")
                    st.rerun()

        with c_prev:
            st.subheader("Pré-visualização")
            if st.session_state.logo_personalizada is not None:
                st.image(st.session_state.logo_personalizada, caption="Logo Ativa no Sistema", width=200)
            else:
                st.info("Nenhuma imagem carregada até o momento.")
