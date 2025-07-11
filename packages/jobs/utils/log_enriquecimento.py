# packages/jobs/utils/log_enriquecimento.py

from datetime import datetime
from psycopg2.extensions import connection as PGConnection
from tqdm import tqdm


def registrar_log_enriquecimento(
    conn: PGConnection,
    uc_id: str,
    etapa: str,
    resultado: str,
    detalhes: str = None,
    data_execucao: datetime = None,
):
    """
    Salva log do enriquecimento para uma UC específica.

    :param conn: conexão ativa com o banco de dados (psycopg2)
    :param uc_id: ID da unidade consumidora (string única)
    :param etapa: nome da etapa (ex: geo_info, cnpj, reclames, etc)
    :param resultado: resultado da etapa (ex: enriched, failed, skipped)
    :param detalhes: mensagem ou motivo do resultado (opcional)
    :param data_execucao: datetime (agora por padrão)
    """
    if data_execucao is None:
        data_execucao = datetime.utcnow()

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO lead_enrichment_log (uc_id, etapa, resultado, detalhes, data_execucao)
            VALUES (%s, %s, %s, %s, %s)
        """, (uc_id, etapa, resultado, detalhes, data_execucao))
    
    tqdm.write(f"📌 Log: uc_id={uc_id}, etapa={etapa}, resultado={resultado}")
