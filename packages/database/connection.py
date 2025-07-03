# packages/database/connection.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Schema padrão (ex: "lead", "public", etc.)
DB_SCHEMA = os.getenv("DB_SCHEMA", "lead")

# Configurações de conexão via variáveis de ambiente
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "dbname":   os.getenv("DB_NAME", "youon"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", ""),
    "port":     os.getenv("DB_PORT", "5432"),
    "sslmode":  os.getenv("DB_SSLMODE", "require"),
    # Garante que o search_path já venha configurado
    "options":  f"-csearch_path={DB_SCHEMA}"
}

@contextmanager
def get_db_connection():
    """
    Context manager que abre/fecha a conexão com o PostgreSQL.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_cursor(commit: bool = False, dict_cursor: bool = True):
    """
    Context manager que fornece um cursor.
    - commit: faz commit ao sair do bloco se True.
    - dict_cursor: usa RealDictCursor para retornar dicts, caso contrário cursor padrão.
    """
    with get_db_connection() as conn:
        cursor_factory = RealDictCursor if dict_cursor else None
        with conn.cursor(cursor_factory=cursor_factory) as cur:
            # Assegura que usamos o schema correto
            cur.execute(f"SET search_path TO {DB_SCHEMA}")
            try:
                yield cur
                if commit:
                    conn.commit()
            except Exception:
                conn.rollback()
                raise
