from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class UsuarioMateria(Base):
    __tablename__ = "USUARIO_MATERIA"
    claveP = Column(Integer, ForeignKey('USUARIO.claveP'), primary_key=True) # O ForeignKey('PROFESOR.claveP')
    claveM = Column(String(10), ForeignKey('MATERIA.claveM'), primary_key=True)