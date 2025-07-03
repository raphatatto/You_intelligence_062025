# packages/jobs/utils/rastreio.py
from packages.database.connection import get_db_cursor

def registrar_status(distribuidora: str, ano: int, camada: str, status: str) -> None:
    sql = """
    INSERT INTO import_status(distribuidora, ano, camada, status, data_execucao)
      VALUES (%s, %s, %s, %s, NOW())
    ON CONFLICT(distribuidora, ano, camada)
      DO UPDATE SET status = EXCLUDED.status,
                    data_execucao = EXCLUDED.data_execucao
    """
    with get_db_cursor(commit=True) as cur:
        cur.execute(sql, (distribuidora, ano, camada, status))

def get_status(distribuidora: str, ano: int, camada: str) -> str | None:
    sql = """
    SELECT status
      FROM import_status
     WHERE distribuidora = %s AND ano = %s AND camada = %s
    """
    with get_db_cursor(commit=False) as cur:
        cur.execute(sql, (distribuidora, ano, camada))
        row = cur.fetchone()
        if not row:
            return None

        # se veio como tupla ou lista
        if isinstance(row, (list, tuple)):
            return row[0]
        # se veio como dict ou RealDictRow
        return row.get("status")
