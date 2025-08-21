import os
import json
import uuid
import time
from contextlib import contextmanager

from packages.database.connection import get_db_connection

WORKER_POLL_SEC = float(os.getenv("WORKER_POLL_SEC", "2"))

@contextmanager
def _conn_cursor():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            yield conn, cur

def enqueue(payload: dict, priority: int = 5, available_at: str | None = None):
    with _conn_cursor() as (conn, cur):
        cur.execute("""
            INSERT INTO import_queue (payload, priority, available_at)
            VALUES (%s, %s, COALESCE(%s, now()))
            RETURNING id
        """, (json.dumps(payload), priority, available_at))
        job_id = cur.fetchone()[0]
        conn.commit()
        return job_id

def dequeue(worker_id: str):
    # pega 1 job pronto, marca como running (row-level lock, transação atômica)
    with _conn_cursor() as (conn, cur):
        cur.execute("""
            UPDATE import_queue AS q SET
              status = 'running',
              started_at = now(),
              worker_id = %s,
              tries = q.tries + 1
            WHERE q.id = (
              SELECT id
              FROM import_queue
              WHERE status = 'queued'
                AND available_at <= now()
              ORDER BY priority ASC, available_at ASC, id ASC
              FOR UPDATE SKIP LOCKED
              LIMIT 1
            )
            RETURNING id, payload, tries, max_retries
        """, (worker_id,))
        row = cur.fetchone()
        conn.commit()
        if not row:
            return None
        job_id, payload, tries, max_retries = row
        return {"id": job_id, "payload": payload, "tries": tries, "max_retries": max_retries}

def complete(job_id: int):
    with _conn_cursor() as (conn, cur):
        cur.execute("""
            UPDATE import_queue
            SET status='done', finished_at=now()
            WHERE id=%s
        """, (job_id,))
        conn.commit()

def fail(job_id: int, delay_sec: int | None = None):
    # re-enfileira com backoff (se ainda não excedeu tentativas)
    with _conn_cursor() as (conn, cur):
        cur.execute("SELECT tries, max_retries FROM import_queue WHERE id=%s", (job_id,))
        tries, max_retries = cur.fetchone()
        if tries < max_retries:
            cur.execute("""
                UPDATE import_queue
                SET status='queued',
                    available_at = now() + make_interval(secs => %s),
                    worker_id=NULL,
                    started_at=NULL
                WHERE id=%s
            """, (delay_sec or 30, job_id))
        else:
            cur.execute("""
                UPDATE import_queue
                SET status='failed', finished_at=now()
                WHERE id=%s
            """, (job_id,))
        conn.commit()
