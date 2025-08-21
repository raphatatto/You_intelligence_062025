import asyncio
from sqlalchemy import select, func
from apps.api.models.analise_model import LeadBruto
from packages.database.session import get_session
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

async def analise_mercado(municipio_id):
    municipio_id = int(municipio_id)

    async for session in get_session():
        # Número total de leads
        total_leads_stmt = select(func.count(LeadBruto.uc_id)).where(LeadBruto.municipio_id == municipio_id)
        total_leads = await session.scalar(total_leads_stmt)

        # Distribuição por tipo de sistema
        tipo_sistema_stmt = select(LeadBruto.tipo_sistema, func.count(LeadBruto.uc_id)).where(LeadBruto.municipio_id == municipio_id).group_by(LeadBruto.tipo_sistema)
        tipo_sistema_result = await session.execute(tipo_sistema_stmt)

        # Distribuição por classe de consumo
        classe_stmt = select(LeadBruto.classe, func.count(LeadBruto.uc_id)).where(LeadBruto.municipio_id == municipio_id).group_by(LeadBruto.classe)
        classe_result = await session.execute(classe_stmt)

        # Distribuição por segmento
        segmento_stmt = select(LeadBruto.segmento, func.count(LeadBruto.uc_id)).where(LeadBruto.municipio_id == municipio_id).group_by(LeadBruto.segmento)
        segmento_result = await session.execute(segmento_stmt)

        # Distribuição por subestação
        subestacao_stmt = select(LeadBruto.subestacao, func.count(LeadBruto.uc_id)).where(LeadBruto.municipio_id == municipio_id).group_by(LeadBruto.subestacao)
        subestacao_result = await session.execute(subestacao_stmt)

        # Densidade de leads por bairro
        bairro_stmt = select(LeadBruto.bairro, func.count(LeadBruto.uc_id)).where(LeadBruto.municipio_id == municipio_id).group_by(LeadBruto.bairro)
        bairro_result = await session.execute(bairro_stmt)

        # Exibindo os resultados
        print(f"Total de Leads para o Município ID {municipio_id}: {total_leads}")
        
        tipo_sistema_data = [(tipo, count) for tipo, count in tipo_sistema_result]
        classe_data = [(classe, count) for classe, count in classe_result]
        segmento_data = [(segmento, count) for segmento, count in segmento_result]
        subestacao_data = [(subestacao, count) for subestacao, count in subestacao_result]
        bairro_data = [(bairro, count) for bairro, count in bairro_result]

        # 1. Gráfico de Tipo de Sistema
        tipo_sistema_df = pd.DataFrame(tipo_sistema_data, columns=["Tipo de Sistema", "Quantidade"])
        plt.figure(figsize=(10, 6))
        sns.barplot(x="Quantidade", y="Tipo de Sistema", data=tipo_sistema_df, palette="Blues_d")
        plt.title('Distribuição de Leads por Tipo de Sistema')
        plt.xlabel('Quantidade de Leads')
        plt.ylabel('Tipo de Sistema')

        # 2. Gráfico de Classe de Consumo
        classe_df = pd.DataFrame(classe_data, columns=["Classe", "Quantidade"])
        plt.figure(figsize=(10, 6))
        sns.barplot(x="Quantidade", y="Classe", data=classe_df, palette="Blues_d")
        plt.title('Distribuição de Leads por Classe de Consumo')
        plt.xlabel('Quantidade de Leads')
        plt.ylabel('Classe de Consumo')

        # 3. Gráfico de Segmento
        segmento_df = pd.DataFrame(segmento_data, columns=["Segmento", "Quantidade"])
        plt.figure(figsize=(10, 6))
        sns.barplot(x="Quantidade", y="Segmento", data=segmento_df, palette="Blues_d")
        plt.title('Distribuição de Leads por Segmento')
        plt.xlabel('Quantidade de Leads')
        plt.ylabel('Segmento')

        # 4. Gráfico de Subestação
        subestacao_df = pd.DataFrame(subestacao_data, columns=["Subestação", "Quantidade"])
        plt.figure(figsize=(10, 6))
        sns.barplot(x="Quantidade", y="Subestação", data=subestacao_df, palette="Blues_d")
        plt.title('Distribuição de Leads por Subestação')
        plt.xlabel('Quantidade de Leads')
        plt.ylabel('Subestação')

        # 5. Gráfico de Densidade de Leads por Bairro
        bairro_df = pd.DataFrame(bairro_data, columns=["Bairro", "Quantidade"])
        plt.figure(figsize=(12, 8))
        sns.barplot(x="Quantidade", y="Bairro", data=bairro_df, palette="Blues_d")
        plt.title('Densidade de Leads por Bairro')
        plt.xlabel('Quantidade de Leads')
        plt.ylabel('Bairro')

        # 6. Gráfico de Potencial de Mercado (Classe vs Tipo de Sistema)
        classe_tipo_df = pd.DataFrame(classe_data + tipo_sistema_data, columns=["Categoria", "Quantidade"])
        plt.figure(figsize=(10, 6))
        sns.barplot(x="Quantidade", y="Categoria", data=classe_tipo_df, palette="Blues_d")
        plt.title('Potencial de Mercado por Classe e Tipo de Sistema')
        plt.xlabel('Quantidade de Leads')
        plt.ylabel('Categoria (Classe ou Tipo de Sistema)')

        # Exibir todos os gráficos ao final
        plt.show()

if __name__ == "__main__":
    municipio_id = input("Digite o ID do município para análise: ").strip()
    asyncio.run(analise_mercado(municipio_id))
