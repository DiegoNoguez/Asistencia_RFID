from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Time
from sqlalchemy.sql import func
from database import Base

class AsistenciaProfesor(Base):
    __tablename__ = "ASISTENCIA_PROFESOR"
    
    id_asistencia = Column(Integer, primary_key=True, autoincrement=True)
    claveP = Column(Integer, ForeignKey('USUARIO.claveP'), nullable=False)
    claveM = Column(String(10), ForeignKey('MATERIA.claveM'), nullable=False)
    fecha = Column(Date, nullable=False, server_default=func.current_date())
    asistio = Column(Integer, nullable=False, default=1)  # 1=Asistió, 0=No asistió
    porcentaje_asistencia = Column(Float, nullable=True, default=100.0)
    hora_registro = Column(Time, nullable=False, server_default=func.current_time())