import hashlib
from packages.database.connection import get_db_cursor

def gerar_import_id(prefixo: str, ano: int, camada: str) -> str:
    """
    Gera um ID único baseado nos dados da importação.
    """
    raw = f"{prefixo}_{ano}_{camada}".encode()
    return hashlib.md5(raw).hexdigest()

def registrar_status(
    prefixo: str,
    ano: int,
    camada: str,
    status: str,
    erro: str = None,
    distribuidora_id: int = None
):
    """
    Registra ou atualiza o status da importação no schema intel_lead.
    """
    import_id = gerar_import_id(prefixo, ano, camada)

    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO import_status (import_id, status, camada, ano, erro, distribuidora_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (import_id) DO UPDATE SET
                status = EXCLUDED.status,
                erro = EXCLUDED.erro,
                distribuidora_id = COALESCE(EXCLUDED.distribuidora_id, import_status.distribuidora_id);
        """, (import_id, status, camada, ano, erro, distribuidora_id))

def get_status(prefixo: str, ano: int, camada: str) -> str:
    """
    Retorna o status atual da importação, baseado no prefixo.
    """
    import_id = gerar_import_id(prefixo, ano, camada)

    with get_db_cursor() as cur:
        cur.execute("SELECT status FROM import_status WHERE import_id = %s", (import_id,))
        row = cur.fetchone()
        return row["status"] if row else None
