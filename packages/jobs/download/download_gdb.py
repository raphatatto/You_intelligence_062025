# packages/jobs/download_gdb.py
# -*- coding: utf-8 -*-
"""
Downloader de FileGDB alinhado ao DB:
- Busca a URL no intel_lead.dataset_url_catalog (filtra por distribuidora/ano)
- Faz download retomável (HTTP Range) com limite de banda
- Extrai .gdb de .zip para data/downloads/{DISTRIBUIDORA}_{ANO}.gdb
- Registra progresso em intel_lead.download_log
- Marca 'foi_importado'=true no dataset_url_catalog quando concluir

Compatível com o worker: se o payload tiver "download": {"distribuidora": "...", "ano": 2023, "max_kbps": 256},
o worker chama baixar_gdb(...) e recebe o caminho final do .gdb.
"""

from __future__ import annotations
import os
import io
import time
import zipfile
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Tuple

import requests
import psycopg2
from psycopg2.extras import DictCursor

# -------------------------------------------------------------------
# Pastas
# -------------------------------------------------------------------
DATA_DIR = Path("data")
DOWNLOAD_DIR = DATA_DIR / "downloads"
TMP_DIR = DATA_DIR / "tmp"

# -------------------------------------------------------------------
# Conexão ao banco (reuso do teu padrão, com fallback por env)
# -------------------------------------------------------------------
def _fallback_conn():
    dsn = (
        f"host={os.getenv('DB_HOST','')}"
        f" dbname={os.getenv('DB_NAME','')}"
        f" user={os.getenv('DB_USER','')}"
        f" password={os.getenv('DB_PASS','')}"
        f" port={os.getenv('DB_PORT','5432')}"
        f" sslmode={os.getenv('DB_SSLMODE','require')}"
    )
    return psycopg2.connect(dsn)

try:
    from packages.database.connection import get_db_connection as _get_conn
    def get_db_connection():
        return _get_conn()
except Exception:
    def get_db_connection():
        return _fallback_conn()

SCHEMA = "intel_lead"

# -------------------------------------------------------------------
# Utilidades
# -------------------------------------------------------------------
def _throttle(start_ts: float, bytes_done: int, max_kbps: int):
    if not max_kbps or max_kbps <= 0:
        return
    elapsed = time.monotonic() - start_ts
    if elapsed <= 0:
        return
    target_bps = max_kbps * 1024
    ideal_time = bytes_done / target_bps
    if ideal_time > elapsed:
        time.sleep(ideal_time - elapsed)

def _is_zip_file(path: Path) -> bool:
    if path.suffix.lower() == ".zip":
        return True
    try:
        with open(path, "rb") as f:
            sig = f.read(4)
            return sig == b"PK\x03\x04"
    except Exception:
        return False

def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def _normalize_dest_name(distribuidora: str, ano: int) -> str:
    base = str(distribuidora).strip().upper().replace(" ", "_")
    return f"{base}_{int(ano)}"

# -------------------------------------------------------------------
# LOGS (intel_lead.download_log)
# -------------------------------------------------------------------
def _log_start(cur, distribuidora: str, ano: int) -> int:
    cur.execute(f"""
        INSERT INTO {SCHEMA}.download_log (distribuidora, ano, status, created_at, updated_at)
        VALUES (%s, %s, 'running', now(), now())
        RETURNING id
    """, (distribuidora, int(ano)))
    return cur.fetchone()[0]

def _log_done(cur, log_id: int, tempo_download: float):
    cur.execute(f"""
        UPDATE {SCHEMA}.download_log
        SET status='done', tempo_download=%s, erro=NULL, updated_at=now()
        WHERE id=%s
    """, (float(tempo_download), log_id))

def _log_error(cur, log_id: int, erro: str):
    cur.execute(f"""
        UPDATE {SCHEMA}.download_log
        SET status='error', erro=%s, updated_at=now()
        WHERE id=%s
    """, (erro[:1000], log_id))

# -------------------------------------------------------------------
# CATÁLOGO (intel_lead.dataset_url_catalog)
# -------------------------------------------------------------------
def _pick_dataset(cur, distribuidora: str, ano: int) -> Optional[dict]:
    """
    Escolhe a melhor linha do catálogo para (distribuidora, ano).
    Critérios:
      - title ILIKE %distribuidora%
      - title ILIKE %ano%  (ou created/modified do próprio ano)
      - preferir não importados (foi_importado=false), depois modificados mais recentes
    """
    like_dist = f"%{distribuidora}%"
    like_ano = f"%{ano}%"
    cur.execute(f"""
        SELECT id, title, url, url_hash, created, modified, origem, tipo, foi_importado
        FROM {SCHEMA}.dataset_url_catalog
        WHERE (title ILIKE %s OR origem ILIKE %s OR COALESCE(tipo,'') ILIKE %s)
          AND (
                title ILIKE %s
                OR EXTRACT(YEAR FROM COALESCE(modified, created)) = %s
              )
        ORDER BY foi_importado ASC, COALESCE(modified, created) DESC, id DESC
        LIMIT 1
    """, (like_dist, like_dist, like_dist, like_ano, int(ano)))
    row = cur.fetchone()
    return dict(row) if row else None

def _ensure_url_hash(cur, row_id: int, url: str):
    h = _sha1(url)
    cur.execute(f"""
      UPDATE {SCHEMA}.dataset_url_catalog
      SET url_hash = COALESCE(url_hash, %s), ultima_verificacao = now()
      WHERE id = %s
    """, (h, row_id))

def _mark_imported(cur, row_id: int, obs: str):
    cur.execute(f"""
      UPDATE {SCHEMA}.dataset_url_catalog
      SET foi_importado = TRUE, ultima_verificacao = now(),
          observacoes = CONCAT(COALESCE(observacoes,''), %s)
      WHERE id = %s
    """, (f"\nbaixado: {obs}", row_id))

# -------------------------------------------------------------------
# Download + extração
# -------------------------------------------------------------------
def _baixar_resumivel(url: str, destino: Path, max_kbps: int = 256, timeout_s: int = 30):
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_suffix(destino.suffix + ".part")

    # HEAD
    try:
        h = requests.head(url, timeout=timeout_s, allow_redirects=True)
        total_size = int(h.headers.get("Content-Length") or 0)
        accept_ranges = "bytes" in (h.headers.get("Accept-Ranges") or "").lower()
    except Exception:
        total_size = 0
        accept_ranges = False

    pos = parcial.stat().st_size if parcial.exists() else 0
    headers = {}
    if accept_ranges and pos > 0:
        headers["Range"] = f"bytes={pos}-"

    start_ts = time.monotonic()
    bytes_done = pos

    with requests.get(url, headers=headers, stream=True, timeout=timeout_s) as r:
        r.raise_for_status()
        mode = "ab" if headers else "wb"
        with open(parcial, mode) as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):  # 256 KB
                if not chunk:
                    continue
                f.write(chunk)
                bytes_done += len(chunk)
                _throttle(start_ts, bytes_done, max_kbps)

    if total_size and bytes_done < total_size:
        raise RuntimeError(f"download incompleto: {bytes_done}/{total_size} bytes")

    parcial.replace(destino)

def _extrair_zip_para_gdb(zip_path: Path, destino_final: Path) -> Path:
    """
    Extrai o .zip para TEMP e retorna o caminho da primeira pasta .gdb encontrada.
    """
    sess = TMP_DIR / f"extract_{int(time.time())}"
    sess.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(sess)
    candidatos = [p for p in sess.rglob("*") if p.is_dir() and p.suffix.lower() == ".gdb"]
    if not candidatos:
        shutil.rmtree(sess, ignore_errors=True)
        raise RuntimeError("nenhuma pasta .gdb encontrada dentro do zip")
    gdb_src = candidatos[0]
    final_path = destino_final / gdb_src.name
    if final_path.exists():
        shutil.rmtree(final_path, ignore_errors=True)
    shutil.move(str(gdb_src), str(final_path))
    zip_path.unlink(missing_ok=True)
    shutil.rmtree(sess, ignore_errors=True)
    return final_path

def _maybe_arcgis_data_url(url: str) -> str:
    """
    Muitos registros do catálogo têm URL no formato:
      https://www.arcgis.com/sharing/rest/content/items/<ITEM_ID>
    Nesses casos, a URL direta do arquivo costuma ser:
      https://www.arcgis.com/sharing/rest/content/items/<ITEM_ID>/data
    """
    u = url.rstrip("/")
    if "/sharing/rest/content/items/" in u and not u.endswith("/data"):
        return u + "/data"
    return url

# -------------------------------------------------------------------
# API externa principal (usada pelo worker e CLI)
# -------------------------------------------------------------------
def baixar_gdb(distribuidora: str, ano: int, url: Optional[str] = None,
               nome_destino: Optional[str] = None, max_kbps: int = 256) -> Path:
    """
    Fluxo completo:
      1) Se nome_destino não vier, usa {DISTRIBUIDORA}_{ANO}
      2) Se já existir data/downloads/{nome_destino}.gdb, retorna direto
      3) Se url não vier, busca no dataset_url_catalog pelo melhor match
      4) Baixa com retomada + throttle; se for zip, extrai para {nome_destino}.gdb
      5) Loga em download_log e marca dataset como foi_importado
    Retorna: caminho final da pasta .gdb
    """
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    nome_destino = nome_destino or _normalize_dest_name(distribuidora, ano)
    final_gdb = DOWNLOAD_DIR / f"{nome_destino}.gdb"
    if final_gdb.exists():
        # já disponível
        return final_gdb

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            log_id = _log_start(cur, distribuidora, ano)
            conn.commit()

            try:
                catalog_row = None
                if not url:
                    catalog_row = _pick_dataset(cur, distribuidora, ano)
                    if not catalog_row:
                        raise RuntimeError("dataset_url_catalog não tem entrada correspondente (distribuidora/ano).")
                    url = str(catalog_row["url"])
                    _ensure_url_hash(cur, catalog_row["id"], url)
                    conn.commit()

                # heurística para ArcGIS: /data
                url = _maybe_arcgis_data_url(url)

                tmp_name = Path(url.split("?")[0]).name or f"{nome_destino}.zip"
                # força .zip quando a URL do ArcGIS não tem extensão
                if "." not in tmp_name:
                    tmp_name = f"{nome_destino}.zip"
                tmp_file = TMP_DIR / tmp_name

                t0 = time.time()
                _baixar_resumivel(url, tmp_file, max_kbps=max_kbps)

                if _is_zip_file(tmp_file):
                    # Extrai e renomeia para {nome_destino}.gdb
                    gdb_extracted = _extrair_zip_para_gdb(tmp_file, DOWNLOAD_DIR)
                    # move/renomeia para padronizado
                    if gdb_extracted.name != f"{nome_destino}.gdb":
                        dest = DOWNLOAD_DIR / f"{nome_destino}.gdb"
                        if dest.exists():
                            shutil.rmtree(dest, ignore_errors=True)
                        shutil.move(str(gdb_extracted), str(dest))
                        final_path = dest
                    else:
                        final_path = gdb_extracted
                else:
                    # pouco comum: servidor entrega .gdb direto como pasta/arquivo
                    if tmp_file.suffix.lower() == ".gdb" and tmp_file.is_dir():
                        dest = DOWNLOAD_DIR / f"{nome_destino}.gdb"
                        if dest.exists():
                            shutil.rmtree(dest, ignore_errors=True)
                        shutil.move(str(tmp_file), str(dest))
                        final_path = dest
                    else:
                        raise RuntimeError(f"formato inesperado: {tmp_file.name}")

                dt = time.time() - t0
                _log_done(cur, log_id, dt)

                if catalog_row:
                    _mark_imported(cur, catalog_row["id"], str(final_path))

                conn.commit()
                return final_path

            except Exception as e:
                _log_error(cur, log_id, str(e))
                conn.commit()
                raise
