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
        from sqlalchemy import text
        if params:
            conn.execute(text(query), params)
        else:
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
# FUNÇÕES DE CRUD PARA PUBLIC.TB_NATUREZA_DESPESA_DETALHADA
# -----------------------------------------------------------------------------
def buscar_ndd_banco():
    try:
        query = "SELECT codigo_ndd, descricao, grupo_despesa, conta_gerencial, criado_em FROM public.tb_natureza_despesa_detalhada ORDER BY codigo_ndd ASC;"
        return executar_consulta_sql(query)
    except Exception as e:
        st.error(f"Erro ao consultar tb_natureza_despesa_detalhada: {e}")
        return pd.DataFrame()

def inserir_ndd_banco(codigo_ndd: str, descricao: str, grupo_despesa: str, conta_gerencial: str):
    query = """
    INSERT INTO public.tb_natureza_despesa_detalhada (codigo_ndd, descricao, grupo_despesa, conta_gerencial)
    VALUES (:codigo_ndd, :descricao, :grupo_despesa, :conta_gerencial);
    """
    executar_comando_sql(query, {
        "codigo_ndd": codigo_ndd, 
        "descricao": descricao, 
        "grupo_despesa": grupo_despesa, 
        "conta_gerencial": conta_gerencial
    })

def atualizar_ndd_banco(codigo_ndd_orig: str, codigo_ndd_novo: str, descricao: str, grupo_despesa: str, conta_gerencial: str):
    query = """
    UPDATE public.tb_natureza_despesa_detalhada
    SET codigo_ndd = :codigo_ndd_novo, descricao = :descricao, grupo_despesa = :grupo_despesa, conta_gerencial = :conta_gerencial
    WHERE codigo_ndd = :codigo_ndd_orig;
    """
    executar_comando_sql(query, {
        "codigo_ndd_orig": codigo_ndd_orig,
        "codigo_ndd_novo": codigo_ndd_novo,
        "descricao": descricao,
        "grupo_despesa": grupo_despesa,
        "conta_gerencial": conta_gerencial
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
        SELECT codigo_conta, nivel, nome_conta, ativo, criado_em
        FROM public.tb_contas_gerenciais
        ORDER BY codigo_conta ASC;
        """
        return executar_consulta_sql(query)
    except Exception as e:
        st.error(f"Erro ao consultar tb_contas_gerenciais: {e}")
        return pd.DataFrame()

def inserir_conta_gerencial_banco(codigo_conta: str, nome_conta: str, nivel: str, ativo: bool):
    query = """
    INSERT INTO public.tb_contas_gerenciais (codigo_conta, nome_conta, nivel, ativo)
    VALUES (:codigo_conta, :nome_conta, :nivel, :ativo);
    """
    executar_comando_sql(query, {
        "codigo_conta": codigo_conta,
        "nome_conta": nome_conta,
        "nivel": nivel,
        "ativo": ativo
    })

def atualizar_conta_gerencial_banco(codigo_conta_orig: str, codigo_conta_novo: str, nome_conta: str, nivel: str, ativo: bool):
    query = """
    UPDATE public.tb_contas_gerenciais
    SET codigo_conta = :codigo_conta_novo, nome_conta = :nome_conta, nivel = :nivel, ativo = :ativo
    WHERE codigo_conta = :codigo_conta_orig;
    """
    executar_comando_sql(query, {
        "codigo_conta_orig": codigo_conta_orig,
        "codigo_conta_novo": codigo_conta_novo,
        "nome_conta": nome_conta,
        "nivel": nivel,
        "ativo": ativo
    })

def excluir_conta_gerencial_banco(codigo_conta: str):
    query = "DELETE FROM public.tb_contas_gerenciais WHERE codigo_conta = :codigo_conta;"
    executar_comando_sql(query, {"codigo_conta": codigo_conta})

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DE PÁGINA E CSS INSTITUCIONAL (PADRÃO UFSM - SEM ARREDONDAMENTO)
# -----------------------------------------------------------------------------
if "logo_personalizada" not in st.session_state:
    st.session_state.logo_personalizada = None

icone_aba = st.session_state.logo_personalizada if st.session_state.logo_personalizada is not None else "🏛️"

st.set_page_config(
    page_title="SiGeO - Sistema de Gestão Orçamentária | UFSM",
    page_icon=icone_aba,
    layout="wide"
)

# Estilização CSS rigorosa: Largura total para a faixa azul e elementos estritamente quadrados (sem border-radius)
st.markdown("""
    <style>
    /* Ocultar barra lateral padrão do Streamlit para controle total do layout institucional */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Ajuste de margens globais para encostar a faixa azul nas bordas da tela */
    .block-container {
        padding-top: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    :root {
        --ufsm-azul-primario: #002b5c;
        --ufsm-azul-secundario: #003366;
        --ufsm-cinza-claro: #f4f6f9;
    }

    /* Faixa Superior Institucional de Largura Total */
    .faixa-superior-ufsm-global {
        width: 100vw;
        position: relative;
        left: calc(-50vw + 50%);
        background: linear-gradient(90deg, #002b5c 0%, #003366 100%);
        padding: 15px 40px;
        color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        margin-bottom: 0px;
        border-radius: 0px !important;
    }
    
    .cabecalho-conteudo {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
    }

    .instituicao-info h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        color: white;
        letter-spacing: 0.5px;
    }
    
    .instituicao-info p {
        margin: 2px 0 0 0;
        font-size: 13px;
        color: #d0dce8;
    }

    /* Forçar elementos quadrados em todo o sistema (sem cantos arredondados) */
    button, input, select, textarea, div, .stButton>button, .stTextInput>div>div>input, .stSelectbox>div>div, .card-inicio {
        border-radius: 0px !important;
    }

    /* Cards de Navegação Estilo Link Retangulares */
    .card-inicio {
        background-color: white;
        border: 1px solid #d1d9e0;
        border-top: 4px solid #002b5c;
        padding: 20px;
        text-align: center;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-radius: 0px !important;
    }
    .card-inicio:hover {
        background-color: #fafbfc;
        border-color: #003366;
    }

    .stButton button[kind="primary"] {
        background-color: #002b5c !important;
        border-color: #002b5c !important;
        color: white !important;
        border-radius: 0px !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background-color: #001a38 !important;
        border-color: #001a38 !important;
    }

    /* Estilização para Impressão e Relatórios Oficiais */
    @media print {
        header, footer, .stButton, .stSelectbox, .no-print {
            display: none !important;
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
        border-bottom: 3px solid #002b5c;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. VARIÁVEIS DE ESTADO
# -----------------------------------------------------------------------------
USUARIOS_PADRAO = [
    {"usuario": "admin", "nome": "Administrador Geral", "senha": "ufsm2026", "perfil": "Administrador"},
    {"usuario": "pra_gestor", "nome": "Gestor PRA", "senha": "pra123", "perfil": "Gestor"},
]

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "inicio"

if "tabela_usuarios" not in st.session_state:
    st.session_state.tabela_usuarios = USUARIOS_PADRAO.copy()

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "dados_tg_raw" not in st.session_state:
    st.session_state.dados_tg_raw = None

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
        st.markdown("""
            <div style="width: 100vw; position: relative; left: calc(-50vw + 50%); background: #002b5c; padding: 20px 40px; color: white; margin-bottom: 40px;">
                <h2 style="margin: 0; font-size: 22px;">UFSM - Universidade Federal de Santa Maria</h2>
                <p style="margin: 2px 0 0 0; font-size: 13px; color: #d0dce8;">SiGeO - Sistema de Gestão Orçamentária</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
        with col_l2:
            st.markdown("<h3 style='color: #002b5c; text-align: center;'>Autenticação no Sistema</h3>", unsafe_allow_html=True)
            with st.form("form_login"):
                usuario_input = st.text_input("Usuário:")
                senha_input = st.text_input("Senha:", type="password")
                btn_entrar = st.form_submit_button("Entrar no Sistema", type="primary", use_container_width=True)
                
                if btn_entrar:
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
    # 4. CABEÇALHO INSTITUCIONAL GLOBAL E BARRA DE LINKS HORIZONTAIS (TODAS AS TELAS)
    # -----------------------------------------------------------------------------
    st.markdown("""
        <div class="faixa-superior-ufsm-global">
            <div class="cabecalho-conteudo">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="font-size: 32px;">🏛️</div>
                    <div class="instituicao-info">
                        <h1>UFSM</h1>
                        <p>Universidade Federal de Santa Maria | SiGeO - Sistema de Gestão Orçamentária</p>
                    </div>
                </div>
                <div style="font-size: 12px; color: #d0dce8; text-align: right;">
                    Usuário: <b>{}</b> ({})
                </div>
            </div>
        </div>
    """.format(st.session_state.usuario_logado['nome'], st.session_state.usuario_logado['perfil']), unsafe_allow_html=True)

    # Barra de Links Horizontais estilo Portal UFSM (Textos / Links Limpos)
    st.markdown("""
        <div style="width: 100vw; position: relative; left: calc(-50vw + 50%); background-color: #001f3f; padding: 10px 40px; margin-bottom: 25px; border-bottom: 1px solid #004080;">
            <div style="max-width: 1400px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 20px; align-items: center; font-size: 14px; font-weight: 600;">
                <span style="color: #ffffff; cursor: default;">≡ Menu</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Botões de navegação horizontal equivalentes aos links solicitados
    c_nav1, c_nav2, c_nav3, c_nav4, c_nav5, c_nav6, c_nav7 = st.columns(7)
    
    with c_nav1:
        if st.button("Início", use_container_width=True, type="primary" if st.session_state.pagina_atual == "inicio" else "secondary"):
            st.session_state.pagina_atual = "inicio"
            st.rerun()
    with c_nav2:
        if st.button("Carga", use_container_width=True, type="primary" if st.session_state.pagina_atual == "carga" else "secondary"):
            st.session_state.pagina_atual = "carga"
            st.rerun()
    with c_nav3:
        if st.button("Relatórios", use_container_width=True, type="primary" if st.session_state.pagina_atual == "relatorio" else "secondary"):
            st.session_state.pagina_atual = "relatorio"
            st.rerun()
    with c_nav4:
        if st.button("UGs", use_container_width=True, type="primary" if st.session_state.pagina_atual == "unidades_consolidadas" else "secondary"):
            st.session_state.pagina_atual = "unidades_consolidadas"
            st.rerun()
    with c_nav5:
        if st.button("Contas", use_container_width=True, type="primary" if st.session_state.pagina_atual == "contas" else "secondary"):
            st.session_state.pagina_atual = "contas"
            st.rerun()
    with c_nav6:
        if st.button("NDD", use_container_width=True, type="primary" if st.session_state.pagina_atual == "ndd" else "secondary"):
            st.session_state.pagina_atual = "ndd"
            st.rerun()
    with c_nav7:
        if st.button("Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario_logado = None
            st.rerun()

    def converter_valor(val):
        if pd.isna(val): return 0.0
        if isinstance(val, (int, float)): return float(val)
        val_str = str(val).strip().replace(".", "").replace(",", ".")
        try: return float(val_str)
        except: return 0.0

    # -----------------------------------------------------------------------------
    # TELA 0: INÍCIO / DASHBOARD
    # -----------------------------------------------------------------------------
    if st.session_state.pagina_atual == "inicio":
        st.markdown("### 📌 Módulos Operacionais do SiGeO")
        st.write("Selecione abaixo o módulo desejado para gerenciar os dados orçamentários:")

        col_h1, col_h2, col_h3 = st.columns(3)

        with col_h1:
            st.markdown("""
                <div class="card-inicio">
                    <h4>Carga de Dados</h4>
                    <p style="font-size: 13px; color: #555;">Importação de planilhas do Tesouro Gerencial e processamento em lote para o Supabase.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Carga de Dados", use_container_width=True, type="primary", key="btn_h_carga"):
                st.session_state.pagina_atual = "carga"
                st.rerun()

        with col_h2:
            st.markdown("""
                <div class="card-inicio">
                    <h4>Relatórios</h4>
                    <p style="font-size: 13px; color: #555;">Demonstrativos de execução orçamentária e comparativos estruturados.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Relatórios", use_container_width=True, type="primary", key="btn_h_rel"):
                st.session_state.pagina_atual = "relatorio"
                st.rerun()

        with col_h3:
            st.markdown("""
                <div class="card-inicio">
                    <h4>Configurações</h4>
                    <p style="font-size: 13px; color: #555;">Gerenciamento de UGs, Contas Gerenciais, NDDs e cadastros do sistema.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Configurações", use_container_width=True, type="primary", key="btn_h_conf"):
                st.session_state.pagina_atual = "unidades_consolidadas"
                st.rerun()

    # -----------------------------------------------------------------------------
    # PÁGINA 1: CARGA DA PLANILHA
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "carga":
        st.markdown("<h2 style='color: #002b5c;'>Carga do Relatório do Tesouro Gerencial</h2>", unsafe_allow_html=True)
        st.write("Faça o upload da planilha líquida/executada do Tesouro Gerencial (.xlsx ou .csv) e mapeie as colunas para carregar no Supabase.")

        arquivo = st.file_uploader("Selecione o arquivo da UFSM", type=["csv", "xlsx"])

        if arquivo is not None:
            try:
                if arquivo.name.endswith(".csv"):
                    try: df = pd.read_csv(arquivo, sep=";", encoding="latin1")
                    except: df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)
                
                colunas = list(df.columns)
                st.success(f"Arquivo carregado com sucesso! Total de {len(df):,} linhas encontradas.")

                st.markdown("---")
                st.subheader("Mapeamento Dinâmico de Colunas")

                c_m1, c_m2, c_m3 = st.columns(3)
                with c_m1:
                    col_ex = st.selectbox("Coluna de Exercício / Ano:", colunas, index=0 if len(colunas) > 0 else 0)
                    col_ug = st.selectbox("Coluna de UG Responsável:", colunas, index=min(6, len(colunas)-1))
                with c_m2:
                    col_mes = st.selectbox("Coluna de Mês / Competência:", colunas, index=min(1, len(colunas)-1))
                with c_m3:
                    col_nd = st.selectbox("Coluna de Natureza de Despesa (NDD):", colunas, index=min(11, len(colunas)-1))
                    col_val = st.selectbox("Coluna de Valor Liquidado:", colunas, index=len(colunas)-1)

                if st.button("Processar e Visualizar Dados Tratados", type="primary"):
                    df_tratado = pd.DataFrame()
                    df_tratado["exercicio"] = pd.to_numeric(df[col_ex], errors="coerce").fillna(datetime.now().year).astype(int)
                    df_tratado["mes_competencia"] = pd.to_datetime(df[col_mes].astype(str), errors="coerce").dt.month.fillna(1).astype(int)
                    df_tratado["ug_responsavel"] = df[col_ug].astype(str).str.strip()
                    df_tratado["natureza_despesa_detalhada"] = df[col_nd].astype(str).str.strip()
                    df_tratado["valor_liquidado"] = df[col_val].apply(converter_valor)

                    st.session_state.dados_tg_raw = df_tratado
                    st.success("Dados tratados com sucesso!")
                    st.dataframe(df_tratado.head(5), use_container_width=True)

                if st.session_state.dados_tg_raw is not None:
                    st.markdown("---")
                    if st.button("Gravar Dados no Supabase", type="primary"):
                        with st.spinner("Enviando lotes de dados para o Supabase..."):
                            carregar_dados_para_supabase(st.session_state.dados_tg_raw, "tb_execucao_despesa")
                            st.success("Carga concluída com sucesso no banco de dados Supabase!")

            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}")

    # -----------------------------------------------------------------------------
    # PÁGINA 2: RELATÓRIO DE EXECUÇÃO ORÇAMENTÁRIA
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "relatorio":
        st.markdown("<h2 style='color: #002b5c;'>Demonstrativo de Execução Orçamentária</h2>", unsafe_allow_html=True)
        
        c_a1, c_a2 = st.columns(2)
        ano_atual_sel = c_a1.number_input("Ano Atual:", value=datetime.now().year, step=1)
        ano_ant_sel = c_a2.number_input("Ano Comparativo:", value=datetime.now().year - 1, step=1)

        if st.button("Executar Consulta SQL no Supabase", type="primary"):
            with st.spinner("Buscando dados diretamente do Supabase..."):
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
                    LEFT JOIN tb_contas_gerenciais cg ON ndd.conta_gerencial LIKE '%' || cg.codigo_conta || '%'
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

    # -----------------------------------------------------------------------------
    # CADASTRO DE UNIDADES GESTORAS (PUBLIC.TB_UGS)
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "unidades_consolidadas":
        st.markdown("<h2 style='color: #002b5c;'>Cadastro de Unidades Gestoras (UGs)</h2>", unsafe_allow_html=True)
        df_ugs = buscar_ugs_banco()

        col_u1, col_u2 = st.columns([1, 2])
        with col_u1:
            st.subheader("Adicionar Nova UG")
            with st.form("form_add_ug", clear_on_submit=True):
                codigo_input = st.text_input("Código da UG *:")
                nome_input = st.text_input("Nome da UG:")
                sigla_input = st.text_input("Sigla:")
                ativo_input = st.checkbox("UG Ativa", value=True)
                
                if st.form_submit_button("Salvar UG", use_container_width=True, type="primary"):
                    if not codigo_input.strip():
                        st.error("O campo 'Código da UG' é obrigatório.")
                    else:
                        try:
                            inserir_ug_banco(codigo_input.strip(), nome_input.strip() if nome_input else None, sigla_input.strip() if sigla_input else None, ativo_input)
                            st.success("UG cadastrada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")

        with col_u2:
            st.subheader(f"Unidades Cadastradas ({len(df_ugs)})")
            if df_ugs.empty:
                st.info("Nenhuma UG cadastrada.")
            else:
                for _, row in df_ugs.iterrows():
                    ug_cod = row["codigo_ug"]
                    c_txt, c_btn = st.columns([6, 1])
                    c_txt.markdown(f"**[{ug_cod}]** {row.get('sigla', '')} - {row.get('nome', '')}")
                    if c_btn.button("🗑️", key=f"del_ug_{ug_cod}"):
                        excluir_ug_banco(ug_cod)
                        st.rerun()

    # -----------------------------------------------------------------------------
    # CONTAS GERENCIAIS
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "contas":
        st.markdown("<h2 style='color: #002b5c;'>Gestão de Contas Gerenciais</h2>", unsafe_allow_html=True)
        df_cg = buscar_contas_gerenciais_banco()
        
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            st.subheader("Nova Conta")
            with st.form("form_cg", clear_on_submit=True):
                c_cod_in = st.text_input("Código da Conta:")
                c_nome_in = st.text_input("Nome da Conta:")
                c_nivel_in = st.text_input("Nível:", value="1")
                c_ativo_in = st.checkbox("Ativa", value=True)
                
                if st.form_submit_button("Salvar Conta", use_container_width=True, type="primary"):
                    if c_cod_in and c_nome_in:
                        inserir_conta_gerencial_banco(c_cod_in.strip(), c_nome_in.strip(), c_nivel_in.strip(), c_ativo_in)
                        st.success("Salvo com sucesso!")
                        st.rerun()

        with col_c2:
            st.subheader(f"Contas Cadastradas ({len(df_cg)})")
            if df_cg.empty:
                st.info("Nenhuma conta cadastrada.")
            else:
                for _, row in df_cg.iterrows():
                    st.markdown(f"**[{row['codigo_conta']}]** {row['nome_conta']} (Nível: {row['nivel']})")

    # -----------------------------------------------------------------------------
    # NATUREZA DE DESPESA DETALHADA (NDD)
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "ndd":
        st.markdown("<h2 style='color: #002b5c;'>Natureza de Despesa Detalhada (NDD)</h2>", unsafe_allow_html=True)
        df_ndd = buscar_ndd_banco()
        
        col_n1, col_n2 = st.columns([1, 2])
        with col_n1:
            st.subheader("Nova NDD")
            with st.form("form_ndd", clear_on_submit=True):
                n_cod_in = st.text_input("Código NDD:")
                n_desc_in = st.text_input("Descrição:")
                n_grp_in = st.text_input("Grupo de Despesa:")
                
                if st.form_submit_button("Salvar NDD", use_container_width=True, type="primary"):
                    if n_cod_in and n_desc_in:
                        inserir_ndd_banco(n_cod_in.strip(), n_desc_in.strip(), n_grp_in.strip() if n_grp_in else None, "1.0")
                        st.success("NDD salva com sucesso!")
                        st.rerun()

        with col_n2:
            st.subheader(f"NDDs Cadastradas ({len(df_ndd)})")
            if df_ndd.empty:
                st.info("Nenhuma NDD cadastrada.")
            else:
                for _, row in df_ndd.iterrows():
                    st.markdown(f"**[{row['codigo_ndd']}]** {row['descricao']}")
