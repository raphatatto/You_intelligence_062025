import geopandas as gpd
from psycopg2 import connect
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "dbname": "youon",
    "user": "postgres",
    "password": "your_password_here"
}

# ─── FUNÇÃO PRINCIPAL ─────────────────────────────────────────
def importar_ucat(gdb_folder: str | Path, distribuidora: str, ano: int):
    camada = "UCAT_tab"
    gdb_path = next(gdb_folder.glob("*.gdb"), None)
    if not gdb_path:
        raise FileNotFoundError("❌ GDB não encontrada na pasta informada")

    print(f"📥 Lendo {camada} da GDB {gdb_path.name}")
    df = gpd.read_file(gdb_path, layer=camada)

    conn = connect(**DB_CONFIG)
    cur = conn.cursor()
    total = 0

    for _, row in df.iterrows():
        try:
            id_lead = row.get("COD_ID")
            status = "raw"
            origem = camada.lower()
            data_conexao = row.get("DAT_CON")

            cur.execute("""
                INSERT INTO lead_bruto (
                    id, id_interno, cnae, grupo_tensao, modalidade,
                    tipo_sistema, situacao, distribuidora, origem,
                    status, data_conexao, classe, segmento,
                    subestacao, municipio_ibge, bairro, cep
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                id_lead,
                id_lead,
                row.get("CNAE"),
                row.get("GRU_TEN"),
                row.get("GRU_TAR"),
                row.get("TIP_SIST"),
                row.get("SIT_ATIV"),
                distribuidora,
                origem,
                status,
                data_conexao,
                row.get("CLAS_SUB"),
                row.get("CONJ"),
                row.get("SUB"),
                row.get("MUN"),
                row.get("BRR"),
                row.get("CEP")
            ))

            # Demanda
            dem_ponta = [int(row.get(f"DEM_P_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
            dem_fora = [int(row.get(f"DEM_F_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
            cur.execute("""
                INSERT INTO lead_demanda (id, lead_id, dem_ponta, dem_fora_ponta)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (id_lead, id_lead, dem_ponta, dem_fora))

            # Energia
            ene_p = [int(row.get(f"ENE_P_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
            ene_f = [int(row.get(f"ENE_F_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
            ene = [p + f for p, f in zip(ene_p, ene_f)]
            cur.execute("""
                INSERT INTO lead_energia (id, lead_id, ene, potencia)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (id_lead, id_lead, ene, float(row.get("DEM_CONT") or 0)))

            # Qualidade
            dic = [int(row.get(f"DIC_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
            fic = [int(row.get(f"FIC_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
            cur.execute("""
                INSERT INTO lead_qualidade (id, lead_id, dic, fic)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (id_lead, id_lead, dic, fic))

            total += 1

        except Exception as err:
            print(f"⚠️  Erro ao importar linha: {err}")
            continue

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ {total} registros de {camada} inseridos para {distribuidora.upper()} {ano}")
