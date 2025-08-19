# packages/jobs/importers/importer_ucbt_job.py
# -*- coding: utf-8 -*-
"""
Importer UCBT otimizado para baixa RAM e alinhado ao schema intel_lead.

- Lê FileGDB (layer UCBT) via Fiona em streaming (sem carregar tudo na memória)
- Processa em chunks pequenos (default 5k) com pausa curta entre chunks
- Insere:
    * intel_lead.lead_bruto
    * intel_lead.lead_energia_mensal   (energia_total)
    * intel_lead.lead_demanda_mensal   (demanda_total, demanda_contratada)
    * intel_lead.lead_qualidade_mensal (dic, fic, sem_rede)
- Usa COPY por micro-batches para evitar picos de memória
- Idempotência: uc_id determinístico (hash de dist_id|ano|camada|COD_ID) e import_id por execução

Env vars úteis:
- DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT, DB_SSLMODE=require
- UCBT_CHUNK_SIZE (default 5000)
- UCBT_ROWS_PER_COPY (default 20000)
- UCBT_SLEEP_MS_BETWEEN (default 120)  # em milissegundos
"""

from __future__ import annotations
import os
import io
import gc
import sys
import uuid
import time
import argparse
import hashlib
from pathlib import Path
from typing import List, Tuple, Dict

import pandas as pd
import fiona
import psycopg2
from tqdm import tqdm

# --------------------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------------------
SCHEMA = "intel_lead"

UCBT_CHUNK_SIZE = int(os.getenv("UCBT_CHUNK_SIZE", "5000"))
UCBT_ROWS_PER_COPY = int(os.getenv("UCBT_ROWS_PER_COPY", "20000"))
UCBT_SLEEP_MS_BETWEEN = int(os.getenv("UCBT_SLEEP_MS_BETWEEN", "120"))

# --------------------------------------------------------------------------------------
# Conexão ao banco (com fallback por env)
# --------------------------------------------------------------------------------------
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

# --------------------------------------------------------------------------------------
# Sanitizadores (usa os do projeto; se não houver, fallbacks no-ops)
# --------------------------------------------------------------------------------------
try:
    from packages.jobs.utils.sanitize import (
        sanitize_cnae, sanitize_grupo_tensao, sanitize_modalidade, sanitize_tipo_sistema,
        sanitize_situacao, sanitize_classe, sanitize_pac, sanitize_str, sanitize_int, sanitize_numeric
    )
except Exception:
    def sanitize_cnae(x): return pd.Series(x, dtype="string")
    def sanitize_grupo_tensao(x): return pd.Series(x, dtype="string")
    def sanitize_modalidade(x): return pd.Series(x, dtype="string")
    def sanitize_tipo_sistema(x): return pd.Series(x, dtype="string")
    def sanitize_situacao(x): return pd.Series(x, dtype="string")
    def sanitize_classe(x): return pd.Series(x, dtype="string")
    def sanitize_pac(x): return pd.to_numeric(x, errors="coerce")
    def sanitize_str(x): return pd.Series(x, dtype="string")
    def sanitize_int(x): return pd.to_numeric(x, errors="coerce").astype("Int64")
    def sanitize_numeric(x): return pd.to_numeric(x, errors="coerce")

# Rastreio (opcional)
try:
    from packages.jobs.utils.rastreio import registrar_status, gerar_import_id
except Exception:
    def registrar_status(*args, **kwargs): pass
    def gerar_import_id(distribuidora_nome: str, ano: int, camada: str) -> str:
        base = f"{distribuidora_nome}-{ano}-{camada}"
        return hashlib.md5(base.encode()).hexdigest()[:16]

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def detectar_layer_ucbt(gdb_path: Path) -> str | None:
    """
    Detecta nome da layer UCBT dentro do GDB (lida com variações).
    """
    candidates = {"UCBT_tab", "UCBT", "UCBT_TAB", "ucbt_tab"}
    try:
        layers = set(fiona.listlayers(str(gdb_path)))
    except Exception:
        return None
    for name in candidates:
        if name in layers:
            return name
    for ly in (layers or []):
        if ly.upper().startswith("UCBT"):
            return ly
    return None

def gerar_uc_id(cod_id: str, ano: int, camada: str, dist_id: int | str) -> str:
    base = f"{dist_id}|{ano}|{camada}|{cod_id}"
    h = hashlib.md5(base.encode()).hexdigest()
    return f"UC:{h}"

def copy_dataframe(cur, df: pd.DataFrame, table_full: str, columns: List[str]) -> int:
    """
    COPY em CSV para a tabela destino. DataFrame deve conter apenas as colunas listadas.
    """
    if df.empty:
        return 0
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, columns=columns, na_rep='\\N')
    buf.seek(0)
    cur.copy_expert(
        f"COPY {table_full} ({','.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')",
        buf
    )
    return len(df)

def copy_rows_buffered(cur, table_full: str, columns: List[str], rows: List[Tuple], rows_per_copy: int) -> int:
    """
    COPY a partir de lista de tuplas, quebrando em micro-batches para controlar memória.
    """
    if not rows:
        return 0
    total = 0
    for i in range(0, len(rows), rows_per_copy):
        chunk = rows[i:i + rows_per_copy]
        df = pd.DataFrame.from_records(chunk, columns=columns)
        total += copy_dataframe(cur, df, table_full, columns)
        del df
        gc.collect()
    return total

# --------------------------------------------------------------------------------------
# Núcleo de processamento
# --------------------------------------------------------------------------------------
def processar_chunk(
    chunk_data: List[dict],
    cur,
    import_id: str,
    ano: int,
    camada: str,
    dist_id: int | str,
    rows_per_copy: int
) -> Tuple[int, Dict[str, int]]:
    """
    Processa um chunk:
      - insere lead_bruto (idempotente via uc_id)
      - gera e insere tabelas mensais (energia/demanda/qualidade)
    Retorna: (linhas_bruto_inseridas, {energia, demanda, qualidade})
    """
    df = pd.DataFrame(chunk_data)
    if df.empty:
        return 0, {"energia": 0, "demanda": 0, "qualidade": 0}

    # colunas esperadas (garantir existência)
    base_cols = [
        "COD_ID","DIST","CNAE","DAT_CON","PAC","GRU_TEN","GRU_TAR","TIP_SIST",
        "SIT_ATIV","CLAS_SUB","CONJ","MUN","BRR","CEP","PN_CON","DESCR",
        "SEMRED","DEM_CONT"
    ]
    energia_cols = [f"ENE_{i:02d}" for i in range(1, 13)]
    demanda_cols = [f"DEM_{i:02d}" for i in range(1, 13)]
    qualidade_cols = [f"DIC_{i:02d}" for i in range(1, 13)] + [f"FIC_{i:02d}" for i in range(1, 13)]

    for col in base_cols + energia_cols + demanda_cols + qualidade_cols:
        if col not in df.columns:
            df[col] = None

    # filtra linhas válidas (COD_ID é a chave natural)
    df = df[df["COD_ID"].notna()].copy()
    if df.empty:
        return 0, {"energia": 0, "demanda": 0, "qualidade": 0}

    # Sanitização e mapeamento -> lead_bruto
    df["uc_id"]            = [gerar_uc_id(str(c), int(ano), camada, dist_id) for c in df["COD_ID"]]
    df["import_id"]        = import_id
    df["cod_id"]           = df["COD_ID"].astype(str)
    # se sua coluna no banco for TEXT, troque sanitize_int por sanitize_str aqui
    df["distribuidora_id"] = sanitize_int(df["DIST"])
    df["origem"]           = camada
    df["ano"]              = int(ano)

    df["cnae"]         = sanitize_cnae(df["CNAE"])
    df["grupo_tensao"] = sanitize_grupo_tensao(df["GRU_TEN"])
    df["modalidade"]   = sanitize_modalidade(df["GRU_TAR"])
    df["tipo_sistema"] = sanitize_tipo_sistema(df["TIP_SIST"])
    df["situacao"]     = sanitize_situacao(df["SIT_ATIV"])
    df["classe"]       = sanitize_classe(df["CLAS_SUB"])
    df["segmento"]     = sanitize_str(df["CONJ"])
    df["municipio_id"] = sanitize_int(df["MUN"])
    df["bairro"]       = sanitize_str(df["BRR"])
    # CEP/PON_CON como TEXT no banco (preserva zeros à esquerda)
    df["cep"]          = sanitize_str(df["CEP"])
    df["pn_con"]       = sanitize_str(df["PN_CON"])
    df["descricao"]    = sanitize_str(df["DESCR"])
    df["pac"]          = sanitize_pac(df["PAC"])
    # DATE de verdade
    df["data_conexao"] = pd.to_datetime(df["DAT_CON"], errors="coerce").dt.date

    colunas_bruto = [
        "uc_id","import_id","cod_id","distribuidora_id","origem","ano","data_conexao",
        "cnae","grupo_tensao","modalidade","tipo_sistema","situacao","classe","segmento",
        "municipio_id","bairro","cep","pac","pn_con","descricao"
    ]
    df_bruto = df[colunas_bruto].copy()

    # INSERT lead_bruto via staging + ON CONFLICT (uc_id) DO NOTHING
    cur.execute(f"CREATE TEMP TABLE _stg_lb (LIKE {SCHEMA}.lead_bruto INCLUDING ALL) ON COMMIT DROP;")
    copy_dataframe(cur, df_bruto, f"_stg_lb", colunas_bruto)
    cur.execute(f"""
        INSERT INTO {SCHEMA}.lead_bruto ({','.join(colunas_bruto)})
        SELECT {','.join(colunas_bruto)} FROM _stg_lb
        ON CONFLICT (uc_id) DO NOTHING
    """)
    inserted_bruto = cur.rowcount

    # Mapear lead_bruto_id para cada uc_id do chunk (somente deste import)
    cur.execute(
        f"SELECT id, uc_id FROM {SCHEMA}.lead_bruto WHERE import_id = %s AND uc_id = ANY(%s)",
        (import_id, list(df["uc_id"]))
    )
    id_map = dict(cur.fetchall())

    # Geração das séries mensais (linhas em memória apenas do chunk atual)
    energia_rows: List[Tuple] = []
    demanda_rows: List[Tuple] = []
    qualidade_rows: List[Tuple] = []

    dem_contratada_series = sanitize_numeric(df.get("DEM_CONT"))
    sem_rede_series = sanitize_numeric(df.get("SEMRED"))

    for idx, row in df.iterrows():
        lead_bruto_id = id_map.get(row["uc_id"])
        if not lead_bruto_id:
            continue

        dem_contratada = dem_contratada_series.iloc[idx] if dem_contratada_series is not None else None
        sem_rede = sem_rede_series.iloc[idx] if sem_rede_series is not None else None

        # ENERGIA: apenas energia_total na UCBT
        for mes in range(1, 13):
            energia_rows.append((
                uuid.uuid4(),            # id (uuid) requerido nas tabelas mensais
                lead_bruto_id, mes,
                None, None,
                sanitize_numeric(row.get(f"ENE_{mes:02d}")),
                camada, import_id
            ))

        # DEMANDA
        for mes in range(1, 13):
            demanda_rows.append((
                uuid.uuid4(),
                lead_bruto_id, mes,
                None, None,
                sanitize_numeric(row.get(f"DEM_{mes:02d}")),
                dem_contratada,
                camada, import_id
            ))

        # QUALIDADE
        for mes in range(1, 13):
            qualidade_rows.append((
                uuid.uuid4(),
                lead_bruto_id, mes,
                sanitize_numeric(row.get(f"DIC_{mes:02d}")),
                sanitize_numeric(row.get(f"FIC_{mes:02d}")),
                sem_rede,
                camada, import_id
            ))

    energia_cols   = ["id","lead_bruto_id","mes","energia_ponta","energia_fora_ponta","energia_total","origem","import_id"]
    demanda_cols   = ["id","lead_bruto_id","mes","demanda_ponta","demanda_fora_ponta","demanda_total","demanda_contratada","origem","import_id"]
    qualidade_cols = ["id","lead_bruto_id","mes","dic","fic","sem_rede","origem","import_id"]

    energia_count   = copy_rows_buffered(cur, f"{SCHEMA}.lead_energia_mensal",   energia_cols,   energia_rows, UCBT_ROWS_PER_COPY)
    demanda_count   = copy_rows_buffered(cur, f"{SCHEMA}.lead_demanda_mensal",   demanda_cols,   demanda_rows, UCBT_ROWS_PER_COPY)
    qualidade_count = copy_rows_buffered(cur, f"{SCHEMA}.lead_qualidade_mensal", qualidade_cols, qualidade_rows, UCBT_ROWS_PER_COPY)

    # limpeza do chunk
    del df, df_bruto, energia_rows, demanda_rows, qualidade_rows
    gc.collect()

    return inserted_bruto, {"energia": energia_count, "demanda": demanda_count, "qualidade": qualidade_count}

# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Importer UCBT otimizado (baixa RAM)")
    ap.add_argument("--gdb", required=True, help="Caminho do .gdb")
    ap.add_argument("--distribuidora", required=True, help="Nome/código da distribuidora")
    ap.add_argument("--distribuidora-id", type=int, default=None, help="ID inteiro da distribuidora (se existir)")
    ap.add_argument("--ano", type=int, required=True)
    ap.add_argument("--import-id", type=str, default=None, help="Import ID externo; se não informado, será gerado")
    ap.add_argument("--chunk-size", type=int, default=UCBT_CHUNK_SIZE)
    ap.add_argument("--rows-per-copy", type=int, default=UCBT_ROWS_PER_COPY)
    ap.add_argument("--sleep-ms-between", type=int, default=UCBT_SLEEP_MS_BETWEEN)
    ap.add_argument("--modo-debug", action="store_true")
    args = ap.parse_args()

    gdb_path = Path(args.gdb)
    if not gdb_path.exists():
        raise FileNotFoundError(f"GDB não encontrado: {gdb_path}")

    layer = detectar_layer_ucbt(gdb_path)
    if not layer:
        raise RuntimeError("Camada UCBT não encontrada no GDB (tentei UCBT_tab/UCBT).")

    dist_id = args.distribuidora_id if args.distribuidora_id is not None else args.distribuidora
    import_id = args.import_id or gerar_import_id(args.distribuidora, args.ano, "UCBT")

    registrar_status(
        import_id=import_id, camada="UCBT", distribuidora_nome=args.distribuidora,
        ano=args.ano, stage="importando", status="running",
        last_message=f"Layer={layer}"
    )

    with get_db_connection() as conn, conn.cursor() as cur, fiona.open(str(gdb_path), layer=layer) as src:
        total = len(src)
        pbar = tqdm(total=total, desc=f"UCBT {args.distribuidora} {args.ano}", unit="reg")

        chunk_data: List[dict] = []
        total_bruto = total_e = total_d = total_q = 0

        def flush():
            nonlocal chunk_data, total_bruto, total_e, total_d, total_q
            if not chunk_data:
                return
            inserted, agg = processar_chunk(
                chunk_data, cur, import_id, args.ano, "UCBT", dist_id, args.rows_per_copy
            )
            conn.commit()
            total_bruto += inserted
            total_e += agg["energia"]; total_d += agg["demanda"]; total_q += agg["qualidade"]
            chunk_data = []
            if args.sleep_ms_between > 0:
                time.sleep(args.sleep_ms_between / 1000.0)

        for feat in src:
            props = feat.get("properties") or {}
            chunk_data.append(props)
            if len(chunk_data) >= args.chunk_size:
                flush()
            pbar.update(1)

        flush()
        pbar.close()

        registrar_status(
            import_id=import_id, camada="UCBT", distribuidora_nome=args.distribuidora,
            ano=args.ano, stage="finalizado", status="completed",
            linhas_processadas=total_bruto,
            last_message=f"energia={total_e}, demanda={total_d}, qualidade={total_q}"
        )

        if args.modo_debug:
            print(f"Inseridos lead_bruto={total_bruto} | energia={total_e} | demanda={total_d} | qualidade={total_q}")

if __name__ == "__main__":
    main()
