from sqlalchemy import Column, Integer, String
from database import Base

# Modelo para profesores/administradores
class Usuario(Base):
    __tablename__ = "USUARIO"
    
    claveP = Column(Integer, primary_key=True)
    claveT = Column(String(10))
    nombre = Column(String(20))
    ape1 = Column(String(15))
    ape2 = Column(String(15))
    idRol = Column(Integer)
    password = Column(String(100))

# Modelo para alumnos
class Alumno(Base):
    __tablename__ = "ALUMNO"
    
    matricula = Column(String(10), primary_key=True)
    claveT = Column(String(10))
    nombre = Column(String(20))
    ape1 = Column(String(15))
    ape2 = Column(String(15))
    numGrupo = Column(Integer)
    password = Column(String(100))
    correo = Column(String(100), unique=True, nullable=True)