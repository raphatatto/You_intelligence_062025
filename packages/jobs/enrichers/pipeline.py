from packages.jobs.enrichers.enrich_geo_job import enrich_geo_info
from packages.jobs.enrichers.enrich_cnpj_job import enrich_cnpj

def rodar_pipeline_enriquecimento():
    print("🚀 Iniciando pipeline de enriquecimento...")
    
    # Etapa 1: Geolocalização
    try:
        enrich_geo_info()
    except Exception as e:
        print("❌ Erro ao enriquecer com Google:", str(e))
    
    # Etapa 2: Busca de CNPJ
    try:
        enrich_cnpj()
    except Exception as e:
        print("❌ Erro ao enriquecer CNPJ:", str(e))
    
    print("✅ Pipeline de enriquecimento concluído.")
