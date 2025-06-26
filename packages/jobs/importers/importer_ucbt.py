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
    def fmt(lst):
        return "{" + ",".join(map(str, lst)) + "}" if len(lst) > 0 else r"\N"
    return pd.Series([fmt(row) for row in data])

def main(gdb_path: Path, distribuidora: str, ano: int, camada: str = "UCBT_tab"):
    if camada not in listlayers(gdb_path):
        print(f"❌ Camada {camada} não encontrada em {gdb_path.name}")
        return

    print(f"📥 Lendo camada '{camada}' do arquivo {gdb_path.name}")
    df = gpd.read_file(gdb_path, layer=camada)

    try:
        col_sujas = df.columns[df.astype(str)
                               .apply(lambda col: col.str.contains("106022|YEL", na=False))
                               .any()]
        for col in col_sujas:
            print(f"🧼 Removendo coluna suja: {col}")
            df.drop(columns=[col], inplace=True)

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

        with get_db_cursor() as cur_check:
            cur_check.execute("SELECT id FROM lead_bruto WHERE id = ANY(%s)", (list(df_bruto["id"]),))
            ids_existentes = {row[0] for row in cur_check.fetchall()}
        df_bruto = df_bruto[~df_bruto["id"].isin(ids_existentes)]
        df = df[df["COD_ID"].isin(df_bruto["id"])]

        if df_bruto.empty:
            print("⚠️ Nenhum novo registro UCBT para importar.")
            return

        ene = [c for c in df.columns if c.startswith("ENE_")]
        dic = [c for c in df.columns if c.startswith("DIC_")]
        fic = [c for c in df.columns if c.startswith("FIC_")]

        df_energia = pd.DataFrame({
            "id": df["COD_ID"],
            "lead_id": df["COD_ID"],
            "ene": _to_pg_array(df[ene].fillna(0).astype(int).values) if ene else None,
            "potencia": df.get("CAR_INST", pd.Series([0] * len(df))).fillna(0).astype(int),
        })

        df_qualidade = pd.DataFrame({
            "id": df["COD_ID"],
            "lead_id": df["COD_ID"],
            "dic": _to_pg_array(df[dic].fillna(0).astype(int).values) if dic else None,
            "fic": _to_pg_array(df[fic].fillna(0).astype(int).values) if fic else None,
        })

        with get_db_cursor(commit=True) as cur:
            for table, dataframe, cols in [
                ("lead_bruto", df_bruto, list(df_bruto.columns)),
                ("lead_energia", df_energia, list(df_energia.columns)),
                ("lead_qualidade", df_qualidade, list(df_qualidade.columns)),
            ]:
                buf = io.StringIO()
                dataframe.to_csv(buf, index=False, header=False, columns=cols, na_rep=r"\N")
                buf.seek(0)
                cur.copy_expert(f"COPY {table} ({','.join(cols)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf)

            cur.execute("""
                INSERT INTO import_status (distribuidora, ano, camada, status, data_execucao)
                VALUES (%s, %s, %s, %s, now())
                ON CONFLICT (distribuidora, ano)
                DO UPDATE SET camada = EXCLUDED.camada, status = EXCLUDED.status, data_execucao = now();
            """, (distribuidora, ano, camada, "success"))

        print(f"✅ UCBT importado com sucesso: {len(df_bruto)} novos leads")

    except Exception as e:
        print(f"❌ Erro ao importar UCBT: {e}")
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO import_status (distribuidora, ano, camada, status, data_execucao)
                VALUES (%s, %s, %s, %s, now())
                ON CONFLICT (distribuidora, ano)
                DO UPDATE SET camada = EXCLUDED.camada, status = EXCLUDED.status, data_execucao = now();
            """, (distribuidora, ano, camada, "failed"))
