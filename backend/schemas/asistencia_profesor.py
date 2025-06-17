from pydantic import BaseModel
from datetime import date
from typing import Optional

class AsistenciaProfesorBase(BaseModel):
    claveP: int
    claveM: str
    fecha: Optional[date] = None
    asistio: int = 1
    porcentaje_asistencia: float = 100.0

class AsistenciaProfesorCreate(AsistenciaProfesorBase):
    pass

class AsistenciaProfesor(AsistenciaProfesorBase):
    id_asistencia: int
    
    class Config:
        orm_mode = True

class AsistenciaProfesorConsulta(BaseModel):
    claveP: int
    nombre: str
    materia: str
    claveM: str
    asistencias: int
    total_clases: int
    porcentaje: float

class RegistroAsistenciaProfesor(BaseModel):
    claveP: int
    claveM: str
    presente: bool = True  # Se convertirá a 1/0 en el endpoint