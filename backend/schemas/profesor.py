from pydantic import BaseModel
from typing import List
from .materia import MateriaResponse

class ProfesorBase(BaseModel):
    claveP: int
    nombre: str
    ape1: str
    idRol: int

class ProfesorResponse(ProfesorBase):
    class Config:
        from_attributes = True