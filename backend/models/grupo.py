from sqlalchemy import Column, Integer, String
from database import Base # Asegúrate de que tu Base declarativa está accesible aquí

class Grupo(Base):
    """
    Modelo para la tabla que define la entidad Grupo.
    'numGrup' es la clave primaria.
    """
    __tablename__ = "GRUPO" # Asigna el nombre real de tu tabla en la base de datos

    numGrup = Column(Integer, primary_key=True)
    carrera = Column(String(8), nullable=False) # Asumo que 'carrera' no puede ser nula por la imagen