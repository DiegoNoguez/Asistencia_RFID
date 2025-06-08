from sqlalchemy import Column, String, ForeignKey
from database import Base

class MateriaAlumno(Base):
    __tablename__ = "ALUMNO_MATERIA"
    claveM = Column(String(10), ForeignKey('MATERIA.claveM'), primary_key=True)
    matricula = Column(String(10), ForeignKey('ALUMNO.matricula'), primary_key=True)