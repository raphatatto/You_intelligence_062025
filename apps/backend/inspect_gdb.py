import fiona

# Caminho completo para a pasta .gdb
gdb_path = "C:/vai/You_intelligence_062025/data/processed/CPFL_Paulista_63_2023-12-31_V11_20241223-0817.gdb"

# Lista todas as camadas (camadas = tabelas com geodados)
camadas = fiona.listlayers(gdb_path)
print("Camadas disponíveis:", camadas)

# Exemplo: carregar a primeira camada
import geopandas as gpd
gdf = gpd.read_file(gdb_path, layer=camadas[0])
print(gdf.head())
