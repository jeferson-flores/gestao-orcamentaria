import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Relatório Gerencial de Custos - UFSM", 
    page_icon="📊",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 1. CARREGAMENTO E MAPEAMENTO AUTOMÁTICO (ND, PIS E UNIDADES/UGS)
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_e_mapear_dados(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo, sheet_name='Base')
    
    # Tratamento de Strings para evitar erros de busca
    cols_str = [
        'UG Responsável Nome', 'UG Beneficiada ACC Nome', 'PI Código PI', 
        'PI Nome', 'Natureza Despesa Detalhada Código', 'Natureza Despesa Detalhada Nome',
        'Favorecido Doc. Nome', 'Documento Hábil Número'
    ]
    for col in cols_str:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Mapeamento Gerencial de Contas e Totalizadores (Grupos 1 a 8)
    def mapear_estrutura_gerencial(row):
        nd_cod = str(row['Natureza Despesa Detalhada Código'])
        nd_nome = str(row['Natureza Despesa Detalhada Nome']).upper()
        pi_nome = str(row['PI Nome']).upper()
        texto = f"{nd_cod} {nd_nome} {pi_nome}"
        
        # Grupo 1: Infraestrutura e Manutenção Predial
        if any(k in texto for k in ["OBRA", "REFORMA", "BENFEITORIA", "ADEQUACAO", "CONSTRUCAO"]):
            return "1.1. Obras, Reformas e Adequações", "G-1.0 Total de Infraestrutura e Manutenção Predial"
        elif any(k in texto for k in ["ENERGIA", "AGUA", "GAS", "CONCESSIONARIA", "LUZ", "TELEFONIA"]):
            return "1.2. Concessionárias (Energia, Água, Gás)", "G-1.0 Total de Infraestrutura e Manutenção Predial"
        elif any(k in texto for k in ["MANUT", "CONSERVACAO", "PREDIAL", "REPARO"]) and not "TI" in texto:
            return "1.3. Manutenção Predial e Conservação", "G-1.0 Total de Infraestrutura e Manutenção Predial"
        elif any(k in texto for k in ["VERDE", "JARDIM", "PAISAGISMO", "LIMPEZA URBANA"]):
            return "1.4. Conservação de Áreas Verdes e Limpeza Urbana", "G-1.0 Total de Infraestrutura e Manutenção Predial"
            
        # Grupo 2: Serviços Terceirizados e Operacionais
        elif any(k in texto for k in ["VIGILANCIA", "PORTARIA", "SEGURANCA"]):
            return "2.1. Serviços de Vigilância e Portaria", "G-2.0 Total de Serviços Terceirizados e Operacionais"
        elif any(k in texto for k in ["HIGIENIZACAO", "LIMPEZA", "DESINFECCAO"]):
            return "2.2. Serviços de Limpeza e Higienização", "G-2.0 Total de Serviços Terceirizados e Operacionais"
        elif any(k in texto for k in ["MOTORISTA", "APOIO ADMIN", "SECRETARIA", "TRANSPORTE"]):
            return "2.3. Apoio Administrativo e Motoristas", "G-2.0 Total de Serviços Terceirizados e Operacionais"
        elif any(k in texto for k in ["RECEPCAO", "SERVICOS GERAIS", "COPA"]):
            return "2.4. Recepção e Serviços Gerais", "G-2.0 Total de Serviços Terceirizados e Operacionais"
            
        # Grupo 3: TI e Comunicação
        elif any(k in texto for k in ["TI", "INFORMATICA", "SOFTWARE", "SISTEMA", "NUVEM", "REDES", "COMPUTAD"]):
            if "LICENCA" in texto or "SOFTWARE" in texto:
                return "3.2. Licenças de Software, Sistemas e Nuvem", "G-3.0 Total de Tecnologia da Informação e Comunicação"
            elif "LINK" in texto or "INTERNET" in texto:
                return "3.3. Conectividade, Redes e Telefonia", "G-3.0 Total de Tecnologia da Informação e Comunicação"
            return "3.1. Equipamentos e Infraestrutura de TI", "G-3.0 Total de Tecnologia da Informação e Comunicação"
            
        # Grupo 4: Assistência Estudantil e RU
        elif any(k in texto for k in ["RU", "RESTAURANTE", "ALIMENTA", "MARMITA"]):
            return "4.1. Restaurante Universitário (RU) - Insumos e Operação", "G-4.0 Total de Assistência Estudantil e RU"
        elif any(k in texto for k in ["BOLSA", "ASSIST", "PERMANENCIA", "PRAE", "PNAES"]):
            return "4.2. Bolsas de Assistência Estudantil e Permanência", "G-4.0 Total de Assistência Estudantil e RU"
        elif any(k in texto for k in ["MORADIA", "CEU"]):
            return "4.3. Moradia Estudantil e Apoio ao Estudante", "G-4.0 Total de Assistência Estudantil e RU"
            
        # Grupo 5: Ensino, Pesquisa, Extensão e Unidades Especializadas
        elif any(k in texto for k in ["GRADUACAO", "POS-GRADUACAO", "PROAP", "CAPES", "CNPQ"]):
            return "5.1. Bolsas de Graduação, Pós e Extensão", "G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas"
        elif any(k in texto for k in ["LABORATORIO", "DIDATICO", "PESQUISA", "INSUMO"]):
            return "5.2. Material Didático, de Laboratório e Insumos de Pesquisa", "G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas"
        elif any(k in texto for k in ["EXTENSAO", "INOVACAO", "FIEX", "FOMENTO", "PROJETO"]):
            return "5.3. Fomento a Projetos de Pesquisa, Extensão e Inovação", "G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas"
        elif any(k in texto for k in ["HVU", "FAZENDA", "COLEGIO", "POLITECNICO", "CTISM"]):
            return "5.4. Unidades Especializadas (HVU, Fazenda, Colégios)", "G-5.0 Total de Ensino, Pesquisa, Extensão e Unidades Especializadas"

        # Grupo 6: Viagens e Eventos
        elif any(k in texto for k in ["DIARIA", "PASSAGEM", "VIAGEM"]):
            return "6.1. Passagens e Diárias (Nacionais e Internacionais)", "G-6.0 Total de Viagens, Eventos e Capacitação"
        elif any(k in texto for k in ["EVENTO", "CONGRESSO", "CULTURA"]):
            return "6.2. Eventos Acadêmicos, Culturais e Congressos", "G-6.0 Total de Viagens, Eventos e Capacitação"
        elif any(k in texto for k in ["CAPACITACAO", "TREINAMENTO", "CURSO"]):
            return "6.3. Capacitação e Desenvolvimento de Servidores", "G-6.0 Total de Viagens, Eventos e Capacitação"

        # Grupo 7: Equipamentos e Logística
        elif any(k in texto for k in ["EQUIPAMENTO", "MOBILIARIO", "MAQUINA"]):
            return "7.1. Aquisição de Equipamentos e Mobiliário", "G-7.0 Total de Equipamentos, Acervo e Logística"
        elif any(k in texto for k in ["BIBLIOTECA", "LIVRO", "PERIODICO"]):
            return "7.2. Biblioteca (Livros, Periódicos e Bases Científicas)", "G-7.0 Total de Equipamentos, Acervo e Logística"
        elif any(k in texto for k in ["FROTA", "COMBUSTIVEL", "VEICULO"]):
            return "7.3. Frota e Combustíveis", "G-7.0 Total de Equipamentos, Acervo e Logística"

        # Grupo 8: Despesas Operacionais Gerais
        elif any(k in texto for k in ["EXPEDIENTE", "SUPRIMENTO", "ESCRITORIO"]):
            return "8.1. Material de Expediente e Suprimentos", "G-8.0 Total de Despesas Operacionais e Encargos Institucionais"
        elif any(k in texto for k in ["ENCARGOS", "TAXA", "IMPOSTO", "TRIBUTO", "PIS", "PASEP"]):
            return "8.2. Encargos Institucionais e Impostos", "G-8.0 Total de Despesas Operacionais e Encargos Institucionais"
        else:
            return "8.3. Outras Despesas Operacionais", "G-8.0 Total de Despesas Operacionais e Encargos Institucionais"

    # Aplicação do Mapeamento
    res = df.apply(mapear_estrutura_gerencial, axis=1)
    df['Conta_Gerencial'] = [r[0] for r in res]
    df['Grupo_Gerencial'] = [r[1] for r in res]
    
    # Relações de Identificação
    df['PI_Descricao'] = df['PI Código PI'] + " - " + df['PI Nome']
    df['Conta_Contabil'] = df['Natureza Despesa Detalhada Código'] + " - " + df['Natureza Despesa Detalhada Nome']
    df['Ano'] = df['Mês Referência ACC (Código Completo)'].astype(str).str[:4]
    
    return df

# -----------------------------------------------------------------------------
# 2. INTERFACE E FILTROS LATERAIS
# -----------------------------------------------------------------------------
st.title("📊 Relatório Gerencial de Custos e Execução Orçamentária - UFSM")

df = carregar_e_mapear_dados("Liquida_mes_comp_2022-2026.xlsx")

st.sidebar.header("🔍 Filtros de Pesquisa")

# Filtro de Ano
anos_disponiveis = sorted(df['Ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano de Referência", anos_disponiveis, default=anos_disponiveis[-1:])

# Filtro de Unidades / UG
unidades_disponiveis = sorted(df['UG Responsável Nome'].unique())
unidades_selecionadas = st.sidebar.multiselect("Unidade Gestora (UG)", unidades_disponiveis)

# Aplicar Filtros
df_filtrado = df.copy()
if anos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Ano'].isin(anos_selecionados)]
if unidades_selecionadas:
    df_filtrado = df_filtrado[df_filtrado['UG Responsável Nome'].isin(unidades_selecionadas)]

# -----------------------------------------------------------------------------
# 3. PAINEL DE METRICAS (KPIS)
# -----------------------------------------------------------------------------
total_geral = df_filtrado['DetaCusto Acum. DH - Moeda Origem'].sum()
qtd_registros = len(df_filtrado)
qtd_unidades = df_filtrado['UG Responsável Nome'].nunique()
qtd_pis = df_filtrado['PI Código PI'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Custo Total Acumulado", f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("Lançamentos / Registros", f"{qtd_registros:,}".replace(",", "."))
col3.metric("Unidades Gestoras (UGs)", qtd_unidades)
col4.metric("Planos Internos (PIs)", qtd_pis)

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. ESTRUTURA EXPANSÍVEL E TOTALIZADORES
# -----------------------------------------------------------------------------
st.subheader("📑 Demonstrativo Gerencial por Grupo de Custos")

modo_visao = st.radio(
    "Modo de Exibição:", 
    ["Sintético (Apenas Totais dos Grupos)", "Analítico / Expansível (Totais com Botões '+' para Contas e PIs)"], 
    horizontal=True
)

resumo_grupos = df_filtrado.groupby('Grupo_Gerencial')['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
resumo_grupos.columns = ['Grupo Gerencial', 'Valor Total (R$)']
resumo_grupos['% do Total'] = (resumo_grupos['Valor Total (R$)'] / total_geral * 100) if total_geral > 0 else 0

if modo_visao == "Sintético (Apenas Totais dos Grupos)":
    st.dataframe(
        resumo_grupos.style.format({'Valor Total (R$)': 'R$ {:,.2f}', '% do Total': '{:.2f}%'}),
        use_container_width=True
    )
else:
    grupos = sorted(df_filtrado['Grupo_Gerencial'].unique())
    for grupo in grupos:
        df_grp = df_filtrado[df_filtrado['Grupo_Gerencial'] == grupo]
        val_grp = df_grp['DetaCusto Acum. DH - Moeda Origem'].sum()
        pct_grp = (val_grp / total_geral * 100) if total_geral > 0 else 0
        
        # Expansor com Sinal de "+" para abrir a árvore de contas e PIs
        with st.expander(f"➕ **{grupo}** | Total: **R$ {val_grp:,.2f}** ({pct_grp:.2f}%)".replace(",", "X").replace(".", ",").replace("X", ".")):
            
            df_detalhe = df_grp.groupby(['Conta_Gerencial', 'Conta_Contabil', 'PI_Descricao'])['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
            df_detalhe.columns = ['Subgrupo Gerencial', 'Conta Contábil (ND)', 'Plano Interno (PI)', 'Valor (R$)']
            
            st.dataframe(
                df_detalhe.style.format({'Valor (R$)': 'R$ {:,.2f}'}),
                use_container_width=True
            )

# -----------------------------------------------------------------------------
# 5. GRÁFICOS ANALÍTICOS
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📈 Análise Gráfica dos Custos")

tab_g1, tab_g2 = st.tabs(["Distribuição por Totalizador Gerencial", "Evolução Mensal"])

with tab_g1:
    fig_pie = px.pie(
        resumo_grupos, 
        values='Valor Total (R$)', 
        names='Grupo Gerencial',
        title='Participação Relativa de Cada Grupo Totalizador',
        hole=0.35
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with tab_g2:
    if 'Mês Referência ACC (Código Completo) Sigla Completa (MMM/AAAA)' in df_filtrado.columns:
        df_tempo = df_filtrado.groupby(['Mês Referência ACC (Código Completo)', 'Mês Referência ACC (Código Completo) Sigla Completa (MMM/AAAA)'])['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
        df_tempo = df_tempo.sort_values('Mês Referência ACC (Código Completo)')
        
        fig_line = px.line(
            df_tempo, 
            x='Mês Referência ACC (Código Completo) Sigla Completa (MMM/AAAA)', 
            y='DetaCusto Acum. DH - Moeda Origem',
            title='Evolução Histórica do Custo Acumulado',
            markers=True,
            labels={'DetaCusto Acum. DH - Moeda Origem': 'Custo (R$)', 'Mês Referência ACC (Código Completo) Sigla Completa (MMM/AAAA)': 'Mês'}
        )
        st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. EXPORTAÇÃO DE DADOS
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📥 Exportação de Dados")

csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download da Base Filtrada em CSV",
    data=csv_data,
    file_name="relatorio_gerencial_custos_ufsm.csv",
    mime="text/csv"
)
