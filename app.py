import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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

# Customização CSS (Menu Lateral + Estilo de Impressão)
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

TOTALIZADORES_PADRAO = [
    "G-1.0 Total de Infraestrutura e Manutenção Predial",
    "G-2.0 Total de Serviços Terceirizados e Operacionais",
    "G-3.0 Total de Tecnologia da Informação e Comunicação",
    "G-4.0 Total de Assistência Estudantil e RU",
    "G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas",
    "G-6.0 Total de Viagens, Eventos e Capacitação",
    "G-7.0 Total de Equipamentos, Acervo e Logística",
    "G-8.0 Total de Despesas Operacionais e Encargos Institucionais"
]

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

MAPA_CONTAS_TOTALIZADORES_PADRAO = {
    "1.1. Obras, Reformas e Adequações": "G-1.0 Total de Infraestrutura e Manutenção Predial",
    "1.2. Concessionárias (Energia, Água, Gás)": "G-1.0 Total de Infraestrutura e Manutenção Predial",
    "1.3. Manutenção Predial e Conservação": "G-1.0 Total de Infraestrutura e Manutenção Predial",
    "1.4. Conservação de Áreas Verdes e Limpeza Urbana": "G-1.0 Total de Infraestrutura e Manutenção Predial",
    
    "2.1. Serviços de Vigilância e Portaria": "G-2.0 Total de Serviços Terceirizados e Operacionais",
    "2.2. Serviços de Limpeza e Higienização": "G-2.0 Total de Serviços Terceirizados e Operacionais",
    "2.3. Apoio Administrativo e Motoristas": "G-2.0 Total de Serviços Terceirizados e Operacionais",
    "2.4. Recepção e Serviços Gerais": "G-2.0 Total de Serviços Terceirizados e Operacionais",
    
    "3.1. Equipamentos e Infraestrutura de TI": "G-3.0 Total de Tecnologia da Informação e Comunicação",
    "3.2. Licenças de Software, Sistemas e Nuvem": "G-3.0 Total de Tecnologia da Informação e Comunicação",
    "3.3. Conectividade, Redes e Telefonia": "G-3.0 Total de Tecnologia da Informação e Comunicação",
    
    "4.1. Restaurante Universitário (RU) - Insumos e Operação": "G-4.0 Total de Assistência Estudantil e RU",
    "4.2. Bolsas de Assistência Estudantil e Permanência": "G-4.0 Total de Assistência Estudantil e RU",
    "4.3. Moradia Estudantil e Apoio ao Estudante": "G-4.0 Total de Assistência Estudantil e RU",
    
    "5.1. Bolsas de Graduação, Pós e Extensão": "G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas",
    "5.2. Material Didático, de Laboratório e Insumos de Pesquisa": "G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas",
    "5.3. Fomento a Projetos de Pesquisa, Extensão e Inovação": "G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas",
    "5.4. Unidades Especializadas (HVU, Fazenda, Colégios)": "G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas",
    
    "6.1. Passagens e Diárias (Nacionais e Internacionais)": "G-6.0 Total de Viagens, Eventos e Capacitação",
    "6.2. Eventos Acadêmicos, Culturais e Congressos": "G-6.0 Total de Viagens, Eventos e Capacitação",
    "6.3. Capacitação e Desenvolvimento de Servidores": "G-6.0 Total de Viagens, Eventos e Capacitação",
    
    "7.1. Aquisição de Equipamentos e Mobiliário": "G-7.0 Total de Equipamentos, Acervo e Logística",
    "7.2. Biblioteca (Livros, Periódicos e Bases Científicas)": "G-7.0 Total de Equipamentos, Acervo e Logística",
    "7.3. Frota e Combustíveis": "G-7.0 Total de Equipamentos, Acervo e Logística",
    
    "8.1. Material de Expediente e Suprimentos": "G-8.0 Total de Despesas Operacionais e Encargos Institucionais",
    "8.2. Encargos Institucionais e Impostos": "G-8.0 Total de Despesas Operacionais e Encargos Institucionais",
    "8.3. Outras Despesas Operacionais": "G-8.0 Total de Despesas Operacionais e Encargos Institucionais",
    "Sem Classificação": "G-8.0 Total de Despesas Operacionais e Encargos Institucionais"
}

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

if "totalizadores" not in st.session_state:
    st.session_state.totalizadores = TOTALIZADORES_PADRAO.copy()

if "contas_gerenciais" not in st.session_state:
    st.session_state.contas_gerenciais = PLANO_CONTAS_PADRAO.copy()

if "mapa_contas_totalizadores" not in st.session_state:
    st.session_state.mapa_contas_totalizadores = MAPA_CONTAS_TOTALIZADORES_PADRAO.copy()

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

# Controle de edição inline
if "editando_unidade" not in st.session_state:
    st.session_state.editando_unidade = None

if "editando_conta" not in st.session_state:
    st.session_state.editando_conta = None

if "editando_totalizador" not in st.session_state:
    st.session_state.editando_totalizador = None

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

    # MÓDULOS DE OPERAÇÃO E CONSULTA
    if st.sidebar.button("📁 1. Carga da Planilha", use_container_width=True, type="primary" if st.session_state.pagina_atual == "carga" else "secondary"):
        st.session_state.pagina_atual = "carga"
        st.rerun()

    if st.sidebar.button("📊 2. Relatório Executivo", use_container_width=True, type="primary" if st.session_state.pagina_atual == "relatorio" else "secondary"):
        st.session_state.pagina_atual = "relatorio"
        st.rerun()

    st.sidebar.markdown("---")
    
    # SEÇÃO DE CONFIGURAÇÕES
    st.sidebar.subheader("⚙️ Configurações")

    if st.sidebar.button("🏛️ Configuração de Unidades", use_container_width=True, type="primary" if st.session_state.pagina_atual == "unidades" else "secondary"):
        st.session_state.pagina_atual = "unidades"
        st.rerun()

    if st.sidebar.button("🏷️ Configuração de Contas & PIs", use_container_width=True, type="primary" if st.session_state.pagina_atual == "contas" else "secondary"):
        st.session_state.pagina_atual = "contas"
        st.rerun()

    if st.sidebar.button("👤 Cadastro de Usuários", use_container_width=True, type="primary" if st.session_state.pagina_atual == "usuarios" else "secondary"):
        st.session_state.pagina_atual = "usuarios"
        st.rerun()

    if st.sidebar.button("🎨 Configuração Visual", use_container_width=True, type="primary" if st.session_state.pagina_atual == "config" else "secondary"):
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
    # PÁGINA 2: RELATÓRIO EXECUTIVO (COM COMPARAÇÃO MENSAL E ANUAL)
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
                    <h4>PRÓ-REITORIA DE ADMINISTRAÇÃO - RELATÓRIO EXECUTIVO ORÇAMENTÁRIO</h4>
                    <p style="margin:2px 0 0 0; font-size:12px; color:#777;">Emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        if st.session_state.dados_tg_raw is None:
            st.info("👋 Por favor, faça a carga do arquivo na aba **'1. Carga da Planilha'** para acessar os relatórios.")
        else:
            df = st.session_state.dados_tg_raw.copy()
            colunas = list(df.columns)

            # Localizador de colunas por nome
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

            # Filtro opcional do Resultado Lei
            mascara_lei = df[col_resultado_lei].astype(str).str.contains("2", na=False)
            df_disc = df[mascara_lei].copy() if mascara_lei.sum() > 0 else df.copy()

            # Tratamento de dados basico
            df_disc["Valor_Tratado"] = df_disc[col_valor].apply(converter_valor)
            df_disc["Unidade_Consolidada"] = df_disc[col_ug_nome].astype(str).map(
                lambda x: st.session_state.mapa_ugs.get(x.strip(), "Encargos Gerais da UFSM / Outros")
            )
            df_disc["PI_Completo"] = df_disc[col_pi_cod].astype(str).str.strip() + " - " + df_disc[col_pi_nome].astype(str).str.strip()
            df_disc["Conta_Gerencial"] = df_disc["PI_Completo"].map(
                lambda x: st.session_state.dicionario_pis.get(x, "Sem Classificação")
            )
            df_disc["Grupo_Totalizador"] = df_disc["Conta_Gerencial"].map(
                lambda c: st.session_state.mapa_contas_totalizadores.get(c, "G-8.0 Total de Despesas Operacionais e Encargos Institucionais")
            )

            # TRATAMENTO DE DATAS (Mês/Ano)
            df_disc["Data_Ref"] = pd.to_datetime(df_disc[col_mes_ref], errors='coerce', dayfirst=True)
            # Se falhou ao converter, tenta interpretar datas em formato texto tipo "JAN/2026" ou "2026-01"
            if df_disc["Data_Ref"].isna().all():
                df_disc["Data_Ref"] = pd.to_datetime(df_disc[col_mes_ref].astype(str), format='%m/%Y', errors='coerce')

            df_disc["Ano_Mes"] = df_disc["Data_Ref"].dt.to_period("M")

            # CONTROLES DE FILTRO
            c_flag, c_unid, c_mes, c_imp = st.columns([1.5, 2, 2, 1])

            with c_flag:
                tipo_visao = st.radio("📌 Visão do Relatório:", ["Mensal", "Anual"], horizontal=True)

            with c_unid:
                lista_unidades_select = ["--- TOTAL DA UFSM ---"] + sorted(st.session_state.unidades_consolidadas)
                unidade_selecionada = st.selectbox("🏛️ Unidade:", lista_unidades_select)

            # Filtro da Unidade
            df_filtrado_unidade = df_disc.copy()
            if unidade_selecionada != "--- TOTAL DA UFSM ---":
                df_filtrado_unidade = df_filtrado_unidade[df_filtrado_unidade["Unidade_Consolidada"] == unidade_selecionada]

            # Lista de Meses Disponíveis para Seleção
            periodos_disponiveis = sorted([p for p in df_filtrado_unidade["Ano_Mes"].dropna().unique()], reverse=True)
            
            with c_mes:
                if periodos_disponiveis:
                    periodo_sel = st.selectbox("📅 Mês de Referência:", periodos_disponiveis, format_func=lambda x: str(x))
                else:
                    periodo_sel = None
                    st.warning("Nenhuma data válida encontrada na planilha.")

            with c_imp:
                st.write(" ")
                if st.button("🖨️ Imprimir / PDF", type="primary", use_container_width=True):
                    st.components.v1.html("<script>window.parent.print();</script>", height=0, width=0)

            st.markdown("---")

            if periodo_sel is not None:
                totalizadores_lista = sorted(st.session_state.totalizadores)
                contas_lista = sorted(st.session_state.contas_gerenciais)

                if tipo_visao == "Mensal":
                    # DEFINIÇÃO DOS 4 MESES COMPARATIVOS
                    m_atual = periodo_sel
                    m_1 = periodo_sel - 1
                    m_2 = periodo_sel - 2
                    m_ano_ant = periodo_sel - 12

                    lbl_m_atual = str(m_atual)
                    lbl_m_1 = str(m_1)
                    lbl_m_2 = str(m_2)
                    lbl_m_ano_ant = str(m_ano_ant)

                    # Subsets
                    df_m0 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == m_atual]
                    df_m1 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == m_1]
                    df_m2 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == m_2]
                    df_m12 = df_filtrado_unidade[df_filtrado_unidade["Ano_Mes"] == m_ano_ant]

                    soma_m0 = df_m0.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                    soma_m1 = df_m1.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                    soma_m2 = df_m2.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                    soma_m12 = df_m12.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()

                    # MONTAGEM DA TABELA MENSAL
                    linhas = []
                    tot_g_m0, tot_g_m1, tot_g_m2, tot_g_m12 = 0.0, 0.0, 0.0, 0.0

                    for tot in totalizadores_lista:
                        contas_do_tot = [c for c in contas_lista if st.session_state.mapa_contas_totalizadores.get(c) == tot]
                        
                        v_tot_m0 = sum([soma_m0.get(c, 0.0) for c in contas_do_tot])
                        v_tot_m1 = sum([soma_m1.get(c, 0.0) for c in contas_do_tot])
                        v_tot_m2 = sum([soma_m2.get(c, 0.0) for c in contas_do_tot])
                        v_tot_m12 = sum([soma_m12.get(c, 0.0) for c in contas_do_tot])

                        linhas.append({
                            "Estrutura": f"📊 {tot}",
                            lbl_m_atual: v_tot_m0,
                            lbl_m_1: v_tot_m1,
                            lbl_m_2: v_tot_m2,
                            lbl_m_ano_ant: v_tot_m12,
                            "Tipo": "Totalizador"
                        })

                        for c in contas_do_tot:
                            linhas.append({
                                "Estrutura": f"  ├─ {c}",
                                lbl_m_atual: soma_m0.get(c, 0.0),
                                lbl_m_1: soma_m1.get(c, 0.0),
                                lbl_m_2: soma_m2.get(c, 0.0),
                                lbl_m_ano_ant: soma_m12.get(c, 0.0),
                                "Tipo": "Conta"
                            })

                        tot_g_m0 += v_tot_m0
                        tot_g_m1 += v_tot_m1
                        tot_g_m2 += v_tot_m2
                        tot_g_m12 += v_tot_m12

                    df_exibicao = pd.DataFrame(linhas)

                    # KPI Cards
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric(f"Atual ({lbl_m_atual})", f"R$ {tot_g_m0:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    k2.metric(f"Mês Anterior ({lbl_m_1})", f"R$ {tot_g_m1:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    k3.metric(f"2º Mês Ant. ({lbl_m_2})", f"R$ {tot_g_m2:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    k4.metric(f"Ano Ant. ({lbl_m_ano_ant})", f"R$ {tot_g_m12:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                    col_cols_exibir = [lbl_m_atual, lbl_m_1, lbl_m_2, lbl_m_ano_ant]

                else:
                    # VISÃO ANUAL (ACUMULADO ATÉ O MÊS DE REFERÊNCIA)
                    ano_atual = periodo_sel.year
                    mes_ref_num = periodo_sel.month

                    ano_1 = ano_atual - 1
                    ano_2 = ano_atual - 2

                    lbl_a0 = f"Jan-{periodo_sel.strftime('%b')}/{ano_atual}"
                    lbl_a1 = f"Jan-{periodo_sel.strftime('%b')}/{ano_1}"
                    lbl_a2 = f"Jan-{periodo_sel.strftime('%b')}/{ano_2}"

                    # Filtro de intervalo acumulado
                    df_a0 = df_filtrado_unidade[(df_filtrado_unidade["Ano_Mes"].dt.year == ano_atual) & (df_filtrado_unidade["Ano_Mes"].dt.month <= mes_ref_num)]
                    df_a1 = df_filtrado_unidade[(df_filtrado_unidade["Ano_Mes"].dt.year == ano_1) & (df_filtrado_unidade["Ano_Mes"].dt.month <= mes_ref_num)]
                    df_a2 = df_filtrado_unidade[(df_filtrado_unidade["Ano_Mes"].dt.year == ano_2) & (df_filtrado_unidade["Ano_Mes"].dt.month <= mes_ref_num)]

                    soma_a0 = df_a0.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                    soma_a1 = df_a1.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()
                    soma_a2 = df_a2.groupby("Conta_Gerencial")["Valor_Tratado"].sum().to_dict()

                    linhas = []
                    tot_g_a0, tot_g_a1, tot_g_a2 = 0.0, 0.0, 0.0

                    for tot in totalizadores_lista:
                        contas_do_tot = [c for c in contas_lista if st.session_state.mapa_contas_totalizadores.get(c) == tot]
                        
                        v_tot_a0 = sum([soma_a0.get(c, 0.0) for c in contas_do_tot])
                        v_tot_a1 = sum([soma_a1.get(c, 0.0) for c in contas_do_tot])
                        v_tot_a2 = sum([soma_a2.get(c, 0.0) for c in contas_do_tot])

                        linhas.append({
                            "Estrutura": f"📊 {tot}",
                            lbl_a0: v_tot_a0,
                            lbl_a1: v_tot_a1,
                            lbl_a2: v_tot_a2,
                            "Tipo": "Totalizador"
                        })

                        for c in contas_do_tot:
                            linhas.append({
                                "Estrutura": f"  ├─ {c}",
                                lbl_a0: soma_a0.get(c, 0.0),
                                lbl_a1: soma_a1.get(c, 0.0),
                                lbl_a2: soma_a2.get(c, 0.0),
                                "Tipo": "Conta"
                            })

                        tot_g_a0 += v_tot_a0
                        tot_g_a1 += v_tot_a1
                        tot_g_a2 += v_tot_a2

                    df_exibicao = pd.DataFrame(linhas)

                    # KPI Cards Anuais
                    k1, k2, k3 = st.columns(3)
                    k1.metric(f"Acumulado {lbl_a0}", f"R$ {tot_g_a0:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    k2.metric(f"Acumulado {lbl_a1}", f"R$ {tot_g_a1:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    k3.metric(f"Acumulado {lbl_a2}", f"R$ {tot_g_a2:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                    col_cols_exibir = [lbl_a0, lbl_a1, lbl_a2]

            st.markdown("---")

            # TABELA COMPARATIVA COMPLETA
            st.subheader(f"📋 Demonstrativo Financeiro Comparativo ({tipo_visao})")
            
            df_tabela_final = df_exibicao[["Estrutura"] + col_cols_exibir].copy()

            # Adicionar Linha de Total Geral ao Final do Relatório
            somas_totais = {"Estrutura": "🏆 TOTAL GERAL DO RELATÓRIO"}
            for col_c in col_cols_exibir:
                somas_totais[col_c] = df_exibicao[df_exibicao["Tipo"] == "Totalizador"][col_c].sum()

            df_tabela_final = pd.concat([df_tabela_final, pd.DataFrame([somas_totais])], ignore_index=True)

            # Formatação de Moeda para todas as colunas de valores
            dict_format = {col_c: "R$ {:,.2f}" for col_c in col_cols_exibir}

            st.dataframe(
                df_tabela_final.style.format(dict_format),
                use_container_width=True,
                height=650
            )
            
    # -----------------------------------------------------------------------------
    # CONFIGURAÇÃO DE UNIDADES E UGs
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "unidades":
        st.header("⚙️ Configuração de Unidades Organizacionais & Mapeamento de UGs")
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
                        for ug_k, val in list(st.session_state.mapa_ugs.items()):
                            if val == unidade:
                                st.session_state.mapa_ugs[ug_k] = "Encargos Gerais da UFSM / Outros"
                        st.rerun()

                    if st.session_state.editando_unidade == unidade:
                        with st.container():
                            c_in, c_save, c_canc = st.columns([4, 1, 1])
                            novo_nome_u = c_in.text_input("Novo nome:", value=unidade, key=f"inp_u_{idx}")
                            if c_save.button("Salvar", key=f"save_u_{idx}"):
                                if novo_nome_u and novo_nome_u != unidade:
                                    st.session_state.unidades_consolidadas[idx] = novo_nome_u
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
    # CONFIGURAÇÃO DE CONTAS, TOTALIZADORES & MAPEAMENTO DE PIs
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "contas":
        st.header("⚙️ Configuração de Totalizadores, Contas Gerenciais & PIs")
        st.write("Gerencie totalizadores, plano de contas, vinculação de contas nos totalizadores e mapeamento dos PIs.")

        tab_t0, tab_c1, tab_c2, tab_c3 = st.tabs([
            "📊 Cadastro de Totalizadores", 
            "📌 Cadastro de Contas Gerenciais", 
            "🔗 Vinculação de Contas aos Totalizadores", 
            "🏷️ Mapeamento de PIs"
        ])

        # TAB 0: CADASTRO DE TOTALIZADORES
        with tab_t0:
            col_add_t, col_list_t = st.columns([1, 2])

            with col_add_t:
                st.subheader("Adicionar Totalizador")
                novo_totalizador = st.text_input("Nome do Totalizador/Grupo:")
                if st.button("➕ Adicionar Totalizador", use_container_width=True):
                    if novo_totalizador and novo_totalizador not in st.session_state.totalizadores:
                        st.session_state.totalizadores.append(novo_totalizador)
                        st.success(f"Totalizador '{novo_totalizador}' adicionado!")
                        st.rerun()

            with col_list_t:
                st.subheader(f"Totalizadores Cadastrados ({len(st.session_state.totalizadores)})")
                
                for idx, tot in enumerate(st.session_state.totalizadores):
                    c_nome, c_edit, c_del = st.columns([5, 1, 1])
                    c_nome.write(f"• **{tot}**")
                    
                    if c_edit.button("✏️", key=f"edit_tot_{idx}", help="Alterar nome do Totalizador"):
                        st.session_state.editando_totalizador = tot
                        st.rerun()

                    if c_del.button("🗑️", key=f"del_tot_{idx}", help="Excluir Totalizador"):
                        st.session_state.totalizadores.remove(tot)
                        for c_k, v_tot in list(st.session_state.mapa_contas_totalizadores.items()):
                            if v_tot == tot:
                                st.session_state.mapa_contas_totalizadores[c_k] = "G-8.0 Total de Despesas Operacionais e Encargos Institucionais"
                        st.rerun()

                    if st.session_state.editando_totalizador == tot:
                        with st.container():
                            c_in, c_save, c_canc = st.columns([4, 1, 1])
                            novo_nome_tot = c_in.text_input("Novo nome:", value=tot, key=f"inp_tot_{idx}")
                            if c_save.button("Salvar", key=f"save_tot_{idx}"):
                                if novo_nome_tot and novo_nome_tot != tot:
                                    st.session_state.totalizadores[idx] = novo_nome_tot
                                    for c_k, v_tot in st.session_state.mapa_contas_totalizadores.items():
                                        if v_tot == tot:
                                            st.session_state.mapa_contas_totalizadores[c_k] = novo_nome_tot
                                    st.success("Totalizador alterado com sucesso!")
                                st.session_state.editando_totalizador = None
                                st.rerun()

                            if c_canc.button("Cancelar", key=f"canc_tot_{idx}"):
                                st.session_state.editando_totalizador = None
                                st.rerun()

        # TAB 1: CADASTRO DE CONTAS GERENCIAIS
        with tab_c1:
            col_add, col_list = st.columns([1, 2])

            with col_add:
                st.subheader("Adicionar Nova Conta")
                nova_conta = st.text_input("Nome/Código da Conta:")
                tot_para_conta = st.selectbox("Associar ao Totalizador:", st.session_state.totalizadores)

                if st.button("➕ Adicionar Conta", use_container_width=True):
                    if nova_conta and nova_conta not in st.session_state.contas_gerenciais:
                        st.session_state.contas_gerenciais.append(nova_conta)
                        st.session_state.mapa_contas_totalizadores[nova_conta] = tot_para_conta
                        st.success(f"Conta '{nova_conta}' adicionada e associada ao '{tot_para_conta}'!")
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
                        if conta in st.session_state.mapa_contas_totalizadores:
                            del st.session_state.mapa_contas_totalizadores[conta]
                        for pi_k, val in list(st.session_state.dicionario_pis.items()):
                            if val == conta:
                                st.session_state.dicionario_pis[pi_k] = "Sem Classificação"
                        st.rerun()

                    if st.session_state.editando_conta == conta:
                        with st.container():
                            c_in, c_save, c_canc = st.columns([4, 1, 1])
                            novo_nome_c = c_in.text_input("Novo nome:", value=conta, key=f"inp_c_{idx}")
                            if c_save.button("Salvar", key=f"save_c_{idx}"):
                                if novo_nome_c and novo_nome_c != conta:
                                    st.session_state.contas_gerenciais[idx] = novo_nome_c
                                    if conta in st.session_state.mapa_contas_totalizadores:
                                        st.session_state.mapa_contas_totalizadores[novo_nome_c] = st.session_state.mapa_contas_totalizadores.pop(conta)
                                    for pi_k, val in st.session_state.dicionario_pis.items():
                                        if val == conta:
                                            st.session_state.dicionario_pis[pi_k] = novo_nome_c
                                    st.success("Conta alterada com sucesso!")
                                st.session_state.editando_conta = None
                                st.rerun()

                            if c_canc.button("Cancelar", key=f"canc_c_{idx}"):
                                st.session_state.editando_conta = None
                                st.rerun()

        # TAB 2: VINCULAÇÃO DE CONTAS AOS TOTALIZADORES
        with tab_c2:
            st.subheader("Associação das Contas Gerenciais nos Totalizadores")
            st.write("Defina a qual Totalizador (Grupo Gerencial) cada Conta pertence:")

            for conta_item in st.session_state.contas_gerenciais:
                col_lbl_c, col_sel_tot = st.columns([2, 2])
                col_lbl_c.write(f"🏷️ **{conta_item}**")

                tot_atual = st.session_state.mapa_contas_totalizadores.get(conta_item, st.session_state.totalizadores[0])
                if tot_atual not in st.session_state.totalizadores:
                    tot_atual = st.session_state.totalizadores[0]

                idx_t = st.session_state.totalizadores.index(tot_atual)

                novo_tot_ass = col_sel_tot.selectbox(
                    "Totalizador / Grupo:",
                    st.session_state.totalizadores,
                    index=idx_t,
                    key=f"sel_tot_for_{conta_item}"
                )
                st.session_state.mapa_contas_totalizadores[conta_item] = novo_tot_ass

        # TAB 3: MAPEAMENTO DE PIs
        with tab_c3:
            st.subheader("Mapeamento de Planos Internos (PI SIAFI -> Conta Gerencial)")

            if st.session_state.dados_tg_raw is None:
                st.warning("⚠️ Carregue a planilha na aba '1. Carga da Planilha' para listar os PIs e realizar o mapeamento.")
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
                        "Associar à Conta:",
                        st.session_state.contas_gerenciais,
                        index=idx_def,
                        key=f"sel_pi_{pi_item}"
                    )
                    st.session_state.dicionario_pis[pi_item] = nova_ass

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
        st.header("⚙️ Configurações Visuais e Logomarca")
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
