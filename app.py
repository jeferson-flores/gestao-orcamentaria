import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sistema Gerencial de Custos e Execução Orçamentária - UFSM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 1. CARREGAMENTO DE DADOS E DICIONÁRIOS AUTOMÁTICOS
# =============================================================================

@st.cache_data
def carregar_dados_completos(caminho_arquivo):
    xls = pd.ExcelFile(caminho_arquivo)
    
    # Leitura das Abas
    df_base = pd.read_excel(xls, sheet_name='Base')
    
    # Tratamento de Nulos e Formatação de Strings
    cols_texto = [
        'UG Responsável Código', 'UG Responsável Nome', 'UG Beneficiada ACC Código', 
        'UG Beneficiada ACC Nome', 'PI Código PI', 'PI Nome', 
        'Natureza Despesa Detalhada Código', 'Natureza Despesa Detalhada Nome',
        'Favorecido Doc. Número', 'Favorecido Doc. Nome', 'Documento Hábil Número',
        'DH - Observação Texto', 'NE Número Completo'
    ]
    for col in cols_texto:
        if col in df_base.columns:
            df_base[col] = df_base[col].fillna('SEM INFORMACAO').astype(str).str.strip()

    # Garantir valor numérico
    if 'DetaCusto Acum. DH - Moeda Origem' in df_base.columns:
        df_base['DetaCusto Acum. DH - Moeda Origem'] = pd.to_numeric(df_base['DetaCusto Acum. DH - Moeda Origem'], errors='coerce').fillna(0)

    # Regras de Mapeamento de Contas Gerenciais (Subgrupos 1.1 a 8.3)
    def classificar_conta_gerencial(row):
        nd_cod = str(row.get('Natureza Despesa Detalhada Código', ''))
        nd_nome = str(row.get('Natureza Despesa Detalhada Nome', '')).upper()
        pi_cod = str(row.get('PI Código PI', ''))
        pi_nome = str(row.get('PI Nome', '')).upper()
        
        texto_comb = f"{nd_cod} {nd_nome} {pi_cod} {pi_nome}"
        
        # Grupo 1
        if any(k in texto_comb for k in ["OBRA", "REFORMA", "BENFEITORIA", "ADEQUACAO", "CONSTRUCAO"]):
            return "1.1. Obras, Reformas e Adequações"
        elif any(k in texto_comb for k in ["ENERGIA", "AGUA", "GAS", "CONCESSIONARIA", "LUZ", "TELEFONIA"]):
            return "1.2. Concessionárias (Energia, Água, Gás)"
        elif any(k in texto_comb for k in ["MANUT", "CONSERVACAO", "PREDIAL", "REPARO"]) and not "TI" in texto_comb:
            return "1.3. Manutenção Predial e Conservação"
        elif any(k in texto_comb for k in ["VERDE", "JARDIM", "PAISAGISMO", "LIMPEZA URBANA"]):
            return "1.4. Conservação de Áreas Verdes e Limpeza Urbana"
            
        # Grupo 2
        elif any(k in texto_comb for k in ["VIGILANCIA", "PORTARIA", "SEGURANCA"]):
            return "2.1. Serviços de Vigilância e Portaria"
        elif any(k in texto_comb for k in ["HIGIENIZACAO", "LIMPEZA", "DESINFECCAO"]):
            return "2.2. Serviços de Limpeza e Higienização"
        elif any(k in texto_comb for k in ["MOTORISTA", "APOIO ADMIN", "SECRETARIA", "TRANSPORTE"]):
            return "2.3. Apoio Administrativo e Motoristas"
        elif any(k in texto_comb for k in ["RECEPCAO", "SERVICOS GERAIS", "COPA"]):
            return "2.4. Recepção e Serviços Gerais"
            
        # Grupo 3
        elif any(k in texto_comb for k in ["TI", "INFORMATICA", "SOFTWARE", "SISTEMA", "NUVEM", "REDES", "COMPUTAD"]):
            if "LICENCA" in texto_comb or "SOFTWARE" in texto_comb:
                return "3.2. Licenças de Software, Sistemas e Nuvem"
            elif "LINK" in texto_comb or "INTERNET" in texto_comb:
                return "3.3. Conectividade, Redes e Telefonia"
            return "3.1. Equipamentos e Infraestrutura de TI"
            
        # Grupo 4
        elif any(k in texto_comb for k in ["RU", "RESTAURANTE", "ALIMENTA", "MARMITA"]):
            return "4.1. Restaurante Universitário (RU) - Insumos e Operação"
        elif any(k in texto_comb for k in ["BOLSA", "ASSIST", "PERMANENCIA", "PRAE", "PNAES"]):
            return "4.2. Bolsas de Assistência Estudantil e Permanência"
        elif any(k in texto_comb for k in ["MORADIA", "CEU"]):
            return "4.3. Moradia Estudantil e Apoio ao Estudante"
            
        # Grupo 5
        elif any(k in texto_comb for k in ["GRADUACAO", "POS-GRADUACAO", "PROAP", "CAPES", "CNPQ"]):
            return "5.1. Bolsas de Graduação, Pós e Extensão"
        elif any(k in texto_comb for k in ["LABORATORIO", "DIDATICO", "PESQUISA", "INSUMO"]):
            return "5.2. Material Didático, de Laboratório e Insumos de Pesquisa"
        elif any(k in texto_comb for k in ["EXTENSAO", "INOVACAO", "FIEX", "FOMENTO", "PROJETO"]):
            return "5.3. Fomento a Projetos de Pesquisa, Extensão e Inovação"
        elif any(k in texto_comb for k in ["HVU", "FAZENDA", "COLEGIO", "POLITECNICO", "CTISM"]):
            return "5.4. Unidades Especializadas (HVU, Fazenda, Colégios)"

        # Grupo 6
        elif any(k in texto_comb for k in ["DIARIA", "PASSAGEM", "VIAGEM"]):
            return "6.1. Passagens e Diárias (Nacionais e Internacionais)"
        elif any(k in texto_comb for k in ["EVENTO", "CONGRESSO", "CULTURA"]):
            return "6.2. Eventos Acadêmicos, Culturais e Congressos"
        elif any(k in texto_comb for k in ["CAPACITACAO", "TREINAMENTO", "CURSO"]):
            return "6.3. Capacitação e Desenvolvimento de Servidores"

        # Grupo 7
        elif any(k in texto_comb for k in ["EQUIPAMENTO", "MOBILIARIO", "MAQUINA"]):
            return "7.1. Aquisição de Equipamentos e Mobiliário"
        elif any(k in texto_comb for k in ["BIBLIOTECA", "LIVRO", "PERIODICO"]):
            return "7.2. Biblioteca (Livros, Periódicos e Bases Científicas)"
        elif any(k in texto_comb for k in ["FROTA", "COMBUSTIVEL", "VEICULO"]):
            return "7.3. Frota e Combustíveis"

        # Grupo 8
        elif any(k in texto_comb for k in ["EXPEDIENTE", "SUPRIMENTO", "ESCRITORIO"]):
            return "8.1. Material de Expediente e Suprimentos"
        elif any(k in texto_comb for k in ["ENCARGOS", "TAXA", "IMPOSTO", "TRIBUTO", "PIS", "PASEP"]):
            return "8.2. Encargos Institucionais e Impostos"
        else:
            return "8.3. Outras Despesas Operacionais"

    df_base['Conta_Gerencial'] = df_base.apply(classificar_conta_gerencial, axis=1)

    # MAPEMAENTO DOS GRUPOS TOTALIZADORES
    mapa_totalizadores = {
        '1.1': 'G-1.0 Total de Infraestrutura e Manutenção Predial',
        '1.2': 'G-1.0 Total de Infraestrutura e Manutenção Predial',
        '1.3': 'G-1.0 Total de Infraestrutura e Manutenção Predial',
        '1.4': 'G-1.0 Total de Infraestrutura e Manutenção Predial',
        '2.1': 'G-2.0 Total de Serviços Terceirizados e Operacionais',
        '2.2': 'G-2.0 Total de Serviços Terceirizados e Operacionais',
        '2.3': 'G-2.0 Total de Serviços Terceirizados e Operacionais',
        '2.4': 'G-2.0 Total de Serviços Terceirizados e Operacionais',
        '3.1': 'G-3.0 Total de Tecnologia da Informação e Comunicação',
        '3.2': 'G-3.0 Total de Tecnologia da Informação e Comunicação',
        '3.3': 'G-3.0 Total de Tecnologia da Informação e Comunicação',
        '4.1': 'G-4.0 Total de Assistência Estudantil e RU',
        '4.2': 'G-4.0 Total de Assistência Estudantil e RU',
        '4.3': 'G-4.0 Total de Assistência Estudantil e RU',
        '5.1': 'G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas',
        '5.2': 'G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas',
        '5.3': 'G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas',
        '5.4': 'G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas',
        '6.1': 'G-6.0 Total de Viagens, Eventos e Capacitação',
        '6.2': 'G-6.0 Total de Viagens, Eventos e Capacitação',
        '6.3': 'G-6.0 Total de Viagens, Eventos e Capacitação',
        '7.1': 'G-7.0 Total de Equipamentos, Acervo e Logística',
        '7.2': 'G-7.0 Total de Equipamentos, Acervo e Logística',
        '7.3': 'G-7.0 Total de Equipamentos, Acervo e Logística',
        '8.1': 'G-8.0 Total de Despesas Operacionais e Encargos Institucionais',
        '8.2': 'G-8.0 Total de Despesas Operacionais e Encargos Institucionais',
        '8.3': 'G-8.0 Total de Despesas Operacionais e Encargos Institucionais'
    }

    df_base['Grupo_Totalizador'] = df_base['Conta_Gerencial'].str[:3].map(mapa_totalizadores).fillna('G-8.0 Total de Despesas Operacionais e Encargos Institucionais')
    
    # Colunas Auxiliares de Datas e Nomes
    df_base['Ano'] = df_base['Mês Referência ACC (Código Completo)'].astype(str).str[:4]
    df_base['Conta_Contabil_Formatada'] = df_base['Natureza Despesa Detalhada Código'] + " - " + df_base['Natureza Despesa Detalhada Nome']
    df_base['PI_Formatado'] = df_base['PI Código PI'] + " - " + df_base['PI Nome']
    
    return df_base

# Carregamento
df_base = carregar_dados_completos("Liquida_mes_comp_2022-2026.xlsx")

# =============================================================================
# 2. BARRA LATERAL - FILTROS MULTI-SELEÇÃO COMBO
# =============================================================================

st.sidebar.title("📌 Filtros do Relatório")

# Filtro 1: Ano
lista_anos = sorted(df_base['Ano'].unique())
anos_sel = st.sidebar.multiselect("Exercício (Ano)", lista_anos, default=lista_anos[-1:])

# Filtro 2: UG Responsável
lista_ugs = sorted(df_base['UG Responsável Nome'].unique())
ugs_sel = st.sidebar.multiselect("Unidade Gestora (UG)", lista_ugs)

# Filtro 3: Grupo Totalizador
lista_grupos = sorted(df_base['Grupo_Totalizador'].unique())
grupos_sel = st.sidebar.multiselect("Grupo Gerencial Totalizador", lista_grupos)

# Filtro 4: Contas Gerenciais
lista_contas_gerenciais = sorted(df_base['Conta_Gerencial'].unique())
contas_gerenciais_sel = st.sidebar.multiselect("Conta Gerencial", lista_contas_gerenciais)

# Aplicação dos Filtros
df_f = df_base.copy()

if anos_sel:
    df_f = df_f[df_f['Ano'].isin(anos_sel)]
if ugs_sel:
    df_f = df_f[df_f['UG Responsável Nome'].isin(ugs_sel)]
if grupos_sel:
    df_f = df_f[df_f['Grupo_Totalizador'].isin(grupos_sel)]
if contas_gerenciais_sel:
    df_f = df_f[df_f['Conta_Gerencial'].isin(contas_gerenciais_sel)]

# =============================================================================
# 3. CABEÇALHO E PAINEL DE METRICAS (KPIS)
# =============================================================================

st.title("🏛️ Painel Gerencial de Custos e Execução - UFSM")
st.markdown("Acompanhamento consolidado por **Unidades Gestoras, Contas Gerenciais e Planos Internos (PIs)**.")

valor_total = df_f['DetaCusto Acum. DH - Moeda Origem'].sum()
total_registros = len(df_f)
total_ugs = df_f['UG Responsável Nome'].nunique()
total_pis = df_f['PI Código PI'].nunique()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Custo Total Acumulado", f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
m2.metric("Total de Lançamentos", f"{total_registros:,}".replace(",", "."))
m3.metric("Unidades Gestoras (UGs)", total_ugs)
m4.metric("Planos Internos (PIs)", total_pis)

st.markdown("---")

# =============================================================================
# 4. ESTRUTURA EXPANSÍVEL COM TOTALIZADORES GERENCIAIS
# =============================================================================

st.subheader("📑 Demostrativo de Custos com Totalizadores")

modo_exibicao = st.radio(
    "Selecione o Nível de Detalhamento:",
    ["Visão Sintética (Somente Totais dos Grupos Gerenciais)", "Visão Analítica Expansível (Clicar no '+' para abrir Contas e PIs)"],
    horizontal=True
)

if modo_exibicao == "Visão Sintética (Somente Totais dos Grupos Gerenciais)":
    df_sint = df_f.groupby('Grupo_Totalizador')['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
    df_sint.columns = ['Grupo Totalizador Gerencial', 'Valor Total (R$)']
    df_sint['% Representação'] = (df_sint['Valor Total (R$)'] / valor_total * 100) if valor_total > 0 else 0
    df_sint = df_sint.sort_values(by='Grupo Totalizador Gerencial')
    
    st.dataframe(
        df_sint.style.format({'Valor Total (R$)': 'R$ {:,.2f}', '% Representação': '{:.2f}%'}),
        use_container_width=True
    )

else:
    # MODO EXPANSÍVEL POR GRUPO GERENCIAL DE 1 A 8
    grupos_unicos = sorted(df_f['Grupo_Totalizador'].unique())
    
    for grp in grupos_unicos:
        df_grp = df_f[df_f['Grupo_Totalizador'] == grp]
        val_grp = df_grp['DetaCusto Acum. DH - Moeda Origem'].sum()
        pct_grp = (val_grp / valor_total * 100) if valor_total > 0 else 0
        
        # Expansor com Sinal de +
        titulo_expander = f"➕ {grp}  |  TOTAL: R$ {val_grp:,.2f} ({pct_grp:.2f}%)".replace(",", "X").replace(".", ",").replace("X", ".")
        
        with st.expander(titulo_expander):
            df_det = df_grp.groupby(['Conta_Gerencial', 'Conta_Contabil_Formatada', 'PI_Formatado'])['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
            df_det.columns = ['Subgrupo Gerencial', 'Conta Contábil (ND)', 'Plano Interno (PI)', 'Valor Acumulado (R$)']
            df_det = df_det.sort_values(by=['Subgrupo Gerencial', 'Valor Acumulado (R$)'], ascending=[True, False])
            
            st.dataframe(
                df_det.style.format({'Valor Acumulado (R$)': 'R$ {:,.2f}'}),
                use_container_width=True
            )

# =============================================================================
# 5. PAINEL DE GRÁFICOS ANALÍTICOS
# =============================================================================

st.markdown("---")
st.subheader("📊 Visualização Gráfica e Comparações")

tab_g1, tab_g2, tab_g3 = st.tabs(["Distribuição por Grupo Totalizador", "Top 10 Unidades Gestoras", "Evolução Temporal"])

with tab_g1:
    resumo_pie = df_f.groupby('Grupo_Totalizador')['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
    fig_pie = px.pie(
        resumo_pie, 
        values='DetaCusto Acum. DH - Moeda Origem', 
        names='Grupo_Totalizador',
        title='Proporção dos Custos por Grupo Totalizador Gerencial',
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with tab_g2:
    top_ugs = df_f.groupby('UG Responsável Nome')['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
    top_ugs = top_ugs.sort_values(by='DetaCusto Acum. DH - Moeda Origem', ascending=True).tail(10)
    
    fig_bar = px.bar(
        top_ugs,
        x='DetaCusto Acum. DH - Moeda Origem',
        y='UG Responsável Nome',
        orientation='h',
        title='Top 10 Unidades Gestoras com Maior Custo Acumulado',
        labels={'DetaCusto Acum. DH - Moeda Origem': 'Valor (R$)', 'UG Responsável Nome': 'Unidade Gestora'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab_g3:
    if 'Mês Referência ACC (Código Completo) Sigla Completa (MMM/AAAA)' in df_f.columns:
        df_mes = df_f.groupby(['Mês Referência ACC (Código Completo)', 'Mês Referência ACC (Código Completo) Sigla Completa (MMM/AAAA)'])['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
        df_mes = df_mes.sort_values(by='Mês Referência ACC (Código Completo)')
        
        fig_line = px.line(
            df_mes,
            x='Mês Referência ACC (Código Completo) Sigla Completa (MMM/AAAA)',
            y='DetaCusto Acum. DH - Moeda Origem',
            title='Evolução Histórica Mensal dos Custos Liquidados',
            markers=True,
            labels={'DetaCusto Acum. DH - Moeda Origem': 'Custo Total (R$)', 'Mês Referência ACC (Código Completo) Sigla Completa (MMM/AAAA)': 'Mês/Ano'}
        )
        st.plotly_chart(fig_line, use_container_width=True)

# =============================================================================
# 6. TABELA ANALÍTICA DE LANÇAMENTOS E DOCUMENTOS HÁBEIS
# =============================================================================

st.markdown("---")
st.subheader("🔍 Consulta Detalhada de Lançamentos (Documentos Hábeis)")

with st.expander("Clique para visualizar os lançamentos individuais"):
    cols_exibir = [
        'Ano', 'UG Responsável Nome', 'Grupo_Totalizador', 'Conta_Gerencial',
        'Conta_Contabil_Formatada', 'PI_Formatado', 'Favorecido Doc. Nome',
        'Documento Hábil Número', 'DH - Observação Texto', 'DetaCusto Acum. DH - Moeda Origem'
    ]
    cols_existentes = [c for c in cols_exibir if c in df_f.columns]
    
    st.dataframe(
        df_f[cols_existentes].head(1000).style.format({'DetaCusto Acum. DH - Moeda Origem': 'R$ {:,.2f}'}),
        use_container_width=True
    )

# Download CSV
csv_export = df_f.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Exportar Base Filtrada (CSV)",
    data=csv_export,
    file_name="relatorio_custos_ufsm_filtrado.csv",
    mime="text/csv"
)
