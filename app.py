import streamlit as st
import pandas as pd
import plotly.express as px
import ssl
import urllib.request

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
@st.cache_data
def carregar_dados():
    try:
        # Desabilitar verificação SSL para evitar erro de certificado
        ssl._create_default_https_context = ssl._create_unverified_context
        df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")
        # Verificar se o DataFrame tem as colunas necessárias
        colunas_obrigatorias = ['ano', 'senioridade', 'contrato', 'tamanho_empresa', 'Salário']
        if df.empty or not all(col in df.columns for col in colunas_obrigatorias):
            raise ValueError("Dados inválidos ou colunas ausentes")
        return df
    except Exception as e:
        # Usar dados de exemplo como fallback
        df = pd.DataFrame({
            "ano": [2023, 2023, 2023, 2024, 2024, 2024],
            "senioridade": ["Junior", "Pleno", "Senior", "Junior", "Pleno", "Senior"],
            "contrato": ["CLT", "PJ", "CLT", "CLT", "PJ", "CLT"],
            "tamanho_empresa": ["Pequena", "Média", "Grande", "Pequena", "Média", "Grande"],
            "Salário": [3000, 6000, 10000, 3500, 6500, 11000]
        })
        return df

df = carregar_dados()

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# Verificar se o DataFrame tem dados
colunas_obrigatorias = ['ano', 'senioridade', 'contrato', 'tamanho_empresa']
if df.empty or not all(col in df.columns for col in colunas_obrigatorias):
    st.error("❌ Erro: Os dados não contêm as colunas esperadas.")
    st.stop()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['Salário'].mean()
    salario_maximo = df_filtrado['Salário'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["senioridade"].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"R$ {salario_medio:,.0f}")
col2.metric("Salário máximo", f"R$ {salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Senioridade mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('senioridade')['Salário'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        top_cargos.columns = ['senioridade', 'Salário']
        grafico_cargos = px.bar(
            top_cargos,
            x='Salário',
            y='senioridade',
            orientation='h',
            title="Top senioridades por salário médio",
            labels={'Salário': 'Média salarial anual (R$)', 'senioridade': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de senioridades.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='Salário',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'Salário': 'Faixa salarial (R$)', 'count': 'Quantidade'}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        contrato_contagem = df_filtrado['contrato'].value_counts().reset_index()
        contrato_contagem.columns = ['tipo_contrato', 'quantidade']
        grafico_contrato = px.pie(
            contrato_contagem,
            names='tipo_contrato',
            values='quantidade',
            title='Proporção dos tipos de contrato',
            hole=0.5
        )
        grafico_contrato.update_traces(textinfo='percent+label')
        grafico_contrato.update_layout(title_x=0.1)
        st.plotly_chart(grafico_contrato, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de contrato.")

with col_graf4:
    if not df_filtrado.empty:
        tamanho_media = df_filtrado.groupby('tamanho_empresa')['Salário'].mean().reset_index()
        grafico_tamanho = px.bar(
            tamanho_media,
            x='tamanho_empresa',
            y='Salário',
            title='Salário médio por tamanho da empresa',
            labels={'tamanho_empresa': 'Tamanho da Empresa', 'Salário': 'Salário Médio (R$)'}
        )
        grafico_tamanho.update_layout(title_x=0.1)
        st.plotly_chart(grafico_tamanho, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de tamanho de empresa.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
