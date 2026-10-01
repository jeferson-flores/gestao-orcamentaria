import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine, text
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

def executar_consulta_sql(query: str, params: dict = None) -> pd.DataFrame:
    engine = get_db_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), con=conn, params=params)

def executar_comando_sql(query: str, params: dict = None):
    engine = get_db_engine()
    with engine.begin() as conn:
        conn.execute(text(query), params or {})

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
# 1. INICIALIZAÇÃO DA SESSÃO
# -----------------------------------------------------------------------------
if "logo_personalizada" not in st.session_state:
    st.session_state.logo_personalizada = None

icone_aba = "🏛️"

st.set_page_config(
    page_title="SiGeO - Sistema de Gestão Orçamentária",
    page_icon=icone_aba,
    layout="wide"
)

st.markdown("""
    <style>
    div[data-testid="stSidebar"] button {
        width: 100%;
        border-radius: 6px;
        height: 2.8em;
        font-weight: bold;
        margin-bottom: 4px;
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
# 2. ESTRUTURAS PADRÃO
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
    "PRO-REITORIA DE ADMINISTRACAO DA UFSM": "PRA - Pró-Reitoria de Administração",
    "PRO-REITORIA de planejamento DA UFSM": "PROPLAN - Pró-Reitoria de Planejamento",
    "CENTRO DE TECNOLOGIA DA UFSM": "CT - Centro de Tecnologia",
    "CENTRO DE CIENCIAS NATURAIS E EXATAS DA UFSM": "CCNE - Centro de Ciências Naturais e Exatas",
    "CENTRO DE CIENCIAS SOCIAIS E HUMANAS DA UFSM": "CCSH - Centro de Ciências Sociais e Humanas"
}

USUARIOS_PADRAO = [
    {"usuario": "admin", "nome": "Administrador Geral", "senha": "ufsm2026", "perfil": "Administrador"},
    {"usuario": "pra_gestor", "nome": "Gestor PRA", "senha": "pra123", "perfil": "Gestor"},
]

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
    # 4. MENU LATERAL
    # -----------------------------------------------------------------------------
    if st.session_state.logo_personalizada is not None:
        st.sidebar.image(st.session_state.logo_personalizada, use_container_width=True)
    
    st.sidebar.title("SiGeO - Gestão Orçamentária")
    st.sidebar.caption(f"Usuário: **{st.session_state.usuario_logado['nome']}**")
    
    if st.sidebar.button("🚪 Sair / Logout"):
        st.session_state.autenticado = False
        st.session_state.usuario_logado = None
        st.rerun()

    st.sidebar.markdown("---")

    if st.sidebar.button("📁 1. Carga da Planilha", use_container_width=True, type="primary" if st.session_state.pagina_atual == "carga" else "secondary"):
        st.session_state.pagina_atual = "carga"
        st.rerun()

    if st.sidebar.button("📈 Relatório Execução Orçamentária", use_container_width=True, type="primary" if st.session_state.pagina_atual == "relatorio" else "secondary"):
        st.session_state.pagina_atual = "relatorio"
        st.rerun()

    with st.sidebar.expander("⚙️ Configurações e Cadastros", expanded=False):
        if st.button("📌 Cadastro de UGs", use_container_width=True, type="primary" if st.session_state.pagina_atual == "unidades_consolidadas" else "secondary"):
            st.session_state.pagina_atual = "unidades_consolidadas"
            st.rerun()

        if st.button("🔗 Mapeamento de UGs", use_container_width=True, type="primary" if st.session_state.pagina_atual == "mapeamento_ugs" else "secondary"):
            st.session_state.pagina_atual = "mapeamento_ugs"
            st.rerun()

        if st.button("🏷️ Contas Gerenciais", use_container_width=True, type="primary" if st.session_state.pagina_atual == "contas" else "secondary"):
            st.session_state.pagina_atual = "contas"
            st.rerun()

        if st.button("📑 Naturezas de Despesa", use_container_width=True, type="primary" if st.session_state.pagina_atual == "ndd" else "secondary"):
            st.session_state.pagina_atual = "ndd"
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
                st.subheader("🚀 Exportação e Carga Massiva para o Supabase")
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
            st.subheader("📊 Demonstrativo Financeiro Comparativo (Consulta SQL Direta do Supabase)")
            
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
                            SUM(CASE WHEN e.exercicio = :ano_ant THEN e.valor_liquidado ELSE 0 END) AS "Ano Anterior",
                            SUM(CASE WHEN e.exercicio = :ano_atual THEN e.valor_liquidado ELSE 0 END) AS "Ano Atual"
                        FROM tb_execucao_despesa e
                        LEFT JOIN tb_natureza_despesa_detalhada ndd ON e.natureza_despesa_detalhada = ndd.codigo_ndd
                        LEFT JOIN tb_contas_gerenciais cg ON ndd.conta_gerencial LIKE '%' || cg.codigo_conta || '%'
                        WHERE e.exercicio IN (:ano_ant, :ano_atual)
                        GROUP BY cg.nivel, cg.codigo_conta, cg.nome_conta, e.natureza_despesa_detalhada
                        ORDER BY "Código" ASC;
                        """
                        
                        df_relatorio_sql = executar_consulta_sql(query_relatorio, {"ano_ant": int(ano_ant_sel), "ano_atual": int(ano_atual_sel)})

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
                col_pi_nome = encontrar_coluna(["nome pi", "descrição pi", "plano interno"], 12 if len(colunas)>12 else 0)
                col_valor = encontrar_coluna(["valor", "executado", "pago", "liquidado", "saldo"], -1)

                mascara_lei = df[col_resultado_lei].astype(str).str.contains("2", na=False)
                df_disc = df[mascara_lei].copy() if mascara_lei.sum() > 0 else df.copy()

                df_disc["Valor_Tratado"] = df_disc[col_valor].apply(converter_valor)
                df_disc["Unidade_Consolidada"] = df_disc[col_ug_nome].astype(str).str.strip().map(
                    lambda x: st.session_state.mapa_ugs.get(x, "CCSH - Centro de Ciências Sociais e Humanas" if "SOCIAL" in x or "HUMANA" in x else "Encargos Gerais da UFSM / Outros")
                )
                df_disc["PI_Completo"] = df_disc[col_pi_cod].astype(str).str.strip() + " - " + df_disc[col_pi_nome].astype(str).str.strip()
                df_disc["Conta_Gerencial"] = df_disc["PI_Completo"].map(lambda x: st.session_state.dicionario_pis.get(x, "Outras Despesas Operacionais"))

                df_disc["Data_Ref"] = pd.to_datetime(df_disc[col_mes_ref], errors='coerce', dayfirst=True)
                if df_disc["Data_Ref"].isna().all():
                    df_disc["Data_Ref"] = pd.to_datetime(df_disc[col_mes_ref].astype(str), format='%m/%Y', errors='coerce')

                df_disc["Ano_Mes"] = df_disc["Data_Ref"].dt.to_period("M")

                meses_siglas = {1: "JAN", 2: "FEV", 3: "MAR", 4: "ABR", 5: "MAI", 6: "JUN", 7: "JUL", 8: "AGO", 9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ"}
                
                def fmt_mmm_aaaa(periodo):
                    if pd.isna(periodo): return ""
                    return f"{meses_siglas[periodo.month]}/{periodo.year}"

                c_flag, c_unid, c_mes, c_imp = st.columns([1.5, 2, 2, 1])
                with c_flag:
                    tipo_visao = st.radio("📌 Visão:", ["Mensal", "Anual"], horizontal=True)
                with c_unid:
                    lista_unidades_select = ["--- TOTAL DA UFSM ---"] + sorted(st.session_state.unidades_consolidadas)
                    unidade_selecionada = st.selectbox("🏛️ Unidade:", lista_unidades_select)

                df_filtrado_unidade = df_disc.copy()
                if unidade_selecionada != "--- TOTAL DA UFSM ---":
                    df_filtrado_unidade = df_filtrado_unidade[df_filtrado_unidade["Unidade_Consolidada"] == unidade_selecionada]

                periodos_disponiveis = sorted([p for p in df_filtrado_unidade["Ano_Mes"].dropna().unique()], reverse=True)
                
                with c_mes:
                    periodo_sel = st.selectbox("📅 Mês de Referência:", periodos_disponiveis, format_func=fmt_mmm_aaaa) if periodos_disponiveis else None

                with c_imp:
                    st.write(" ")
                    if st.button("🖨️ Imprimir", type="primary", use_container_width=True):
                        st.components.v1.html("<script>window.parent.print();</script>", height=0, width=0)

                st.markdown("---")

                if periodo_sel is not None:
                    df_contas_cg = buscar_contas_gerenciais_banco()
                    niveis_lista = sorted(df_contas_cg["nivel"].dropna().unique().tolist()) if not df_contas_cg.empty else ["1", "2"]

                    if tipo_visao == "Mensal":
                        p0, p1, p2, p3 = periodo_sel, periodo_sel - 1, periodo_sel - 2, periodo_sel - 12
                        lbl_0, lbl_1 = f"{fmt_mmm_aaaa(p0)} (R$)", f"{fmt_mmm_aaaa(p1)} (R$)"
                        var_1_str = f"Var. % ({fmt_mmm_aaaa(p0)} vs {fmt_mmm_aaaa(p1)})"
                        lbl_2, var_2_str = f"{fmt_mmm_aaaa(p2)} (R$)", f"Var. % ({fmt_mmm_aaaa(p1)} vs {fmt_mmm_aaaa(p2)})"
                        lbl_3, var_3_str = f"{fmt_mmm_aaaa(p3)} (R$)", f"Var. % ({fmt_mmm_aaaa(p0)} vs {fmt_mmm_aaaa(p3)})"

                        s0 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == p0].groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s1 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == p1].groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s2 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == p2].groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s3 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == p3].groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()

                        cols_valores = [lbl_0, lbl_1, lbl_2, lbl_3]
                        cols_cabecalho = ["Estrutura Gerencial / Nível", lbl_0, lbl_1, var_1_str, lbl_2, var_2_str, lbl_3, var_3_str]
                        larguras_colunas = [3.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2]
                        dict_somas = {lbl_0: s0, lbl_1: s1, lbl_2: s2, lbl_3: s3}
                        mapeamento_var = {var_1_str: (lbl_0, lbl_1), var_2_str: (lbl_1, lbl_2), var_3_str: (lbl_0, lbl_3)}
                    else:
                        ano_atual, mes_ref_num = periodo_sel.year, periodo_sel.month
                        ano_1, ano_2 = ano_atual - 1, ano_atual - 2
                        sigla_mes = meses_siglas[mes_ref_num]

                        lbl_0, lbl_1 = f"JAN-{sigla_mes}/{ano_atual} (R$)", f"JAN-{sigla_mes}/{ano_1} (R$)"
                        var_1_str = f"Var. % ({ano_atual} vs {ano_1})"
                        lbl_2, var_2_str = f"JAN-{sigla_mes}/{ano_2} (R$)", f"Var. % ({ano_1} vs {ano_2})"

                        s0 = df_filtrado_unidade[(df_filtrado_unidade["Ano_Mes"].dt.year == ano_atual) & (df_filtrado_unidade["Ano_Mes"].dt.month <= mes_ref_num)].groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s1 = df_filtrado_unidade[(df_filtrado_unidade["Ano_Mes"].dt.year == ano_1) & (df_filtrado_unidade["Ano_Mes"].dt.month <= mes_ref_num)].groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                        s2 = df_filtrado_unidade[(df_filtrado_unidade["Ano_Mes"].dt.year == ano_2) & (df_filtrado_unidade["Ano_Mes"].dt.month <= mes_ref_num)].groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()

                        cols_valores = [lbl_0, lbl_1, lbl_2]
                        cols_cabecalho = ["Estrutura Gerencial / Nível", lbl_0, lbl_1, var_1_str, lbl_2, var_2_str]
                        larguras_colunas = [3.5, 1.5, 1.5, 1.5, 1.5, 1.5]
                        dict_somas = {lbl_0: s0, lbl_1: s1, lbl_2: s2}
                        mapeamento_var = {var_1_str: (lbl_0, lbl_1), var_2_str: (lbl_1, lbl_2)}

                    c_lbl_tit, c_btn_exp_all = st.columns([4, 1])
                    with c_lbl_tit:
                        st.subheader(f"📋 Execução Orçamentária Comparativa ({tipo_visao})")
                    with c_btn_exp_all:
                        if st.button("🔄 Expandir/Recolher", use_container_width=True):
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
                        color = "#dc2626" if v > 0 else ("#2563eb" if v < 0 else "#64748b")
                        return f"<span style='color: {color}; font-weight: bold;'>{v:+.2f}%</span>".replace(".", ",")

                    somas_totais_gerais = {col: 0.0 for col in cols_valores}

                    for i_niv, nivel_val in enumerate(niveis_lista):
                        contas_do_nivel = df_contas_cg[df_contas_cg["nivel"] == nivel_val]["nome_conta"].dropna().tolist() if not df_contas_cg.empty else []
                        is_expanded = nivel_val in st.session_state.tot_expandidos_set

                        val_tot_dict = {col: sum([dict_somas[col].get(c, 0.0) for c in contas_do_nivel]) for col in cols_valores}
                        for col in cols_valores:
                            somas_totais_gerais[col] += val_tot_dict[col]

                        vars_tot_dict = {
                            col_var: ((val_tot_dict[v_atual] - val_tot_dict[v_ant]) / val_tot_dict[v_ant] * 100.0) if val_tot_dict[v_ant] > 0 else 0.0
                            for col_var, (v_atual, v_ant) in mapeamento_var.items()
                        }

                        cols_row = st.columns(larguras_colunas)
                        c_btn, c_txt = cols_row[0].columns([0.35, 9.65])
                        btn_symbol = "➖" if is_expanded else "➕"
                        if c_btn.button(btn_symbol, key=f"btn_toggle_niv_{i_niv}"):
                            if is_expanded: st.session_state.tot_expandidos_set.remove(nivel_val)
                            else: st.session_state.tot_expandidos_set.add(nivel_val)
                            st.rerun()

                        c_txt.markdown(f"<div style='font-weight: bold; margin-top: 4px;'>Nível {nivel_val}</div>", unsafe_allow_html=True)

                        idx_col = 1
                        for col in cols_cabecalho[1:]:
                            v_str = fmt_moeda(val_tot_dict[col]) if col in cols_valores else fmt_percent_html(vars_tot_dict[col])
                            cols_row[idx_col].markdown(f"<div style='text-align: right; font-weight: bold; margin-top: 4px;'>{v_str}</div>", unsafe_allow_html=True)
                            idx_col += 1

                        if is_expanded:
                            for conta in contas_do_nivel:
                                cols_sub = st.columns(larguras_colunas)
                                cols_sub[0].markdown(f"<div style='padding-left: 28px; color: #334155;'>↳ {conta}</div>", unsafe_allow_html=True)

                                val_sub_dict = {col: dict_somas[col].get(conta, 0.0) for col in cols_valores}
                                vars_sub_dict = {
                                    col_var: ((val_sub_dict[v_atual] - val_sub_dict[v_ant]) / val_sub_dict[v_ant] * 100.0) if val_sub_dict[v_ant] > 0 else 0.0
                                    for col_var, (v_atual, v_ant) in mapeamento_var.items()
                                }

                                idx_col_sub = 1
                                for col in cols_cabecalho[1:]:
                                    v_sub_str = fmt_moeda(val_sub_dict[col]) if col in cols_valores else fmt_percent_html(vars_sub_dict[col])
                                    cols_sub[idx_col_sub].markdown(f"<div style='text-align: right; color: #475569;'>{v_sub_str}</div>", unsafe_allow_html=True)
                                    idx_col_sub += 1

                        st.markdown("<div style='border-bottom: 1px solid #e2e8f0; margin: 2px 0;'></div>", unsafe_allow_html=True)

                    cols_tot_g = st.columns(larguras_colunas)
                    cols_tot_g[0].markdown("<div style='font-weight: bold; color: #003366; font-size: 15px;'>TOTAL GERAL</div>", unsafe_allow_html=True)

                    vars_gerais_dict = {
                        col_var: ((somas_totais_gerais[v_atual] - somas_totais_gerais[v_ant]) / somas_totais_gerais[v_ant] * 100.0) if somas_totais_gerais[v_ant] > 0 else 0.0
                        for col_var, (v_atual, v_ant) in mapeamento_var.items()
                    }

                    idx_col_g = 1
                    for col in cols_cabecalho[1:]:
                        v_g_str = fmt_moeda(somas_totais_gerais[col]) if col in cols_valores else fmt_percent_html(vars_gerais_dict[col])
                        cols_tot_g[idx_col_g].markdown(f"<div style='text-align: right; font-weight: bold; color: #003366; font-size: 15px;'>{v_g_str}</div>", unsafe_allow_html=True)
                        idx_col_g += 1

    # -----------------------------------------------------------------------------
    # CADASTRO DE UNIDADES GESTORAS (PUBLIC.TB_UGS)
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "unidades_consolidadas":
        st.header("📌 Cadastro de Unidades Gestoras (UGs)")
        df_ugs = buscar_ugs_banco()

        col_u1, col_u2 = st.columns([1, 2])
        with col_u1:
            st.subheader("➕ Adicionar Nova UG")
            with st.form("form_add_ug", clear_on_submit=True):
                codigo_input = st.text_input("Código da UG *:")
                nome_input = st.text_input("Nome da UG:")
                sigla_input = st.text_input("Sigla:")
                ativo_input = st.checkbox("UG Ativa", value=True)
                
                if st.form_submit_button("Salvar UG", type="primary", use_container_width=True):
                    if not codigo_input.strip():
                        st.error("Obrigatório preencher o código.")
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
                    ug_cod, ug_nome, ug_sigla, ug_ativo = row["codigo_ug"], row["nome"] or "", row["sigla"] or "", bool(row["ativo"])
                    c_txt, c_btn_edit, c_btn_del = st.columns([5, 1, 1])
                    c_txt.markdown(f"{'🟢' if ug_ativo else '🔴'} **[{ug_cod}]** {ug_sigla} - {ug_nome}")
                    
                    if c_btn_edit.button("✏️", key=f"edit_ug_{ug_cod}"):
                        st.session_state.editando_codigo_ug = ug_cod
                        st.rerun()
                    if c_btn_del.button("🗑️", key=f"del_ug_{ug_cod}"):
                        try:
                            excluir_ug_banco(ug_cod)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")

                    if st.session_state.editando_codigo_ug == ug_cod:
                        with st.form(f"form_edit_ug_{ug_cod}"):
                            e_cod = st.text_input("Código", value=str(ug_cod))
                            e_nome = st.text_input("Nome", value=ug_nome)
                            e_sigla = st.text_input("Sigla", value=ug_sigla)
                            e_ativo = st.checkbox("Ativo", value=ug_ativo)
                            if st.form_submit_button("Atualizar"):
                                atualizar_ug_banco(ug_cod, e_cod, e_nome, e_sigla, e_ativo)
                                st.session_state.editando_codigo_ug = None
                                st.rerun()

    # -----------------------------------------------------------------------------
    # MAPEAMENTO DE UGs
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "mapeamento_ugs":
        st.header("🔗 Mapeamento de UGs")
        ugs_para_mapear = set(st.session_state.mapa_ugs.keys())
        if st.session_state.dados_tg_raw is not None:
            col_ug_nom = st.session_state.dados_tg_raw.columns[6]
            for u in st.session_state.dados_tg_raw[col_ug_nom].dropna().unique():
                ugs_para_mapear.add(str(u).strip())

        for ug_item in sorted(list(ugs_para_mapear)):
            c_ug, c_sel = st.columns([2, 2])
            c_ug.write(f"🏢 **{ug_item}**")
            def_val = st.session_state.mapa_ugs.get(ug_item, "Encargos Gerais da UFSM / Outros")
            idx_u = st.session_state.unidades_consolidadas.index(def_val) if def_val in st.session_state.unidades_consolidadas else 0
            st.session_state.mapa_ugs[ug_item] = c_sel.selectbox("Alocar para:", st.session_state.unidades_consolidadas, index=idx_u, key=f"map_{ug_item}")

    # -----------------------------------------------------------------------------
    # CONTAS GERENCIAIS
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "contas":
        st.header("🏷️ Gestão de Contas Gerenciais")
        df_cg = buscar_contas_gerenciais_banco()
        c_add, c_list = st.columns([1, 2])

        with c_add:
            with st.form("form_cg", clear_on_submit=True):
                codigo_conta_in = st.text_input("Código da Conta *:")
                nome_conta_in = st.text_input("Nome da Conta *:")
                nivel_in = st.text_input("Nível:", value="1")
                ativo_in = st.checkbox("Ativa", value=True)
                if st.form_submit_button("Salvar Conta", type="primary"):
                    inserir_conta_gerencial_banco(codigo_conta_in, nome_conta_in, nivel_in, ativo_in)
                    st.rerun()

        with c_list:
            for _, row in df_cg.iterrows():
                c_cod, c_nome, c_niv, c_ativo = row["codigo_conta"], row["nome_conta"], row["nivel"], bool(row["ativo"])
                c_t, c_e, c_d = st.columns([5, 1, 1])
                c_t.markdown(f"{'🟢' if c_ativo else '🔴'} **[{c_cod}]** {c_nome} (Nível: {c_niv})")
                if c_e.button("✏️", key=f"ed_cg_{c_cod}"):
                    st.session_state.editando_codigo_conta = c_cod
                    st.rerun()
                if c_d.button("🗑️", key=f"dl_cg_{c_cod}"):
                    excluir_conta_gerencial_banco(c_cod)
                    st.rerun()

                if st.session_state.editando_codigo_conta == c_cod:
                    with st.form(f"form_ed_cg_{c_cod}"):
                        e_cod = st.text_input("Código", value=str(c_cod))
                        e_nome = st.text_input("Nome", value=c_nome)
                        e_niv = st.text_input("Nível", value=str(c_niv))
                        e_ativo = st.checkbox("Ativo", value=c_ativo)
                        if st.form_submit_button("Atualizar"):
                            atualizar_conta_gerencial_banco(c_cod, e_cod, e_nome, e_niv, e_ativo)
                            st.session_state.editando_codigo_conta = None
                            st.rerun()

    # -----------------------------------------------------------------------------
    # NATUREZA DE DESPESA DETALHADA (NDD)
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "ndd":
        st.header("📑 Natureza de Despesa Detalhada (NDD)")
        df_cg_opcoes = buscar_contas_gerenciais_banco()
        opcoes_cg = ["Nenhum (Sem vínculo)"] + [f"[{r['codigo_conta']}] - {r['nome_conta']}" for _, r in df_cg_opcoes.iterrows()] if not df_cg_opcoes.empty else ["Nenhum (Sem vínculo)"]
        df_ndd = buscar_ndd_banco()

        c_add_n, c_list_n = st.columns([1, 2])
        with c_add_n:
            with st.form("form_ndd", clear_on_submit=True):
                cod_ndd_in = st.text_input("Código NDD *:")
                desc_ndd_in = st.text_input("Descrição *:")
                grupo_despesa_in = st.text_input("Grupo de Despesa:")
                conta_gerencial_sel = st.selectbox("Conta Gerencial *:", opcoes_cg)
                if st.form_submit_button("Salvar NDD", type="primary"):
                    inserir_ndd_banco(cod_ndd_in, desc_ndd_in, grupo_despesa_in, conta_gerencial_sel)
                    st.rerun()

        with c_list_n:
            for _, row in df_ndd.iterrows():
                n_cod, n_desc, n_cg = row["codigo_ndd"], row["descricao"], row["conta_gerencial"]
                c_t, c_e, c_d = st.columns([5, 1, 1])
                c_t.markdown(f"🏷 **[{n_cod}]** {n_desc} | Conta: {n_cg}")
                if c_e.button("✏️", key=f"ed_ndd_{n_cod}"):
                    st.session_state.editando_codigo_ndd = n_cod
                    st.rerun()
                if c_d.button("🗑️", key=f"dl_ndd_{n_cod}"):
                    excluir_ndd_banco(n_cod)
                    st.rerun()

                if st.session_state.editando_codigo_ndd == n_cod:
                    with st.form(f"form_ed_ndd_{n_cod}"):
                        e_nc = st.text_input("Código", value=str(n_cod))
                        e_nd = st.text_input("Descrição", value=n_desc)
                        e_ng = st.text_input("Grupo", value=row["grupo_despesa"] or "")
                        e_ncg = st.selectbox("Conta Gerencial", opcoes_cg, index=opcoes_cg.index(n_cg) if n_cg in opcoes_cg else 0)
                        if st.form_submit_button("Atualizar"):
                            atualizar_ndd_banco(n_cod, e_nc, e_nd, e_ng, e_ncg)
                            st.session_state.editando_codigo_ndd = None
                            st.rerun()

    # -----------------------------------------------------------------------------
    # CADASTRO DE USUÁRIOS
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "usuarios":
        st.header("⚙️ Gestão de Usuários e Permissões")
        c_usr_add, c_usr_list = st.columns([1, 2])
        with c_usr_add:
            with st.form("form_user", clear_on_submit=True):
                novo_usr_id = st.text_input("Usuário (Login):")
                novo_usr_nome = st.text_input("Nome Completo:")
                novo_usr_pass = st.text_input("Senha:", type="password")
                novo_usr_perf = st.selectbox("Perfil:", ["Administrador", "Gestor", "Consulta"])
                if st.form_submit_button("Cadastrar Usuário", type="primary"):
                    st.session_state.tabela_usuarios.append({"usuario": novo_usr_id, "nome": novo_usr_nome, "senha": novo_usr_pass, "perfil": novo_usr_perf})
                    st.rerun()

        with c_usr_list:
            st.dataframe(pd.DataFrame(st.session_state.tabela_usuarios)[["usuario", "nome", "perfil"]], use_container_width=True)

    # -----------------------------------------------------------------------------
    # CONFIGURAÇÕES VISUAIS
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "config":
        st.header("⚙️ Configuração Visual e Logomarca")
        arquivo_logo = st.file_uploader("Selecione uma imagem (.png, .jpg):", type=["png", "jpg", "jpeg"])
        if arquivo_logo is not None:
            st.session_state.logo_personalizada = arquivo_logo.getvalue()
            st.success("Logo atualizada!")
            st.rerun()
        if st.session_state.logo_personalizada is not None:
            st.image(st.session_state.logo_personalizada, width=200)
            if st.button("Remover Logo"):
                st.session_state.logo_personalizada = None
                st.rerun()
