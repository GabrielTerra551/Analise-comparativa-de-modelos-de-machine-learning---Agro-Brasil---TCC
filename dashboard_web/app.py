from __future__ import annotations

import os
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_REGRESSAO = BASE_DIR / "analise_resultados" / "consolidado_regressao.csv"
CSV_CLASSIFICACAO = BASE_DIR / "analise_resultados" / "consolidado_classificacao.csv"

METRICAS_REGRESSAO = ["R2", "MAE", "RMSE"]
METRICAS_CLASSIFICACAO = ["Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]
METRICAS_MAIOR_MELHOR = {"R2", "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"}
ORDEM_HORIZONTES = ["3 dias", "7 dias", "15 dias", "30 dias"]
TIPOS_VALIDOS = {"RegressÃ£o", "ClassificaÃ§Ã£o"}

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("DASHBOARD_WEB_SECRET_KEY", "dashboard-web-dev-secret")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)


def _senha_dashboard() -> str:
    return os.environ.get("DASHBOARD_WEB_PASSWORD", "agrobrasil123")


def _esta_autenticado() -> bool:
    return session.get("dashboard_auth") is True


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _esta_autenticado():
            if request.path.startswith("/api/"):
                return jsonify({"error": "NÃ£o autenticado."}), 401
            return redirect(url_for("index"))
        return view_func(*args, **kwargs)

    return wrapper


@lru_cache(maxsize=1)
def carregar_dados() -> tuple[pd.DataFrame, pd.DataFrame]:
    df_reg = pd.read_csv(CSV_REGRESSAO)
    df_clf = pd.read_csv(CSV_CLASSIFICACAO)

    df_reg = _preparar_dataframe(df_reg, METRICAS_CLASSIFICACAO)
    df_clf = _preparar_dataframe(df_clf, METRICAS_REGRESSAO)

    return df_reg, df_clf



def _preparar_dataframe(df: pd.DataFrame, metricas_remover: list[str]) -> pd.DataFrame:
    df = df.copy()
    df = df.drop(columns=metricas_remover, errors="ignore")

    metricas_presentes = [
        *[m for m in METRICAS_REGRESSAO if m in df.columns],
        *[m for m in METRICAS_CLASSIFICACAO if m in df.columns],
    ]
    for coluna in metricas_presentes:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

    df["Identificador"] = df["modelo_nome"] + " | " + df["dataset_nome"] + " | " + df["ticker"]
    df["Horizonte"] = pd.Categorical(df["Horizonte"], categories=ORDEM_HORIZONTES, ordered=True)

    return df



def _configuracao_tipo(tipo: str) -> tuple[pd.DataFrame, list[str]]:
    df_reg, df_clf = carregar_dados()
    tipo_normalizado = tipo if tipo in TIPOS_VALIDOS else "RegressÃ£o"
    if tipo_normalizado == "ClassificaÃ§Ã£o":
        return df_clf, METRICAS_CLASSIFICACAO
    return df_reg, METRICAS_REGRESSAO



def _defaults_para_tipo(tipo: str) -> dict[str, Any]:
    df, metricas = _configuracao_tipo(tipo)
    metrica_ordenar = metricas[0]
    return {
        "tipo": tipo if tipo in TIPOS_VALIDOS else "RegressÃ£o",
        "modelos": sorted(df["modelo_nome"].dropna().unique().tolist()),
        "datasets": sorted(df["dataset_nome"].dropna().unique().tolist()),
        "tickers": sorted(df["ticker"].dropna().unique().tolist()),
        "horizontes": [h for h in ORDEM_HORIZONTES if h in df["Horizonte"].astype(str).unique()],
        "metrica_ordenar": metrica_ordenar,
        "ordem_desc": metrica_ordenar in METRICAS_MAIOR_MELHOR,
        "top_n": min(20, len(df)),
    }



def _metadata_tipo(tipo: str) -> dict[str, Any]:
    df, metricas = _configuracao_tipo(tipo)
    defaults = _defaults_para_tipo(tipo)
    top_n_min = 5 if len(df) >= 5 else 1
    return {
        "tipo": defaults["tipo"],
        "metricas": metricas,
        "options": {
            "modelos": defaults["modelos"],
            "datasets": defaults["datasets"],
            "tickers": defaults["tickers"],
            "horizontes": defaults["horizontes"],
            "metricas": metricas,
            "top_n_min": top_n_min,
            "top_n_max": int(len(df)),
        },
        "defaults": defaults,
    }



def _valor_json(valor: Any) -> Any:
    if pd.isna(valor):
        return None
    if isinstance(valor, pd.Timestamp):
        return valor.isoformat()
    return valor.item() if hasattr(valor, "item") else valor



def _registros(df: pd.DataFrame, colunas: list[str]) -> list[dict[str, Any]]:
    if df.empty:
        return []

    registros = []
    for _, linha in df[colunas].iterrows():
        item: dict[str, Any] = {}
        for coluna in colunas:
            valor = linha[coluna]
            if coluna == "Horizonte" and valor is not None:
                item[coluna] = str(valor)
            else:
                item[coluna] = _valor_json(valor)
        registros.append(item)
    return registros



def _parse_filtros(payload: dict[str, Any]) -> tuple[dict[str, Any], pd.DataFrame, list[str]]:
    tipo = payload.get("tipo", "RegressÃ£o")
    df, metricas = _configuracao_tipo(tipo)
    defaults = _defaults_para_tipo(tipo)

    filtros = {
        "tipo": defaults["tipo"],
        "modelos": payload["modelos"] if "modelos" in payload else defaults["modelos"],
        "datasets": payload["datasets"] if "datasets" in payload else defaults["datasets"],
        "tickers": payload["tickers"] if "tickers" in payload else defaults["tickers"],
        "horizontes": payload["horizontes"] if "horizontes" in payload else defaults["horizontes"],
        "metrica_ordenar": payload.get("metrica_ordenar", defaults["metrica_ordenar"]),
        "ordem_desc": bool(payload.get("ordem_desc", defaults["ordem_desc"])),
        "top_n": int(payload.get("top_n", defaults["top_n"])),
    }

    if filtros["metrica_ordenar"] not in metricas:
        filtros["metrica_ordenar"] = defaults["metrica_ordenar"]

    filtros["top_n"] = max(1, min(filtros["top_n"], len(df))) if len(df) else 1

    return filtros, df, metricas



def aplicar_filtros(df: pd.DataFrame, filtros: dict[str, Any]) -> pd.DataFrame:
    df_filtrado = df.copy()
    df_filtrado = df_filtrado[df_filtrado["modelo_nome"].isin(filtros["modelos"])]
    df_filtrado = df_filtrado[df_filtrado["dataset_nome"].isin(filtros["datasets"])]
    df_filtrado = df_filtrado[df_filtrado["ticker"].isin(filtros["tickers"])]
    df_filtrado = df_filtrado[df_filtrado["Horizonte"].astype(str).isin(filtros["horizontes"])]
    df_filtrado = df_filtrado.sort_values(
        by=filtros["metrica_ordenar"],
        ascending=not filtros["ordem_desc"],
    )
    df_filtrado = df_filtrado.head(filtros["top_n"])
    return df_filtrado.reset_index(drop=True)



def _opcoes_graficos(df_filtrado: pd.DataFrame, metricas: list[str], filtros: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    horizontes_disponiveis = [
        h for h in ORDEM_HORIZONTES if h in df_filtrado["Horizonte"].astype(str).unique().tolist()
    ]
    tickers_disponiveis = sorted(df_filtrado["ticker"].dropna().unique().tolist())

    heatmap_metric = payload.get("heatmap_metric", filtros["metrica_ordenar"])
    if heatmap_metric not in metricas:
        heatmap_metric = metricas[0]

    heatmap_horizon = payload.get("heatmap_horizon")
    if heatmap_horizon not in horizontes_disponiveis:
        heatmap_horizon = horizontes_disponiveis[0] if horizontes_disponiveis else None

    evolution_metric = payload.get("evolution_metric", filtros["metrica_ordenar"])
    if evolution_metric not in metricas:
        evolution_metric = metricas[0]

    evolution_ticker = payload.get("evolution_ticker")
    if evolution_ticker not in tickers_disponiveis:
        evolution_ticker = tickers_disponiveis[0] if tickers_disponiveis else None

    box_metric = payload.get("box_metric", filtros["metrica_ordenar"])
    if box_metric not in metricas:
        box_metric = metricas[0]

    return {
        "available": {
            "heatmap_metrics": metricas,
            "heatmap_horizons": horizontes_disponiveis,
            "evolution_metrics": metricas,
            "evolution_tickers": tickers_disponiveis,
            "box_metrics": metricas,
        },
        "selected": {
            "heatmap_metric": heatmap_metric,
            "heatmap_horizon": heatmap_horizon,
            "evolution_metric": evolution_metric,
            "evolution_ticker": evolution_ticker,
            "box_metric": box_metric,
        },
    }



def _grafico_ranking(df_filtrado: pd.DataFrame, filtros: dict[str, Any]) -> dict[str, Any]:
    metrica = filtros["metrica_ordenar"]
    df_bar = df_filtrado.head(20).copy()
    if df_bar.empty:
        return {"records": []}
    df_bar["Label"] = df_bar["Identificador"] + " (" + df_bar["Horizonte"].astype(str) + ")"
    return {
        "records": _registros(df_bar, ["Label", metrica]),
        "metric": metrica,
        "descending": filtros["ordem_desc"],
        "higher_is_better": metrica in METRICAS_MAIOR_MELHOR,
    }



def _grafico_heatmap(df_filtrado: pd.DataFrame, chart_controls: dict[str, Any]) -> dict[str, Any]:
    horizonte = chart_controls["selected"]["heatmap_horizon"]
    metrica = chart_controls["selected"]["heatmap_metric"]
    if not horizonte:
        return {"x": [], "y": [], "z": [], "metric": metrica, "horizon": None}

    df_heat = df_filtrado[df_filtrado["Horizonte"].astype(str) == horizonte].copy()
    if df_heat.empty:
        return {"x": [], "y": [], "z": [], "metric": metrica, "horizon": horizonte}

    df_heat["Col"] = df_heat["dataset_nome"] + " | " + df_heat["ticker"]
    pivot = df_heat.pivot_table(index="modelo_nome", columns="Col", values=metrica, aggfunc="mean")
    pivot = pivot.sort_index(axis=0).sort_index(axis=1)

    return {
        "x": [str(col) for col in pivot.columns.tolist()],
        "y": [str(idx) for idx in pivot.index.tolist()],
        "z": [[_valor_json(valor) for valor in linha] for linha in pivot.to_numpy().tolist()],
        "metric": metrica,
        "horizon": horizonte,
        "higher_is_better": metrica in METRICAS_MAIOR_MELHOR,
    }



def _grafico_evolucao(df_filtrado: pd.DataFrame, chart_controls: dict[str, Any]) -> dict[str, Any]:
    ticker = chart_controls["selected"]["evolution_ticker"]
    metrica = chart_controls["selected"]["evolution_metric"]
    if not ticker:
        return {"records": [], "metric": metrica, "ticker": None}

    df_evo = df_filtrado[df_filtrado["ticker"] == ticker].copy()
    if df_evo.empty:
        return {"records": [], "metric": metrica, "ticker": ticker}

    df_evo["Horizonte_num"] = df_evo["Horizonte"].astype(str).str.extract(r"(\d+)").astype(int)
    df_evo = df_evo.sort_values("Horizonte_num")
    df_evo["Grupo"] = df_evo["modelo_nome"] + " | " + df_evo["dataset_nome"]

    return {
        "records": _registros(df_evo, ["Horizonte", "Grupo", metrica]),
        "metric": metrica,
        "ticker": ticker,
    }



def _grafico_box(df_filtrado: pd.DataFrame, chart_controls: dict[str, Any]) -> dict[str, Any]:
    metrica = chart_controls["selected"]["box_metric"]
    return {
        "records": _registros(df_filtrado, ["modelo_nome", "dataset_nome", metrica]),
        "metric": metrica,
    }



def _resumo_estatistico(df_filtrado: pd.DataFrame, metricas: list[str]) -> list[dict[str, Any]]:
    if df_filtrado.empty:
        return []

    resumo = df_filtrado.groupby("modelo_nome")[metricas].agg(["mean", "std", "min", "max"]).round(4)
    registros: list[dict[str, Any]] = []
    for modelo, linha in resumo.iterrows():
        item: dict[str, Any] = {"modelo_nome": modelo}
        for metrica in metricas:
            for stat in ["mean", "std", "min", "max"]:
                item[f"{metrica} ({stat})"] = _valor_json(linha[(metrica, stat)])
        registros.append(item)
    return registros



def _melhores_por_cenario(df_filtrado: pd.DataFrame, filtros: dict[str, Any]) -> list[dict[str, Any]]:
    if df_filtrado.empty:
        return []

    metrica = filtros["metrica_ordenar"]
    melhor_maior = metrica in METRICAS_MAIOR_MELHOR
    agrupado = df_filtrado.groupby(["ticker", "Horizonte"], observed=True)[metrica]
    idx = agrupado.idxmax() if melhor_maior else agrupado.idxmin()

    melhores = df_filtrado.loc[idx, ["ticker", "Horizonte", "modelo_nome", "dataset_nome", metrica]].copy()
    melhores = melhores.sort_values(["ticker", "Horizonte"])
    melhores.columns = ["Ticker", "Horizonte", "Modelo", "Dataset", metrica]
    return _registros(melhores, ["Ticker", "Horizonte", "Modelo", "Dataset", metrica])


@app.get("/")
def index():
    if _esta_autenticado():
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.post("/login")
def login():
    senha = request.form.get("password", "")
    if senha == _senha_dashboard():
        session["dashboard_auth"] = True
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Senha invÃ¡lida. Tente novamente."), 401


@app.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.get("/api/metadata")
@login_required
def api_metadata():
    tipo = request.args.get("tipo", "RegressÃ£o")
    return jsonify(_metadata_tipo(tipo))


@app.post("/api/dashboard-data")
@login_required
def api_dashboard_data():
    payload = request.get_json(silent=True) or {}
    filtros, df_base, metricas = _parse_filtros(payload)
    df_filtrado = aplicar_filtros(df_base, filtros)
    chart_controls = _opcoes_graficos(df_filtrado, metricas, filtros, payload)

    colunas_tabela = ["Identificador", "Horizonte", *metricas]
    colunas_detalhe = ["modelo_nome", "dataset_nome", "ticker", "Horizonte", *metricas]

    resposta = {
        "filters": filtros,
        "options": _metadata_tipo(filtros["tipo"])["options"],
        "cards": {
            "results_count": int(len(df_filtrado)),
            "metric": filtros["metrica_ordenar"],
            "order": "Descendente â†“" if filtros["ordem_desc"] else "Ascendente â†‘",
        },
        "table": {
            "columns": colunas_tabela,
            "metricas": metricas,
            "sort_metric": filtros["metrica_ordenar"],
            "higher_is_better": filtros["metrica_ordenar"] in METRICAS_MAIOR_MELHOR,
            "rows": _registros(df_filtrado, colunas_tabela),
        },
        "details": {
            "columns": ["Modelo", "Dataset", "Ticker", "Horizonte", *metricas],
            "rows": [
                {
                    "Modelo": item["modelo_nome"],
                    "Dataset": item["dataset_nome"],
                    "Ticker": item["ticker"],
                    "Horizonte": item["Horizonte"],
                    **{metrica: item.get(metrica) for metrica in metricas},
                }
                for item in _registros(df_filtrado, colunas_detalhe)
            ],
        },
        "charts": {
            "controls": chart_controls,
            "ranking": _grafico_ranking(df_filtrado, filtros),
            "heatmap": _grafico_heatmap(df_filtrado, chart_controls),
            "evolution": _grafico_evolucao(df_filtrado, chart_controls),
            "box": _grafico_box(df_filtrado, chart_controls),
        },
        "summary": {
            "columns": ["modelo_nome", *[f"{metrica} ({stat})" for metrica in metricas for stat in ["mean", "std", "min", "max"]]],
            "rows": _resumo_estatistico(df_filtrado, metricas),
        },
        "best_by_scenario": {
            "metric": filtros["metrica_ordenar"],
            "rows": _melhores_por_cenario(df_filtrado, filtros),
        },
    }
    return jsonify(resposta)


# if __name__ == "__main__":
#     # O debug=True vai te mostrar o erro exato no terminal e no navegador
#     app.run(host='127.0.0.1', port=8000, debug=True)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000)