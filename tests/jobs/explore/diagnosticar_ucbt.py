import sys
import geopandas as gpd
from fiona import listlayers
from pathlib import Path

def diagnosticar_gdb(caminho_gdb: Path):
    print(f"📁 Verificando GDB: {caminho_gdb}\n")

    # Listar todas as camadas
    try:
        camadas = listlayers(str(caminho_gdb))
        print("📚 Camadas encontradas:")
        for camada in camadas:
            print(f" - {camada}")
    except Exception as e:
        print(f"❌ Erro ao listar camadas: {e}")
        return

    print("\n🔍 Inspecionando colunas por camada:\n")
    for camada in camadas:
        try:
            df = gpd.read_file(str(caminho_gdb), layer=camada)
            print(f"🔸 Camada: {camada}")
            print(f"   → {len(df)} registros")
            print(f"   → Colunas: {list(df.columns)}\n")
        except Exception as e:
            print(f"   ⚠️ Erro ao ler camada '{camada}': {e}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python diagnosticar_gdb.py <caminho_para_o_arquivo_gdb>")
        sys.exit(1)

    caminho_gdb = Path(sys.argv[1])
    if not caminho_gdb.exists():
        print(f"❌ Arquivo não encontrado: {caminho_gdb}")
        sys.exit(1)

    diagnosticar_gdb(caminho_gdb)
