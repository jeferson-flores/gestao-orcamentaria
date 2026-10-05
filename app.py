import streamlit as st
from datetime import datetime
import pandas as pd
import re
import plotly.express as px
from sqlalchemy import create_engine, text
from supabase import Client, create_client

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


def carregar_dados_para_supabase(
    df: pd.DataFrame, nome_tabela: str = "tb_execucao_despesa"
):
  engine = get_db_engine()
  df.to_sql(
      nome_tabela, con=engine, if_exists="append", index=False, chunksize=2000
  )


def executar_consulta_sql(query: str, params: dict = None) -> pd.DataFrame:
  engine = get_db_engine()
  with engine.connect() as conn:
    if params:
      return pd.read_sql_query(text(query), con=conn, params=params)
    else:
      return pd.read_sql_query(text(query), con=conn)


def executar_comando_sql(query: str, params: dict = None):
  engine = get_db_engine()
  with engine.begin() as conn:
    if params:
      conn.execute(text(query), params)
    else:
      conn.execute(text(query))


# -----------------------------------------------------------------------------
# FUNÇÕES DE CRUD PARA A TABELA PUBLIC.TB_UNIDADES
# -----------------------------------------------------------------------------
def buscar_unidades_banco():
  try:
    query = "SELECT codigo_unidade, nome_unidade, nivel, unidade_pai, ativo, criado_em FROM public.tb_unidades ORDER BY codigo_unidade ASC;"
    return executar_consulta_sql(query)
  except Exception as e:
    st.error(f"Erro ao consultar tb_unidades no Supabase: {e}")
    return pd.DataFrame()


def inserir_unidade_banco(
    codigo_unidade: str,
    nome_unidade: str,
    nivel: str,
    unidade_pai: str,
    ativo: bool,
):
  query = """
    INSERT INTO public.tb_unidades (codigo_unidade, nome_unidade, nivel, unidade_pai, ativo)
    VALUES (:codigo_unidade, :nome_unidade, :nivel, :unidade_pai, :ativo);
    """
  executar_comando_sql(
      query,
      {
          "codigo_unidade": codigo_unidade,
          "nome_unidade": nome_unidade,
          "nivel": nivel,
          "unidade_pai": unidade_pai if unidade_pai else None,
          "ativo": ativo,
      },
  )


def atualizar_unidade_banco(
    codigo_unidade_orig: str,
    codigo_unidade_novo: str,
    nome_unidade: str,
    nivel: str,
    unidade_pai: str,
    ativo: bool,
):
  query = """
    UPDATE public.tb_unidades
    SET codigo_unidade = :codigo_unidade_novo, nome_unidade = :nome_unidade, nivel = :nivel, unidade_pai = :unidade_pai, ativo = :ativo
    WHERE codigo_unidade = :codigo_unidade_orig;
    """
  executar_comando_sql(
      query,
      {
          "codigo_unidade_orig": codigo_unidade_orig,
          "codigo_unidade_novo": codigo_unidade_novo,
          "nome_unidade": nome_unidade,
          "nivel": nivel,
          "unidade_pai": unidade_pai if unidade_pai else None,
          "ativo": ativo,
      },
  )


def excluir_unidade_banco(codigo_unidade: str):
  query = "DELETE FROM public.tb_unidades WHERE codigo_unidade = :codigo_unidade;"
  executar_comando_sql(query, {"codigo_unidade": codigo_unidade})


# -----------------------------------------------------------------------------
# FUNÇÕES DE CRUD PARA A TABELA PUBLIC.TB_UGS
# -----------------------------------------------------------------------------
def buscar_ugs_banco():
  try:
    query = "SELECT codigo_ug, nome, unidade, ativo, criado_em FROM public.tb_ugs ORDER BY codigo_ug ASC;"
    return executar_consulta_sql(query)
  except Exception as e:
    st.error(f"Erro ao consultar tb_ugs no Supabase: {e}")
    return pd.DataFrame()


def inserir_ug_banco(codigo_ug: str, nome: str, unidade: str, ativo: bool):
  query = """
    INSERT INTO public.tb_ugs (codigo_ug, nome, unidade, ativo)
    VALUES (:codigo_ug, :nome, :unidade, :ativo);
    """
  executar_comando_sql(
      query,
      {"codigo_ug": codigo_ug, "nome": nome, "unidade": unidade, "ativo": ativo},
  )


def atualizar_ug_banco(
    codigo_ug_orig: str,
    codigo_ug_novo: str,
    nome: str,
    unidade: str,
    ativo: bool,
):
  query = """
    UPDATE public.tb_ugs
    SET codigo_ug = :codigo_ug_novo, nome = :nome, unidade = :unidade, ativo = :ativo
    WHERE codigo_ug = :codigo_ug_orig;
    """
  executar_comando_sql(
      query,
      {
          "codigo_ug_orig": codigo_ug_orig,
          "codigo_ug_novo": codigo_ug_novo,
          "nome": nome,
          "unidade": unidade,
          "ativo": ativo,
      },
  )


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


def inserir_ndd_banco(
    codigo_ndd: str, descricao: str, grupo_despesa: str, conta_gerencial: str
):
  query = """
    INSERT INTO public.tb_natureza_despesa_detalhada (codigo_ndd, descricao, grupo_despesa, conta_gerencial)
    VALUES (:codigo_ndd, :descricao, :grupo_despesa, :conta_gerencial);
    """
  executar_comando_sql(
      query,
      {
          "codigo_ndd": codigo_ndd,
          "descricao": descricao,
          "grupo_despesa": grupo_despesa,
          "conta_gerencial": conta_gerencial,
      },
  )


def atualizar_ndd_banco(
    codigo_ndd_orig: str,
    codigo_ndd_novo: str,
    descricao: str,
    grupo_despesa: str,
    conta_gerencial: str,
):
  query = """
    UPDATE public.tb_natureza_despesa_detalhada
    SET codigo_ndd = :codigo_ndd_novo, descricao = :descricao, grupo_despesa = :grupo_despesa, conta_gerencial = :conta_gerencial
    WHERE codigo_ndd = :codigo_ndd_orig;
    """
  executar_comando_sql(
      query,
      {
          "codigo_ndd_orig": codigo_ndd_orig,
          "codigo_ndd_novo": codigo_ndd_novo,
          "descricao": descricao,
          "grupo_despesa": grupo_despesa,
          "conta_gerencial": conta_gerencial,
      },
  )


def excluir_ndd_banco(codigo_ndd: str):
  query = (
      "DELETE FROM public.tb_natureza_despesa_detalhada WHERE codigo_ndd ="
      " :codigo_ndd;"
  )
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


def inserir_conta_gerencial_banco(
    codigo_conta: str, nome_conta: str, nivel: str, ativo: bool
):
  query = """
    INSERT INTO public.tb_contas_gerenciais (codigo_conta, nome_conta, nivel, ativo)
    VALUES (:codigo_conta, :nome_conta, :nivel, :ativo);
    """
  executar_comando_sql(
      query,
      {
          "codigo_conta": codigo_conta,
          "nome_conta": nome_conta,
          "nivel": nivel,
          "ativo": ativo,
      },
  )


def atualizar_conta_gerencial_banco(
    codigo_conta_orig: str,
    codigo_conta_novo: str,
    nome_conta: str,
    nivel: str,
    ativo: bool,
):
  query = """
    UPDATE public.tb_contas_gerenciais
    SET codigo_conta = :codigo_conta_novo, nome_conta = :nome_conta, nivel = :nivel, ativo = :ativo
    WHERE codigo_conta = :codigo_conta_orig;
    """
  executar_comando_sql(
      query,
      {
          "codigo_conta_orig": codigo_conta_orig,
          "codigo_conta_novo": codigo_conta_novo,
          "nome_conta": nome_conta,
          "nivel": nivel,
          "ativo": ativo,
      },
  )


def excluir_conta_gerencial_banco(codigo_conta: str):
  query = (
      "DELETE FROM public.tb_contas_gerenciais WHERE codigo_conta ="
      " :codigo_conta;"
  )
  executar_comando_sql(query, {"codigo_conta": codigo_conta})


# -----------------------------------------------------------------------------
# 1. INICIALIZAÇÃO DA SESSÃO E CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
if "logo_personalizada" not in st.session_state:
  st.session_state.logo_personalizada = None

icone_aba = (
    st.session_state.logo_personalizada
    if st.session_state.logo_personalizada is not None
    else "🏛️"
)

st.set_page_config(
    page_title="SiGeO - Sistema de Gestão Orçamentária | UFSM",
    page_icon=icone_aba,
    layout="wide",
)

# Estilização CSS geral para padronização dos botões primários
st.markdown(
    """
    <style>
    :root {
        --ufsm-azul-primario: #003366;
        --ufsm-azul-secundario: #005599;
        --ufsm-cinza-claro: #f4f6f9;
    }

    .faixa-superior-ufsm {
        background: linear-gradient(90deg, #003366 0%, #005599 100%);
        padding: 24px 30px;
        border-radius: 8px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .faixa-superior-ufsm h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        color: white;
    }
    .faixa-superior-ufsm p {
        margin: 5px 0 0 0;
        font-size: 15px;
        color: #e0e8f0;
    }

    div[data-testid="stSidebar"] {
        background-color: var(--ufsm-cinza-claro);
        border-right: 1px solid #e1e4e8;
    }

    div[data-testid="stSidebar"] button {
        width: 100%;
        border-radius: 6px;
        height: 2.8em;
        font-weight: bold;
        margin-bottom: 4px;
    }

    /* Padronização global de botões primários em azul UFSM */
    .stButton button[kind="primary"], div[data-testid="stFormSubmitButton"] button {
        background-color: #003366 !important;
        border-color: #003366 !important;
        color: white !important;
    }
    
    .stButton button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #002244 !important;
        border-color: #002244 !important;
    }

    @media print {
        [data-testid="stSidebar"], header, footer, .stButton, .stSelectbox, .no-print {
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
        border-bottom: 3px solid #003366;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    .titulo-impressao h2 {
        margin: 0;
        color: #003366;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .titulo-impressao h4 {
        margin: 4px 0 0 0;
        color: #444444;
        font-size: 14px;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. VARIÁVEIS DE ESTADO
# -----------------------------------------------------------------------------
USUARIOS_PADRAO = [
    {
        "usuario": "admin",
        "nome": "Administrador Geral",
        "senha": "ufsm2026",
        "perfil": "Administrador",
    },
    {
        "usuario": "pra_gestor",
        "nome": "Gestor PRA",
        "senha": "pra123",
        "perfil": "Gestor",
    },
]

if "pagina_atual" not in st.session_state:
  st.session_state.pagina_atual = "inicio"

if "tabela_usuarios" not in st.session_state:
  st.session_state.tabela_usuarios = USUARIOS_PADRAO.copy()

if "usuario_logado" not in st.session_state:
  st.session_state.usuario_logado = None

if "dados_tg_raw" not in st.session_state:
  st.session_state.dados_tg_raw = None

if "tot_expandidos_set" not in st.session_state:
  st.session_state.tot_expandidos_set = set()

if "editando_codigo_ug" not in st.session_state:
  st.session_state.editando_codigo_ug = None

if "editando_codigo_unidade" not in st.session_state:
  st.session_state.editando_codigo_unidade = None

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
    st.markdown(
        "<h1 style='color: #003366; text-align: center;'>SiGeO - UFSM</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3 style='text-align: center; color: #555;'>Sistema de Gestão"
        " Orçamentária</h3>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    with st.form("form_login"):
      c_user, c_pass = st.columns(2)
      usuario_input = c_user.text_input("Usuário:")
      senha_input = c_pass.text_input("Senha:", type="password")

      btn_entrar = st.form_submit_button(
          "Entrar no Sistema", type="primary", use_container_width=True
      )

      if btn_entrar:
        usuario_encontrado = None
        for u in st.session_state.tabela_usuarios:
          if (
              u["usuario"].lower() == usuario_input.strip().lower()
              and u["senha"] == senha_input
          ):
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
  else:
    st.sidebar.markdown(
        "<h2 style='color: #003366; text-align: center; margin-bottom:"
        " 0;'>🏛️ UFSM</h2>",
        unsafe_allow_html=True,
    )

  st.sidebar.markdown(
      "<h3 style='text-align: center; color: #003366; margin-top:"
      " 5px;'>SiGeO</h3>",
      unsafe_allow_html=True,
  )
  st.sidebar.caption(
      f"Usuário: **{st.session_state.usuario_logado['nome']}**"
      f" ({st.session_state.usuario_logado['perfil']})"
  )

  st.sidebar.markdown("---")

  # 1. Início
  if st.sidebar.button(
      "🏠 Início",
      use_container_width=True,
      type=(
          "primary"
          if st.session_state.pagina_atual == "inicio"
          else "secondary"
      ),
  ):
    st.session_state.pagina_atual = "inicio"
    st.rerun()

  # 2. Configurações
  with st.sidebar.expander("⚙️ Configurações", expanded=False):
    if st.button(
        "📝 Texto de Abertura",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "texto_abertura"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "texto_abertura"
      st.rerun()
    if st.button(
        "🎨 Identidade Visual",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "config"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "config"
      st.rerun()

  # 3. Cadastros
  with st.sidebar.expander("🗂️ Cadastros", expanded=False):
    if st.button(
        "👤 Usuários",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "usuarios"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "usuarios"
      st.rerun()
    if st.button(
        "🏢 Unidades",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "unidades"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "unidades"
      st.rerun()
    if st.button(
        "📌 UGs",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "unidades_consolidadas"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "unidades_consolidadas"
      st.rerun()
    if st.button(
        "🏷️ Contas Gerenciais",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "contas"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "contas"
      st.rerun()
    if st.button(
        "📑 Naturezas de Despesas",
        use_container_width=True,
        type=(
            "primary" if st.session_state.pagina_atual == "ndd" else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "ndd"
      st.rerun()

  # 4. Gestão de Dados
  with st.sidebar.expander("📊 Gestão de Dados", expanded=False):
    if st.button(
        "📁 Carga do Relatório do Tesouro Gerencial",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "carga"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "carga"
      st.rerun()
    if st.button(
        "📥 Lançamentos",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "lancamentos"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "lancamentos"
      st.rerun()
    if st.button(
        "🔮 Simulações (Gestão)",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "simulacoes_gestao"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "simulacoes_gestao"
      st.rerun()

  # 5. Relatórios
  with st.sidebar.expander("📈 Relatórios", expanded=False):
    if st.button(
        "📋 Demonstrativo de Execução Orçamentária",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "relatorio"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "relatorio"
      st.rerun()
    if st.button(
        "📊 Simulações Orçamentárias",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "simulacoes_orcamentarias"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "simulacoes_orcamentarias"
      st.rerun()

  st.sidebar.markdown("---")

  # 6. Sair
  if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.autenticado = False
    st.session_state.usuario_logado = None
    st.rerun()

  st.sidebar.markdown(
      "<p style='text-align: center; font-size: 11px; color: #666;'>Universidade"
      " Federal de Santa Maria<br>© 2026</p>",
      unsafe_allow_html=True,
  )


  def converter_valor(val):
    if pd.isna(val):
      return 0.0
    if isinstance(val, (int, float)):
      return float(val)
    val_str = str(val).strip().replace(".", "").replace(",", ".")
    try:
      return float(val_str)
    except:
      return 0.0


  def extrair_mes(val):
    if pd.isna(val):
      return 1
    if isinstance(val, (int, float)):
      m = int(val)
      return m if 1 <= m <= 12 else 1
    val_str = str(val).strip()
    try:
      m = int(float(val_str))
      if 1 <= m <= 12:
        return m
    except:
      pass
    match = re.search(r'\d+', val_str)
    if match:
      m = int(match.group())
      if 1 <= m <= 12:
        return m
    try:
      dt = pd.to_datetime(val_str, errors='coerce')
      if pd.notna(dt):
        return dt.month
    except:
      pass
    return 1


  # -----------------------------------------------------------------------------
  # TELA: INÍCIO / DASHBOARD
  # -----------------------------------------------------------------------------
  if st.session_state.pagina_atual == "inicio":
    st.markdown(
        """
            <div class="faixa-superior-ufsm">
                <h1>SiGeO - Sistema de Gestão Orçamentária</h1>
                <p>Universidade Federal de Santa Maria (UFSM) | Pró-Reitoria de Administração</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Bem-vindo ao SiGeO")

    col_logo_ini, col_texto_ini = st.columns([1, 2])

    with col_logo_ini:
      st.markdown("### 🖼️ Campo para Logo")
      if st.session_state.logo_personalizada is not None:
        st.image(st.session_state.logo_personalizada, width=180)
      else:
        st.info("Logo institucional padrão ou a ser configurada.")

    with col_texto_ini:
      st.markdown("### 📝 Campo para Texto Inicial")
      st.info(
          "Este espaço exibirá o texto inicial cadastrado no sistema (a ser"
          " integrado com tabela dedicada no banco de dados em breve)."
      )

    st.markdown("---")
    st.info(
        "💡 **Dica**: Utilize o menu lateral esquerdo para navegar entre os"
        " módulos de Cadastros, Gestão de Dados e Relatórios."
    )

  # -----------------------------------------------------------------------------
  # PÁGINA: CARGA DO RELATÓRIO DO TESOURO GERENCIAL
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "carga":
    st.markdown(
        "<h2 style='color: #003366;'>📁 Carga do Relatório do Tesouro Gerencial"
        " e Gravação no Supabase</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Faça o upload da planilha líquida/executada do Tesouro Gerencial (.xlsx"
        " ou .csv) e mapeie as colunas para carregar no Supabase."
    )

    arquivo = st.file_uploader(
        "Selecione o arquivo da UFSM", type=["csv", "xlsx"]
    )

    if arquivo is not None:
      try:
        if arquivo.name.endswith(".csv"):
          try:
            df = pd.read_csv(arquivo, sep=";", encoding="latin1")
          except:
            df = pd.read_csv(arquivo)
        else:
          df = pd.read_excel(arquivo)

        colunas = list(df.columns)
        st.success(
            f"Arquivo carregado com sucesso! Total de {len(df):,} linhas"
            " encontradas."
        )

        st.markdown("---")
        st.subheader("⚙ Mapeamento Dinâmico de Colunas")
        st.info(
            "Selecione abaixo a correspondência correta das colunas do seu"
            " arquivo para padronização:"
        )

        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
          col_ex = st.selectbox(
              "Coluna de Exercício / Ano:",
              colunas,
              index=0 if len(colunas) > 0 else 0,
          )
          col_ug = st.selectbox(
              "Coluna de UG Responsável:",
              colunas,
              index=min(6, len(colunas) - 1),
          )
        with c_m2:
          col_mes = st.selectbox(
              "Coluna de Mês / Competência:",
              colunas,
              index=min(1, len(colunas) - 1),
          )
          col_desc = st.selectbox(
              "Coluna de Descrição / Histórico:",
              colunas,
              index=min(2, len(colunas) - 1),
          )
        with c_m3:
          col_nd = st.selectbox(
              "Coluna de Natureza de Despesa (NDD):",
              colunas,
              index=min(11, len(colunas) - 1),
          )
          col_val = st.selectbox(
              "Coluna de Valor Liquidado:", colunas, index=len(colunas) - 1
          )

        if st.button("🔄 Processar e Visualizar Dados Tratados", type="primary"):
          df_tratado = pd.DataFrame()
          df_tratado["exercicio"] = (
              pd.to_numeric(df[col_ex], errors="coerce")
              .fillna(datetime.now().year)
              .astype(int)
          )
          df_tratado["mes_competencia"] = df[col_mes].apply(extrair_mes)
          df_tratado["ug_responsavel"] = df[col_ug].astype(str).str.strip()
          df_tratado["natureza_despesa_detalhada"] = (
              df[col_nd].astype(str).str.strip()
          )
          df_tratado["descricao"] = df[col_desc].astype(str).str.strip()
          df_tratado["valor_liquidado"] = df[col_val].apply(converter_valor)

          st.session_state.dados_tg_raw = df_tratado
          st.success("Dados tratados com sucesso!")
          st.dataframe(df_tratado.head(5), use_container_width=True)

        if st.session_state.dados_tg_raw is not None:
          st.markdown("---")
          st.subheader("🚀 Exportação e Carga Massiva para o Supabase")
          if st.button("🚀 Gravar Dados no Supabase", type="primary"):
            with st.spinner("Enviando lotes de dados para o Supabase..."):
              carregar_dados_para_supabase(
                  st.session_state.dados_tg_raw, "tb_execucao_despesa"
              )
              st.success(
                  "🎉 Carga concluída com sucesso no banco de dados Supabase!"
              )

      except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")

    elif st.session_state.dados_tg_raw is not None:
      st.info("Planilha tratada armazenada na memória local do sistema.")
      if st.button("Remover e Enviar Nova Planilha", type="primary"):
        st.session_state.dados_tg_raw = None
        st.rerun()

  # -----------------------------------------------------------------------------
  # PÁGINA: DEMONSTRATIVO DE EXECUÇÃO ORÇAMENTÁRIA (COM FILTROS E MESES)
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "relatorio":
    c_head1, c_head2 = st.columns([1, 4])
    with c_head1:
      if st.session_state.logo_personalizada is not None:
        st.image(st.session_state.logo_personalizada, width=130)
      else:
        st.markdown(
            "<h2 style='color: #003366; margin: 0;'>🏛️ UFSM</h2>",
            unsafe_allow_html=True,
        )
    with c_head2:
      st.markdown(
          f"""
                <div class="cabecalho-impressao">
                    <div class="titulo-impressao">
                        <h2>UNIVERSIDADE FEDERAL DE SANTA MARIA</h2>
                        <h4>PRÓ-REITORIA DE ADMINISTRAÇÃO - DEMONSTRATIVO DE EXECUÇÃO ORÇAMENTÁRIA</h4>
                    </div>
                    <div style="text-align: right; font-size: 11px; color: #555;">
                        <b>SiGeO</b> - Sistema de Gestão Orçamentária<br>
                        Emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
                    </div>
                </div>
            """,
          unsafe_allow_html=True,
      )

    st.subheader(
        "📊 Demonstrativo Financeiro Comparativo (Consulta SQL Direta do"
        " Supabase)"
    )

    # --- CARREGAR OPÇÕES PARA OS FILTROS DE UNIDADES E CONTAS GERENCIAIS ---
    try:
      df_unidades_filtro = executar_consulta_sql(
          "SELECT DISTINCT ug_responsavel FROM tb_execucao_despesa WHERE"
          " ug_responsavel IS NOT NULL ORDER BY ug_responsavel;"
      )
      unidades_opcoes = (
          df_unidades_filtro["ug_responsavel"].tolist()
          if not df_unidades_filtro.empty
          else []
      )
    except Exception:
      unidades_opcoes = []

    try:
      df_contas_filtro = executar_consulta_sql(
          "SELECT codigo_conta, nome_conta FROM tb_contas_gerenciais ORDER BY"
          " codigo_conta;"
      )
      contas_opcoes = (
          [
              f"{row['codigo_conta']} - {row['nome_conta']}"
              for _, row in df_contas_filtro.iterrows()
          ]
          if not df_contas_filtro.empty
          else []
      )
    except Exception:
      contas_opcoes = []

    # Nomes dos meses para o seletor unificado
    meses_nomes = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }
    lista_meses_ano = [f"{m:02d} - {meses_nomes[m]}" for m in range(1, 13)]

    # Layout de Filtros
    c_f1, c_f2, c_f3, c_f4 = st.columns(4)
    with c_f1:
      # Busca dinâmica dos anos disponíveis no banco de dados (incluindo 2022, 2023, etc.)
      try:
        df_anos_db = executar_consulta_sql(
            "SELECT DISTINCT exercicio FROM tb_execucao_despesa WHERE exercicio IS NOT NULL ORDER BY exercicio DESC;"
        )
        anos_disponiveis = df_anos_db["exercicio"].tolist() if not df_anos_db.empty else [datetime.now().year, datetime.now().year - 1, datetime.now().year - 2]
      except Exception:
        anos_disponiveis = [datetime.now().year, datetime.now().year - 1, datetime.now().year - 2]
      
      ano_selecionado = st.selectbox("Ano de Referência:", options=anos_disponiveis, index=0)
    with c_f2:
      mes_ano_selecionado_str = st.selectbox(
          "Mês/Ano Encerrado:", options=lista_meses_ano, index=min(datetime.now().month - 1, 11)
      )
      mes_encerrado = int(mes_ano_selecionado_str.split(" - ")[0])
    with c_f3:
      unidade_selecionada = st.selectbox(
          "Unidade (UG):", options=["Todas"] + unidades_opcoes
      )
    with c_f4:
      conta_selecionada = st.selectbox(
          "Conta Gerencial:", options=["Todas"] + contas_opcoes
      )

    if st.button("🔍 Executar Consulta SQL no Supabase", type="primary"):
      with st.spinner(
          "Buscando e processando dados diretamente do Supabase..."
      ):
        try:
          # Construção da query dinâmica para extrair as contas e a execução mês a mês do ano selecionado
          meses_esquerda = list(range(1, mes_encerrado + 1))
          meses_direita = list(range(mes_encerrado + 1, 13))

          # Montando sumparizações condicionais por mês
          case_meses_sql = ""
          for m in range(1, 13):
            case_meses_sql += f'SUM(CASE WHEN e.exercicio = {ano_selecionado} AND e.mes_competencia = {m} THEN e.valor_liquidado ELSE 0 END) AS "mes_{m}",\n'

          query_relatorio = f"""
                    SELECT 
                        COALESCE(cg.nivel, 'Nível 1') AS "Nível",
                        COALESCE(cg.codigo_conta, 'S/C') AS "Código",
                        COALESCE(cg.nome_conta, e.natureza_despesa_detalhada) AS "Conta Gerencial",
                        {case_meses_sql}
                        SUM(CASE WHEN e.exercicio = {ano_selecionado - 1} THEN e.valor_liquidado ELSE 0 END) AS "Ano Anterior"
                    FROM tb_execucao_despesa e
                    LEFT JOIN tb_natureza_despesa_detalhada ndd ON e.natureza_despesa_detalhada = ndd.codigo_ndd
                    LEFT JOIN tb_contas_gerenciais cg ON ndd.conta_gerencial LIKE '%%' || cg.codigo_conta || '%%'
                    WHERE e.exercicio IN ({ano_selecionado}, {ano_selecionado - 1})
                    """

          params = {}

          if unidade_selecionada != "Todas":
            query_relatorio += " AND e.ug_responsavel = :unidade"
            params["unidade"] = unidade_selecionada

          if conta_selecionada != "Todas":
            codigo_conta_limpo = conta_selecionada.split(" - ")[0]
            query_relatorio += " AND cg.codigo_conta = :conta"
            params["conta"] = codigo_conta_limpo

          query_relatorio += """
                    GROUP BY "Nível", "Código", "Conta Gerencial"
                    ORDER BY "Código" ASC, "Conta Gerencial" ASC;
                    """

          df_sql = executar_consulta_sql(
              query_relatorio, params=params if params else None
          )

          if df_sql.empty:
            st.warning(
                "Nenhum registro encontrado no Supabase para os filtros"
                " selecionados."
            )
          else:
            # Montar DataFrame final formatado com os blocos solicitados
            df_final = pd.DataFrame()
            df_final["Nível"] = df_sql["Nível"]
            df_final["Código"] = df_sql["Código"]
            df_final["Conta Gerencial"] = df_sql["Conta Gerencial"]

            # Colunas à esquerda: Meses anteriores ou iguais ao mês encerrado (Executados)
            cols_executadas = []
            for m in meses_esquerda:
              nome_col = f"{meses_nomes[m][:3]}/{str(ano_selecionado)[-2:]} (Exec.)"
              df_final[nome_col] = df_sql[f"mes_{m}"]
              cols_executadas.append(nome_col)

            # Totalizador da execução até o mês encerrado
            if cols_executadas:
              df_final["Total Executado"] = df_final[cols_executadas].sum(axis=1)
            else:
              df_final["Total Executado"] = 0.0

            # Colunas à direita: Meses restantes para completar o ano (Orçados / Zerados inicialmente)
            cols_orcadas = []
            for m in meses_direita:
              nome_col = f"{meses_nomes[m][:3]}/{str(ano_selecionado)[-2:]} (Orç.)"
              df_final[nome_col] = 0.0  # Inicialmente zerados conforme instrução
              cols_orcadas.append(nome_col)

            # Totalizador dos meses orçados
            if cols_orcadas:
              df_final["Total Orçado"] = df_final[cols_orcadas].sum(axis=1)
            else:
              df_final["Total Orçado"] = 0.0

            # Total Geral Projetado (Executado + Orçado)
            df_final["Total Geral"] = df_final["Total Executado"] + df_final["Total Orçado"]
            
            # Comparativo com o Ano Anterior
            df_final["Ano Anterior"] = df_sql["Ano Anterior"]
            df_final["Variação (%)"] = (
                (
                    df_final["Total Geral"]
                    - df_final["Ano Anterior"]
                )
                / df_final["Ano Anterior"].replace(0, float("nan"))
            ) * 100.0

            # Formatação visual do DataFrame (Padrão brasileiro sem "R$")
            def fmt_moeda(val):
              if pd.isna(val):
                return ""
              s = f"{val:,.2f}"
              return s.replace(",", "X").replace(".", ",").replace("X", ".")

            def fmt_perc(val):
              if pd.isna(val):
                return ""
              s = f"{val:+.2f}%"
              return s.replace(".", ",")

            format_dict = {
                "Ano Anterior": fmt_moeda,
                "Total Executado": fmt_moeda,
                "Total Orçado": fmt_moeda,
                "Total Geral": fmt_moeda,
                "Variação (%)": fmt_perc,
            }
            for col in cols_executadas + cols_orcadas:
              format_dict[col] = fmt_moeda

            st.markdown(f"### Demonstrativo Orçamentário (Mês Encerrado: **{mes_ano_selecionado_str}**)")
            st.dataframe(
                df_final.style.format(format_dict),
                use_container_width=True,
            )

        except Exception as e:
          st.error(f"Erro ao consultar o Supabase: {e}")

  # -----------------------------------------------------------------------------
  # CADASTRO: UNIDADES (`public.tb_unidades`)
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "unidades":
    st.markdown(
        "<h2 style='color: #003366;'>🏢 Cadastro de Unidades</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Gerencie o cadastro de Unidades (`public.tb_unidades`) com suporte a"
        " hierarquia (unidade pai)."
    )

    df_unidades = buscar_unidades_banco()

    opcoes_unidade_pai = ["Nenhuma (Unidade Raiz)"]
    if not df_unidades.empty:
      for _, r_un in df_unidades.iterrows():
        opcoes_unidade_pai.append(
            f"{r_un['codigo_unidade']} - {r_un['nome_unidade']}"
        )

    col_uni1, col_uni2 = st.columns([1, 2])

    with col_uni1:
      st.subheader("➕ Adicionar Nova Unidade")
      with st.form("form_add_unidade", clear_on_submit=True):
        codigo_unidade_in = st.text_input(
            "Código da Unidade * (Único):", placeholder="Ex: 01.01"
        )
        nome_unidade_in = st.text_input(
            "Nome da Unidade *:", placeholder="Ex: Pró-Reitoria de Administração"
        )
        nivel_in = st.text_input("Nível:", value="1")

        pai_sel = st.selectbox("Unidade Pai:", opcoes_unidade_pai)
        ativo_unidade_in = st.checkbox("Unidade Ativa", value=True)

        btn_salvar_unidade = st.form_submit_button(
            "Salvar Unidade", use_container_width=True, type="primary"
        )

        if btn_salvar_unidade:
          if not codigo_unidade_in.strip() or not nome_unidade_in.strip():
            st.error(
                "Os campos 'Código da Unidade' e 'Nome da Unidade' são"
                " obrigatórios."
            )
          else:
            try:
              unidade_pai_val = None
              if pai_sel != "Nenhuma (Unidade Raiz)":
                unidade_pai_val = pai_sel.split(" - ")[0].strip()

              inserir_unidade_banco(
                  codigo_unidade=codigo_unidade_in.strip(),
                  nome_unidade=nome_unidade_in.strip(),
                  nivel=nivel_in.strip() if nivel_in else "1",
                  unidade_pai=unidade_pai_val,
                  ativo=ativo_unidade_in,
              )
              st.success(
                  f"Unidade '{codigo_unidade_in}' cadastrada com sucesso!"
              )
              st.rerun()
            except Exception as e:
              st.error(f"Erro ao salvar unidade: {e}")

    with col_uni2:
      st.subheader(f"Unidades Cadastradas ({len(df_unidades)})")

      if df_unidades.empty:
        st.info("Nenhuma unidade cadastrada na tabela `public.tb_unidades`.")
      else:
        for idx, row in df_unidades.iterrows():
          u_cod = row["codigo_unidade"]
          u_nome = row["nome_unidade"] if pd.notna(row["nome_unidade"]) else ""
          u_nivel = row["nivel"] if pd.notna(row["nivel"]) else "1"
          u_pai = row["unidade_pai"] if pd.notna(row["unidade_pai"]) else ""
          u_ativo = bool(row["ativo"]) if pd.notna(row["ativo"]) else True

          status_str = "🟢" if u_ativo else "🔴"
          pai_info = f" | Pai: {u_pai}" if u_pai else ""
          display_text = (
              f"{status_str} **[{u_cod}]** {u_nome} *(Nível:"
              f" {u_nivel}{pai_info})*"
          )

          c_txt, c_btn_edit, c_btn_del = st.columns([5, 1, 1])
          c_txt.markdown(display_text, unsafe_allow_html=True)

          if c_btn_edit.button(
              "✏️",
              key=f"edit_unidade_btn_{u_cod}",
              help="Alterar dados da unidade",
          ):
            st.session_state.editando_codigo_unidade = u_cod
            st.rerun()

          if c_btn_del.button(
              "🗑️", key=f"del_unidade_btn_{u_cod}", help="Excluir unidade"
          ):
            try:
              excluir_unidade_banco(u_cod)
              st.success(f"Unidade [{u_cod}] excluída com sucesso!")
              st.rerun()
            except Exception as e:
              st.error(f"Erro ao excluir unidade: {e}")

          if st.session_state.editando_codigo_unidade == u_cod:
            with st.container():
              st.markdown("---")
              st.markdown(f"**Editando Unidade Cod: {u_cod}**")

              edit_cod = st.text_input(
                  "Código Unidade:", value=str(u_cod), key=f"edit_un_cod_{u_cod}"
              )
              edit_nome = st.text_input(
                  "Nome da Unidade:", value=u_nome, key=f"edit_un_nome_{u_cod}"
              )
              edit_nivel = st.text_input(
                  "Nível:", value=str(u_nivel), key=f"edit_un_nivel_{u_cod}"
              )

              opcoes_pai_edit = ["Nenhuma (Unidade Raiz)"]
              idx_pai_def = 0
              for _, r_op in df_unidades.iterrows():
                if r_op["codigo_unidade"] != u_cod:
                  opcoes_pai_edit.append(
                      f"{r_op['codigo_unidade']} - {r_op['nome_unidade']}"
                  )

              if u_pai:
                for i_op, op in enumerate(opcoes_pai_edit):
                  if op.startswith(str(u_pai)):
                    idx_pai_def = i_op
                    break

              edit_pai_sel = st.selectbox(
                  "Unidade Pai:",
                  opcoes_pai_edit,
                  index=idx_pai_def,
                  key=f"edit_un_pai_{u_cod}",
              )
              edit_ativo = st.checkbox(
                  "Ativo", value=u_ativo, key=f"edit_un_ativo_{u_cod}"
              )

              c_save, c_canc = st.columns(2)
              if c_save.button(
                  "💾 Salvar Alterações",
                  key=f"save_unidade_btn_{u_cod}",
                  type="primary",
              ):
                try:
                  novo_pai_val = None
                  if edit_pai_sel != "Nenhuma (Unidade Raiz)":
                    novo_pai_val = edit_pai_sel.split(" - ")[0].strip()

                  atualizar_unidade_banco(
                      codigo_unidade_orig=u_cod,
                      codigo_unidade_novo=edit_cod.strip(),
                      nome_unidade=edit_nome.strip(),
                      nivel=edit_nivel.strip() if edit_nivel else "1",
                      unidade_pai=novo_pai_val,
                      ativo=edit_ativo,
                  )
                  st.session_state.editando_codigo_unidade = None
                  st.success("Unidade alterada com sucesso!")
                  st.rerun()
                except Exception as e:
                  st.error(f"Erro ao atualizar unidade: {e}")

              if c_canc.button(
                  "Cancelar",
                  key=f"canc_unidade_btn_{u_cod}",
                  type="secondary",
              ):
                st.session_state.editando_codigo_unidade = None
                st.rerun()
              st.markdown("---")

  # -----------------------------------------------------------------------------
  # CADASTRO: UGS
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "unidades_consolidadas":
    st.markdown(
        "<h2 style='color: #003366;'>📌 Cadastro de UGs</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Gestão das Unidades Gestoras cadastradas no banco de dados"
        " (`public.tb_ugs`)."
    )

    df_ugs = buscar_ugs_banco()
    df_unidades_opcoes = buscar_unidades_banco()

    opcoes_unidades = ["Nenhuma (Selecione a Unidade)"]
    if not df_unidades_opcoes.empty:
      for _, r_un in df_unidades_opcoes.iterrows():
        opcoes_unidades.append(
            f"{r_un['codigo_unidade']} - {r_un['nome_unidade']}"
        )

    col_u1, col_u2 = st.columns([1, 2])

    with col_u1:
      st.subheader("➕ Adicionar Nova UG")
      with st.form("form_add_ug", clear_on_submit=True):
        codigo_input = st.text_input(
            "Código da UG * (Único):", placeholder="Ex: 153164"
        )
        nome_input = st.text_input(
            "Nome da UG *:", placeholder="Ex: Pró-Reitoria de Administração"
        )
        unidade_sel = st.selectbox("Unidade Vinculada *:", opcoes_unidades)
        ativo_input = st.checkbox("UG Ativa", value=True)

        btn_salvar = st.form_submit_button(
            "Salvar UG", use_container_width=True, type="primary"
        )

        if btn_salvar:
          if (
              not codigo_input.strip()
              or not nome_input.strip()
              or unidade_sel == "Nenhuma (Selecione a Unidade)"
          ):
            st.error(
                "Os campos 'Código da UG', 'Nome da UG' e 'Unidade Vinculada' são"
                " obrigatórios."
            )
          else:
            try:
              unidade_val = unidade_sel.split(" - ")[0].strip()
              inserir_ug_banco(
                  codigo_ug=codigo_input.strip(),
                  nome=nome_input.strip(),
                  unidade=unidade_val,
                  ativo=ativo_input,
              )
              st.success(f"UG '{codigo_input}' cadastrada com sucesso!")
              st.rerun()
            except Exception as e:
              st.error(f"Erro ao salvar UG: {e}")

    with col_u2:
      st.subheader(f"Unidades Gestoras Cadastradas ({len(df_ugs)})")

      if df_ugs.empty:
        st.info("Nenhuma UG cadastrada na tabela `public.tb_ugs`.")
      else:
        for idx, row in df_ugs.iterrows():
          ug_cod = row["codigo_ug"]
          ug_nome = row["nome"] if pd.notna(row["nome"]) else ""
          ug_unidade = row["unidade"] if pd.notna(row["unidade"]) else ""
          ug_ativo = bool(row["ativo"]) if pd.notna(row["ativo"]) else True

          status_str = "🟢" if ug_ativo else "🔴"
          display_text = (
              f"{status_str} **[{ug_cod}]** {ug_nome} *(Unidade:"
              f" {ug_unidade})*"
          )

          c_txt, c_btn_edit, c_btn_del = st.columns([5, 1, 1])
          c_txt.markdown(display_text)

          if c_btn_edit.button(
              "✏️", key=f"edit_ug_btn_{ug_cod}", help="Alterar dados da UG"
          ):
            st.session_state.editando_codigo_ug = ug_cod
            st.rerun()

          if c_btn_del.button(
              "🗑️", key=f"del_ug_btn_{ug_cod}", help="Excluir UG"
          ):
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

              edit_cod = st.text_input(
                  "Código UG:", value=str(ug_cod), key=f"edit_cod_{ug_cod}"
              )
              edit_nome = st.text_input(
                  "Nome:", value=ug_nome, key=f"edit_nome_{ug_cod}"
              )

              idx_un_def = 0
              if ug_unidade:
                for i_op, op in enumerate(opcoes_unidades):
                  if op.startswith(str(ug_unidade)):
                    idx_un_def = i_op
                    break

              edit_unidade_sel = st.selectbox(
                  "Unidade Vinculada:",
                  opcoes_unidades,
                  index=idx_un_def,
                  key=f"edit_unidade_{ug_cod}",
              )
              edit_ativo = st.checkbox(
                  "Ativo", value=ug_ativo, key=f"edit_ativo_{ug_cod}"
              )

              c_save, c_canc = st.columns(2)
              if c_save.button(
                  "💾 Salvar Alterações",
                  key=f"save_ug_btn_{ug_cod}",
                  type="primary",
              ):
                if edit_unidade_sel == "Nenhuma (Selecione a Unidade)":
                  st.error("Selecione uma unidade válida.")
                else:
                  try:
                    novo_unidade_val = edit_unidade_sel.split(" - ")[0].strip()
                    atualizar_ug_banco(
                        codigo_ug_orig=ug_cod,
                        codigo_ug_novo=edit_cod.strip(),
                        nome=edit_nome.strip(),
                        unidade=novo_unidade_val,
                        ativo=edit_ativo,
                    )
                    st.session_state.editando_codigo_ug = None
                    st.success("Unidade Gestora alterada com sucesso!")
                    st.rerun()
                  except Exception as e:
                    st.error(f"Erro ao atualizar UG: {e}")

              if c_canc.button(
                  "Cancelar", key=f"canc_ug_btn_{ug_cod}", type="secondary"
              ):
                st.session_state.editando_codigo_ug = None
                st.rerun()
              st.markdown("---")

  # -----------------------------------------------------------------------------
  # CADASTRO: CONTAS GERENCIAIS
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "contas":
    st.markdown(
        "<h2 style='color: #003366;'>🏷️ Gestão de Contas Gerenciais</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Gerencie o cadastro de Contas Gerenciais"
        " (`public.tb_contas_gerenciais`)."
    )

    df_cg = buscar_contas_gerenciais_banco()
    col_add_cg, col_list_cg = st.columns([1, 2])

    with col_add_cg:
      st.subheader("➕ Nova Conta Gerencial")
      with st.form("form_add_cg", clear_on_submit=True):
        codigo_conta_in = st.text_input(
            "Código da Conta * (Ex: 1.0, 1.1):", placeholder="Ex: 1.1"
        )
        nome_conta_in = st.text_input(
            "Nome da Conta *:", placeholder="Ex: Obras e Reformas"
        )
        nivel_in = st.text_input(
            "Nível (Ex: 1, 2, 3 ou Nível 1):", value="1"
        )
        ativo_in = st.checkbox("Conta Ativa", value=True)

        btn_save_cg = st.form_submit_button(
            "Salvar Conta Gerencial", use_container_width=True, type="primary"
        )

        if btn_save_cg:
          if not codigo_conta_in.strip() or not nome_conta_in.strip():
            st.error(
                "Os campos 'Código da Conta' e 'Nome da Conta' são"
                " obrigatórios."
            )
          else:
            try:
              inserir_conta_gerencial_banco(
                  codigo_conta=codigo_conta_in.strip(),
                  nome_conta=nome_conta_in.strip(),
                  nivel=nivel_in.strip() if nivel_in else "1",
                  ativo=ativo_in,
              )
              st.success(f"Conta '{codigo_conta_in}' inserida com sucesso!")
              st.rerun()
            except Exception as e:
              st.error(f"Erro ao inserir conta gerencial: {e}")

    with col_list_cg:
      st.subheader(f"Contas Gerenciais Cadastradas ({len(df_cg)})")

      if df_cg.empty:
        st.info(
            "Nenhuma Conta Gerencial cadastrada na tabela"
            " `public.tb_contas_gerenciais`."
        )
      else:
        for idx, row in df_cg.iterrows():
          c_cod = row["codigo_conta"]
          c_nome = row["nome_conta"] if pd.notna(row["nome_conta"]) else ""
          c_niv = row["nivel"] if pd.notna(row["nivel"]) else "1"
          c_ativo = bool(row["ativo"]) if pd.notna(row["ativo"]) else True

          status_icon = "🟢" if c_ativo else "🔴"
          disp_str = f"{status_icon} **[{c_cod}]** {c_nome} *(Nível: {c_niv})*"

          c_txt, c_btn_edit, c_btn_del = st.columns([5, 1, 1])
          c_txt.markdown(disp_str, unsafe_allow_html=True)

          if c_btn_edit.button(
              "✏️", key=f"edit_cg_btn_{c_cod}", help="Editar Conta"
          ):
            st.session_state.editando_codigo_conta = c_cod
            st.rerun()

          if c_btn_del.button(
              "🗑️", key=f"del_cg_btn_{c_cod}", help="Excluir Conta"
          ):
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

              e_cod = st.text_input(
                  "Código da Conta:", value=str(c_cod), key=f"edit_cg_cod_{c_cod}"
              )
              e_nome = st.text_input(
                  "Nome da Conta:", value=c_nome, key=f"edit_cg_nome_{c_cod}"
              )
              e_niv = st.text_input(
                  "Nível:", value=str(c_niv), key=f"edit_cg_niv_{c_cod}"
              )
              e_ativo = st.checkbox(
                  "Ativo", value=c_ativo, key=f"edit_cg_ativo_{c_cod}"
              )

              c_save, c_canc = st.columns(2)
              if c_save.button(
                  "💾 Salvar", key=f"save_cg_btn_{c_cod}", type="primary"
              ):
                try:
                  atualizar_conta_gerencial_banco(
                      codigo_conta_orig=c_cod,
                      codigo_conta_novo=e_cod.strip(),
                      nome_conta=e_nome.strip(),
                      nivel=e_niv.strip() if e_niv else "1",
                      ativo=e_ativo,
                  )
                  st.session_state.editando_codigo_conta = None
                  st.success("Conta Gerencial atualizada com sucesso!")
                  st.rerun()
                except Exception as e:
                  st.error(f"Erro ao atualizar conta: {e}")

              if c_canc.button(
                  "Cancelar", key=f"canc_cg_btn_{c_cod}", type="secondary"
              ):
                st.session_state.editando_codigo_conta = None
                st.rerun()
              st.markdown("---")

  # -----------------------------------------------------------------------------
  # CADASTRO: NATUREZAS DE DESPESAS
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "ndd":
    st.markdown(
        "<h2 style='color: #003366;'>📑 Natureza de Despesa Detalhada"
        " (NDD)</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Gerencie a estrutura da Natureza de Despesa Detalhada"
        " (`public.tb_natureza_despesa_detalhada`)."
    )

    df_cg_opcoes = buscar_contas_gerenciais_banco()
    opcoes_cg = ["Nenhum (Sem vínculo)"]
    if not df_cg_opcoes.empty:
      for _, r_cg in df_cg_opcoes.iterrows():
        nome_c = (
            f" - {r_cg['nome_conta']}"
            if pd.notna(r_cg["nome_conta"]) and r_cg["nome_conta"]
            else ""
        )
        opcoes_cg.append(f"[{r_cg['codigo_conta']}]{nome_c}")

    df_ndd = buscar_ndd_banco()
    col_add_ndd, col_list_ndd = st.columns([1, 2])

    with col_add_ndd:
      st.subheader("➕ Nova NDD")
      with st.form("form_add_ndd", clear_on_submit=True):
        cod_ndd_in = st.text_input(
            "Código NDD * (Único):", placeholder="Ex: 33903001"
        )
        desc_ndd_in = st.text_input(
            "Descrição *:", placeholder="Ex: Combustíveis e Lubrificantes"
        )
        grupo_despesa_in = st.text_input(
            "Grupo de Despesa:", placeholder="Ex: Material de Consumo"
        )
        conta_gerencial_sel = st.selectbox(
            "Conta Gerencial *:", opcoes_cg
        )

        btn_save_ndd = st.form_submit_button(
            "Salvar NDD", use_container_width=True, type="primary"
        )

        if btn_save_ndd:
          if (
              not cod_ndd_in.strip()
              or not desc_ndd_in.strip()
              or conta_gerencial_sel == "Nenhum (Sem vínculo)"
          ):
            st.error(
                "Os campos 'Código NDD', 'Descrição' e 'Conta Gerencial' são"
                " obrigatórios."
            )
          else:
            try:
              inserir_ndd_banco(
                  codigo_ndd=cod_ndd_in.strip(),
                  descricao=desc_ndd_in.strip(),
                  grupo_despesa=(
                      grupo_despesa_in.strip() if grupo_despesa_in else None
                  ),
                  conta_gerencial=conta_gerencial_sel,
              )
              st.success(f"NDD '{cod_ndd_in}' salva com sucesso!")
              st.rerun()
            except Exception as e:
              st.error(f"Erro ao salvar NDD: {e}")

    with col_list_ndd:
      st.subheader(f"NDDs Cadastradas ({len(df_ndd)})")

      if df_ndd.empty:
        st.info("Nenhuma Natureza de Despesa Detalhada cadastrada.")
      else:
        for idx, row in df_ndd.iterrows():
          n_cod = row["codigo_ndd"]
          n_desc = row["descricao"] if pd.notna(row["descricao"]) else ""
          n_grp = row["grupo_despesa"] if pd.notna(row["grupo_despesa"]) else ""
          n_cg = row["conta_gerencial"] if pd.notna(row["conta_gerencial"]) else ""

          lbl_grp = f" *(Grupo: {n_grp})*" if n_grp else ""
          lbl_cg = f" | Conta: {n_cg}" if n_cg else ""
          disp_ndd = f"🏷 **[{n_cod}]** {n_desc}{lbl_grp}{lbl_cg}"

          c_txt, c_btn_edit, c_btn_del = st.columns([5, 1, 1])
          c_txt.markdown(disp_ndd)

          if c_btn_edit.button(
              "✏️", key=f"edit_ndd_btn_{n_cod}", help="Editar NDD"
          ):
            st.session_state.editando_codigo_ndd = n_cod
            st.rerun()

          if c_btn_del.button(
              "🗑️", key=f"del_ndd_btn_{n_cod}", help="Excluir NDD"
          ):
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

              e_ndd_cod = st.text_input(
                  "Código NDD:", value=str(n_cod), key=f"edit_ndd_cod_{n_cod}"
              )
              e_ndd_desc = st.text_input(
                  "Descrição:", value=n_desc, key=f"edit_ndd_desc_{n_cod}"
              )
              e_ndd_grp = st.text_input(
                  "Grupo de Despesa:", value=n_grp, key=f"edit_ndd_grp_{n_cod}"
              )

              idx_cg_def = 0
              if n_cg:
                for i_op, op in enumerate(opcoes_cg):
                  if op == n_cg:
                    idx_cg_def = i_op
                    break

              e_ndd_cg_sel = st.selectbox(
                  "Conta Gerencial:",
                  opcoes_cg,
                  index=idx_cg_def,
                  key=f"edit_ndd_cg_{n_cod}",
              )

              c_save, c_canc = st.columns(2)
              if c_save.button(
                  "💾 Salvar", key=f"save_ndd_btn_{n_cod}", type="primary"
              ):
                try:
                  atualizar_ndd_banco(
                      codigo_ndd_orig=n_cod,
                      codigo_ndd_novo=e_ndd_cod.strip(),
                      descricao=e_ndd_desc.strip(),
                      grupo_despesa=(
                          e_ndd_grp.strip() if e_ndd_grp else None
                      ),
                      conta_gerencial=e_ndd_cg_sel,
                  )
                  st.session_state.editando_codigo_ndd = None
                  st.success("NDD alterada com sucesso
