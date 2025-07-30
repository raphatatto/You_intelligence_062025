import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "port": os.getenv("DB_PORT", 5432),
    "sslmode": "require"
}

TABELAS = [
    ("lead_bruto", "lead_passivo"),
    ("lead_energia", "lead_energia_passivo"),
    ("lead_demanda", "lead_demanda_passivo"),
    ("lead_qualidade", "lead_qualidade_passivo")
]

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def mover_leads_inuteis():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Passo 1: Buscar UCs desativadas
            cur.execute("SELECT uc_id FROM intel_lead.lead_bruto WHERE status = 'desativado'")
            uc_ids = [row[0] for row in cur.fetchall()]

        if not uc_ids:
            print("✅ Nenhum lead desativado para mover.")
            return

        print(f"🔄 Movendo {len(uc_ids)} leads desativados para tabelas _passivo...")

        for origem, destino in TABELAS:
            with conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO intel_lead.{destino}
                    SELECT * FROM intel_lead.{origem}
                    WHERE uc_id = ANY(%s)
                """, (uc_ids,))
                print(f"✅ Inserido em {destino}")

                cur.execute(f"""
                    DELETE FROM intel_lead.{origem}
                    WHERE uc_id = ANY(%s)
                """, (uc_ids,))
                print(f"❌ Removido de {origem}")

        conn.commit()
        print("🏁 Migração finalizada com sucesso.")

    finally:
        conn.close()

if __name__ == "__main__":
    mover_leads_inuteis()
