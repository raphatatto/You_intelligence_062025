# PS C:\Users\GuilhermeCostaProenç\OneDrive - You On\Área de Trabalho\You_intelligence_062025> python tests/jobs/explore/diagnosticar_ucbt.py "data/downloads/CPFL_Paulista_2023.gdb"

import sys
import geopandas as gpd
from fiona import listlayers
from pathlib import Path

def diagnosticar_ucbt(caminho_gdb: Path):
    print(f"📁 Verificando GDB: {caminho_gdb}\n")

    # Listar todas as camadas
    try:
        camadas = listlayers(str(caminho_gdb))
        camada_ucbt = next((c for c in camadas if c.upper().startswith("UCBT")), None)

        if not camada_ucbt:
            print("❌ Nenhuma camada começando com 'UCBT' foi encontrada.")
            return

        print(f"🔍 Camada UCBT identificada: {camada_ucbt}")
    except Exception as e:
        print(f"❌ Erro ao listar camadas: {e}")
        return

    try:
        df = gpd.read_file(str(caminho_gdb), layer=camada_ucbt)
        print(f"\n🔸 Camada: {camada_ucbt}")
        print(f"   → {len(df)} registros")
        print(f"   → Colunas: {list(df.columns)}\n")
    except Exception as e:
        print(f"❌ Erro ao ler camada '{camada_ucbt}': {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python diagnosticar_ucbt.py <caminho_para_o_arquivo_gdb>")
        sys.exit(1)

    caminho_gdb = Path(sys.argv[1])
    if not caminho_gdb.exists():
        print(f"❌ Arquivo não encontrado: {caminho_gdb}")
        sys.exit(1)

    diagnosticar_ucbt(caminho_gdb)
