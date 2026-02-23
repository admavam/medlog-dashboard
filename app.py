# =============================================
# DASHBOARD ONLINE - MEDLOG
# PRONTO PARA HOSPEDAGEM (STREAMLIT CLOUD)
# =============================================

"""
INSTRUÇÕES PARA PUBLICAR ONLINE (GRÁTIS)

1) Crie uma conta em:
   https://streamlit.io/cloud

2) Crie um repositório no GitHub contendo:
   - este arquivo: app.py
   - seu Excel padrão (opcional)
   - arquivo requirements.txt (modelo abaixo)

3) requirements.txt deve conter:

   streamlit
   pandas
   plotly
   openpyxl

4) No Streamlit Cloud:
   - Clique em "New App"
   - Conecte seu GitHub
   - Selecione o repositório
   - Arquivo principal: app.py

5) Clique em Deploy.

Você receberá um LINK público como:

   https://medlog-dashboard.streamlit.app

"""

import streamlit as st
import pandas as pd
import plotly.express as px
import re

# =============================================
# CONFIGURAÇÃO
# =============================================

st.set_page_config(page_title="MEDLOG Dashboard Online", layout="wide")

st.title("📊 Dashboard Online - MEDLOG")
st.markdown("Painel de desempenho, movimentação e evolução do estoque")

# =============================================
# FUNÇÃO UTILITÁRIA
# =============================================

def limpar_moeda(valor):
    if pd.isnull(valor):
        return 0.0
    valor = re.sub(r"[R$\s\.]", "", str(valor))
    valor = valor.replace(",", ".")
    try:
        return float(valor)
    except:
        return 0.0

# =============================================
# UPLOAD
# =============================================

arquivo = st.file_uploader("📂 Envie o arquivo Excel (.xlsx)", type=["xlsx"])

if arquivo:

    df = pd.read_excel(arquivo)

    # =============================================
    # NORMALIZAÇÃO DOS NOMES DAS COLUNAS
    # =============================================
    import unicodedata

    def normalizar_coluna(col):
        col = str(col).strip()
        col = unicodedata.normalize("NFKD", col).encode("ASCII", "ignore").decode("ASCII")
        return col.lower()

    df.columns = [normalizar_coluna(c) for c in df.columns]

    # Mapeamento flexível de colunas esperadas
    mapa_colunas = {
        "mes": "mes",
        "codigo": "codigo",
        "descricao dos produtos": "descricao dos produtos",
        "custo unitario": "custo unitario",
        "ncm": "ncm",
        "estoque do mes anterior": "estoque do mes anterior",
        "entradas": "entradas",
        "saidas": "saidas",
        "estoque do mes": "estoque do mes",
        "custo total": "custo total",
    }

    colunas_necessarias = list(mapa_colunas.values())

    colunas_necessarias = [
        "Mês",
        "Codigo",
        "Descrição dos Produtos",
        "Custo Unitario",
        "NCM",
        "Estoque do mês anterior",
        "Entradas",
        "Saídas",
        "Estoque do mês",
        "Custo Total",
    ]

    faltantes = [c for c in colunas_necessarias if c not in df.columns]
    if faltantes:
        st.error(f"Colunas ausentes: {faltantes}")
        st.stop()

    df["custo unitario"] = df["custo unitario"].apply(limpar_moeda)
    df["custo total"] = df["custo total"].apply(limpar_moeda)

    df["mes_ordenacao"] = pd.to_datetime(df["mes"], format="%b/%y", errors="coerce")
    df = df.sort_values("mes_ordenacao")

    # =============================================
    # FILTROS
    # =============================================

    st.sidebar.header("🔎 Filtros")

    filtro_mes = st.sidebar.multiselect(
        "Mês",
        options=df["mes"].unique(),
        default=df["mes"].unique()
    )

    filtro_codigo = st.sidebar.multiselect(
        "Código",
        options=df["codigo"].unique(),
        default=df["codigo"].unique()
    )

    filtro_descricao = st.sidebar.multiselect(
        "Descrição",
        options=df["descricao dos produtos"].unique(),
        default=df["descricao dos produtos"].unique()
    )

    filtro_ncm = st.sidebar.multiselect(
        "NCM",
        options=df["ncm"].unique(),
        default=df["ncm"].unique()
    )

    df_filtrado = df[
        (df["mes"].isin(filtro_mes)) &
        (df["codigo"].isin(filtro_codigo)) &
        (df["descricao dos produtos"].isin(filtro_descricao)) &
        (df["ncm"].isin(filtro_ncm))
    ]

    # =============================================
    # KPIs
    # =============================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Estoque Atual", int(df_filtrado["estoque do mes"].sum()))
    col2.metric("Entradas", int(df_filtrado["entradas"].sum()))
    col3.metric("Saídas", int(df_filtrado["saidas"].sum()))
    col4.metric("Valor em Estoque (R$)", f"{df_filtrado['custo total'].sum():,.2f}")

    st.divider()

    # =============================================
    # GRÁFICOS
    # =============================================

    estoque_mes = df_filtrado.groupby("mes_ordenacao")["Estoque do mês"].sum().reset_index()
    fig1 = px.line(estoque_mes, x="mes_ordenacao", y="Estoque do mês",
                   title="Evolução do Estoque")
    st.plotly_chart(fig1, use_container_width=True)

    movimentacao = df_filtrado.groupby("mes_ordenacao")[["entradas", "saidas"]].sum().reset_index()
    fig2 = px.line(movimentacao, x="mes_ordenacao", y=["Entradas", "Saídas"],
                   title="Entradas x Saídas")
    st.plotly_chart(fig2, use_container_width=True)

    top_produtos = (
        df_filtrado.groupby("Descrição dos Produtos")["custo total"]
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

    valor_estoque = df_filtrado.groupby("mes_ordenacao")["custo total"].sum().reset_index()
    fig5 = px.area(valor_estoque, x="mes_ordenacao", y="Custo Total",
                   title="Valor Total em Estoque por Mês")
    st.plotly_chart(fig5, use_container_width=True)

    st.divider()

    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Baixar Dados Filtrados",
        csv,
        "dados_filtrados_medlog.csv",
        "text/csv"
    )

else:
    st.info("Aguardando envio do arquivo Excel para gerar o dashboard.")
