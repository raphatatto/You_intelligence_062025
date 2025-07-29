import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

# Caminhos
DIAG_DIR = Path("data/diagnosticos")
LATEST_DIR = max(DIAG_DIR.iterdir(), key=lambda p: p.stat().st_mtime)
ESTRUTURA_PATH = LATEST_DIR / "estrutura_banco.json"
SUGESTOES_PATH = LATEST_DIR / "sugestoes_melhorias.json"
SUGESTOES_MD_PATH = LATEST_DIR / "sugestoes_melhorias.md"

def recomendar_melhorias():
    with open(ESTRUTURA_PATH, "r", encoding="utf-8") as f:
        estrutura = json.load(f)

    sugestoes = []
    score = 100

    # 🔎 Preparações
    colunas_gerais = defaultdict(list)
    indices_gerais = defaultdict(list)
    for tabela, dados in estrutura["tabelas"].items():
        for c in dados["colunas"]:
            colunas_gerais[c["nome"]].append(tabela)
        for i in dados["indices"]:
            indices_gerais[tabela].append(i["nome"])

    # 🚨 1. Falta de PKs
    for tabela, dados in estrutura["tabelas"].items():
        if not dados["primary_keys"]:
            sugestoes.append({
                "tipo": "chave primária",
                "recomendacao": f"Adicionar PK em `{tabela}`",
                "motivacao": "Sem PK definida — risco de duplicidade e joins problemáticos"
            })
            score -= 7

    # 🚨 2. Tabelas grandes sem índice
    for tabela, dados in estrutura["tabelas"].items():
        if dados["linhas"] > 1_000_000 and not dados["indices"]:
            sugestoes.append({
                "tipo": "índice",
                "recomendacao": f"Adicionar índice em `{tabela}`",
                "motivacao": f"Tabela com {dados['linhas']} registros e sem nenhum índice"
            })
            score -= 6

    # 🚨 3. Tabelas sem FKs
    for tabela, dados in estrutura["tabelas"].items():
        if not dados["foreign_keys"]:
            sugestoes.append({
                "tipo": "foreign key",
                "recomendacao": f"Avaliar se `{tabela}` deveria ter FKs",
                "motivacao": "Sem FKs — pode indicar acoplamento fraco ou falta de modelagem relacional"
            })
            score -= 3

    # 🚨 4. Views genéricas
    for view in estrutura["views"]:
        nome = view["nome"].lower()
        if any(p in nome for p in ["tmp", "teste", "debug"]):
            sugestoes.append({
                "tipo": "view",
                "recomendacao": f"Excluir ou revisar view `{view['nome']}`",
                "motivacao": "Nome indica uso temporário ou não produtivo"
            })
            score -= 2

    # 🚨 5. Colunas repetidas demais
    for nome_coluna, tabelas in colunas_gerais.items():
        if len(tabelas) >= 4 and nome_coluna not in ("id", "created_at", "updated_at", "status"):
            sugestoes.append({
                "tipo": "coluna",
                "recomendacao": f"Padronizar ou revisar coluna `{nome_coluna}`",
                "motivacao": f"Presente em {len(tabelas)} tabelas — possível desnormalização"
            })
            score -= 1

    # 🚨 6. Colunas de tipo genérico
    for tabela, dados in estrutura["tabelas"].items():
        tipos_gen = sum(1 for c in dados["colunas"] if c["tipo"] in ("text", "jsonb", "character varying"))
        total = len(dados["colunas"])
        if total and tipos_gen / total > 0.6:
            sugestoes.append({
                "tipo": "coluna",
                "recomendacao": f"Revisar granularidade de tipos em `{tabela}`",
                "motivacao": "Mais de 60% dos campos são genéricos (text/jsonb/varchar)"
            })
            score -= 3

    # ✅ Resultado final
    resultado = {
        "score_geral": max(score, 0),
        "sugestoes": sugestoes
    }

    # Salvar JSON
    with open(SUGESTOES_PATH, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    # Salvar Markdown
    with open(SUGESTOES_MD_PATH, "w", encoding="utf-8") as f:
        f.write(f"# Sugestões de Melhorias — {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        f.write(f"**Score geral:** {resultado['score_geral']}/100\n\n")
        for i, s in enumerate(sugestoes, 1):
            f.write(f"## {i}. {s['recomendacao']}\n")
            f.write(f"- Tipo: {s['tipo']}\n")
            f.write(f"- Motivo: {s['motivacao']}\n\n")

    print(f" Diagnóstico salvo em {SUGESTOES_PATH}")
    print(f" Score final: {resultado['score_geral']} — {len(sugestoes)} recomendações")

if __name__ == "__main__":
    print(" Rodando análise de melhorias...")
    recomendar_melhorias()
