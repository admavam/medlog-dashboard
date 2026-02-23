import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="MEDLOG Dashboard", layout="wide")

st.title("📊 Dashboard Online - MEDLOG")
st.markdown("Painel de desempenho, movimentação e evolução do estoque")

def limpar_moeda(valor):
    if pd.isnull(valor):
        return 0.0
    valor = re.sub(r"[R$\s\.]", "", str(valor))
    valor = valor.replace(",", ".")
    try:
        return float(valor)
    except:
        return 0.0

arquivo = st.file_uploader("📂 Envie o arquivo Excel (.xlsx)", type=["xlsx"])

if arquivo:

    df = pd.read_excel(arquivo)

    df["Custo Unitario"] = df["Custo Unitario"].apply(limpar_moeda)
    df["Custo Total"] = df["Custo Total"].apply(limpar_moeda)

    df["Mês_Ordenação"] = pd.to_datetime(df["Mês"], format="%b/%y", errors="coerce")
    df = df.sort_values("Mês_Ordenação")

    st.sidebar.header("🔎 Filtros")

    filtro_mes = st.sidebar.multiselect(
        "Mês",
        options=df["Mês"].unique(),
        default=df["Mês"].unique()
    )

    filtro_codigo = st.sidebar.multiselect(
        "Código",
        options=df["Codigo"].unique(),
        default=df["Codigo"].unique()
    )

    filtro_descricao = st.sidebar.multiselect(
        "Descrição",
        options=df["Descrição dos Produtos"].unique(),
        default=df["Descrição dos Produtos"].unique()
    )

    filtro_ncm = st.sidebar.multiselect(
        "NCM",
        options=df["NCM"].unique(),
        default=df["NCM"].unique()
    )

    df_filtrado = df[
        (df["Mês"].isin(filtro_mes)) &
        (df["Codigo"].isin(filtro_codigo)) &
        (df["Descrição dos Produtos"].isin(filtro_descricao)) &
        (df["NCM"].isin(filtro_ncm))
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Estoque Atual", int(df_filtrado["Estoque do mês"].sum()))
    col2.metric("Entradas", int(df_filtrado["Entradas"].sum()))
    col3.metric("Saídas", int(df_filtrado["Saídas"].sum()))
    col4.metric("Valor em Estoque (R$)", f"{df_filtrado['Custo Total'].sum():,.2f}")

    st.divider()

    estoque_mes = df_filtrado.groupby("Mês_Ordenação")["Estoque do mês"].sum().reset_index()
    fig1 = px.line(estoque_mes, x="Mês_Ordenação", y="Estoque do mês",
                   title="Evolução do Estoque")
    st.plotly_chart(fig1, use_container_width=True)

    movimentacao = df_filtrado.groupby("Mês_Ordenação")[["Entradas", "Saídas"]].sum().reset_index()
    fig2 = px.line(movimentacao, x="Mês_Ordenação", y=["Entradas", "Saídas"],
                   title="Entradas x Saídas")
    st.plotly_chart(fig2, use_container_width=True)

    top_produtos = (
        df_filtrado.groupby("Descrição dos Produtos")["Custo Total"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig3 = px.bar(top_produtos, x="Custo Total", y="Descrição dos Produtos",
                  orientation="h",
                  title="Top 10 Produtos por Valor")
    st.plotly_chart(fig3, use_container_width=True)

    giro = (
        df_filtrado.groupby("Descrição dos Produtos")["Saídas"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig4 = px.bar(giro, x="Descrição dos Produtos", y="Saídas",
                  title="Top 10 Giro de Estoque")
    st.plotly_chart(fig4, use_container_width=True)

    valor_estoque = df_filtrado.groupby("Mês_Ordenação")["Custo Total"].sum().reset_index()
    fig5 = px.area(valor_estoque, x="Mês_Ordenação", y="Custo Total",
                   title="Valor Total em Estoque por Mês")
    st.plotly_chart(fig5, use_container_width=True)

    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Baixar Dados Filtrados",
        csv,
        "dados_filtrados_medlog.csv",
        "text/csv"
    )

else:
    st.info("Aguardando envio do arquivo Excel.")
