import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. INICIALIZAÇÃO DA SESSÃO (Necessário antes de set_page_config para o Favicon)
# -----------------------------------------------------------------------------
if "logo_personalizada" not in st.session_state:
    st.session_state.logo_personalizada = None

# Define o ícone da aba: usa a logo em bytes se existir, senão usa emoji padrão
icone_aba = st.session_state.logo_personalizada if st.session_state.logo_personalizada is not None else "🏛️"

# Configuração da página e aba do Chrome
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

    /* Estilização para Impressão */
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

# MAPEAMENTO PADRÃO DAS NATUREZAS DE DESPESA DETALHADAS
MAPA_NATUREZAS_PADRAO = {
    "'-8 - SEM INFORMACAO": "8.3. Outras Despesas Operacionais",
    "31901143 - 13º SALARIO": "8.3. Outras Despesas Operacionais",
    "31901145 - FERIAS - 1/3 CONSTITUCIONAL": "8.3. Outras Despesas Operacionais",
    "33903004 - GAS E OUTROS MATERIAIS ENGARRAFADOS": "1.2. Concessionárias (Energia, Água, Gás)",
    "33903007 - GENEROS DE ALIMENTACAO": "4.1. Restaurante Universitário (RU) - Insumos e Operação",
    "33903010 - MATERIAL ODONTOLOGICO": "5.2. Material Didático, de Laboratório e Insumos de Pesquisa",
    "33903011 - MATERIAL QUIMICO": "5.2. Material Didático, de Laboratório e Insumos de Pesquisa",
    "33903012 - MATERIAL DE COUDELARIA OU DE USO ZOOTECNICO": "5.4. Unidades Especializadas (HVU, Fazenda, Colégios)",
    "33903014 - MATERIAL EDUCATIVO E ESPORTIVO": "5.2. Material Didático, de Laboratório e Insumos de Pesquisa",
    "33903015 - MATERIAL P/ FESTIVIDADES E HOMENAGENS": "6.2. Eventos Acadêmicos, Culturais e Congressos",
    "33903016 - MATERIAL DE EXPEDIENTE": "8.1. Material de Expediente e Suprimentos",
    "33903017 - MATERIAL DE TIC - MATERIAL DE CONSUMO": "3.1. Equipamentos e Infraestrutura de TI",
    "33903019 - MATERIAL DE ACONDICIONAMENTO E EMBALAGEM": "8.1. Material de Expediente e Suprimentos",
    "33903020 - MATERIAL DE CAMA, MESA E BANHO": "4.3. Moradia Estudantil e Apoio ao Estudante",
    "33903021 - MATERIAL DE COPA E COZINHA": "4.1. Restaurante Universitário (RU) - Insumos e Operação",
    "33903022 - MATERIAL DE LIMPEZA E PROD. DE HIGIENIZACAO": "2.2. Serviços de Limpeza e Higienização",
    "33903024 - MATERIAL P/ MANUT.DE BENS IMOVEIS/INSTALACOES": "1.3. Manutenção Predial e Conservação",
    "33903025 - MATERIAL P/ MANUTENCAO DE BENS MOVEIS": "1.3. Manutenção Predial e Conservação",
    "33903026 - MATERIAL ELETRICO E ELETRONICO": "1.3. Manutenção Predial e Conservação",
    "33903028 - MATERIAL DE PROTECAO E SEGURANCA": "2.1. Serviços de Vigilância e Portaria",
    "33903029 - MATERIAL P/ AUDIO, VIDEO E FOTO": "3.1. Equipamentos e Infraestrutura de TI",
    "33903030 - MATERIAL PARA COMUNICACOES": "3.3. Conectividade, Redes e Telefonia",
    "33903031 - SEMENTES, MUDAS DE PLANTAS E INSUMOS": "1.4. Conservação de Áreas Verdes e Limpeza Urbana",
    "33903035 - MATERIAL LABORATORIAL": "5.2. Material Didático, de Laboratório e Insumos de Pesquisa",
    "33903036 - MATERIAL HOSPITALAR": "5.4. Unidades Especializadas (HVU, Fazenda, Colégios)",
    "33903041 - MATERIAL P/ UTILIZACAO EM GRAFICA": "8.1. Material de Expediente e Suprimentos",
    "33903042 - FERRAMENTAS": "1.3. Manutenção Predial e Conservação",
    "33903044 - MATERIAL DE SINALIZACAO VISUAL E OUTROS": "1.3. Manutenção Predial e Conservação",
    "33903046 - MATERIAL BIBLIOGRAFICO": "7.2. Biblioteca (Livros, Periódicos e Bases Científicas)",
    "33909214 - DIARIAS - CIVIL": "6.1. Passagens e Diárias (Nacionais e Internacionais)"
}

USUARIOS_PADRAO = [
    {"usuario": "admin", "nome": "Administrador Geral", "senha": "ufsm2026", "perfil": "Administrador"},
    {"usuario": "pra_gestor", "nome": "Gestor PRA", "senha": "pra123", "perfil": "Gestor"},
]

# Inicialização da Memória do Sistema
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "carga"

if "contas_gerenciais" not in st.session_state:
    st.session_state.contas_gerenciais = PLANO_CONTAS_PADRAO.copy()

if "unidades_consolidadas" not in st.session_state:
    st.session_state.unidades_consolidadas = UNIDADES_UFSM_PADRAO.copy()

if "mapa_ugs" not in st.session_state:
    st.session_state.mapa_ugs = MAPA_UGS_PADRAO.copy()

if "tabela_usuarios" not in st.session_state:
    st.session_state.tabela_usuarios = USUARIOS_PADRAO.copy()

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "dicionario_naturezas" not in st.session_state:
    st.session_state.dicionario_naturezas = MAPA_NATUREZAS_PADRAO.copy()

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

    if st.sidebar.button("🏷️ Configuração de Contas & Naturezas", use_container_width=True, type="primary" if st.session_state.pagina_atual == "contas" else "secondary"):
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
    # PÁGINA 2: RELATÓRIO EXECUTIVO
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
                    22UNIVERSIDADE FEDERAL DE SANTA MARIA - UFSM</h2>
                    <h4>PRÓ-REITORIA DE ADMINISTRAÇÃO - RELATÓRIO EXECUTIVO ORÇAMENTÁRIO</h4>
                    <p style="margin:2px 0 0 0; font-size:12px; color:#777;">Emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        if st.session_state.dados_tg_raw is None:
            st.info("👋 Por favor, faça a carga do arquivo na aba **'1. Carga da Planilha'** para acessar os relatórios.")
        else:
            df = st.session_state.dados_tg_raw
            colunas = list(df.columns)

            col_resultado_lei = colunas[1] if len(colunas) > 1 else colunas[0]   # Coluna B
            col_ug_nome = colunas[6] if len(colunas) > 6 else colunas[0]         # Coluna G
            col_nat_cod = colunas[13] if len(colunas) > 13 else colunas[0]       # Coluna N (Natureza Despesa Código)
            col_nat_nome = colunas[14] if len(colunas) > 14 else col_nat_cod     # Coluna O (Natureza Despesa Nome)
            col_valor = colunas[19] if len(colunas) > 19 else colunas[-1]       # Coluna T

            df_disc = df[df[col_resultado_lei].astype(str).str.contains("2", na=False)].copy()
            df_disc["Valor_Tratado"] = df_disc[col_valor].apply(converter_valor)
            
            df_disc["Unidade_Consolidada"] = df_disc[col_ug_nome].astype(str).map(
                lambda x: st.session_state.mapa_ugs.get(x.strip(), "Encargos Gerais da UFSM / Outros")
            )

            df_disc["ND_Completa"] = df_disc[col_nat_cod].astype(str).str.strip() + " - " + df_disc[col_nat_nome].astype(str).str.strip()
            df_disc["Conta_Gerencial"] = df_disc["ND_Completa"].map(
                lambda x: st.session_state.dicionario_naturezas.get(x, "Sem Classificação")
            )

            col_sel_u, col_btn_imp = st.columns([3, 1])

            with col_sel_u:
                lista_unidades_select = ["--- TOTAL DA UFSM ---"] + sorted(st.session_state.unidades_consolidadas)
                unidade_selecionada = st.selectbox("🏛️ Selecione a Unidade para Análise:", lista_unidades_select)

            with col_btn_imp:
                st.write(" ")
                if st.button("🖨️ Imprimir / Gerar PDF", type="primary", use_container_width=True):
                    st.components.v1.html("<script>window.parent.print();</script>", height=0, width=0)

            if unidade_selecionada != "--- TOTAL DA UFSM ---":
                df_relatorio = df_disc[df_disc["Unidade_Consolidada"] == unidade_selecionada].copy()
            else:
                df_relatorio = df_disc.copy()

            val_total = df_relatorio["Valor_Tratado"].sum()
            qtd_naturezas = df_relatorio["ND_Completa"].nunique()

            k1, k2, k3 = st.columns(3)
            k1.metric("Visão Selecionada", unidade_selecionada)
            k2.metric("Total Executado (Discricionário)", f"R$ {val_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            k3.metric("Naturezas de Despesa Ativas", qtd_naturezas if val_total > 0 else 0)

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
                st.subheader("🔍 Detalhamento por Natureza de Despesa Detalhada")
                df_det = df_relatorio.groupby(["Conta_Gerencial", "ND_Completa"])["Valor_Tratado"].sum().reset_index()
                df_det.columns = ["Conta Gerencial", "Natureza de Despesa Detalhada", "Valor (R$)"]
                df_det = df_det[df_det["Valor (R$)"] > 0].sort_values(by="Valor (R$)", ascending=False)
                st.dataframe(df_det.style.format({"Valor (R$)": "R$ {:,.2f}"}), use_container_width=True)

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
    # CONFIGURAÇÃO DE CONTAS & MAPEAMENTO DE NATUREZAS DE DESPESA
    # -----------------------------------------------------------------------------
    elif st.session_state.pagina_atual == "contas":
        st.header("⚙️ Configuração de Contas Gerenciais & Mapeamento de Naturezas de Despesa")
        st.write("Gerencie a estrutura do Plano de Contas e vincule as Naturezas de Despesa Detalhadas (SIAFI).")

        tab_c1, tab_c2 = st.tabs(["📌 Cadastro de Contas Gerenciais", "🔗 Mapeamento de Naturezas de Despesa"])

        # TAB 1: CADASTRO DE CONTAS GERENCIAIS
        with tab_c1:
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
                        for nat_k, val in list(st.session_state.dicionario_naturezas.items()):
                            if val == conta:
                                st.session_state.dicionario_naturezas[nat_k] = "Sem Classificação"
                        st.rerun()

                    if st.session_state.editando_conta == conta:
                        with st.container():
                            c_in, c_save, c_canc = st.columns([4, 1, 1])
                            novo_nome_c = c_in.text_input("Novo nome:", value=conta, key=f"inp_c_{idx}")
                            if c_save.button("Salvar", key=f"save_c_{idx}"):
                                if novo_nome_c and novo_nome_c != conta:
                                    st.session_state.contas_gerenciais[idx] = novo_nome_c
                                    for nat_k, val in st.session_state.dicionario_naturezas.items():
                                        if val == conta:
                                            st.session_state.dicionario_naturezas[nat_k] = novo_nome_c
                                    st.success("Conta alterada com sucesso!")
                                st.session_state.editando_conta = None
                                st.rerun()

                            if c_canc.button("Cancelar", key=f"canc_c_{idx}"):
                                st.session_state.editando_conta = None
                                st.rerun()

        # TAB 2: MAPEAMENTO DE NATUREZAS DE DESPESA
        with tab_c2:
            st.subheader("Mapeamento de Naturezas de Despesa Detalhadas (SIAFI -> Conta Gerencial)")

            col_b1_nat, col_b2_nat = st.columns([2, 1])
            with col_b1_nat:
                st.caption("Associe cada Natureza de Despesa Detalhada a uma Conta Gerencial:")
            with col_b2_nat:
                if st.button("Restaurar Mapeamento Padrão de Naturezas"):
                    st.session_state.dicionario_naturezas = MAPA_NATUREZAS_PADRAO.copy()
                    st.success("Mapeamento padrão de Naturezas de Despesa restaurado!")
                    st.rerun()

            naturezas_para_mapear = set(st.session_state.dicionario_naturezas.keys())

            if st.session_state.dados_tg_raw is not None:
                df = st.session_state.dados_tg_raw
                colunas = list(df.columns)
                
                col_nat_cod = colunas[13] if len(colunas) > 13 else colunas[0]
                col_nat_nome = colunas[14] if len(colunas) > 14 else col_nat_cod

                df_nat = df[[col_nat_cod, col_nat_nome]].drop_duplicates().dropna()
                df_nat["ND_Completa"] = df_nat[col_nat_cod].astype(str).str.strip() + " - " + df_nat[col_nat_nome].astype(str).str.strip()
                for nat_p in df_nat["ND_Completa"].unique():
                    naturezas_para_mapear.add(nat_p)

            st.write(f"**Total de Naturezas de Despesa identificadas:** {len(naturezas_para_mapear)}")

            for nat_item in sorted(list(naturezas_para_mapear)):
                col_lbl, col_sel = st.columns([2, 2])
                col_lbl.write(f"📌 **{nat_item}**")
                
                conta_sugerida = st.session_state.dicionario_naturezas.get(nat_item, "Sem Classificação")
                if conta_sugerida == "Sem Classificação":
                    n_up = nat_item.upper()
                    if "ALIMENT" in n_up or "RU" in n_up:
                        conta_sugerida = "4.1. Restaurante Universitário (RU) - Insumos e Operação"
                    elif "BOLSA" in n_up or "ASSIST" in n_up:
                        conta_sugerida = "4.2. Bolsas de Assistência Estudantil e Permanência"
                    elif "ENERGIA" in n_up or "AGUA" in n_up or "GAS" in n_up:
                        conta_sugerida = "1.2. Concessionárias (Energia, Água, Gás)"
                    elif "OBRA" in n_up or "REFORMA" in n_up:
                        conta_sugerida = "1.1. Obras, Reformas e Adequações"
                    elif "TIC" in n_up or "INFORMATICA" in n_up:
                        conta_sugerida = "3.1. Equipamentos e Infraestrutura de TI"
                    elif "EXPEDIENTE" in n_up or "EMBALAGEM" in n_up:
                        conta_sugerida = "8.1. Material de Expediente e Suprimentos"
                    elif "LABORATORIAL" in n_up or "QUIMICO" in n_up:
                        conta_sugerida = "5.2. Material Didático, de Laboratório e Insumos de Pesquisa"

                idx_def = st.session_state.contas_gerenciais.index(conta_sugerida) if conta_sugerida in st.session_state.contas_gerenciais else 0

                nova_ass = col_sel.selectbox(
                    "Associar à Conta:",
                    st.session_state.contas_gerenciais,
                    index=idx_def,
                    key=f"sel_nat_{nat_item}"
                )
                st.session_state.dicionario_naturezas[nat_item] = nova_ass

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
