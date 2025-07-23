import pandas as pd
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from packages.database.connection import get_db_connection

CSV_PATH = Path("data/scripts/url.csv")
URL_BASE = "https://www.arcgis.com/sharing/rest/content/items"

def gerar_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()

def inserir_dados_catalogo():
    try:
        df = pd.read_csv(CSV_PATH)
        df.columns = [col.strip().lower() for col in df.columns]
        print(f"📄 Linhas no CSV: {len(df)}")

        if "id" not in df.columns:
            print("❌ Coluna 'id' não encontrada no CSV.")
            return

        inseridos = 0

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                for idx, row in df.iterrows():
                    arcgis_id = str(row.get("id", "")).strip()
                    if not arcgis_id:
                        print(f"⚠️ Linha {idx}: ID vazio, ignorado.")
                        continue

                    url = f"{URL_BASE}/{arcgis_id}/data"
                    url_hash = gerar_hash(url)

                    title = str(row.get("title", "")).strip()
                    description = str(row.get("description", "")).strip()
                    tipo = str(row.get("type", "")).strip()
                    snippet = str(row.get("snippet", "")).strip()

                    tags_raw = row.get("tags", "")
                    tags = [tag.strip() for tag in str(tags_raw).split(",")] if tags_raw else []

                    created = row.get("created")
                    modified = row.get("modified")

                    query = """
                        INSERT INTO intel_lead.dataset_url_catalog (
                            title, description, url, url_hash, created, modified,
                            tipo, snippet, tags, ultima_verificacao
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (url_hash) DO NOTHING;
                    """
                    cursor.execute(query, (
                        title,
                        description,
                        url,
                        url_hash,
                        created,
                        modified,
                        tipo,
                        snippet,
                        tags,
                        datetime.now(timezone.utc)
                    ))

                    if cursor.rowcount > 0:
                        inseridos += 1
                        print(f"✅ Inserido [{inseridos}]: {title}")
                    else:
                        print(f"⚠️ Já existia: {title}")

            conn.commit()
            print(f"\n🎯 Fim da execução: {inseridos} novos registros inseridos.")

    except Exception as e:
        print(f"❌ ERRO FATAL: {e}")

if __name__ == "__main__":
    inserir_dados_catalogo()
