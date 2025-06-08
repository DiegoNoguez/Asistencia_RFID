from sqlalchemy import Column, String, Time
from database import Base # Asegúrate de que tu Base declarativa está accesible aquí

class Materia(Base):
    """
    Modelo para la tabla que representa una Materia (asignatura).
    'claveM' es la clave primaria.
    """
    __tablename__ = "MATERIA" # Asigna el nombre real de tu tabla en la base de datos

    claveM = Column(String(10), primary_key=True)
    hrInicio = Column(Time, nullable=False) # La imagen indica 'Nulo: No'
    hrFinal = Column(Time, nullable=False) # La imagen indica 'Nulo: No'
    nomMateria = Column(String(100), nullable=True) # La imagen indica 'Nulo: Sí'
    