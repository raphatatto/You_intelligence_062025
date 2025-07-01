import geopandas as gpd
from pathlib import Path

def encontrar_leads_dic_fic(threshold_dic=10, threshold_fic=10):
    caminho_sp = Path("data/processed/CPFL_Paulista_*.gdb")
    caminho_rj = Path("data/processed/Enel_RJ_*.gdb")

    arquivos = list(caminho_sp.parent.glob("*.gdb"))

    leads_encontrados = []

    for gdb in arquivos:
        try:
            gdf = gpd.read_file(gdb, layer=0)
            filtrado = gdf[(gdf["DIC"] > threshold_dic) & (gdf["FIC"] > threshold_fic)]
            for _, row in filtrado.iterrows():
                leads_encontrados.append({
                    "nome": row.get("NomeUC", "sem_nome"),
                    "DIC": row["DIC"],
                    "FIC": row["FIC"],
                    "bairro": row.get("Bairro"),
                    "uf": row.get("UF")
                })
        except Exception as e:
            print(f"Erro ao processar {gdb.name}: {e}")

    return leads_encontrados
