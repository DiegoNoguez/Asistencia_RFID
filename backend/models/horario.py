from sqlalchemy import Column, BigInteger, String, Time, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Horario(Base):
    __tablename__ = "HORARIO"

    idHorario = Column(Integer, primary_key=True, autoincrement=True)
    matricula = Column(String(10), ForeignKey('ALUMNO.matricula'), nullable=False)
    claveM = Column(String(8), ForeignKey('MATERIA.claveM'), nullable=False)
    numGrup = Column(Integer, ForeignKey('GRUPO.numGrup'))
    dia = Column(String(10), nullable=False)
    hora = Column(String(20), nullable=False)

    grupo = relationship("Grupo") 