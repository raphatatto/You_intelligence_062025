import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "dbname": os.getenv("DB_NAME", "youon"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "your_password_here"),
    "port": os.getenv("DB_PORT", "5432"),
    "sslmode": "require"
}


@contextmanager
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_cursor(commit=False, dict_cursor=True):
    with get_db_connection() as conn:
        cursor_factory = RealDictCursor if dict_cursor else None
        with conn.cursor(cursor_factory=cursor_factory) as cur:
            try:
                yield cur
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
