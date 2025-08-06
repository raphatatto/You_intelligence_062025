from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class analise(BaseModel):
    id:float
    nome:str
    uf:str

