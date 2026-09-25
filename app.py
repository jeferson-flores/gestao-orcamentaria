import streamlit as st
import pandas as pd

# Preservando toda a lógica e estrutura da versão anterior...

# -----------------------------------------------------------------------------
# MAPEAMENTO DOS GRUPOS TOTALIZADORES (ADICIONADO SOBRE A VERSÃO ANTERIOR)
# -----------------------------------------------------------------------------
MAPEAMENTO_TOTALIZADORES = {
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
    '8.3': 'G-8.0 Total de Despesas Operacionais e Encargos Institucionais',
}

# Criando a coluna de Grupo Totalizador no DataFrame
df['Grupo_Totalizador'] = df['Conta_Gerencial'].str[:3].map(MAPEAMENTO_TOTALIZADORES).fillna('G-8.0 Total de Despesas Operacionais e Encargos Institucionais')

# -----------------------------------------------------------------------------
# BLOCO DE RELATÓRIO COM TOTALIZADORES E EXPANSÃO (+)
# -----------------------------------------------------------------------------
st.subheader("📑 Demonstrativo Gerencial com Totalizadores")

opcao_relatorio = st.radio(
    "Visualização do Relatório:",
    ["Apenas Totais dos Grupos (Sintético)", "Expansível por Grupo (+ / -) (Analítico)"],
    horizontal=True
)

total_geral = df_filtrado['DetaCusto Acum. DH - Moeda Origem'].sum()

if opcao_relatorio == "Apenas Totais dos Grupos (Sintético)":
    # Visão Sintética
    df_sintetico = df_filtrado.groupby('Grupo_Totalizador')['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
    df_sintetico.columns = ['Grupo Totalizador', 'Valor Total (R$)']
    df_sintetico['% Participação'] = (df_sintetico['Valor Total (R$)'] / total_geral * 100) if total_geral > 0 else 0
    
    st.dataframe(
        df_sintetico.style.format({'Valor Total (R$)': 'R$ {:,.2f}', '% Participação': '{:.2f}%'}),
        use_container_width=True
    )

else:
    # Visão Expansível com botões "+"
    grupos_ordenados = sorted(df_filtrado['Grupo_Totalizador'].unique())
    
    for grupo in grupos_ordenados:
        df_grupo = df_filtrado[df_filtrado['Grupo_Totalizador'] == grupo]
        total_grupo = df_grupo['DetaCusto Acum. DH - Moeda Origem'].sum()
        pct_grupo = (total_grupo / total_geral * 100) if total_geral > 0 else 0
        
        # Botão "+" / Expansor com o Totalizador
        with st.expander(f"➕ **{grupo}** — Total: **R$ {total_grupo:,.2f}** ({pct_grupo:.2f}%)".replace(",", "X").replace(".", ",").replace("X", ".")):
            
            # Detalhamento das Contas Contábeis / NDs dentro do Grupo
            df_contas = df_grupo.groupby(['Conta_Gerencial', 'Natureza Despesa Detalhada Código', 'Natureza Despesa Detalhada Nome'])['DetaCusto Acum. DH - Moeda Origem'].sum().reset_index()
            df_contas.columns = ['Conta Gerencial', 'Código ND', 'Nome da Conta Contábil / ND', 'Valor (R$)']
            
            st.dataframe(
                df_contas.style.format({'Valor (R$)': 'R$ {:,.2f}'}),
                use_container_width=True
            )
