import pandas as pd
import psycopg2
import io

# Caminho local do CSV
csv_path = r"C:\Users\GuilhermeCostaProenç\OneDrive - You On\Área de Trabalho\You_intelligence_062025\data\scripts\Tabela de Municipios TOM.csv"

# Conexão com o banco
conn = psycopg2.connect(
    host="psql-database-mapping.postgres.database.azure.com",
    dbname="db_youon_intelligence",
    user="guilherme@psql-database-mapping",
    password="SenhaForteAqui",
    port=5432,
    sslmode="require"
)

# Leitura e limpeza do CSV
df = pd.read_csv(csv_path, encoding='latin1', sep=';')
df = df.rename(columns={
    df.columns[1]: 'id_ibge',
    df.columns[3]: 'nome',
    df.columns[4]: 'uf'
})
df = df[['id_ibge', 'nome', 'uf']].copy()
df['id_ibge'] = df['id_ibge'].astype(int)
df['nome'] = df['nome'].str.title().str.strip()
df['uf'] = df['uf'].str.upper().str.strip()

# Convertendo para CSV em memória
output = io.StringIO()
df.to_csv(output, sep='\t', header=False, index=False)
output.seek(0)

# Inserção via COPY
with conn:
    with conn.cursor() as cur:
        cur.execute("SET search_path TO intel_lead")
        cur.copy_from(output, 'municipio', sep='\t', columns=('id', 'nome', 'uf'))

print("✅ Municípios inseridos com sucesso.")
