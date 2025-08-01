from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, date

# -------------------------------
# 📌 Schema principal de listagem
# -------------------------------

class LeadOut(BaseModel):
    uc_id: str
    nome_fantasia: Optional[str] = None
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    cnae: Optional[str] = None
    cnae_descricao: Optional[str] = None
    classe: Optional[str] = None
    grupo_tensao: Optional[str] = None
    modalidade: Optional[str] = None
    estado: Optional[str] = None
    municipio: Optional[str] = None
    distribuidora_nome: Optional[str] = None
    pac: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    segmento_desc: Optional[str] = None
    status: Optional[str] = None
    media_dic: Optional[float] = None
    media_fic: Optional[float] = None

class LeadList(BaseModel):
    total: int
    items: List[LeadOut]


# -------------------------------
# 📋 Schema detalhado (backend)
# -------------------------------

class LeadDetalhado(BaseModel):
    id: str
    uc_id: str
    cod_id: Optional[str]
    import_id: Optional[str]
    distribuidora_id: Optional[int]
    distribuidora_nome: Optional[str]
    origem: Optional[str]
    ano: Optional[int]
    status: Optional[str]
    data_conexao: Optional[date]
    grupo_tensao: Optional[str]
    modalidade: Optional[str]
    tipo_sistema: Optional[str]
    situacao: Optional[str]
    classe: Optional[str]
    cnae: Optional[str]
    municipio_id: Optional[int]
    municipio: Optional[str]
    estado: Optional[str]
    bairro: Optional[str]
    cep: Optional[str]
    pac: Optional[float]
    pn_con: Optional[str]
    descricao: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    cnae_descricao: Optional[str]
    segmento_desc: Optional[str]
    distribuidora_nome: Optional[str]
    cnpj: Optional[str]
    nome_fantasia: Optional[str]
    razao_social: Optional[str]
    telefone: Optional[str]
    email: Optional[str]
    site: Optional[str]
    receita_situacao: Optional[str]
    receita_abertura: Optional[str]
    receita_natureza: Optional[str]
    receita_porte: Optional[str]
    receita_capital_social: Optional[float]
    receita_atividade_principal: Optional[str]
    receita_municipio: Optional[str]
    receita_uf: Optional[str]
    enriched_at: Optional[datetime]

    media_dic: Optional[float]
    media_fic: Optional[float]
    soma_horas_sem_rede: Optional[float]

    media_energia_total: Optional[float]
    media_energia_ponta: Optional[float]
    media_energia_fora: Optional[float]

    media_demanda_total: Optional[float]
    media_demanda_ponta: Optional[float]
    media_demanda_fora: Optional[float]


# -------------------------------
# 📈 Qualidade (usado isolado)
# -------------------------------

class LeadQualidade(BaseModel):
    dicMed: Optional[float] = None
    ficMed: Optional[float] = None
    dicMes: Optional[List[float]] = None
    ficMes: Optional[List[float]] = None


# -------------------------------
# 🗺️ Mapa interativo
# -------------------------------

class LeadMapOut(BaseModel):
    uc_id: str
    latitude: float
    longitude: float
    classe: Optional[str] = None
    grupo_tensao: Optional[str] = None
    potencia: Optional[float] = None
    distribuidora: Optional[str] = None
    status: Optional[str] = None


# -------------------------------
# 📊 Resumo de dados
# -------------------------------

class LeadResumo(BaseModel):
    total_leads: int
    total_com_cnpj: int
    total_enriquecidos: int
    media_potencia: Optional[float] = None
    por_classe: Dict[str, int]


# -------------------------------
# 🌍 Enriquecimento Google Maps
# -------------------------------

class GeoGoogleOut(BaseModel):
    nome_estabelecimento: Optional[str] = None
    endereco_formatado: Optional[str] = None
    telefone: Optional[str] = None
    site: Optional[str] = None
    atualizado_em: Optional[datetime] = None


# -------------------------------
# 📦 Status de importação
# -------------------------------

class ImportStatusOut(BaseModel):
    distribuidora: str
    ano: int
    camada: str
    status: str
    data_execucao: datetime
