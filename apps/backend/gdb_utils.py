import geopandas as gpd
import fiona
from pathlib import Path

def listar_camadas(gdb_path: Path):
    """Lista todas as camadas disponíveis dentro de um .gdb"""
    return fiona.listlayers(gdb_path)

def ler_gdb(gdb_path: Path, layer: str = None):
    """Lê uma camada específica de um .gdb"""
    if layer is None:
        layers = listar_camadas(gdb_path)
        if not layers:
            raise ValueError("Nenhuma camada encontrada.")
        layer = layers[0]
    print(f"Lendo camada '{layer}' de {gdb_path.name}")
    return gpd.read_file(gdb_path, layer=layer)
