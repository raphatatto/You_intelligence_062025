from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class LeadBruto(Base):
    __tablename__ = "lead_bruto"

    id = Column(String, primary_key=True, index=True)
    nome_uc = Column(String, nullable=True)
    cnpj = Column(String, nullable=True, index=True)
    classe = Column(String, nullable=True)
    subgrupo = Column(String, nullable=True)
    modalidade = Column(String, nullable=True)
    segmento = Column(String, nullable=True)        # home | cni | gtd
    municipio_ibge = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    data_conexao = Column(DateTime, nullable=True)
