from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class MateriaGrupo(Base):
    __tablename__ = "GRUPO_MATERIA"

    claveM = Column(String(10), ForeignKey('MATERIA.claveM'), primary_key=True)
    numGrup = Column(Integer, ForeignKey('GRUPO.numGrup'), primary_key=True)