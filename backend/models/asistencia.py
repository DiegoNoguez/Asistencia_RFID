from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey
from database import Base

class Asistencia(Base):

    __tablename__ = "ASISTENCIA" 

    idAsistencia = Column(Integer, primary_key=True, autoincrement=True)
    matricula = Column(String(10), ForeignKey('ALUMNO.matricula'), nullable=False)
    claveM = Column(String(8), ForeignKey('MATERIA.claveM'), nullable=False)
    numGrup = Column(Integer, nullable=False) # Asumo que no puede ser nulo por la imagen
    fecha = Column(Date, nullable=False)
    horaRegistro = Column(Time, nullable=False)
    presente = Column(Boolean, nullable=False, default=False) # tinyint(1) suele ser booleano
    observaciones = Column(String(100), nullable=True)