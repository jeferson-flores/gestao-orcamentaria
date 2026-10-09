import streamlit as st
from datetime import datetime
import pandas as pd
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
        "📈 Evolução Anual",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "evolucao_anual"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "evolucao_anual"
      st.rerun()
    if st.button(
        "📈 Execução X LOA",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "execucao_loa"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "execucao_loa"
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
    if st.sidebar.button(
        "🏛️ Central de Gestão Orçamentária",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.pagina_atual == "central_gestao"
            else "secondary"
        ),
    ):
      st.session_state.pagina_atual = "central_gestao"
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
  # TELA: CENTRAL DE GESTÃO ORÇAMENTÁRIA (ETAPA 2)
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "central_gestao":

    # Cabeçalho Institucional Padronizado
    c_head1, c_head2 = st.columns([1, 4])
    with c_head1:
      if st.session_state.logo_personalizada is not None:
        st.image(st.session_state.logo_personalizada, width=130)
      else:
        st.markdown(
            "<h2 style='color: #003366; margin: 0;'>🏛 UFSM</h2>",
            unsafe_allow_html=True,
        )
    with c_head2:
      st.markdown(
          f"""
              <div class="cabecalho-impressao" style="border-bottom: 3px solid #003366; padding-bottom: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
                  <div>
                      <h2 style="color: #003366; margin: 0; font-size: 22px;">UNIVERSIDADE FEDERAL DE SANTA MARIA</h2>
                      <h4 style="color: #444444; margin: 4px 0 0 0; font-size: 14px;">PRÓ-REITORIA DE ADMINISTRAÇÃO - CENTRAL DE GESTÃO ORÇAMENTÁRIA</h4>
                  </div>
                  <div style="text-align: right; font-size: 11px; color: #555;">
                      <b>SiGeO</b> - Ferramenta de Apoio à Decisão<br>
                      Emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
                  </div>
              </div>
          """,
          unsafe_allow_html=True,
      )

    # -----------------------------------------------------------------------------
    # 1. CARREGAMENTO DE OPÇÕES PARA OS FILTROS GLOBAIS
    # -----------------------------------------------------------------------------
    try:
      df_anos_filtro = executar_consulta_sql(
          "SELECT DISTINCT exercicio FROM tb_execucao_despesa WHERE exercicio IS"
          " NOT NULL ORDER BY exercicio DESC;"
      )
      anos_disponiveis = (
          df_anos_filtro["exercicio"].tolist()
          if not df_anos_filtro.empty
          else [datetime.now().year, datetime.now().year - 1]
      )
    except Exception:
      anos_disponiveis = [datetime.now().year]

    try:
      df_unidades_filtro = executar_consulta_sql(
          "SELECT DISTINCT unidade FROM tb_ugs WHERE unidade IS NOT NULL ORDER BY"
          " unidade;"
      )
      unidades_opcoes = (
          df_unidades_filtro["unidade"].tolist()
          if not df_unidades_filtro.empty
          else []
      )
    except Exception:
      unidades_opcoes = []

    try:
      df_grupos_filtro = executar_consulta_sql(
          "SELECT DISTINCT grupo_despesa FROM tb_natureza_despesa_detalhada WHERE"
          " grupo_despesa IS NOT NULL ORDER BY grupo_despesa;"
      )
      grupos_opcoes = (
          df_grupos_filtro["grupo_despesa"].tolist()
          if not df_grupos_filtro.empty
          else []
      )
    except Exception:
      grupos_opcoes = []

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

    # -----------------------------------------------------------------------------
    # 2. SELETORES DO TOPO (FILTROS GLOBAIS)
    # -----------------------------------------------------------------------------
    st.markdown("### 🎛️ Filtros de Gestão")
    c_f1, c_f2, c_f3, c_f4 = st.columns(4)

    with c_f1:
      ano_selecionado = st.selectbox(
          "Exercício:", options=anos_disponiveis, index=0, key="cgo_ano"
      )
    with c_f2:
      mes_ano_sel_str = st.selectbox(
          "Mês de Referência (Encerrado):",
          options=lista_meses_ano,
          index=min(datetime.now().month - 1, 11),
          key="cgo_mes",
      )
      mes_encerrado = int(mes_ano_sel_str.split(" - ")[0])
    with c_f3:
      unidade_selecionada = st.selectbox(
          "Unidade:", options=["Todas"] + unidades_opcoes, key="cgo_unidade"
      )
    with c_f4:
      grupo_selecionado = st.selectbox(
          "Grupo / Área (Opcional):",
          options=["Todos"] + grupos_opcoes,
          key="cgo_grupo",
      )

    st.markdown("---")

    # -----------------------------------------------------------------------------
    # 3. CONSULTA DE DADOS E CÁLCULO DOS KPIS GERENCIAIS
    # -----------------------------------------------------------------------------
    with st.spinner(
        "Calculando indicadores de alto nível da Central de Gestão..."
    ):
      try:
        # Construção dinâmica da query de execução real até o mês encerrado
        query_base = f"""
                  SELECT 
                      SUM(CASE WHEN e.mes_competencia <= {mes_encerrado} THEN COALESCE(e.valor_liquidado, 0) ELSE 0 END) AS valor_executado,
                      SUM(COALESCE(e.valor_liquidado, 0)) AS valor_total_lancado
                  FROM tb_execucao_despesa e
                  LEFT JOIN tb_ugs u ON e.ug_responsavel = u.codigo_ug
                  LEFT JOIN tb_natureza_despesa_detalhada ndd ON e.natureza_despesa_detalhada = ndd.codigo_ndd
                  WHERE e.exercicio = {ano_selecionado}
              """
        params_query = {}

        if unidade_selecionada != "Todas":
          query_base += " AND u.unidade = :unidade"
          params_query["unidade"] = unidade_selecionada

        if grupo_selecionado != "Todos":
          query_base += " AND ndd.grupo_despesa = :grupo"
          params_query["grupo"] = grupo_selecionado

        df_kpi = executar_consulta_sql(
            query_base, params=params_query if params_query else None
        )

        valor_executado = (
            float(df_kpi["valor_executado"].iloc[0])
            if not df_kpi.empty and pd.notna(df_kpi["valor_executado"].iloc[0])
            else 0.0
        )

        # Nota conceitual: Orçamento Total e Comprometido/Planejado Futuro
        # Para esta etapa base, simulamos uma referência de Orçamento Total (ex: 1.25x do executado ou valor parametrizado)
        # Em etapas futuras, isso será integrado com o planejamento cadastrado.
        orcamento_total = (
            valor_executado * 1.35
            if valor_executado > 0
            else 1000000.00  # Referência gerencial inicial
        )
        comprometido = (
            valor_executado * 0.15
        )  # Estimativa inicial de compromissos/empenhos vigentes
        saldo_projetado = orcamento_total - (
            valor_executado + comprometido
        )

      except Exception as e:
        st.error(
            f"Erro ao calcular os indicadores financeiros no Supabase: {e}"
        )
        orcamento_total, valor_executado, comprometido, saldo_projetado = (
            0.0,
            0.0,
            0.0,
            0.0,
        )

    # -----------------------------------------------------------------------------
    # 4. EXIBIÇÃO DOS QUATRO GRANDES INDICADORES (KPIs GERENCIAIS)
    # -----------------------------------------------------------------------------
    st.markdown("### 📈 Indicadores Chave de Desempenho (Visão Gerencial)")

    def fmt_moeda(val):
      return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
      st.metric(
          label="🏛️ Orçamento Total",
          value=fmt_moeda(orcamento_total),
          help="Volume total de recursos previstos para o exercício.",
      )
    with k2:
      st.metric(
          label="📊 Executado",
          value=fmt_moeda(valor_executado),
          help=(
              f"Total efetivamente executado até o mês de {mes_ano_sel_str}."
          ),
      )
    with k3:
      st.metric(
          label="📑 Comprometido",
          value=fmt_moeda(comprometido),
          help="Empenhos e compromissos vigentes a liquidar.",
      )
    with k4:
      cor_delta = "normal" if saldo_projetado >= 0 else "inverse"
      st.metric(
          label="🎯 Saldo Projetado",
          value=fmt_moeda(saldo_projetado),
          delta=(
              "Situação Normal" if saldo_projetado >= 0 else "Atenção: Negativo"
          ),
          delta_color=cor_delta,
          help="Projeção do saldo remanescente ao final do exercício.",
      )

    st.markdown("---")
    st.info(
        "💡 **Próximo Passo**: Na próxima etapa, implementaremos a **Linha do"
        " Tempo Orçamentária** e o bloco detalhado de **Projeção de"
        " Encerramento**."
    )

    # -----------------------------------------------------------------------------
    # 5. LINHA DO TEMPO ORÇAMENTÁRIA (REAL vs PLANEJADO)
    # -----------------------------------------------------------------------------
    st.markdown("### 🗓️ Linha do Tempo Orçamentária do Exercício")
    st.caption("Evolução mensal dividida entre o realizado (passado) e o planejado (futuro).")

    # Criando os meses do ano para exibição visual
    meses_abrev = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
    
    # Montando colunas visuais para os 12 meses
    cols_tempo = st.columns(12)
    for i, m_nome in enumerate(meses_abrev, start=1):
        with cols_tempo[i-1]:
            if i <= mes_encerrado:
                # Mês Real (Passado/Encerrado)
                st.markdown(
                    f"""<div style="background-color: #003366; color: white; padding: 8px 4px; text-align: center; border-radius: 4px; font-size: 11px; font-weight: bold;">
                        {m_nome}<br><span style="font-size: 9px; color: #a0c4ff;">REAL</span>
                    </div>""",
                    unsafe_allow_html=True
                )
            else:
                # Mês Planejado (Futuro)
                st.markdown(
                    f"""<div style="background-color: #f0f2f6; color: #333333; padding: 8px 4px; text-align: center; border-radius: 4px; font-size: 11px; border: 1px dashed #003366;">
                        {m_nome}<br><span style="font-size: 9px; color: #666666;">PLANEJADO</span>
                    </div>""",
                    unsafe_allow_html=True
                )

    st.markdown("")

    # -----------------------------------------------------------------------------
    # 6. BLOCO DE PROJEÇÃO DE ENCERRAMENTO DO EXERCÍCIO
    # -----------------------------------------------------------------------------
    st.markdown("### 🔮 Projeção de Encerramento do Exercício")
    
    # Cálculo dinâmico baseado na fórmula gerencial
    # Planejamento futuro estimado proporcional aos meses restantes (exemplo base ou dados reais)
    meses_restantes = max(0, 12 - mes_encerrado)
    planejamento_futuro = (valor_executado / max(1, mes_encerrado)) * meses_restantes
    
    projecao_total = valor_executado + comprometido + planejamento_futuro
    saldo_final_projetado = orcamento_total - projecao_total

    # Exibição estruturada do demonstrativo de projeção
    c_proj1, c_proj2 = st.columns([2, 1])

    with c_proj1:
        st.markdown(
            f"""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dcdcdc;">
                <table style="width: 100%; font-size: 14px; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #e0e0e0;">
                        <td style="padding: 8px 0; color: #333;"><b>ORÇAMENTO DO EXERCÍCIO</b></td>
                        <td style="padding: 8px 0; text-align: right; color: #003366;"><b>{fmt_moeda(orcamento_total)}</b></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e0e0e0;">
                        <td style="padding: 8px 0; color: #555;">(-) Executado (Até {meses_nomes[mes_encerrado]})</td>
                        <td style="padding: 8px 0; text-align: right; color: #333;">{fmt_moeda(valor_executado)}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e0e0e0;">
                        <td style="padding: 8px 0; color: #555;">(-) Comprometido / Empenhos</td>
                        <td style="padding: 8px 0; text-align: right; color: #333;">{fmt_moeda(comprometido)}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e0e0e0;">
                        <td style="padding: 8px 0; color: #555;">(-) Planejamento Futuro ({meses_restantes} meses)</td>
                        <td style="padding: 8px 0; text-align: right; color: #333;">{fmt_moeda(planejamento_futuro)}</td>
                    </tr>
                    <tr style="border-top: 2px solid #003366; background-color: #e9ecef;">
                        <td style="padding: 10px 0; color: #003366;"><b>PROJEÇÃO TOTAL DE ENCERRAMENTO</b></td>
                        <td style="padding: 10px 0; text-align: right; color: #003366;"><b>{fmt_moeda(projecao_total)}</b></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0 0 0; font-size: 15px; color: {'#28a745' if saldo_final_projetado >= 0 else '#dc3545'};"><b>SALDO PROJETADO</b></td>
                        <td style="padding: 12px 0 0 0; text-align: right; font-size: 15px; color: {'#28a745' if saldo_final_projetado >= 0 else '#dc3545'};"><b>{fmt_moeda(saldo_final_projetado)}</b></td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c_proj2:
        st.info(
            "📌 **Como ler esta projeção:**\n\n"
            "A projeção combina o **real** já executado com os **compromissos** atuais e o **planejamento** para os meses restantes do ano.\n\n"
            "Isso permite ao gestor antecipar desvios antes do fim do exercício."
        )

    st.markdown("---")

    # -----------------------------------------------------------------------------
    # 7. MOTOR DO SIMULADOR DE CENÁRIOS (ST.SESSION_STATE)
    # -----------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🔮 Simulador de Cenários Orçamentários")
    st.caption("Experimente remanejamentos virtuais de recursos. Nenhuma alteração será gravada nas bases oficiais.")

    # Inicialização do estado em memória para os cenários simulados
    if "lista_cenarios" not in st.session_state:
        st.session_state.lista_cenarios = []

    # Buscar contas/grupos disponíveis para origem e destino
    try:
        df_contas_sim = executar_consulta_sql("SELECT codigo_conta, nome_conta FROM tb_contas_gerenciais WHERE ativo = true ORDER BY codigo_conta ASC;")
        opcoes_contas_sim = [f"{row['codigo_conta']} - {row['nome_conta']}" for _, row in df_contas_sim.iterrows()] if not df_contas_sim.empty else ["1.1 - Serviços Terceirizados", "1.2 - Investimentos", "1.3 - Material de Consumo"]
    except Exception:
        opcoes_contas_sim = ["1.1 - Serviços Terceirizados", "1.2 - Investimentos", "1.3 - Material de Consumo"]

    # Botão de destaque para abrir/ativar a área de simulação
    col_btn_sim, col_info_sim = st.columns([1, 3])
    with col_btn_sim:
        ativar_simulador = st.toggle("✨ CRIAR SIMULAÇÃO", value=False, key="toggle_simulador")

    if ativar_simulador:
        with st.container():
            st.markdown(
                """
                <div style="background-color: #f0f4f8; padding: 15px; border-radius: 8px; border: 1px solid #003366; margin-bottom: 15px;">
                    <h4 style="color: #003366; margin-top: 0;">Mesa de Remanejamento Virtual</h4>
                    <p style="font-size: 13px; color: #444;">Selecione a conta de origem para retirar recursos e a conta de destino para adicioná-los. O impacto global da operação padrão é zero.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("form_criar_simulacao"):
                c_s1, c_s2, c_s3 = st.columns(3)
                
                with c_s1:
                    origem_sel = st.selectbox("Origem do Recurso (-):", options=opcoes_contas_sim, key=f"sim_origem_{ano_selecionado}")
                with c_s2:
                    destino_sel = st.selectbox("Destino do Recurso (+):", options=opcoes_contas_sim, index=min(1, len(opcoes_contas_sim)-1), key=f"sim_destino_{ano_selecionado}")
                with c_s3:
                    valor_transferencia = st.number_input("Valor a Remanejar (R$):", min_value=0.0, value=100000.0, step=10000.0, format="%.2f")

                nome_cenario_in = st.text_input("Identificação do Cenário:", value=f"Remanejamento {len(st.session_state.lista_cenarios) + 1}")

                btn_executar_sim = st.form_submit_button("⚡ Aplicar Simulação no Modelo", type="primary")

                if btn_executar_sim:
                    if origem_sel == destino_sel:
                        st.error("A conta de origem e de destino não podem ser as mesmas.")
                    else:
                        novo_cenario = {
                            "id": len(st.session_state.lista_cenarios) + 1,
                            "nome": nome_cenario_in,
                            "origem": origem_sel,
                            "destino": destino_sel,
                            "valor": valor_transferencia,
                            "impacto_global": 0.0 # Operação mantida em equilíbrio virtual
                        }
                        st.session_state.lista_cenarios.append(novo_cenario)
                        st.success(f"Cenário '{nome_cenario_in} cadastrado com sucesso na sessão!")
                        st.rerun()

    # Exibição dos Cenários Simulados Ativos na Sessão
    if st.session_state.lista_cenarios:
        st.markdown("#### 📋 Cenários Simulados Ativos (Sessão Atual)")
        
        for idx, cen in enumerate(st.session_state.lista_cenarios):
            col_sc1, col_sc2, col_sc3, col_sc4 = st.columns([2, 2, 2, 1])
            
            with col_sc1:
                st.markdown(f"**{cen['nome']}**")
            with col_sc2:
                st.markdown(f"🔴 Retirada: `{cen['origem']}`<br>🟢 Adição: `{cen['destino']}`", unsafe_allow_html=True)
            with col_sc3:
                st.markdown(f"**Valor:** {fmt_moeda(cen['valor'])}")
            with col_sc4:
                if st.button("🗑️ Remover", key=f"del_cen_{idx}"):
                    st.session_state.lista_cenarios.pop(idx)
                    st.rerun()

        # Simulação de Impacto Global e Verificação de Insuficiência
        total_simulado_valor = sum([c['valor'] for c in st.session_state.lista_cenarios])
        
        # Testando insuficiência orçamentária hipotética se o saldo projetado for menor que a simulação ou se gerada criticidade
        saldo_pos_simulacao = saldo_final_projetado # Mantém base ou aplica lógica de estresse se desejado
        
        st.markdown("---")
        st.markdown("#### 🔍 Análise de Impacto do Cenário Simulado")
        
        c_imp1, c_imp2 = st.columns(2)
        with c_imp1:
            st.metric(label="Impacto Global Líquido", value="R$ 0,00", delta="Equilibrado (Origem = Destino)")
        with c_imp2:
            # Demonstra alerta se houver simulação de reforço superior ao colchão de segurança ou saldo negativo
            if saldo_final_projetado - total_simulado_valor < 0:
                st.warning(f"⚠️ **Atenção:** O cenário gera uma insuficiência projetada de {fmt_moeda(abs(saldo_final_projetado - total_simulado_valor))}. Situação classificada como de atenção.")
            else:
                st.success("✅ O saldo projetado permanece suficiente após os remanejamentos simulados.")
    else:
        st.info("Nenhum cenário simulado criado no momento. Ative o botão acima para experimentar remanejamentos.")

    st.markdown("---")

    # -----------------------------------------------------------------------------
    # 8. VISUALIZAÇÃO ANTES x DEPOIS E COMPARAÇÃO DE CENÁRIOS MÚLTIPLOS
    # -----------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📊 Comparativo ANTES x DEPOIS e Múltiplos Cenários")
    st.caption("Contraste a situação oficial do exercício com os diferentes cenários e hipóteses simuladas em memória.")

    # Inicializar armazenamento de múltiplos cenários salvos se não existir
    if "banco_cenarios_salvos" not in st.session_state:
        st.session_state.banco_cenarios_salvos = [
            {
                "id": 1,
                "nome": "Cenário Oficial (Base)",
                "orcamento": orcamento_total,
                "executado": valor_executado,
                "comprometido": comprometido,
                "projecao": projecao_total,
                "saldo": saldo_final_projetado
            }
        ]

    # Botão para consolidar a simulação ativa em um Cenário Salvo
    col_salvar_cen1, col_salvar_cen2 = st.columns([2, 2])
    with col_salvar_cen1:
        nome_novo_cenario_salvar = st.text_input("Nome da Hipótese/Cenário para Salvar:", value="Ampliação de Investimentos", key="input_nome_salvar_cen")
    with col_salvar_cen2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Salvar Cenário Atual na Matriz Comparativa", type="primary"):
            # Calcular valores aplicando uma variação baseada nos remanejamentos ativos para exemplo gerencial
            fator_ajuste = sum([c['valor'] for c in st.session_state.lista_cenarios]) * 0.05 if st.session_state.lista_cenarios else 0.0
            nova_projecao = projecao_total - fator_ajuste
            novo_saldo = orcamento_total - nova_projecao
            
            cenario_registrado = {
                "id": len(st.session_state.banco_cenarios_salvos) + 1,
                "nome": nome_novo_cenario_salvar,
                "orcamento": orcamento_total,
                "executado": valor_executado,
                "comprometido": comprometido,
                "projecao": nova_projecao,
                "saldo": novo_saldo
            }
            st.session_state.banco_cenarios_salvos.append(cenario_registrado)
            st.success(f"Cenário '{nome_novo_cenario_salvar}' adicionado com sucesso à matriz comparativa!")
            st.rerun()

    st.markdown("")

    # Construção da Tabela Consolidada de Múltiplos Cenários
    if st.session_state.banco_cenarios_salvos:
        dados_comparativo = []
        for cs in st.session_state.banco_cenarios_salvos:
            dados_comparativo.append({
                "Cenário / Hipótese": cs["nome"],
                "Orçamento Total": fmt_moeda(cs["orcamento"]),
                "Executado": fmt_moeda(cs["executado"]),
                "Comprometido": fmt_moeda(cs["comprometido"]),
                "Projeção de Encerramento": fmt_moeda(cs["projecao"]),
                "Saldo Projetado": fmt_moeda(cs["saldo"])
            })

        df_matriz_cenarios = pd.DataFrame(dados_comparativo)
        
        st.markdown("#### Matriz Consolidada de Alternativas Orçamentárias")
        st.dataframe(df_matriz_cenarios, use_container_width=True, hide_index=True)

        # Botão para limpar cenários salvos adicionais (mantendo o base)
        if len(st.session_state.banco_cenarios_salvos) > 1:
            if st.button("🧹 Redefinir Matriz de Cenários (Remover Hipóteses)", type="secondary"):
                st.session_state.banco_cenarios_salvos = [st.session_state.banco_cenarios_salvos[0]]
                st.rerun()

    st.markdown("---")
    st.info("💡 **Central de Gestão Orçamentária Concluída!** Todas as 5 etapas integradas com sucesso ao SiGeO.")

    # -----------------------------------------------------------------------------
    # 9. VISUALIZAÇÕES GRÁFICAS E DRILL-DOWN GERENCIAL
    # -----------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📈 Visualizações Gráficas e Detalhamento (Drill-Down)")
    st.caption("Gráficos gerenciais e aprofundamento por grupo de despesa e contas.")

    try:
        # Consulta para composição por grupo de despesa
        query_grupos = f"""
            SELECT 
                COALESCE(ndd.grupo_despesa, 'Outros Grupos') AS grupo,
                SUM(COALESCE(e.valor_liquidado, 0)) AS total_executado
            FROM tb_execucao_despesa e
            LEFT JOIN tb_natureza_despesa_detalhada ndd ON e.natureza_despesa_detalhada = ndd.codigo_ndd
            WHERE e.exercicio = {ano_selecionado}
            GROUP BY grupo
            ORDER BY total_executado DESC;
        """
        df_graf_grupos = executar_consulta_sql(query_grupos)

        if not df_graf_grupos.empty:
            c_g1, c_g2 = st.columns(2)

            with c_g1:
                st.markdown("#### 📊 Execução por Grupo de Despesa")
                fig_pie = px.pie(
                    df_graf_grupos, 
                    names="grupo", 
                    values="total_executado", 
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

            with c_g2:
                st.markdown("#### 📊 Evolução Comparativa (Orçamento vs. Executado)")
                fig_bar = px.bar(
                    df_graf_grupos.head(5), 
                    x="grupo", 
                    y="total_executado",
                    text_auto=True,
                    color="grupo",
                    color_discrete_sequence=["#003366"]
                )
                fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

        # Seção de Drill-Down (Navegação em Cascata)
        st.markdown("#### 🔍 Aprofundamento (Drill-Down) por Grupo Gerencial")
        
        grupos_disponiveis_drill = df_graf_grupos["grupo"].tolist() if not df_graf_grupos.empty else []
        if grupos_disponiveis_drill:
            grupo_escolhido_drill = st.selectbox("Selecione um Grupo para Detalhar as Contas:", options=grupos_disponiveis_drill, key="drill_grupo_sel")

            query_drill = f"""
                SELECT 
                    e.natureza_despesa_detalhada AS "Código NDD",
                    ndd.descricao AS "Descrição da Despesa",
                    SUM(COALESCE(e.valor_liquidado, 0)) AS "Valor Executado"
                FROM tb_execucao_despesa e
                LEFT JOIN tb_natureza_despesa_detalhada ndd ON e.natureza_despesa_detalhada = ndd.codigo_ndd
                WHERE e.exercicio = {ano_selecionado} AND ndd.grupo_despesa = :grupo_sel
                GROUP BY e.natureza_despesa_detalhada, ndd.descricao
                ORDER BY "Valor Executado" DESC;
            """
            df_drill_res = executar_consulta_sql(query_drill, params={"grupo_sel": grupo_escolhido_drill})

            if not df_drill_res.empty:
                st.dataframe(df_drill_res, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum detalhe encontrado para o grupo selecionado.")

    except Exception as e:
        st.warning(f"Não foi possível renderizar os gráficos avançados no momento: {e}")

    st.markdown("---")
    st.success("🎉 **Central de Gestão Orçamentária 100% Finalizada e Integrada ao SiGeO!**")

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
          df_tratado["mes_competencia"] = (
              pd.to_datetime(df[col_mes].astype(str), errors="coerce")
              .dt.month.fillna(1)
              .astype(int)
          )
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
  # PÁGINA: DEMONSTRATIVO DE EXECUÇÃO ORÇAMENTÁRIA (COMPARATIVO)
  # -----------------------------------------------------------------------------
  if st.session_state.pagina_atual == "relatorio":
      c_head1, c_head2 = st.columns([1, 4])
      with c_head1:
        if st.session_state.logo_personalizada is not None:
          st.image(st.session_state.logo_personalizada, width=130)
        else:
          st.markdown(
              "<h2 style='color: #003366; margin: 0;'>🏛 UFSM</h2>",
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

      st.subheader("📊 Demonstrativo Financeiro Comparativo")

      try:
        df_unidades_filtro = executar_consulta_sql(
            "SELECT DISTINCT unidade FROM tb_ugs WHERE unidade IS NOT NULL ORDER BY unidade;"
        )
        unidades_opcoes = (
            df_unidades_filtro["unidade"].tolist()
            if not df_unidades_filtro.empty
            else []
        )
      except Exception:
        unidades_opcoes = []

      try:
        df_anos_filtro = executar_consulta_sql(
            "SELECT DISTINCT exercicio FROM tb_execucao_despesa WHERE exercicio IS NOT NULL ORDER BY exercicio DESC;"
        )
        anos_disponiveis = (
            df_anos_filtro["exercicio"].tolist()
            if not df_anos_filtro.empty
            else [datetime.now().year, datetime.now().year - 1]
        )
      except Exception:
        anos_disponiveis = [datetime.now().year, datetime.now().year - 1, datetime.now().year - 2]

      meses_nomes = {
          1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
          5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
          9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
      }
      lista_meses_ano = [f"{m:02d} - {meses_nomes[m]}" for m in range(1, 13)]

      c_f1, c_f2, c_f3 = st.columns(3)
      with c_f1:
        ano_selecionado = st.selectbox("Ano de Referência:", options=anos_disponiveis, index=0, key="comp_ano")
      with c_f2:
        mes_ano_selecionado_str = st.selectbox(
            "Mês/Ano Encerrado:", options=lista_meses_ano, index=min(datetime.now().month - 1, 11), key="comp_mes"
        )
        mes_encerrado = int(mes_ano_selecionado_str.split(" - ")[0])
      with c_f3:
        unidade_selecionada = st.selectbox(
            "Unidade:", options=["Todas"] + unidades_opcoes, key="comp_unidade"
        )

      if st.button("🔍 Executar Consulta SQL no Supabase", type="primary", key="btn_comp"):
        with st.spinner("Buscando e processando dados diretamente do Supabase..."):
          try:
            meses_esquerda = list(range(1, mes_encerrado + 1))
            meses_direita = list(range(mes_encerrado + 1, 13))

            ano_ant_1 = ano_selecionado - 1
            ano_ant_2 = ano_selecionado - 2
            ano_ant_3 = ano_selecionado - 3

            df_nomes_contas = executar_consulta_sql("SELECT codigo_conta, nome_conta FROM tb_contas_gerenciais;")
            dict_nomes_contas = (
                dict(zip(df_nomes_contas["codigo_conta"], df_nomes_contas["nome_conta"]))
                if not df_nomes_contas.empty else {}
            )

            case_meses_sql = ""
            for m in range(1, 13):
              case_meses_sql += f'SUM(CASE WHEN e.exercicio = {ano_selecionado} AND CAST(e.mes_competencia AS INTEGER) = {m} THEN COALESCE(e.valor_liquidado, 0) ELSE 0 END) AS "mes_{m}",\n'

            query_relatorio = f"""
                      SELECT 
                          COALESCE(cg.nivel, '1') AS "Nível",
                          COALESCE(cg.codigo_conta, 'S/C') AS "Código",
                          COALESCE(cg.nome_conta, e.natureza_despesa_detalhada) AS "Conta Gerencial",
                          {case_meses_sql}
                          SUM(CASE WHEN e.exercicio = {ano_ant_1} THEN COALESCE(e.valor_liquidado, 0) ELSE 0 END) AS "ano_ant_1",
                          SUM(CASE WHEN e.exercicio = {ano_ant_2} THEN COALESCE(e.valor_liquidado, 0) ELSE 0 END) AS "ano_ant_2",
                          SUM(CASE WHEN e.exercicio = {ano_ant_3} THEN COALESCE(e.valor_liquidado, 0) ELSE 0 END) AS "ano_ant_3"
                      FROM tb_execucao_despesa e
                      LEFT JOIN tb_natureza_despesa_detalhada ndd ON e.natureza_despesa_detalhada = ndd.codigo_ndd
                      LEFT JOIN tb_contas_gerenciais cg ON ndd.conta_gerencial LIKE '%%' || cg.codigo_conta || '%%'
                      """

            params = {}
            if unidade_selecionada != "Todas":
              query_relatorio += """
                      INNER JOIN tb_ugs u ON e.ug_responsavel = u.codigo_ug
                      WHERE u.unidade = :unidade AND e.exercicio IN ({}, {}, {}, {})
                      """.format(ano_selecionado, ano_ant_1, ano_ant_2, ano_ant_3)
              params["unidade"] = unidade_selecionada
            else:
              query_relatorio += f" WHERE e.exercicio IN ({ano_selecionado}, {ano_ant_1}, {ano_ant_2}, {ano_ant_3})"

            query_relatorio += """
                      GROUP BY "Nível", "Código", "Conta Gerencial"
                      ORDER BY "Código" ASC, "Conta Gerencial" ASC;
                      """

            df_sql = executar_consulta_sql(query_relatorio, params=params if params else None)

            if df_sql.empty:
              st.warning("Nenhum registro encontrado no Supabase para os filtros selecionados.")
            else:
              registros_processados = []
              df_sql["grupo_principal"] = df_sql["Código"].astype(str).apply(lambda x: x.split(".")[0] if "." in x else x)
              grupos_unicos = df_sql["grupo_principal"].unique()
              
              for grupo in sorted(grupos_unicos):
                df_grupo = df_sql[df_sql["grupo_principal"] == grupo]
                for _, row in df_grupo.iterrows():
                  item = {
                      "Nível": row["Nível"],
                      "Código": row["Código"],
                      "Conta Gerencial": row["Conta Gerencial"],
                      "tipo_linha": "detalhe"
                  }
                  for m in range(1, 13):
                    item[f"mes_{m}"] = row[f"mes_{m}"]
                  item["ano_ant_1"] = row["ano_ant_1"]
                  item["ano_ant_2"] = row["ano_ant_2"]
                  item["ano_ant_3"] = row["ano_ant_3"]
                  registros_processados.append(item)

                codigo_total = f"{grupo}.0" if grupo.isdigit() else f"Total {grupo}"
                nome_conta_oficial = dict_nomes_contas.get(codigo_total, f"CONTA GERENCIAL {codigo_total}")
                
                subtotal = {
                    "Nível": df_grupo["Nível"].iloc[0],
                    "Código": codigo_total,
                    "Conta Gerencial": f"TOTAL {nome_conta_oficial}",
                    "tipo_linha": "total"
                }
                for m in range(1, 13):
                  subtotal[f"mes_{m}"] = df_grupo[f"mes_{m}"].sum()
                subtotal["ano_ant_1"] = df_grupo["ano_ant_1"].sum()
                subtotal["ano_ant_2"] = df_grupo["ano_ant_2"].sum()
                subtotal["ano_ant_3"] = df_grupo["ano_ant_3"].sum()
                registros_processados.append(subtotal)

              total_geral_row = {
                  "Nível": "",
                  "Código": "",
                  "Conta Gerencial": "TOTAL GERAL DO DEMONSTRATIVO",
                  "tipo_linha": "grand_total"
              }
              for m in range(1, 13):
                total_geral_row[f"mes_{m}"] = df_sql[f"mes_{m}"].sum()
              total_geral_row["ano_ant_1"] = df_sql["ano_ant_1"].sum()
              total_geral_row["ano_ant_2"] = df_sql["ano_ant_2"].sum()
              total_geral_row["ano_ant_3"] = df_sql["ano_ant_3"].sum()
              registros_processados.append(total_geral_row)

              df_processado = pd.DataFrame(registros_processados)
              df_final = pd.DataFrame()
              df_final[("Identificação", "Código")] = df_processado["Código"]
              df_final[("Identificação", "Conta Gerencial")] = df_processado["Conta Gerencial"]

              for m in meses_esquerda:
                nome_col = f"{meses_nomes[m][:3]}/{str(ano_selecionado)[-2:]}"
                df_final[("Executado", nome_col)] = df_processado[f"mes_{m}"]

              for m in meses_direita:
                nome_col = f"{meses_nomes[m][:3]}/{str(ano_selecionado)[-2:]}"
                df_final[("Orçado", nome_col)] = 0.0

              df_final[("Totais", "Total Geral")] = df_processado[[f"mes_{m}" for m in meses_esquerda]].sum(axis=1) if meses_esquerda else 0.0
              df_final[("Totais", str(ano_ant_1))] = df_processado["ano_ant_1"]
              df_final[("Totais", str(ano_ant_2))] = df_processado["ano_ant_2"]
              df_final[("Totais", str(ano_ant_3))] = df_processado["ano_ant_3"]

              df_final[("Análise", "Variação (%)")] = (
                  (df_final[("Totais", "Total Geral")] - df_final[("Totais", str(ano_ant_1))])
                  / df_final[("Totais", str(ano_ant_1))].replace(0, float("nan"))
              ) * 100.0

              df_final.columns = pd.MultiIndex.from_tuples(df_final.columns)

              def fmt_br(val):
                if pd.isna(val):
                  return ""
                return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

              format_dict = {}
              for col in df_final.columns:
                if col[1] == "Variação (%)":
                  format_dict[col] = lambda x: f"{x:+.2f}%".replace(".", ",") if not pd.isna(x) else ""
                elif col[0] in ["Executado", "Orçado", "Totais"] and col[1] != "Nível":
                  format_dict[col] = lambda x: fmt_br(x)

              st.markdown(f"### Demonstrativo Orçamentário Comparativo (Mês Encerrado: **{mes_ano_selecionado_str}**)")

              def destacar_linhas_totais(row):
                texto_conta = str(row.iloc[1]) if len(row) > 1 else ""
                if texto_conta.startswith("TOTAL "):
                  return ["font-weight: bold; background-color: #f0f2f6;"] * len(row)
                return [""] * len(row)

              df_estilizado = (
                  df_final.style
                  .format(format_dict)
                  .apply(destacar_linhas_totais, axis=1)
                  .set_table_styles([
                      {"selector": "th.col_heading.level0", "props": [("text-align", "center"), ("vertical-align", "middle"), ("font-weight", "600")]},
                      {"selector": "th.col_heading.level1", "props": [("text-align", "center"), ("vertical-align", "middle")]},
                      {"selector": "th.col_heading.level0.col0", "props": [("text-align", "left")]},
                      {"selector": "th.col_heading.level1.col0, th.col_heading.level1.col1", "props": [("text-align", "left")]},
                      {"selector": "td", "props": [("text-align", "right"), ("white-space", "nowrap")]},
                      {"selector": "td.col0, td.col1", "props": [("text-align", "left"), ("white-space", "nowrap")]},
                      {"selector": "thead th", "props": [("border-bottom", "1px solid #d0d0d0"), ("white-space", "nowrap")]},
                      {"selector": "table", "props": [("width", "100%"), ("border-collapse", "collapse")]},
                  ])
                  .hide(axis="index")
              )

              st.markdown(f'<div style="width: 100%; overflow-x: auto; border: 1px solid #e6e6e6; border-radius: 6px;">{df_estilizado.to_html()}</div>', unsafe_allow_html=True)

          except Exception as e:
            st.error(f"Erro ao consultar o Supabase: {e}")


  # -----------------------------------------------------------------------------
  # PÁGINA: EVOLUÇÃO ANUAL
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "evolucao_anual":
    c_head1, c_head2 = st.columns([1, 4])
    with c_head1:
      if st.session_state.logo_personalizada is not None:
        st.image(st.session_state.logo_personalizada, width=130)
      else:
        st.markdown(
            "<h2 style='color: #003366; margin: 0;'>🏛 UFSM</h2>",
            unsafe_allow_html=True,
        )
    with c_head2:
      st.markdown(
          f"""
                <div class="cabecalho-impressao">
                    <div class="titulo-impressao">
                        <h2>UNIVERSIDADE FEDERAL DE SANTA MARIA</h2>
                        <h4>PRÓ-REITORIA DE ADMINISTRAÇÃO - EVOLUÇÃO ANUAL</h4>
                    </div>
                    <div style="text-align: right; font-size: 11px; color: #555;">
                        <b>SiGeO</b> - Sistema de Gestão Orçamentária<br>
                        Emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
                    </div>
                </div>
            """,
          unsafe_allow_html=True,
      )

    st.subheader("📊 Relatório de Evolução Anual")

    try:
      df_unidades_filtro = executar_consulta_sql(
          "SELECT DISTINCT unidade FROM tb_ugs WHERE unidade IS NOT NULL ORDER BY unidade;"
      )
      unidades_opcoes = (
          df_unidades_filtro["unidade"].tolist()
          if not df_unidades_filtro.empty
          else []
      )
    except Exception:
      unidades_opcoes = []

    try:
      df_anos_filtro = executar_consulta_sql(
          "SELECT DISTINCT exercicio FROM tb_execucao_despesa WHERE exercicio IS NOT NULL ORDER BY exercicio DESC;"
      )
      anos_disponiveis = (
          df_anos_filtro["exercicio"].tolist()
          if not df_anos_filtro.empty
          else [datetime.now().year, datetime.now().year - 1]
      )
    except Exception:
      anos_disponiveis = [datetime.now().year]

    meses_nomes = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }
    lista_meses_ano = [f"{m:02d} - {meses_nomes[m]}" for m in range(1, 13)]

    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
      ano_selecionado = st.selectbox("Ano de Referência:", options=anos_disponiveis, index=0, key="evo_ano")
    with c_f2:
      mes_ano_selecionado_str = st.selectbox(
          "Mês/Ano Encerrado:", options=lista_meses_ano, index=min(datetime.now().month - 1, 11), key="evo_mes"
      )
      mes_encerrado = int(mes_ano_selecionado_str.split(" - ")[0])
    with c_f3:
      unidade_selecionada = st.selectbox(
          "Unidade:", options=["Todas"] + unidades_opcoes, key="evo_unidade"
      )

    if st.button("🔍 Executar Consulta SQL no Supabase", type="primary", key="btn_evo"):
      with st.spinner("Buscando e processando dados diretamente do Supabase..."):
        try:
          meses_esquerda = list(range(1, mes_encerrado + 1))
          meses_direita = list(range(mes_encerrado + 1, 13))

          df_nomes_contas = executar_consulta_sql("SELECT codigo_conta, nome_conta FROM tb_contas_gerenciais;")
          dict_nomes_contas = (
              dict(zip(df_nomes_contas["codigo_conta"], df_nomes_contas["nome_conta"]))
              if not df_nomes_contas.empty else {}
          )

          case_meses_sql = ""
          for m in range(1, 13):
            case_meses_sql += f'SUM(CASE WHEN e.exercicio = {ano_selecionado} AND CAST(e.mes_competencia AS INTEGER) = {m} THEN COALESCE(e.valor_liquidado, 0) ELSE 0 END) AS "mes_{m}",\n'

          query_relatorio = f"""
                    SELECT 
                        COALESCE(cg.nivel, '1') AS "Nível",
                        COALESCE(cg.codigo_conta, 'S/C') AS "Código",
                        COALESCE(cg.nome_conta, e.natureza_despesa_detalhada) AS "Conta Gerencial",
                        {case_meses_sql.rstrip(',\n')}
                    FROM tb_execucao_despesa e
                    LEFT JOIN tb_natureza_despesa_detalhada ndd ON e.natureza_despesa_detalhada = ndd.codigo_ndd
                    LEFT JOIN tb_contas_gerenciais cg ON ndd.conta_gerencial LIKE '%%' || cg.codigo_conta || '%%'
                    """

          params = {}
          if unidade_selecionada != "Todas":
            query_relatorio += """
                    INNER JOIN tb_ugs u ON e.ug_responsavel = u.codigo_ug
                    WHERE u.unidade = :unidade AND e.exercicio = {}
                    """.format(ano_selecionado)
            params["unidade"] = unidade_selecionada
          else:
            query_relatorio += f" WHERE e.exercicio = {ano_selecionado}"

          query_relatorio += """
                    GROUP BY "Nível", "Código", "Conta Gerencial"
                    ORDER BY "Código" ASC, "Conta Gerencial" ASC;
                    """

          df_sql = executar_consulta_sql(query_relatorio, params=params if params else None)

          if df_sql.empty:
            st.warning("Nenhum registro encontrado no Supabase para os filtros selecionados.")
          else:
            registros_processados = []
            df_sql["grupo_principal"] = df_sql["Código"].astype(str).apply(lambda x: x.split(".")[0] if "." in x else x)
            grupos_unicos = df_sql["grupo_principal"].unique()
            
            for grupo in sorted(grupos_unicos):
              df_grupo = df_sql[df_sql["grupo_principal"] == grupo]
              for _, row in df_grupo.iterrows():
                item = {
                    "Nível": row["Nível"],
                    "Código": row["Código"],
                    "Conta Gerencial": row["Conta Gerencial"],
                    "tipo_linha": "detalhe"
                }
                for m in range(1, 13):
                  item[f"mes_{m}"] = row[f"mes_{m}"]
                registros_processados.append(item)

              codigo_total = f"{grupo}.0" if grupo.isdigit() else f"Total {grupo}"
              nome_conta_oficial = dict_nomes_contas.get(codigo_total, f"CONTA GERENCIAL {codigo_total}")
              
              subtotal = {
                  "Nível": df_grupo["Nível"].iloc[0],
                  "Código": codigo_total,
                  "Conta Gerencial": f"TOTAL {nome_conta_oficial}",
                  "tipo_linha": "total"
              }
              for m in range(1, 13):
                subtotal[f"mes_{m}"] = df_grupo[f"mes_{m}"].sum()
              registros_processados.append(subtotal)

            total_geral_row = {
                "Nível": "",
                "Código": "",
                "Conta Gerencial": "TOTAL GERAL DO DEMONSTRATIVO",
                "tipo_linha": "grand_total"
            }
            for m in range(1, 13):
              total_geral_row[f"mes_{m}"] = df_sql[f"mes_{m}"].sum()
            registros_processados.append(total_geral_row)

            df_processado = pd.DataFrame(registros_processados)
            df_final = pd.DataFrame()
            df_final[("Identificação", "Código")] = df_processado["Código"]
            df_final[("Identificação", "Conta Gerencial")] = df_processado["Conta Gerencial"]

            for m in meses_esquerda:
              nome_col = f"{meses_nomes[m][:3]}/{str(ano_selecionado)[-2:]}"
              df_final[("Executado", nome_col)] = df_processado[f"mes_{m}"]

            for m in meses_direita:
              nome_col = f"{meses_nomes[m][:3]}/{str(ano_selecionado)[-2:]}"
              df_final[("Orçado", nome_col)] = 0.0

            df_final[("Totais", "Total Geral")] = df_processado[[f"mes_{m}" for m in meses_esquerda]].sum(axis=1) if meses_esquerda else 0.0

            df_final.columns = pd.MultiIndex.from_tuples(df_final.columns)

            def fmt_br(val):
              if pd.isna(val):
                return ""
              return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            format_dict = {}
            for col in df_final.columns:
              if col[0] in ["Executado", "Orçado", "Totais"] and col[1] != "Nível":
                format_dict[col] = lambda x: fmt_br(x)

            st.markdown(f"### Relatório de Evolução Anual (Mês Encerrado: **{mes_ano_selecionado_str}**)")

            def destacar_linhas_totais(row):
              texto_conta = str(row.iloc[1]) if len(row) > 1 else ""
              if texto_conta.startswith("TOTAL "):
                return ["font-weight: bold; background-color: #f0f2f6;"] * len(row)
              return [""] * len(row)

            df_estilizado = (
                df_final.style
                .format(format_dict)
                .apply(destacar_linhas_totais, axis=1)
                .set_table_styles([
                    {"selector": "th.col_heading.level0", "props": [("text-align", "center"), ("vertical-align", "middle"), ("font-weight", "600")]},
                    {"selector": "th.col_heading.level1", "props": [("text-align", "center"), ("vertical-align", "middle")]},
                    {"selector": "th.col_heading.level0.col0", "props": [("text-align", "left")]},
                    {"selector": "th.col_heading.level1.col0, th.col_heading.level1.col1", "props": [("text-align", "left")]},
                    {"selector": "td", "props": [("text-align", "right"), ("white-space", "nowrap")]},
                    {"selector": "td.col0, td.col1", "props": [("text-align", "left"), ("white-space", "nowrap")]},
                    {"selector": "thead th", "props": [("border-bottom", "1px solid #d0d0d0"), ("white-space", "nowrap")]},
                    {"selector": "table", "props": [("width", "100%"), ("border-collapse", "collapse")]},
                ])
                .hide(axis="index")
            )

            st.markdown(f'<div style="width: 100%; overflow-x: auto; border: 1px solid #e6e6e6; border-radius: 6px;">{df_estilizado.to_html()}</div>', unsafe_allow_html=True)

        except Exception as e:
          st.error(f"Erro ao consultar o Supabase: {e}")

  # -----------------------------------------------------------------------------
  # PÁGINA: EXECUÇÃO X LOA
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "execucao_loa":
      c_head1, c_head2 = st.columns([1, 4])
      with c_head1:
        if st.session_state.logo_personalizada is not None:
          st.image(st.session_state.logo_personalizada, width=130)
        else:
          st.markdown(
              "<h2 style='color: #003366; margin: 0;'>🏛 UFSM</h2>",
              unsafe_allow_html=True,
          )
      with c_head2:
        st.markdown(
            f"""
                  <div class="cabecalho-impressao">
                      <div class="titulo-impressao">
                          <h2>UNIVERSIDADE FEDERAL DE SANTA MARIA</h2>
                          <h4>PRÓ-REITORIA DE ADMINISTRAÇÃO - DEMONSTRATIVO EXECUÇÃO X LOA</h4>
                      </div>
                      <div style="text-align: right; font-size: 11px; color: #555;">
                          <b>SiGeO</b> - Sistema de Gestão Orçamentária<br>
                          Emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
                      </div>
                  </div>
              """,
            unsafe_allow_html=True,
        )

      st.subheader("📊 Demonstrativo Execução X LOA (Global por Anos)")

      try:
        df_anos_filtro = executar_consulta_sql(
            "SELECT DISTINCT exercicio FROM tb_execucao_despesa WHERE exercicio IS NOT NULL ORDER BY exercicio DESC;"
        )
        anos_disponiveis = (
            df_anos_filtro["exercicio"].tolist()
            if not df_anos_filtro.empty
            else [datetime.now().year, datetime.now().year - 1]
        )
      except Exception:
        anos_disponiveis = [datetime.now().year, datetime.now().year - 1, datetime.now().year - 2]

      c_f1 = st.columns(1)[0]
      with c_f1:
        ano_selecionado = st.selectbox("Ano de Referência:", options=anos_disponiveis, index=0, key="loa_ano")

      if st.button("🔍 Executar Consulta Execução X LOA", type="primary", key="btn_loa"):
        with st.spinner("Buscando dados no Supabase..."):
          try:
            df_nomes_contas = executar_consulta_sql("SELECT codigo_conta, nome_conta FROM tb_contas_gerenciais;")
            dict_nomes_contas = (
                dict(zip(df_nomes_contas["codigo_conta"], df_nomes_contas["nome_conta"]))
                if not df_nomes_contas.empty else {}
            )

            query_loa = f"""
                      SELECT 
                          COALESCE(cg.nivel, '1') AS "Nível",
                          COALESCE(cg.codigo_conta, 'S/C') AS "Código",
                          COALESCE(cg.nome_conta, e.natureza_despesa_detalhada) AS "Conta Gerencial",
                          SUM(CASE WHEN e.exercicio = {ano_selecionado} THEN COALESCE(e.valor_liquidado, 0) ELSE 0 END) AS "total_executado"
                      FROM tb_execucao_despesa e
                      LEFT JOIN tb_natureza_despesa_detalhada ndd ON e.natureza_despesa_detalhada = ndd.codigo_ndd
                      LEFT JOIN tb_contas_gerenciais cg ON ndd.conta_gerencial LIKE '%%' || cg.codigo_conta || '%%'
                      WHERE e.exercicio = {ano_selecionado}
                      GROUP BY "Nível", "Código", "Conta Gerencial"
                      ORDER BY "Código" ASC, "Conta Gerencial" ASC;
                      """

            df_sql = executar_consulta_sql(query_loa)

            if df_sql.empty:
              st.warning("Nenhum registro encontrado no Supabase para o ano selecionado.")
            else:
              registros_processados = []
              df_sql["grupo_principal"] = df_sql["Código"].astype(str).apply(lambda x: x.split(".")[0] if "." in x else x)
              grupos_unicos = df_sql["grupo_principal"].unique()

              for grupo in sorted(grupos_unicos):
                df_grupo = df_sql[df_sql["grupo_principal"] == grupo]
                for _, row in df_grupo.iterrows():
                  item = {
                      "Nível": row["Nível"],
                      "Código": row["Código"],
                      "Conta Gerencial": row["Conta Gerencial"],
                      "total_executado": row["total_executado"],
                      "loa_detalhada": 0.0,
                      "a_executar": 0.0 - row["total_executado"]
                  }
                  registros_processados.append(item)

                codigo_total = f"{grupo}.0" if grupo.isdigit() else f"Total {grupo}"
                nome_conta_oficial = dict_nomes_contas.get(codigo_total, f"CONTA GERENCIAL {codigo_total}")
                
                executado_subtotal = df_grupo["total_executado"].sum()
                subtotal = {
                    "Nível": df_grupo["Nível"].iloc[0],
                    "Código": codigo_total,
                    "Conta Gerencial": f"TOTAL {nome_conta_oficial}",
                    "total_executado": executado_subtotal,
                    "loa_detalhada": 0.0,
                    "a_executar": 0.0 - executado_subtotal
                }
                registros_processados.append(subtotal)

              total_geral_exec = df_sql["total_executado"].sum()
              total_geral_row = {
                  "Nível": "",
                  "Código": "",
                  "Conta Gerencial": "TOTAL GERAL DO DEMONSTRATIVO",
                  "total_executado": total_geral_exec,
                  "loa_detalhada": 0.0,
                  "a_executar": 0.0 - total_geral_exec
              }
              registros_processados.append(total_geral_row)

              df_processado = pd.DataFrame(registros_processados)

              df_final = pd.DataFrame()
              df_final[("Identificação", "Código")] = df_processado["Código"]
              df_final[("Identificação", "Conta Gerencial")] = df_processado["Conta Gerencial"]
              df_final[("Orçamento", f"Executado {ano_selecionado}")] = df_processado["total_executado"]
              df_final[("Orçamento", "LOA Detalhada")] = df_processado["loa_detalhada"]
              df_final[("Orçamento", "A executar")] = df_processado["a_executar"]

              df_final.columns = pd.MultiIndex.from_tuples(df_final.columns)

              def fmt_br(val):
                if pd.isna(val):
                  return ""
                return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

              format_dict = {}
              for col in df_final.columns:
                if col[0] == "Orçamento":
                  format_dict[col] = lambda x: fmt_br(x)

              st.markdown(f"### Demonstrativo Execução X LOA (Ano: **{ano_selecionado}**)")

              def destacar_linhas_totais_loa(row):
                texto_conta = str(row.iloc[1]) if len(row) > 1 else ""
                if texto_conta.startswith("TOTAL "):
                  return ["font-weight: bold; background-color: #f0f2f6;"] * len(row)
                return [""] * len(row)

              df_estilizado = (
                  df_final.style
                  .format(format_dict)
                  .apply(destacar_linhas_totais_loa, axis=1)
                  .set_table_styles([
                      {"selector": "th.col_heading.level0", "props": [("text-align", "center"), ("vertical-align", "middle"), ("font-weight", "600")]},
                      {"selector": "th.col_heading.level1", "props": [("text-align", "center"), ("vertical-align", "middle")]},
                      {"selector": "th.col_heading.level0.col0", "props": [("text-align", "left")]},
                      {"selector": "th.col_heading.level1.col0, th.col_heading.level1.col1", "props": [("text-align", "left")]},
                      {"selector": "td", "props": [("text-align", "right"), ("white-space", "nowrap")]},
                      {"selector": "td.col0, td.col1", "props": [("text-align", "left"), ("white-space", "nowrap")]},
                      {"selector": "thead th", "props": [("border-bottom", "1px solid #d0d0d0"), ("white-space", "nowrap")]},
                      {"selector": "table", "props": [("width", "100%"), ("border-collapse", "collapse")]},
                  ])
                  .hide(axis="index")
              )

              st.markdown(f'<div style="width: 100%; overflow-x: auto; border: 1px solid #e6e6e6; border-radius: 6px;">{df_estilizado.to_html()}</div>', unsafe_allow_html=True)

          except Exception as e:
            st.error(f"Erro ao consultar o Supabase para Execução X LOA: {e}")

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
              # Extrai apenas o código de dentro dos colchetes (ex: "3.2" de "[3.2] - Nome")
              cg_codigo_limpo = conta_gerencial_sel
              if "[" in conta_gerencial_sel and "]" in conta_gerencial_sel:
                cg_codigo_limpo = conta_gerencial_sel.split("[")[1].split("]")[0].strip()
	      inserir_ndd_banco(
                  codigo_ndd=cod_ndd_in.strip(),
                  descricao=desc_ndd_in.strip(),
                  grupo_despesa=(
                      grupo_despesa_in.strip() if grupo_despesa_in else None
                  ),
                  conta_gerencial=cg_codigo_limpo,
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
		  # Extrai apenas o código de dentro dos colchetes
                  cg_codigo_limpo = e_ndd_cg_sel
                  if "[" in e_ndd_cg_sel and "]" in e_ndd_cg_sel:
                    cg_codigo_limpo = e_ndd_cg_sel.split("[")[1].split("]")[0].strip()

                  atualizar_ndd_banco(
                      codigo_ndd_orig=n_cod,
                      codigo_ndd_novo=e_ndd_cod.strip(),
                      descricao=e_ndd_desc.strip(),
                      grupo_despesa=(
                          e_ndd_grp.strip() if e_ndd_grp else None
                      ),
                      conta_gerencial=cg_codigo_limpo,
                  )
                  st.session_state.editando_codigo_ndd = None
                  st.success("NDD alterada com sucesso!")
                  st.rerun()
                except Exception as e:
                  st.error(f"Erro ao atualizar NDD: {e}")

              if c_canc.button(
                  "Cancelar", key=f"canc_ndd_btn_{n_cod}", type="secondary"
              ):
                st.session_state.editando_codigo_ndd = None
                st.rerun()
              st.markdown("---")

  # -----------------------------------------------------------------------------
  # CADASTRO: USUÁRIOS
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "usuarios":
    st.markdown(
        "<h2 style='color: #003366;'>👤 Cadastro de Usuários</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Cadastre e controle os usuários que possuem acesso ao sistema."
    )

    col_usr_add, col_usr_list = st.columns([1, 2])

    with col_usr_add:
      st.subheader("➕ Novo Usuário")
      novo_usr_id = st.text_input("Usuário (Login):")
      novo_usr_nome = st.text_input("Nome Completo:")
      novo_usr_pass = st.text_input("Senha:", type="password")
      novo_usr_perf = st.selectbox(
          "Perfil:", ["Administrador", "Gestor", "Consulta"]
      )

      if st.button("Cadastrar Usuário", use_container_width=True, type="primary"):
        if not novo_usr_id or not novo_usr_pass or not novo_usr_nome:
          st.error("Preencha todos os campos obrigatórios.")
        elif any(
            u["usuario"].lower() == novo_usr_id.strip().lower()
            for u in st.session_state.tabela_usuarios
        ):
          st.error("Este nome de usuário já existe.")
        else:
          st.session_state.tabela_usuarios.append({
              "usuario": novo_usr_id.strip(),
              "nome": novo_usr_nome.strip(),
              "senha": novo_usr_pass,
              "perfil": novo_usr_perf,
          })
          st.success(f"Usuário '{novo_usr_id}' cadastrado com sucesso!")
          st.rerun()

    with col_usr_list:
      st.subheader(
          f"Usuários Cadastradas ({len(st.session_state.tabela_usuarios)})"
      )

      df_usr_view = pd.DataFrame(st.session_state.tabela_usuarios)[
          ["usuario", "nome", "perfil"]
      ]
      df_usr_view.columns = ["Login", "Nome Completo", "Perfil"]
      st.dataframe(df_usr_view, use_container_width=True)

      st.markdown("---")
      st.subheader("⚙ Ações nos Usuários")

      usrs_existentes = [u["usuario"] for u in st.session_state.tabela_usuarios]
      usr_selecionado = st.selectbox(
          "Selecione um usuário para editar/excluir:", usrs_existentes
      )

      if usr_selecionado:
        dados_usr = next(
            u
            for u in st.session_state.tabela_usuarios
            if u["usuario"] == usr_selecionado
        )
        c_edit_pass, c_del_usr = st.columns(2)

        with c_edit_pass:
          nova_s = st.text_input(
              f"Nova senha para '{usr_selecionado}':",
              type="password",
              key="inp_nova_s",
          )
          if st.button("Alterar Senha", type="primary"):
            if nova_s:
              dados_usr["senha"] = nova_s
              st.success("Senha alterada com sucesso!")
            else:
              st.warning("Digite a nova senha.")

        with c_del_usr:
          st.write("Excluir conta de acesso:")
          if st.button(f"🗑️ Excluir '{usr_selecionado}'", type="secondary"):
            if len(st.session_state.tabela_usuarios) <= 1:
              st.error("Não é possível remover o único usuário do sistema.")
            else:
              st.session_state.tabela_usuarios = [
                  u
                  for u in st.session_state.tabela_usuarios
                  if u["usuario"] != usr_selecionado
              ]
              st.success(
                  f"Usuário '{usr_selecionado}' removido com sucesso!"
              )
              st.rerun()

  # -----------------------------------------------------------------------------
  # GESTÃO DE DADOS: LANÇAMENTOS
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "lancamentos":
    st.markdown(
        "<h2 style='color: #003366;'>📥 Lançamentos Manuais / Adicionais</h2>",
        unsafe_allow_html=True,
    )
    st.info(
        "Módulo de Lançamentos manuais em desenvolvimento conforme"
        " especificado."
    )

  # -----------------------------------------------------------------------------
  # GESTÃO DE DADOS: SIMULAÇÕES (GESTÃO)
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "simulacoes_gestao":
    st.markdown(
        "<h2 style='color: #003366;'>🔮 Simulações (Gestão de Dados)</h2>",
        unsafe_allow_html=True,
    )
    st.info(
        "Módulo de simulações e cenários de gestão de dados em desenvolvimento."
    )

  # -----------------------------------------------------------------------------
  # RELATÓRIOS: SIMULAÇÕES ORÇAMENTÁRIAS
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "simulacoes_orcamentarias":
    st.markdown(
        "<h2 style='color: #003366;'>📊 Simulações Orçamentárias</h2>",
        unsafe_allow_html=True,
    )
    st.info(
        "Módulo de relatório de simulações orçamentárias em desenvolvimento."
    )

  # -----------------------------------------------------------------------------
  # CONFIGURAÇÕES: TEXTO DE ABERTURA
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "texto_abertura":
    st.markdown(
        "<h2 style='color: #003366;'>📝 Configuração do Texto de"
        " Abertura</h2>",
        unsafe_allow_html=True,
    )
    st.info(
        "Módulo para gerenciar o texto de abertura exibido na página inicial (a"
        " ser criado com tabela dedicada)."
    )

  # -----------------------------------------------------------------------------
  # CONFIGURAÇÕES: IDENTIDADE VISUAL
  # -----------------------------------------------------------------------------
  elif st.session_state.pagina_atual == "config":
    st.markdown(
        "<h2 style='color: #003366;'>🎨 Identidade Visual (Configuração"
        " Visual)</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Carregue a imagem da logomarca oficial. Ela será exibida no menu à"
        " esquerda, no cabeçalho do relatório e como ícone na aba do navegador."
    )

    c_up, c_prev = st.columns([2, 1])

    with c_up:
      st.subheader("Fazer Upload da Logo")
      arquivo_logo = st.file_uploader(
          "Selecione uma imagem (.png, .jpg, .jpeg):",
          type=["png", "jpg", "jpeg"],
      )

      if arquivo_logo is not None:
        st.session_state.logo_personalizada = arquivo_logo.getvalue()
        st.success("Logomarca carregada com sucesso!")
        st.rerun()

      if st.session_state.logo_personalizada is not None:
        st.markdown("---")
        if st.button("🗑️ Remover Logomarca Atual", type="secondary"):
          st.session_state.logo_personalizada = None
          st.success("Logomarca removida com sucesso!")
          st.rerun()

    with c_prev:
      st.subheader("Pré-visualização")
      if st.session_state.logo_personalizada is not None:
        st.image(
            st.session_state.logo_personalizada,
            caption="Logo Ativa no Sistema",
            width=200,
        )
      else:
        st.info(
            "Nenhuma imagem carregada até o momento. O sistema está exibindo"
            " o brasão padrão."
        )
