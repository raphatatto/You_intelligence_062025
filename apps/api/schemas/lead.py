from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LeadOut(BaseModel):
    id: str
    nome: Optional[str]
    cnpj: Optional[str]
    classe: Optional[str]
    subgrupo: Optional[str]
    modalidade: Optional[str]
    estado: Optional[str]
    municipio: Optional[str]
    distribuidora: Optional[str]
    potencia: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    segmento: Optional[str]
    status: Optional[str]
    cnae: Optional[str]
    dicMed: Optional[float]
    ficMed: Optional[float]
    dicMes: Optional[List[float]]
    ficMes: Optional[List[float]]

class LeadList(BaseModel):
    total: int
    items: List[LeadOut]

class LeadDetail(LeadOut):
    data_conexao: Optional[datetime] = None

class LeadQualidade(BaseModel):
    dicMed: Optional[float]
    ficMed: Optional[float]
    dicMes: Optional[List[float]]
    ficMes: Optional[List[float]]

class LeadMapOut(BaseModel):
    id: str
    latitude: float
    longitude: float
    classe: Optional[str]
    subgrupo: Optional[str]
    potencia: Optional[float]
    distribuidora: Optional[str]
    status: Optional[str]

class LeadResumo(BaseModel):
    total_leads: int
    total_com_cnpj: int
    total_enriquecidos: int
    media_consumo: Optional[float]
    media_potencia: Optional[float]
    por_classe: dict[str, int]
