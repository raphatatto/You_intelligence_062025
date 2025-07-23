from packages.jobs.enrichers.enrich_geo_job import enriquecer_google
from packages.jobs.enrichers.enrich_cnpj_job import enriquecer_cnpj

def rodar_pipeline_enriquecimento():
    print("🚀 Iniciando pipeline de enriquecimento...")
    
    # Etapa 1: Geolocalização
    try:
        enriquecer_google()
    except Exception as e:
        print("❌ Erro ao enriquecer com Google:", str(e))
    
    # Etapa 2: Busca de CNPJ
    try:
        enriquecer_cnpj()
    except Exception as e:
        print("❌ Erro ao enriquecer CNPJ:", str(e))
    
    print("✅ Pipeline de enriquecimento concluído.")
