import pandas as pd
import psycopg2
from io import StringIO

# ============================
# CONFIGURAÇÕES DO BANCO
# ============================
DB_CONFIG = {
    "host": "psql-database-mapping.postgres.database.azure.com",
    "dbname": "db_youon_intelligence",
    "user": "guilherme@psql-database-mapping",
    "password": "SenhaForteAqui",
    "port": 5432,
    "sslmode": "require"
}

EXCEL_PATH = "CNAE_Subclasses_2_3_Estrutura_Detalhada.xlsx"

# ============================
# FUNÇÕES AUXILIARES
# ============================
def limpar_texto(valor):
    return str(valor).replace('\n', ' ').replace('\r', ' ').strip()

# ============================
# LEITURA E PRÉ-PROCESSAMENTO
# ============================
df_raw = pd.read_excel(EXCEL_PATH, skiprows=4, dtype=str)
df_raw.columns = ["secao", "divisao", "grupo", "classe", "subclasse", "descricao"]

# ============================
# CONSTRUÇÃO DA HIERARQUIA
# ============================
rows = []
mem = {"secao": None, "divisao": None, "grupo": None, "classe": None}
secao_map = {}

for _, row in df_raw.iterrows():
    try:
        for nivel in mem:
            if pd.notna(row[nivel]):
                mem[nivel] = str(row[nivel]).strip()

        if pd.notna(row["secao"]) and pd.notna(row["descricao"]) and pd.isna(row["subclasse"]):
            secao_map[mem["secao"]] = limpar_texto(row["descricao"])

        if pd.isna(row["subclasse"]) or pd.isna(row["descricao"]):
            continue

        subclasse_raw = str(row["subclasse"]).strip()

        rows.append({
            "id": subclasse_raw,
            "descricao": limpar_texto(row["descricao"]),
            "subclasse": subclasse_raw,
            "classe": mem["classe"],
            "grupo": mem["grupo"],
            "divisao": mem["divisao"],
            "secao": mem["secao"],
            "secao_descricao": limpar_texto(secao_map.get(mem["secao"], ""))
        })
    except Exception as e:
        print(f"⚠️ Ignorado: {row.get('subclasse', '[linha inválida]')} - Erro: {e}")

# ============================
# INSERÇÃO NO BANCO
# ============================
df = pd.DataFrame(rows)
if df.empty:
    print("⚠️ Nenhuma linha válida para inserir.")
else:
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, sep='\t', header=False, index=False)
    csv_buffer.seek(0)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO intel_lead;")

    try:
        cur.copy_from(
            csv_buffer,
            'cnae',
            columns=['id', 'descricao', 'subclasse', 'classe', 'grupo', 'divisao', 'secao', 'secao_descricao']
        )
        conn.commit()
        print(f"✅ {len(df)} linhas inseridas com sucesso na tabela intel_lead.cnae.")
    except Exception as e:
        conn.rollback()
        print("❌ Erro ao inserir dados:", e)
    finally:
        cur.close()
        conn.close()
