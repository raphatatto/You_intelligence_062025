# tests/test_log_enriquecimento.py

import pytest
from datetime import datetime
from packages.database.connection import get_db_connection
from packages.jobs.utils.log_enriquecimento import registrar_log_enriquecimento


def test_registrar_log_enriquecimento():
    uc_id = "teste_uc_id_123"
    etapa = "geo_info"
    resultado = "enriched"
    detalhes = "mock test"
    data_execucao = datetime(2024, 1, 1, 12, 0, 0)

    with get_db_connection() as conn:
        # Limpa o log para garantir idempotência do teste
        with conn.cursor() as cur:
            cur.execute("DELETE FROM lead_enrichment_log WHERE uc_id = %s", (uc_id,))
        conn.commit()

        # Executa a função
        registrar_log_enriquecimento(
            conn=conn,
            uc_id=uc_id,
            etapa=etapa,
            resultado=resultado,
            detalhes=detalhes,
            data_execucao=data_execucao
        )

        # Valida inserção
        with conn.cursor() as cur:
            cur.execute("""
                SELECT uc_id, etapa, resultado, detalhes, data_execucao
                FROM lead_enrichment_log
                WHERE uc_id = %s
                ORDER BY id DESC LIMIT 1
            """, (uc_id,))
            row = cur.fetchone()

    assert row is not None
    assert row[0] == uc_id
    assert row[1] == etapa
    assert row[2] == resultado
    assert row[3] == detalhes
    assert row[4] == data_execucao
