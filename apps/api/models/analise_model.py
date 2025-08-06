from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Float, DateTime


Base = declarative_base()

class AnaliseMercado(Base):
    __tablename = "municipio"
    __table_args__ = {"schema": "intel_lead"}

    id = Column(float, primary_key=True)
    nome = Column(String, nullable=False)
    uf = Column(String, nullable=False)