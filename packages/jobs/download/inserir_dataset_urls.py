import pandas as pd
import hashlib
from pathlib import Path
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from packages.database.connection import get_db_connection

CSV_PATH = Path("data/scripts/urls.xls")  # ou .xls

def gerar_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()

def inserir_urls_dataset():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔄 Leitura flexível do CSV ou Excel
    if CSV_PATH.suffix == ".csv":
        df = pd.read_csv(CSV_PATH)
    elif CSV_PATH.suffix in [".xls", ".xlsx"]:
        df = pd.read_excel(CSV_PATH)
    else:
        raise ValueError("Formato de arquivo não suportado")

    df.columns = [col.strip().lower() for col in df.columns]

    for _, row in df.iterrows():
        camada = row["camada"].strip().upper()
        distribuidora_nome = row["distribuidora_nome"].strip()
        distribuidora_id = int(row["distribuidora_id"])
        ano = int(row["ano"])
        url = row["url"].strip()
        url_hash = gerar_hash(url)

        query = """
            INSERT INTO intel_lead.dataset_url (
                camada, distribuidora_nome, distribuidora_id, ano, url, url_hash, status, ultima_verificacao
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 'pending', %s
            )
            ON CONFLICT (url_hash) DO NOTHING;
        """
        cursor.execute(query, (
            camada,
            distribuidora_nome,
            distribuidora_id,
            ano,
            url,
            url_hash,
            datetime.utcnow()
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ URLs inseridas com sucesso.")

if __name__ == "__main__":
    inserir_urls_dataset()
