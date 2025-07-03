import os
import io
import pandas as pd
import geopandas as gpd
from pathlib import Path
from fiona import listlayers
from dotenv import load_dotenv
from datetime import datetime
from packages.database.connection import get_db_cursor

load_dotenv()

def _to_pg_array(data):
    """
    Recebe um np.ndarray de shape (n, m) e retorna uma Series
    de strings "{v1,v2,...}" formatadas sem decimais.
    """
    def fmt(lst):
        if len(lst) == 0:
            return r"\N"
        vals = [str(int(v)) for v in lst]
        return "{" + ",".join(vals) + "}"
    return pd.Series([fmt(row) for row in data])

def main(gdb_path: Path, distribuidora: str, ano: int, camada: str):
    if camada not in listlayers(gdb_path):
        print(f"❌ Camada {camada} não encontrada em {gdb_path.name}")
        return

    print(f"📥 Lendo camada '{camada}' do arquivo {gdb_path.name}")
    df = gpd.read_file(gdb_path, layer=camada)

    try:
        # ── Limpeza de colunas com dados quebrado
        # ── Construção do DataFrame lead_bruto ──────────────────────────────
        df_bruto = pd.DataFrame({
            "id": df["COD_ID"],
            "id_interno": df["COD_ID"],
            "cnae": df.get("CNAE"),
            "grupo_tensao": df.get("GRU_TEN"),
            "modalidade": df.get("GRU_TAR"),
            "tipo_sistema": df.get("TIP_SIST"),
            "situacao": df.get("SIT_ATIV"),
            "distribuidora": df.get("DIST"),
            "origem": camada,
            "status": "raw",
            "data_conexao": pd.to_datetime(df.get("DAT_CON"), errors="coerce"),
            "classe": df.get("CLAS_SUB"),
            "segmento": df.get("CONJ"),
            "subestacao": df.get("SUB"),
            "municipio_ibge": df.get("MUN"),
            "bairro": df.get("BRR"),
            "cep": df.get("CEP"),
            "pac": df.get("PAC"),
            "pn_con": df.get("PN_CON"),
            "descricao": df.get("DESCR")
        })
        df_bruto.drop_duplicates(subset="id", inplace=True)

        # ── Colunas de demanda, energia e qualidade ─────────────────────────
        dem_p = [c for c in df.columns if c.startswith("DEM_P_")]
        dem_f = [c for c in df.columns if c.startswith("DEM_F_")]
        ene_p = [c for c in df.columns if c.startswith("ENE_P_")]
        ene_f = [c for c in df.columns if c.startswith("ENE_F_")]
        dic   = [c for c in df.columns if c.startswith("DIC_")]
        fic   = [c for c in df.columns if c.startswith("FIC_")]

        arr_dem_p = df[dem_p].fillna(0).astype(int).values if dem_p else []
        arr_dem_f = df[dem_f].fillna(0).astype(int).values if dem_f else []
        arr_ene_p = df[ene_p].fillna(0).astype(int).values if ene_p else []
        arr_ene_f = df[ene_f].fillna(0).astype(int).values if ene_f else []

        df_demanda = pd.DataFrame({
            "id": df["COD_ID"],
            "lead_id": df["COD_ID"],
            "dem_ponta": _to_pg_array(arr_dem_p) if dem_p else None,
            "dem_fora_ponta": _to_pg_array(arr_dem_f) if dem_f else None,
        }).drop_duplicates(subset="lead_id")

        df_energia = pd.DataFrame({
            "id": df["COD_ID"],
            "lead_id": df["COD_ID"],
            "ene": _to_pg_array(arr_ene_p + arr_ene_f) if ene_p and ene_f else None,
            "potencia": df["DEM_CONT"].fillna(0).astype(int) if "DEM_CONT" in df else pd.Series(0, index=df.index),
        }).drop_duplicates(subset="lead_id")

        df_qualidade = pd.DataFrame({
            "id": df["COD_ID"],
            "lead_id": df["COD_ID"],
            "dic": _to_pg_array(df[dic].fillna(0).astype(int).values) if dic else None,
            "fic": _to_pg_array(df[fic].fillna(0).astype(int).values) if fic else None,
        }).drop_duplicates(subset="lead_id")

        # ── Inserção no banco com COPY explícito ────────────────────────────
        cols_bruto = [
            "id", "id_interno", "cnae", "grupo_tensao", "modalidade", "tipo_sistema",
            "situacao", "distribuidora", "origem", "status", "data_conexao",
            "classe", "segmento", "subestacao", "municipio_ibge", "bairro",
            "cep", "pac", "pn_con", "descricao"
        ]
        cols_demanda = ["id", "lead_id", "dem_ponta", "dem_fora_ponta"]
        cols_energia = ["id", "lead_id", "ene", "potencia"]
        cols_qualidade = ["id", "lead_id", "dic", "fic"]

        with get_db_cursor(commit=True) as cur:
            # lead_bruto
            buf = io.StringIO()
            df_bruto.to_csv(buf, index=False, header=False, columns=cols_bruto, na_rep=r"\N")
            buf.seek(0)
            cur.copy_expert(
                f"COPY lead_bruto ({','.join(cols_bruto)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
            print(f"📤 Enviados {len(df_bruto)} registros para lead_bruto")

            # lead_demanda
            buf = io.StringIO()
            df_demanda.to_csv(buf, index=False, header=False, columns=cols_demanda, na_rep=r"\N")
            buf.seek(0)
            cur.copy_expert(
                f"COPY lead_demanda ({','.join(cols_demanda)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
            print(f"📤 Enviados {len(df_demanda)} registros para lead_demanda")

            # lead_energia
            buf = io.StringIO()
            df_energia.to_csv(buf, index=False, header=False, columns=cols_energia, na_rep=r"\N")
            buf.seek(0)
            cur.copy_expert(
                f"COPY lead_energia ({','.join(cols_energia)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
            print(f"📤 Enviados {len(df_energia)} registros para lead_energia")

            # lead_qualidade
            buf = io.StringIO()
            df_qualidade.to_csv(buf, index=False, header=False, columns=cols_qualidade, na_rep=r"\N")
            buf.seek(0)
            cur.copy_expert(
                f"COPY lead_qualidade ({','.join(cols_qualidade)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)
            print(f"📤 Enviados {len(df_qualidade)} registros para lead_qualidade")

            # registra status
            cur.execute("""
                INSERT INTO import_status (distribuidora, ano, camada, status, data_execucao)
                VALUES (%s, %s, %s, %s, now())
                ON CONFLICT (distribuidora, ano)
                DO UPDATE SET camada = EXCLUDED.camada, status = EXCLUDED.status, data_execucao = now();
            """, (distribuidora, ano, camada, "success"))

        print("✅ UCAT importado com sucesso!")

    except Exception as e:
        print("❌ Erro ao importar UCAT:", str(e))
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO import_status (distribuidora, ano, camada, status, data_execucao)
                VALUES (%s, %s, %s, %s, now())
                ON CONFLICT (distribuidora, ano)
                DO UPDATE SET camada = EXCLUDED.camada, status = EXCLUDED.status, data_execucao = now();
            """, (distribuidora, ano, camada, "failed"))
