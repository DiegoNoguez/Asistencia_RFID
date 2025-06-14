from pydantic import BaseModel
from datetime import time

class MateriaBase(BaseModel):
    claveM: str
    nomMateria: str | None = None

class MateriaResponse(MateriaBase):
    hrInicio: time
    hrFinal: time
    grupos: list[str] = [] # Para frontend