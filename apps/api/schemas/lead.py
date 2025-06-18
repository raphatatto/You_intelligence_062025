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
