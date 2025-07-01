from pathlib import Path
from backend.gdb_utils import ler_gdb

def encontrar_leads_dic_fic(threshold_dic=10, threshold_fic=10):
    gdb_path = Path("data/processed/CPFL_Paulista_63_2023-12-31_V11_20241223-08-40-44.gdb")
    gdf = ler_gdb(gdb_path)
    
    print("Colunas disponíveis:", gdf.columns)
    
    # Exemplo: adaptando para nomes reais de colunas
    leads_filtrados = gdf[(gdf["DIC"] > threshold_dic) & (gdf["FIC"] > threshold_fic)]
    
    return {
        "total": len(leads_filtrados),
        "leads": leads_filtrados.to_dict(orient="records")
    }
