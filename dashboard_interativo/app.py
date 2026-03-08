import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

# ──────────────────────────────────────────────────────────────
# Configuração da página
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard ML — Agro Brasil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# Caminhos dos CSVs consolidados
# ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_REGRESSAO = BASE_DIR / "analise_resultados" / "consolidado_regressao.csv"
CSV_CLASSIFICACAO = BASE_DIR / "analise_resultados" / "consolidado_classificacao.csv"

# ──────────────────────────────────────────────────────────────
# Constantes de métricas
# ──────────────────────────────────────────────────────────────
METRICAS_REGRESSAO = ["R2", "MAE", "RMSE"]
METRICAS_CLASSIFICACAO = ["Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]

# Métricas onde MAIOR = MELHOR (descendente)
METRICAS_MAIOR_MELHOR = {"R2", "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"}
# Métricas onde MENOR = MELHOR (ascendente)
METRICAS_MENOR_MELHOR = {"MAE", "RMSE"}

ORDEM_HORIZONTES = ["3 dias", "7 dias", "15 dias", "30 dias"]


# ──────────────────────────────────────────────────────────────
# Carregamento de dados (com cache)
# ──────────────────────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    """Carrega e retorna os DataFrames de regressão e classificação."""
    df_reg = pd.read_csv(CSV_REGRESSAO)
    df_clf = pd.read_csv(CSV_CLASSIFICACAO)

    # Limpar colunas vazias de cada tipo
    df_reg = df_reg.drop(columns=METRICAS_CLASSIFICACAO, errors="ignore")
    df_clf = df_clf.drop(columns=METRICAS_REGRESSAO, errors="ignore")

    # Coluna de identificação do sub-modelo
    df_reg["Identificador"] = (
        df_reg["modelo_nome"] + " | " + df_reg["dataset_nome"] + " | " + df_reg["ticker"]
    )
    df_clf["Identificador"] = (
        df_clf["modelo_nome"] + " | " + df_clf["dataset_nome"] + " | " + df_clf["ticker"]
    )

    # Ordenar horizontes corretamente
    df_reg["Horizonte"] = pd.Categorical(df_reg["Horizonte"], categories=ORDEM_HORIZONTES, ordered=True)
    df_clf["Horizonte"] = pd.Categorical(df_clf["Horizonte"], categories=ORDEM_HORIZONTES, ordered=True)

    return df_reg, df_clf


def formatar_metricas(df: pd.DataFrame, metricas: list) -> pd.DataFrame:
    """Formata métricas numéricas para 4 casas decimais na exibição."""
    df_fmt = df.copy()
    for col in metricas:
        if col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
    return df_fmt


# ──────────────────────────────────────────────────────────────
# Sidebar — Filtros
# ──────────────────────────────────────────────────────────────
def render_sidebar(df_reg: pd.DataFrame, df_clf: pd.DataFrame):
    """Renderiza a sidebar com todos os filtros e retorna as seleções."""
    st.sidebar.title("📊 Filtros")
    st.sidebar.markdown("---")

    # 1. Tipo de modelo
    tipo = st.sidebar.radio(
        "Tipo de Modelo",
        options=["Regressão", "Classificação"],
        index=0,
        horizontal=True,
    )

    df = df_reg if tipo == "Regressão" else df_clf
    metricas = METRICAS_REGRESSAO if tipo == "Regressão" else METRICAS_CLASSIFICACAO

    st.sidebar.markdown("---")

    # 2. Modelos
    modelos_disponiveis = sorted(df["modelo_nome"].unique())
    modelos_sel = st.sidebar.multiselect(
        "Modelos",
        options=modelos_disponiveis,
        default=modelos_disponiveis,
    )

    # 3. Datasets (estratégias de features)
    datasets_disponiveis = sorted(df["dataset_nome"].unique())
    datasets_sel = st.sidebar.multiselect(
        "Estratégia de Features (Dataset)",
        options=datasets_disponiveis,
        default=datasets_disponiveis,
    )

    # 4. Ativos (tickers)
    tickers_disponiveis = sorted(df["ticker"].unique())
    tickers_sel = st.sidebar.multiselect(
        "Ativos (Ticker)",
        options=tickers_disponiveis,
        default=tickers_disponiveis,
    )

    # 5. Horizonte de previsão
    horizontes_disponiveis = ORDEM_HORIZONTES
    horizontes_sel = st.sidebar.multiselect(
        "Horizonte de Previsão",
        options=horizontes_disponiveis,
        default=horizontes_disponiveis,
    )

    st.sidebar.markdown("---")

    # 6. Ordenação
    metrica_ordenar = st.sidebar.selectbox(
        "Ordenar por Métrica",
        options=metricas,
        index=0,
    )

    ordem_default = metrica_ordenar in METRICAS_MAIOR_MELHOR
    ordem_label = "Melhor primeiro (↓ desc)" if ordem_default else "Melhor primeiro (↑ asc)"

    ordem_desc = st.sidebar.toggle(
        "Ordem Descendente",
        value=ordem_default,
        help="Ative para maior→menor (ex: R², Accuracy). Desative para menor→maior (ex: MAE, RMSE).",
    )

    st.sidebar.markdown("---")

    # 7. Top N
    top_n = st.sidebar.slider(
        "Exibir Top N resultados",
        min_value=5,
        max_value=len(df),
        value=min(20, len(df)),
        step=5,
    )

    return {
        "tipo": tipo,
        "df": df,
        "metricas": metricas,
        "modelos": modelos_sel,
        "datasets": datasets_sel,
        "tickers": tickers_sel,
        "horizontes": horizontes_sel,
        "metrica_ordenar": metrica_ordenar,
        "ordem_desc": ordem_desc,
        "top_n": top_n,
    }


def aplicar_filtros(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    """Aplica os filtros selecionados ao DataFrame."""
    df_filtrado = df.copy()

    df_filtrado = df_filtrado[df_filtrado["modelo_nome"].isin(filtros["modelos"])]
    df_filtrado = df_filtrado[df_filtrado["dataset_nome"].isin(filtros["datasets"])]
    df_filtrado = df_filtrado[df_filtrado["ticker"].isin(filtros["tickers"])]
    df_filtrado = df_filtrado[df_filtrado["Horizonte"].isin(filtros["horizontes"])]

    # Ordenar pela métrica selecionada
    df_filtrado = df_filtrado.sort_values(
        by=filtros["metrica_ordenar"],
        ascending=not filtros["ordem_desc"],
    )

    # Aplicar Top N
    df_filtrado = df_filtrado.head(filtros["top_n"])

    return df_filtrado.reset_index(drop=True)


# ──────────────────────────────────────────────────────────────
# Área principal — Tabela
# ──────────────────────────────────────────────────────────────
def render_tabela(df_filtrado: pd.DataFrame, filtros: dict):
    """Renderiza a tabela de resultados filtrada."""
    metricas = filtros["metricas"]
    colunas_exibir = ["Identificador", "Horizonte"] + metricas

    st.subheader("📋 Tabela de Resultados")

    col_info1, col_info2, col_info3 = st.columns(3)
    col_info1.metric("Resultados exibidos", len(df_filtrado))
    col_info2.metric("Métrica de ordenação", filtros["metrica_ordenar"])
    col_info3.metric("Ordem", "Descendente ↓" if filtros["ordem_desc"] else "Ascendente ↑")

    if df_filtrado.empty:
        st.warning("Nenhum resultado encontrado com os filtros selecionados.")
        return

    df_show = df_filtrado[colunas_exibir].copy()
    df_show.index = range(1, len(df_show) + 1)
    df_show.index.name = "Rank"

    # Destacar a coluna de ordenação com barra de cor
    metrica_ord = filtros["metrica_ordenar"]
    melhor_maior = metrica_ord in METRICAS_MAIOR_MELHOR

    st.dataframe(
        df_show.style.background_gradient(
            subset=[metrica_ord],
            cmap="RdYlGn" if melhor_maior else "RdYlGn_r",
        ).format(
            {col: "{:.4f}" for col in metricas}
        ),
        use_container_width=True,
        height=min(45 * len(df_show) + 40, 600),
    )

    # Detalhes expandíveis
    with st.expander("🔍 Ver detalhes completos (todas as colunas)"):
        colunas_detalhe = ["modelo_nome", "dataset_nome", "ticker", "Horizonte"] + metricas
        df_detalhe = df_filtrado[colunas_detalhe].copy()
        df_detalhe.columns = ["Modelo", "Dataset", "Ticker", "Horizonte"] + metricas
        df_detalhe.index = range(1, len(df_detalhe) + 1)
        st.dataframe(
            df_detalhe.style.format({col: "{:.4f}" for col in metricas}),
            use_container_width=True,
        )


# ──────────────────────────────────────────────────────────────
# Área principal — Gráficos
# ──────────────────────────────────────────────────────────────
def render_graficos(df_filtrado: pd.DataFrame, filtros: dict):
    """Renderiza gráficos comparativos."""
    if df_filtrado.empty:
        return

    metricas = filtros["metricas"]
    metrica_principal = filtros["metrica_ordenar"]

    st.markdown("---")
    st.subheader("📊 Visualizações Comparativas")

    tab_bar, tab_heatmap, tab_evolucao, tab_box = st.tabs([
        "Ranking por Modelo",
        "Heatmap",
        "Evolução por Horizonte",
        "Distribuição (Box Plot)",
    ])

    # ── Tab 1: Bar chart — Ranking ──────────────────────────
    with tab_bar:
        st.markdown(f"**{metrica_principal}** por sub-modelo (Top {filtros['top_n']})")

        df_bar = df_filtrado.head(20).copy()
        df_bar["Label"] = df_bar["Identificador"] + " (" + df_bar["Horizonte"].astype(str) + ")"

        melhor_maior = metrica_principal in METRICAS_MAIOR_MELHOR
        cor_seq = "Greens" if melhor_maior else "Reds_r"

        fig_bar = px.bar(
            df_bar,
            x=metrica_principal,
            y="Label",
            orientation="h",
            color=metrica_principal,
            color_continuous_scale=cor_seq,
            labels={metrica_principal: metrica_principal, "Label": "Sub-modelo"},
        )
        fig_bar.update_layout(
            yaxis=dict(autorange="reversed" if filtros["ordem_desc"] else True),
            height=max(400, len(df_bar) * 30),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Tab 2: Heatmap — Modelo × Dataset ──────────────────
    with tab_heatmap:
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            metrica_heatmap = st.selectbox(
                "Métrica do Heatmap",
                options=metricas,
                index=0,
                key="heatmap_metrica",
            )
        with col_h2:
            horizonte_heatmap = st.selectbox(
                "Horizonte",
                options=[h for h in ORDEM_HORIZONTES if h in df_filtrado["Horizonte"].values],
                index=0,
                key="heatmap_horizonte",
            )

        df_heat = df_filtrado[df_filtrado["Horizonte"] == horizonte_heatmap].copy()

        if not df_heat.empty:
            # Pivot: linhas = modelo_nome, colunas = dataset_nome × ticker
            df_heat["Col"] = df_heat["dataset_nome"] + " | " + df_heat["ticker"]
            pivot = df_heat.pivot_table(
                index="modelo_nome",
                columns="Col",
                values=metrica_heatmap,
                aggfunc="mean",
            )
            melhor_maior_h = metrica_heatmap in METRICAS_MAIOR_MELHOR

            fig_heat = px.imshow(
                pivot,
                text_auto=".4f",
                color_continuous_scale="RdYlGn" if melhor_maior_h else "RdYlGn_r",
                labels=dict(x="Dataset | Ticker", y="Modelo", color=metrica_heatmap),
                aspect="auto",
            )
            fig_heat.update_layout(height=max(300, len(pivot) * 80))
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Sem dados para o horizonte selecionado.")

    # ── Tab 3: Evolução por horizonte (line chart) ──────────
    with tab_evolucao:
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            metrica_evolucao = st.selectbox(
                "Métrica",
                options=metricas,
                index=0,
                key="evolucao_metrica",
            )
        with col_e2:
            ticker_evolucao = st.selectbox(
                "Ativo (Ticker)",
                options=sorted(df_filtrado["ticker"].unique()),
                index=0,
                key="evolucao_ticker",
            )

        df_evo = df_filtrado[df_filtrado["ticker"] == ticker_evolucao].copy()
        df_evo["Horizonte_num"] = df_evo["Horizonte"].astype(str).str.extract(r"(\d+)").astype(int)
        df_evo = df_evo.sort_values("Horizonte_num")
        df_evo["Grupo"] = df_evo["modelo_nome"] + " | " + df_evo["dataset_nome"]

        if not df_evo.empty:
            fig_evo = px.line(
                df_evo,
                x="Horizonte",
                y=metrica_evolucao,
                color="Grupo",
                markers=True,
                labels={metrica_evolucao: metrica_evolucao, "Horizonte": "Horizonte de Previsão"},
            )
            fig_evo.update_layout(height=500)
            st.plotly_chart(fig_evo, use_container_width=True)
        else:
            st.info("Sem dados para o ticker selecionado.")

    # ── Tab 4: Box plot por modelo ──────────────────────────
    with tab_box:
        metrica_box = st.selectbox(
            "Métrica",
            options=metricas,
            index=0,
            key="box_metrica",
        )

        fig_box = px.box(
            df_filtrado,
            x="modelo_nome",
            y=metrica_box,
            color="dataset_nome",
            points="all",
            labels={
                metrica_box: metrica_box,
                "modelo_nome": "Modelo",
                "dataset_nome": "Dataset",
            },
        )
        fig_box.update_layout(height=500)
        st.plotly_chart(fig_box, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# Área principal — Resumo estatístico
# ──────────────────────────────────────────────────────────────
def render_resumo(df_filtrado: pd.DataFrame, filtros: dict):
    """Renderiza um resumo estatístico por modelo."""
    if df_filtrado.empty:
        return

    metricas = filtros["metricas"]

    st.markdown("---")
    st.subheader("📈 Resumo Estatístico por Modelo")

    agg_dict = {m: ["mean", "std", "min", "max"] for m in metricas}
    resumo = df_filtrado.groupby("modelo_nome").agg(agg_dict).round(4)
    resumo.columns = [f"{m} ({stat})" for m, stat in resumo.columns]

    st.dataframe(resumo, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# Área principal — Melhor modelo por cenário
# ──────────────────────────────────────────────────────────────
def render_melhores(df_completo: pd.DataFrame, filtros: dict):
    """Mostra o melhor modelo para cada combinação ticker × horizonte."""
    if df_completo.empty:
        return

    metricas = filtros["metricas"]
    metrica_alvo = filtros["metrica_ordenar"]
    melhor_maior = metrica_alvo in METRICAS_MAIOR_MELHOR

    st.markdown("---")
    st.subheader(f"🏆 Melhor Modelo por Cenário ({metrica_alvo})")

    if melhor_maior:
        idx = df_completo.groupby(["ticker", "Horizonte"], observed=True)[metrica_alvo].idxmax()
    else:
        idx = df_completo.groupby(["ticker", "Horizonte"], observed=True)[metrica_alvo].idxmin()

    melhores = df_completo.loc[idx, ["ticker", "Horizonte", "modelo_nome", "dataset_nome", metrica_alvo]]
    melhores = melhores.sort_values(["ticker", "Horizonte"])
    melhores.columns = ["Ticker", "Horizonte", "Modelo", "Dataset", metrica_alvo]
    melhores.index = range(1, len(melhores) + 1)

    st.dataframe(
        melhores.style.format({metrica_alvo: "{:.4f}"}),
        use_container_width=True,
    )


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────
def main():
    st.title("📊 Dashboard — Análise Comparativa de Modelos ML")
    st.caption("Agronegócio Brasil — Comparação de modelos de Machine Learning para previsão de ações")

    # Carregar dados
    df_reg, df_clf = carregar_dados()

    # Sidebar
    filtros = render_sidebar(df_reg, df_clf)

    # Aplicar filtros
    df_filtrado = aplicar_filtros(filtros["df"], filtros)

    # Renderizar seções
    render_tabela(df_filtrado, filtros)
    render_graficos(df_filtrado, filtros)
    render_resumo(df_filtrado, filtros)
    render_melhores(df_filtrado, filtros)

    # Rodapé
    st.markdown("---")
    st.caption("Dashboard gerado a partir dos CSVs consolidados em `analise_resultados/`.")


if __name__ == "__main__":
    main()
