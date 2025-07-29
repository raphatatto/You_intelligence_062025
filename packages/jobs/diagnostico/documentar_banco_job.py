import json
import pandas as pd
from pathlib import Path
from graphviz import Digraph
from datetime import datetime

# 🧠 Detecta pasta mais recente
DIAG_BASE = Path("data/diagnosticos")
LATEST_DIR = max(DIAG_BASE.iterdir(), key=lambda p: p.stat().st_mtime)
ESTRUTURA_PATH = LATEST_DIR / "estrutura_banco.json"

def gerar_excel(estrutura, pasta_destino):
    tabelas_info = []
    colunas_info = []
    fks_info = []
    indices_info = []

    for tabela, dados in estrutura["tabelas"].items():
        tabelas_info.append({
            "tabela": tabela,
            "qtd_colunas": len(dados["colunas"]),
            "qtd_indices": len(dados["indices"]),
            "qtd_fks": len(dados["foreign_keys"]),
            "linhas": dados["linhas"]
        })

        for col in dados["colunas"]:
            colunas_info.append({
                "tabela": tabela,
                **col
            })

        for fk in dados["foreign_keys"]:
            fks_info.append({
                "tabela": tabela,
                "coluna": fk["coluna"],
                "referencia": fk["referencia"]
            })

        for idx in dados["indices"]:
            indices_info.append({
                "tabela": tabela,
                **idx
            })

    path = pasta_destino / "estrutura_banco.xlsx"
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame(tabelas_info).to_excel(writer, sheet_name="Tabelas", index=False)
        pd.DataFrame(colunas_info).to_excel(writer, sheet_name="Colunas", index=False)
        pd.DataFrame(fks_info).to_excel(writer, sheet_name="ForeignKeys", index=False)
        pd.DataFrame(indices_info).to_excel(writer, sheet_name="Indices", index=False)

    print(f" Excel salvo em: {path}")

def gerar_dot(estrutura, pasta_destino):
    dot = Digraph(comment="Relacionamentos FK")
    for tabela, dados in estrutura["tabelas"].items():
        dot.node(tabela)
        for fk in dados["foreign_keys"]:
            destino = fk["referencia"].split(".")[0]
            dot.edge(tabela, destino, label=fk["coluna"])

    dot_path = pasta_destino / "estrutura_banco.dot"
    dot.save(dot_path)
    print(f" DOT salvo em: {dot_path}")

def gerar_markdown(estrutura, pasta_destino):
    path = pasta_destino / "diagnostico.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Diagnóstico do Banco (intel_lead)\n")
        f.write(f"> Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")

        for tabela, dados in estrutura["tabelas"].items():
            f.write(f"##  {tabela}\n")
            f.write(f"- Colunas: {len(dados['colunas'])}\n")
            f.write(f"- PK: {', '.join(dados['primary_keys']) if dados['primary_keys'] else ' nenhuma'}\n")
            f.write(f"- FKs: {len(dados['foreign_keys'])}\n")
            f.write(f"- Índices: {len(dados['indices'])}\n")
            f.write(f"- Linhas: {dados['linhas']}\n")
            f.write("\n")

    print(f" Markdown salvo em: {path}")

def documentar_banco():
    if not ESTRUTURA_PATH.exists():
        raise FileNotFoundError("Arquivo estrutura_banco.json não encontrado.")

    with open(ESTRUTURA_PATH, "r", encoding="utf-8") as f:
        estrutura = json.load(f)

    pasta_destino = ESTRUTURA_PATH.parent
    gerar_excel(estrutura, pasta_destino)
    gerar_dot(estrutura, pasta_destino)
    gerar_markdown(estrutura, pasta_destino)

if __name__ == "__main__":
    print(" Documentando estrutura do banco...")
    documentar_banco()
