from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Float, DateTime


Base = declarative_base()

class AnaliseMercado(Base):
    __tablename__ = "municipio"
    __table_args__ = {"schema": "intel_lead"}

    id = Column(Float, primary_key=True)
    nome = Column(String, nullable=False)
    uf = Column(String, nullable=False)


class LeadBruto(Base):
    __tablename__ = "lead_bruto"
    __table_args__ ={"schema": "intel_lead"}

    uc_id =  Column(String, primary_key=True)
    import_id = Column(String, nullable=False)
    cod_id =  Column(String, nullable=False)
    distribuidora_id = Column (Float, nullable=False)
    origem =  Column(String, nullable=False)
    ano =  Column (Float, nullable=False)
    status =  Column(String, nullable=False)
    data_conexao =  Column(DateTime, nullable=False)
    cnae =  Column(String, nullable=False)
    grupo_tensao =  Column(String, nullable=False)
    modalidade =  Column(String, nullable=False)
    tipo_sistema =  Column(String, nullable=False)
    situacao =  Column(String, nullable=False)
    classe =  Column(String, nullable=False)
    segmento =  Column(String, nullable=False)
    subestacao =  Column(String, nullable=False)
    municipio_id =  Column(Integer, nullable=True)
    bairro = Column(String, nullable=False)
    cep =  Column(String, nullable=False)
    pac =  Column(String, nullable=False)
    pn_con =  Column(String, nullable=False)
    descricao =  Column(String, nullable=False)
    latitude =  Column(Float, nullable=False)
    longitude =  Column(Float, nullable=False)