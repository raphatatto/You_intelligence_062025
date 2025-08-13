from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class analise(BaseModel):
    id:float
    nome:str
    uf:str


class LeadBrutoOut(BaseModel):
    uc_id: str
    import_id:Optional[str] = None
    cod_id: Optional[str] = None
    distribuidora_id:Optional [float] = None
    origem: Optional[str] = None
    ano: Optional [float]
    status: Optional[str] = None
    data_conexao: Optional[datetime] = None
    cnae: Optional[str] = None
    grupo_tensao: Optional[str] = None
    modalidade: Optional[str] = None
    tipo_sistema: Optional[str] = None
    situacao: Optional[str] = None
    classe: Optional[str] = None
    segmento: Optional[str] = None
    subestacao: Optional[str] = None
    municipio_id: Optional[str] = None
    bairro:Optional[str] = None
    cep: Optional[str] = None
    pac: Optional[int] = None
    pn_con: Optional[str] = None
    descricao: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None