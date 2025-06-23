from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LeadBase(BaseModel):
    id: str
    nome_uc: str | None = None
    cnpj: str | None = None
    classe: str | None = None
    segmento: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = ConfigDict(from_attributes=True)

class LeadDetail(LeadBase):
    subgrupo: str | None = None
    modalidade: str | None = None
    municipio_ibge: int | None = None
    data_conexao: datetime | None = None

class LeadList(BaseModel):
    total: int
    items: list[LeadBase]

class LeadMapOut(BaseModel):
    id: str
    latitude: float
    longitude: float
    classe: str | None = None
    subgrupo: str | None = None
    potencia: float | None = None
    distribuidora: str | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class LeadResumo(BaseModel):
    total_leads: int
    total_com_cnpj: int
    total_enriquecidos: int
    media_consumo: float | None
    media_potencia: float | None
    por_classe: dict[str, int]
