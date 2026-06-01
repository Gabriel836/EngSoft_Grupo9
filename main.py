import pandas as pd
from sqlalchemy import create_engine

# =====================================
# CONEXÃO COM O BANCO
# =====================================

engine = create_engine(
    "postgresql+psycopg2://joao:minhasenha123@localhost/hoteis_db"
)

# =====================================
# CONSULTA DOS DADOS RECENTES
# Últimos 30 dias
# =====================================

query_recente = """
    SELECT
        id_empresa,
        datas AS data,
        nro_leitos_ocupados
    FROM dados_empresa
    WHERE datas >= CURRENT_DATE - INTERVAL '30 days'
    ORDER BY id_empresa, data
"""

# =====================================
# CONSULTA DOS DADOS HISTÓRICOS
# Mesmo mês de anos anteriores
# =====================================

query_historico = """
    SELECT
        id_empresa,
        datas AS data,
        EXTRACT(YEAR FROM datas) AS ano,
        nro_leitos_ocupados
    FROM dados_empresa
    WHERE EXTRACT(MONTH FROM datas) = EXTRACT(MONTH FROM CURRENT_DATE)
      AND EXTRACT(YEAR FROM datas) < EXTRACT(YEAR FROM CURRENT_DATE)
    ORDER BY id_empresa, ano, data
"""

# =====================================
# CARREGA OS DADOS
# =====================================

df_recente = pd.read_sql(query_recente, engine)
df_historico = pd.read_sql(query_historico, engine)

# =====================================
# TRATAMENTO DE DATAS
# =====================================

df_recente["data"] = pd.to_datetime(df_recente["data"])
df_historico["data"] = pd.to_datetime(df_historico["data"])

df_historico["mes"] = df_historico["data"].dt.month
df_historico["dia"] = df_historico["data"].dt.day

# =====================================
# MÉDIA DOS ÚLTIMOS 14 DIAS
# =====================================

media_recente = (
    df_recente
    .sort_values("data")
    .groupby("id_empresa")
    .apply(
        lambda x: x.tail(14)["nro_leitos_ocupados"].mean(),
        include_groups=False
    )
    .reset_index()
    .rename(columns={0: "media_recente"})
)

# =====================================
# PREVISÃO DOS PRÓXIMOS 30 DIAS
# USANDO SAZONALIDADE
# =====================================

datas_futuras = pd.date_range(
    start=pd.Timestamp.today().normalize(),
    periods=30
)

previsoes = []

for data in datas_futuras:

    hist = (
        df_historico[
            (df_historico["mes"] == data.month) &
            (df_historico["dia"] == data.day)
        ]
        .groupby("id_empresa")["nro_leitos_ocupados"]
        .mean()
        .reset_index()
    )

    hist.columns = [
        "id_empresa",
        "media_historica"
    ]

    hist["data_prevista"] = data

    previsoes.append(hist)

df_sazonalidade = pd.concat(
    previsoes,
    ignore_index=True
)

# =====================================
# JUNTA MÉDIA RECENTE + HISTÓRICA
# =====================================

df_modelo = df_sazonalidade.merge(
    media_recente,
    on="id_empresa",
    how="left"
)

# =====================================
# PESOS DO MODELO
# =====================================

PESO_HISTORICO = 0.60
PESO_RECENTE = 0.40

df_modelo["previsao"] = (
    df_modelo["media_historica"] * PESO_HISTORICO +
    df_modelo["media_recente"] * PESO_RECENTE
).round(0)

# =====================================
# INTERVALO DE CONFIANÇA
# =====================================

df_modelo["previsao_min"] = (
    df_modelo["previsao"] * 0.85
).round(0)

df_modelo["previsao_max"] = (
    df_modelo["previsao"] * 1.15
).round(0)

# =====================================
# RESULTADO FINAL
# =====================================

resultado = df_modelo[
    [
        "id_empresa",
        "data_prevista",
        "previsao",
        "previsao_min",
        "previsao_max",
        "media_historica",
        "media_recente"
    ]
].sort_values(
    ["id_empresa", "data_prevista"]
)

print("\n=== PREVISÃO DOS PRÓXIMOS 30 DIAS ===\n")
print(resultado.head(20))

# =====================================
# EXPORTA PARA CSV
# =====================================

resultado.to_csv(
    "previsao_leitos.csv",
    index=False
)

print(
    "\nArquivo 'previsao_leitos.csv' gerado com sucesso."
)

# =====================================
# VALIDAÇÃO DO MODELO
# =====================================

df_validacao = df_recente.merge(
    df_modelo[
        df_modelo["data_prevista"].isin(
            df_recente["data"]
        )
    ],
    left_on=["id_empresa", "data"],
    right_on=["id_empresa", "data_prevista"],
    how="inner"
)

if len(df_validacao) > 0:

    df_validacao["erro_pct"] = (
        abs(
            df_validacao["nro_leitos_ocupados"] -
            df_validacao["previsao"]
        )
        /
        df_validacao["nro_leitos_ocupados"]
        * 100
    )

    print("\n=== ERRO MÉDIO POR EMPRESA ===\n")

    print(
        df_validacao
        .groupby("id_empresa")["erro_pct"]
        .mean()
        .round(2)
    )

else:
    print(
        "\nNão há dados suficientes para validação."
    )
