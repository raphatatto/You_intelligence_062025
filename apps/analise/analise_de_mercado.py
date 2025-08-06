
from sqlalchemy import func

from apps.api.schemas.analise_schema import analise
from packages.database.session import get_session
import sys
import os
# Configuração do banco (troque para o seu)

# Exemplo PostgreSQL: "postgresql+psycopg2://usuario:senha@localhost/meubanco"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
session =(get_session)

# Perguntar município
nome_municipio = input("Digite o nome do município: ")

# Contar leads com esse município
total = session.query(func.count(analise.id)).filter(analise.municipio_nome == nome_municipio).scalar()

print(f"\nMunicípio: {nome_municipio}")
print(f"Total de leads: {total}")

# Fechar sessão
session.close()


