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
    distribuidora_id: int = None,
    linhas_processadas: int = None,
    observacoes: str = None,
    import_id: str = None,
):
    """
    Registra ou atualiza o status da importação no schema intel_lead.
    Preenche data_inicio quando status = running.
    Preenche data_fim e linhas_processadas quando status = completed/failed/no_new_rows.
    """
    import_id = import_id or gerar_import_id(prefixo, ano, camada)

    with get_db_cursor(commit=True) as cur:
        if status == "running":
            cur.execute("""
                INSERT INTO import_status (
                    import_id, distribuidora_id, ano, camada, status, data_inicio
                ) VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (import_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    data_inicio = NOW()
            """, (import_id, distribuidora_id, ano, camada, status))

        elif status in ["completed", "failed", "no_new_rows"]:
            cur.execute("""
                UPDATE import_status
                SET status = %s,
                    erro = %s,
                    linhas_processadas = %s,
                    observacoes = %s,
                    data_fim = NOW()
                WHERE import_id = %s
            """, (status, erro, linhas_processadas, observacoes, import_id))

def get_status(prefixo: str, ano: int, camada: str) -> str:
    """
    Retorna o status atual da importação, baseado no prefixo.
    """
    import_id = gerar_import_id(prefixo, ano, camada)

    with get_db_cursor() as cur:
        cur.execute("SELECT status FROM import_status WHERE import_id = %s", (import_id,))
        row = cur.fetchone()
        return row["status"] if row else None
