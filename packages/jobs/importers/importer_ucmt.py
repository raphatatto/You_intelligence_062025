import geopandas as gpd
from pathlib import Path
from datetime import datetime
from packages.database.connection import get_db_cursor

def parse_data_conexao(raw_data):
    if isinstance(raw_data, str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw_data.strip(), fmt).date()
            except ValueError:
                continue
    elif isinstance(raw_data, datetime):
        return raw_data.date()
    return None

def importar_ucmt(gdb_folder: Path, distribuidora: str, ano: int):
    camada = "UCMT_tab"
    gdb_path = gdb_folder
    print(f"📥 Lendo camada '{camada}' da GDB '{gdb_path.name}'")
    df = gpd.read_file(gdb_path, layer=camada)
    total = 0
    total_linhas = len(df)

    batch_bruto, batch_energia, batch_demanda, batch_qualidade = [], [], [], []
    BATCH_SIZE = 500

    def flush_batches(cur):
        if batch_bruto:
            cur.executemany("""
                INSERT INTO lead_bruto (
                    id, id_interno, cnae, grupo_tensao, modalidade,
                    tipo_sistema, situacao, distribuidora, origem,
                    status, data_conexao, classe, segmento,
                    subestacao, municipio_ibge, bairro, cep,
                    pac, pn_con, sit_atv
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, batch_bruto)
            batch_bruto.clear()
        if batch_energia:
            cur.executemany("""
                INSERT INTO lead_energia (id, lead_id, ene, potencia)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, batch_energia)
            batch_energia.clear()
        if batch_demanda:
            cur.executemany("""
                INSERT INTO lead_demanda (id, lead_id, dem_ponta, dem_fora_ponta)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, batch_demanda)
            batch_demanda.clear()
        if batch_qualidade:
            cur.executemany("""
                INSERT INTO lead_qualidade (id, lead_id, dic, fic)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, batch_qualidade)
            batch_qualidade.clear()

    with get_db_cursor(commit=True) as cur:
        for i, (_, row) in enumerate(df.iterrows(), start=1):
            try:
                id_lead = row.get("COD_ID")
                status = "raw"
                origem = camada.lower()
                data_conexao = parse_data_conexao(row.get("DAT_CON"))

                batch_bruto.append((
                    id_lead, id_lead,
                    row.get("CNAE"), row.get("GRU_TEN"), row.get("GRU_TAR"),
                    row.get("TIP_SIST"), row.get("SIT_ATIV"),
                    distribuidora, origem, status, data_conexao,
                    row.get("CLAS_SUB"), row.get("CONJ"), row.get("SUB"),
                    row.get("MUN"), row.get("BRR"), row.get("CEP"),
                    row.get("PAC"), row.get("PN_CON"), row.get("SIT_ATV")
                ))

                ene = [int(row.get(f"ENE_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
                batch_energia.append((id_lead, id_lead, ene, float(row.get("DEM_CONT") or 0)))

                demanda = [int(row.get(f"DEM_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
                batch_demanda.append((id_lead, id_lead, [], demanda))

                dic = [int(row.get(f"DIC_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
                fic = [int(row.get(f"FIC_{str(m).zfill(2)}") or 0) for m in range(1, 13)]
                batch_qualidade.append((id_lead, id_lead, dic, fic))

                total += 1
                if total % BATCH_SIZE == 0:
                    flush_batches(cur)
                    print(f"🧮 Progresso: {total}/{total_linhas} registros processados...")

            except Exception as err:
                print(f"⚠️  Erro ao importar linha {id_lead}: {err}")
                continue

        flush_batches(cur)
    print(f"✅ {total} registros de '{camada}' inseridos para {distribuidora.upper()} - {ano}")
