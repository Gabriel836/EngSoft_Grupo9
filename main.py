import pandas as pd
from sqlalchemy import create_engine

# 1. Conecta ao banco
engine = create_engine("postgresql://joao:minhasenha123@localhost/hoteis_db")

# 2. Define as queries (são só textos com o SQL dentro)
query_recente = """
    SELECT
        hotel_id,
        DATE(datas) AS data,
        COUNT(*) AS leitos_ocupados
    FROM reservas
    WHERE datas >= CURRENT_DATE - INTERVAL '30 days'
      AND status = 'ativo'
    GROUP BY hotel_id, DATE(datas)
    ORDER BY hotel_id, data
"""

query_historico = """
    SELECT
        hotel_id,
        DATE(datas) AS data,
        EXTRACT(YEAR FROM datas) AS ano,
        COUNT(*) AS leitos_ocupados
    FROM reservas
    WHERE EXTRACT(MONTH FROM datas) = EXTRACT(MONTH FROM CURRENT_DATE)
      AND EXTRACT(YEAR FROM datas) < EXTRACT(YEAR FROM CURRENT_DATE)
      AND status = 'ativo'
    GROUP BY hotel_id, DATE(datas), ano
    ORDER BY hotel_id, ano, data
"""

# 3. Executa as queries e coloca o resultado em DataFrames
df_recente   = pd.read_sql(query_recente,   engine)
df_historico = pd.read_sql(query_historico, engine)

# Garante tipos corretos
df_recente['data'] = pd.to_datetime(df_recente['data'])
df_historico['data'] = pd.to_datetime(df_historico['data'])

# Extrai dia e mês para fazer o join com histórico
df_historico['mes'] = df_historico['data'].dt.month
df_historico['dia'] = df_historico['data'].dt.day

# --- Sinal 1: média recente (últimos 14 dias por hotel) ---
media_recente = (
    df_recente
    .sort_values('data')
    .groupby('hotel_id')
    .apply(lambda x: x.tail(14)['leitos_ocupados'].mean())
    .reset_index()
    .rename(columns={0: 'media_recente'})
)

# --- Sinal 2: média histórica para o período futuro (mesmo dia/mês) ---
# Para cada data futura que queremos prever, buscamos a média dos anos anteriores
datas_futuras = pd.date_range(start=pd.Timestamp.today(), periods=30)

previsoes = []
for data in datas_futuras:
    hist = df_historico[
        (df_historico['mes'] == data.month) &
        (df_historico['dia'] == data.day)
    ].groupby('hotel_id')['leitos_ocupados'].mean().reset_index()
    hist.columns = ['hotel_id', 'media_historica']
    hist['data_prevista'] = data
    previsoes.append(hist)

df_sazonalidade = pd.concat(previsoes)

# Junta os dois sinais
df_modelo = df_sazonalidade.merge(media_recente, on='hotel_id', how='left')

# Pesos: 60% histórico (sazonalidade), 40% recente (tendência atual)
PESO_HISTORICO = 0.60
PESO_RECENTE   = 0.40

df_modelo['previsao'] = (
    df_modelo['media_historica'] * PESO_HISTORICO +
    df_modelo['media_recente']   * PESO_RECENTE
).round(0)

# Intervalo de confiança simples (±15%)
df_modelo['previsao_min'] = (df_modelo['previsao'] * 0.85).round(0)
df_modelo['previsao_max'] = (df_modelo['previsao'] * 1.15).round(0)

resultado = df_modelo[[
    'hotel_id', 'data_prevista',
    'previsao', 'previsao_min', 'previsao_max',
    'media_historica', 'media_recente'
]].sort_values(['hotel_id', 'data_prevista'])

print(resultado.head(10))
# Exportar
resultado.to_csv('previsao_leitos.csv', index=False)

# Compara previsão com o que realmente aconteceu
df_validacao = df_recente.merge(
    df_modelo[df_modelo['data_prevista'].isin(df_recente['data'])],
    left_on=['hotel_id', 'data'],
    right_on=['hotel_id', 'data_prevista']
)

df_validacao['erro_pct'] = abs(
    df_validacao['leitos_ocupados'] - df_validacao['previsao']
) / df_validacao['leitos_ocupados'] * 100

print(df_validacao.groupby('hotel_id')['erro_pct'].mean().round(1))
# Erro < 15% → modelo confiável para planejamento operacional
