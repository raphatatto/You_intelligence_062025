from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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

class LeadDetalhadoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uc_id: str
    import_id: Optional[str] = None
    cod_id: Optional[str] = None
    distribuidora_id: Optional[int] = None
    origem: Optional[str] = None
    ano: Optional[int] = None
    status: Optional[str] = None
    data_conexao: Optional[datetime] = None
    grupo_tensao: Optional[str] = None
    modalidade: Optional[str] = None
    tipo_sistema: Optional[str] = None
    situacao: Optional[str] = None
    classe: Optional[str] = None
    cnae: Optional[str] = None
    municipio_id: Optional[int] = None
    municipio: Optional[str] = None
    estado:Optional[str]
    bairro: Optional[str] = None
    cep: Optional[str] = None
    pac: Optional[float] = None
    pn_con: Optional[str] = None
    descricao: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distribuidora_nome: Optional[str] = None
    cnae_descricao: Optional[str] = None
    segmento_desc: Optional[str] = None
    cnpj:Optional[str] = None
    nome_fantasia:Optional[str] = None
    razao_social:Optional[str] = None
    telefone:Optional[str] = None
    email:Optional[str] = None
    site:Optional[str] = None
    receita_situacao:Optional[str] = None
    receita_abertura:Optional[str] = None
    receita_natureza:Optional[str] = None
    receita_porte:Optional[str] = None
    receita_capital_social:Optional[str] = None
    receita_atividade_principal:Optional[str] = None
    receita_municipio:Optional[str] = None
    receita_uf:Optional[str] = None
    enriched_at:Optional[str] = None
    media_dic:Optional[float] = None
    soma_horas_sem_rede:Optional[datetime] = None
    media_energia_total:Optional[float] = None
    media_demanda_ponta: Optional[float] = None
    media_demanda_fora: Optional[float] = None



class EmpresaInfo(BaseModel):
    razao_social: Optional[str]
    nome_fantasia: Optional[str]
    cnpj: Optional[str]
    cnae: Optional[str]
    cnae_descricao: Optional[str]
    email: Optional[str]
    telefone: Optional[str]
    endereco: Optional[str]


class GeoInfo(BaseModel):
    latitude: Optional[float]
    longitude: Optional[float]
    cep: Optional[str]


class DiagnosticoUC(BaseModel):
    pontuacoes: Optional[dict]
    notas: Optional[dict]
    sugestoes: Optional[List[str]]
    alerta: Optional[str]


class UnidadeConsumidora(BaseModel):
    uc_id: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    municipio: Optional[str]
    uf: Optional[str]
    classe: Optional[str]
    modalidade: Optional[str]
    grupo_tensao: Optional[str]
    distancia_metros: Optional[float]

    
class DetetiveResponse(BaseModel):
    entrada: Dict[str, Any]
    logs: List[str]
    etapas: Dict[str, Any]
    possiveis_matches: List[Dict[str, Any]]
    match_principal: Optional[Dict[str, Any]] = None
    diagnostico: Optional[Dict[str, Any]] = None
    score_confianca: float
