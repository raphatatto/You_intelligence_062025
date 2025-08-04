import json
from datetime import datetime
from pathlib import Path
from packages.database.connection import get_db_connection

def get_tabelas(cursor):
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'intel_lead' AND table_type = 'BASE TABLE'
    """)
    return [row[0] for row in cursor.fetchall()]

def get_colunas(cursor, tabela):
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'intel_lead' AND table_name = %s
    """, (tabela,))
    return [
        {"nome": r[0], "tipo": r[1], "nulo": r[2] == "YES"}
        for r in cursor.fetchall()
    ]

def get_primary_keys(cursor, tabela):
    cursor.execute("""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = %s::regclass AND i.indisprimary
    """, (f"intel_lead.{tabela}",))
    return [r[0] for r in cursor.fetchall()]

def get_foreign_keys(cursor, tabela):
    cursor.execute("""
        SELECT
            kcu.column_name,
            ccu.table_name,
            ccu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'intel_lead'
          AND tc.table_name = %s
    """, (tabela,))
    return [{"coluna": r[0], "referencia": f"{r[1]}.{r[2]}"} for r in cursor.fetchall()]

def get_indices(cursor, tabela):
    cursor.execute("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = 'intel_lead' AND tablename = %s
    """, (tabela,))
    return [{"nome": r[0], "definicao": r[1]} for r in cursor.fetchall()]

def get_num_linhas(cursor, tabela):
    cursor.execute(f"SELECT COUNT(*) FROM intel_lead.{tabela}")
    return cursor.fetchone()[0]

def get_views(cursor):
    cursor.execute("""
        SELECT table_name, view_definition
        FROM information_schema.views
        WHERE table_schema = 'intel_lead'
    """)
    return [{"nome": r[0], "definicao": r[1]} for r in cursor.fetchall()]

def get_views_materializadas(cursor):
    cursor.execute("""
        SELECT matviewname, definition
        FROM pg_matviews
        WHERE schemaname = 'intel_lead'
    """)
    return [{"nome": r[0], "definicao": r[1]} for r in cursor.fetchall()]

def salvar_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def salvar_csv(path: Path, dados: list[dict]):
    import csv
    if not dados:
        return
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)

def analisar_banco():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        resultado = {
            "tabelas": {},
            "views": get_views(cursor),
            "views_materializadas": get_views_materializadas(cursor)
        }

        linhas_tabelas = []
        indices_geral = []
        fks_geral = []

        for tabela in get_tabelas(cursor):
            colunas = get_colunas(cursor, tabela)
            pks = get_primary_keys(cursor, tabela)
            fks = get_foreign_keys(cursor, tabela)
            indices = get_indices(cursor, tabela)
            linhas = get_num_linhas(cursor, tabela)

            resultado["tabelas"][tabela] = {
                "colunas": colunas,
                "primary_keys": pks,
                "foreign_keys": fks,
                "indices": indices,
                "linhas": linhas
            }

            linhas_tabelas.append({"tabela": tabela, "linhas": linhas})
            indices_geral.extend([{"tabela": tabela, **idx} for idx in indices])
            fks_geral.extend([{"tabela": tabela, **fk} for fk in fks])

        agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pasta = Path(f"data/diagnosticos/{agora}")
        pasta.mkdir(parents=True, exist_ok=True)

        salvar_json(pasta / "estrutura_banco.json", resultado)
        salvar_json(pasta / "views.json", resultado["views"])
        salvar_json(pasta / "views_materializadas.json", resultado["views_materializadas"])
        salvar_csv(pasta / "tabelas.csv", linhas_tabelas)
        salvar_csv(pasta / "indices.csv", indices_geral)
        salvar_csv(pasta / "fks.csv", fks_geral)

        print(f" Diagnóstico salvo em: {pasta.absolute()}")

if __name__ == "__main__":
    print(" Rodando análise completa do banco...")
    analisar_banco()
