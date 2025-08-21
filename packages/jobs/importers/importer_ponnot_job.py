# packages/jobs/importers/importer_ponnot_job.py
# -*- coding: utf-8 -*-
"""
PONNOT -> intel_lead.ponto_notavel (schema minimalista)

Alinha dinamicamente ao banco:
- Detecta as colunas existentes em intel_lead.ponto_notavel
- Se 'pn_id' tiver default/identity, NÃO envia pn_id no COPY
- Caso 'pn_id' exista e não tenha default: usa PN_ID do GDB ou gera determinístico (BIGINT)

Colunas que suportamos no banco (usamos só as que existirem):
  pn_id (bigint/int) | latitude (numeric) | longitude (numeric)
  distribuidora_id (text) | ano (int)

Execução leve:
- Fiona em streaming (não carrega tudo em RAM)
- Chunk pequeno (default 5k)
- COPY por micro-batches
"""

from __future__ import annotations
import os, io, gc, sys, time, argparse, hashlib, math
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import pandas as pd
import fiona
import psycopg2
from tqdm import tqdm

SCHEMA = "intel_lead"
TABLE  = f"{SCHEMA}.ponto_notavel"

CHUNK_SIZE = int(os.getenv("PONNOT_CHUNK_SIZE", "5000"))
ROWS_PER_COPY = int(os.getenv("PONNOT_ROWS_PER_COPY", "20000"))
SLEEP_MS = int(os.getenv("PONNOT_SLEEP_MS_BETWEEN", "80"))

# ---------------------- Conexão ----------------------
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

# ---------------------- Detecção de layer ----------------------
def detectar_layer_ponnot(gdb_path: Path) -> Optional[str]:
    cand = {"PONNOT","PON_NOT","PONTO_NOTAVEL","PONTOS_NOTAVEIS","ponnot","pon_not","ponto_notavel"}
    layers = set(fiona.listlayers(str(gdb_path)))
    for name in cand:
        if name in layers: return name
    for ly in layers:
        if ly.upper().startswith("PON"): return ly
    return None

# ---------------------- Introspecção do Banco ----------------------
def introspect_table(cur) -> dict:
    """
    Lê colunas e se pn_id tem default/identity. Retorna:
      {'cols': ['pn_id','latitude',...], 'has_pn_id': True/False, 'pn_id_has_default': True/False}
    """
    cur.execute("""
        SELECT column_name, column_default, data_type
        FROM information_schema.columns
        WHERE table_schema=%s AND table_name=%s
        ORDER BY ordinal_position
    """, (SCHEMA, "ponto_notavel"))
    rows = cur.fetchall()
    cols = [r[0] for r in rows]
    pn_default = None
    if "pn_id" in cols:
        for r in rows:
            if r[0] == "pn_id":
                pn_default = r[1]  # pode ser nextval(...) ou 'generated ...'
                break
    pn_has_default = pn_default is not None and pn_default != ""
    return {"cols": cols, "has_pn_id": "pn_id" in cols, "pn_id_has_default": pn_has_default}

# ---------------------- Utils ----------------------
def props_get_any(props: Dict, keys: List[str]) -> Optional[str]:
    for k in keys:
        v = props.get(k)
        if v is not None and str(v).strip() not in ("", "nan", "NaN"):
            return str(v)
    return None

def feature_lat_lon(feat: dict) -> Tuple[Optional[float], Optional[float]]:
    lat = lon = None
    geom = feat.get("geometry")
    if geom and geom.get("type") == "Point":
        coords = geom.get("coordinates") or []
        if len(coords) >= 2:
            lon, lat = coords[0], coords[1]
    props = feat.get("properties") or {}
    if lat is None:
        v = props_get_any(props, ["LAT","Latitude","lat","Y","y"])
        try: lat = float(v) if v is not None else None
        except: lat = None
    if lon is None:
        v = props_get_any(props, ["LONG","Longitude","long","X","x"])
        try: lon = float(v) if v is not None else None
        except: lon = None
    return lat, lon

def stable_bigint_id(dist: str, ano: int, lat: Optional[float], lon: Optional[float]) -> int:
    lat_s = f"{lat:.6f}" if lat is not None else "null"
    lon_s = f"{lon:.6f}" if lon is not None else "null"
    base = f"{dist}|{ano}|{lat_s}|{lon_s}"
    # 12 hex (~48 bits) cabe em BIGINT
    return int(hashlib.md5(base.encode()).hexdigest()[:12], 16)

def copy_dataframe(cur, df: pd.DataFrame, table_full: str, columns: List[str]) -> int:
    if df.empty: return 0
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, columns=columns, na_rep='\\N')
    buf.seek(0)
    cur.copy_expert(
        f"COPY {table_full} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')",
        buf
    )
    return len(df)

# ---------------------- Núcleo ----------------------
def processar_chunk(
    feats: List[dict],
    cur,
    cols_db: List[str],
    include_pn_id: bool,
    dist_text: str,
    ano: int
) -> int:
    if not feats: return 0

    # mapeamento mínimo para o seu banco
    want_cols = [c for c in ["pn_id","latitude","longitude","distribuidora_id","ano"] if c in cols_db]

    rows = []
    for feat in feats:
        props = feat.get("properties") or {}
        lat, lon = feature_lat_lon(feat)

        # pega PN_ID do GDB se existir
        raw_pn = props_get_any(props, ["PN_ID","PNID","ID_PN","ID","COD","CODIGO"])
        pn_val = None
        if include_pn_id:
            if raw_pn is not None and raw_pn.isdigit():
                try: pn_val = int(raw_pn)
                except: pn_val = None
            if pn_val is None:
                pn_val = stable_bigint_id(dist_text, ano, lat, lon)

        row = {
            "pn_id": pn_val,
            "latitude": float(lat) if lat is not None else None,
            "longitude": float(lon) if lon is not None else None,
            "distribuidora_id": dist_text,
            "ano": int(ano)
        }
        rows.append({k: row[k] for k in want_cols})

    df = pd.DataFrame.from_records(rows, columns=want_cols)

    # tipos finais
    if "latitude" in df:  df["latitude"]  = pd.to_numeric(df["latitude"], errors="coerce")
    if "longitude" in df: df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    if "ano" in df:       df["ano"]       = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")

    # staging + upsert se pn_id faz parte do conjunto
    if include_pn_id and "pn_id" in want_cols:
        cur.execute(f"CREATE TEMP TABLE _stg_pn (LIKE {TABLE} INCLUDING ALL) ON COMMIT DROP;")
        copy_dataframe(cur, df, "_stg_pn", want_cols)
        cur.execute(f"""
            INSERT INTO {TABLE} ({','.join(want_cols)})
            SELECT {','.join(want_cols)} FROM _stg_pn
            ON CONFLICT (pn_id) DO NOTHING
        """)
        inserted = cur.rowcount
    else:
        # sem pn_id -> assume que a coluna no banco tem DEFAULT/IDENTITY
        copy_dataframe(cur, df, TABLE, want_cols)
        # não há rowcount para COPY direto; melhor retornar tamanho do df
        inserted = len(df)

    del df, rows
    gc.collect()
    return inserted

# ---------------------- Main ----------------------
def main():
    ap = argparse.ArgumentParser(description="Importer PONNOT (básico e alinhado ao banco minimalista)")
    ap.add_argument("--gdb", required=True)
    ap.add_argument("--distribuidora", required=True)  # vira distribuidora_id (TEXT)
    ap.add_argument("--ano", type=int, required=True)
    ap.add_argument("--chunk-size", type=int, default=CHUNK_SIZE)
    ap.add_argument("--sleep-ms-between", type=int, default=SLEEP_MS)
    ap.add_argument("--modo-debug", action="store_true")
    args = ap.parse_args()

    gdb = Path(args.gdb)
    if not gdb.exists():
        raise FileNotFoundError(f"GDB não encontrado: {gdb}")

    layer = detectar_layer_ponnot(gdb)
    if not layer:
        raise RuntimeError("Camada PONNOT não encontrada no GDB.")

    dist_text = str(args.distribuidora)

    with get_db_connection() as conn, conn.cursor() as cur, fiona.open(str(gdb), layer=layer) as src:
        # introspecção da tabela do SEU banco
        meta = introspect_table(cur)
        cols_db = meta["cols"]
        include_pn_id = meta["has_pn_id"] and not meta["pn_id_has_default"]

        total = len(src)
        pbar = tqdm(total=total, desc=f"PONNOT {dist_text} {args.ano}", unit="pt")

        chunk: List[dict] = []
        total_ins = 0

        def flush():
            nonlocal chunk, total_ins
            if not chunk: return
            total_ins += processar_chunk(chunk, cur, cols_db, include_pn_id, dist_text, args.ano)
            conn.commit()
            chunk = []
            if args.sleep_ms_between > 0:
                time.sleep(args.sleep_ms_between / 1000.0)

        for feat in src:
            chunk.append(feat)
            if len(chunk) >= args.chunk_size:
                flush()
            pbar.update(1)

        flush()
        pbar.close()

        if args.modo_debug:
            print(f"Inseridos ponto_notavel: {total_ins}")

if __name__ == "__main__":
    main()
