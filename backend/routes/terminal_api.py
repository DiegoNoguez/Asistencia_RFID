from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, date, time
from database import get_db
from models.asistencia import Asistencia
from models.usuario import Alumno
from models.materia import Materia
from models.horario import Horario
from models.alumno_materia import MateriaAlumno
from pydantic import BaseModel
from typing import Optional
import logging

router = APIRouter(prefix="/terminal", tags=["Terminal de Asistencia"])

# Modelo Pydantic para la respuesta de búsqueda
class AlumnoResponse(BaseModel):
    nombre: str
    materia_actual: str
    horario_actual: str
    grupo: int

# Modelo Pydantic para registro de asistencia
class RegistroAsistencia(BaseModel):
    matricula: str
    claveM: str
    numGrup: int
    presente: bool = True
    observaciones: Optional[str] = None

@router.get("/buscar-alumno")
async def buscar_alumno_por_tarjeta(
    claveT: str,  # Puede ser matrícula o claveT (tarjeta)
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Buscar al alumno por matrícula O claveT
        alumno = await db.scalar(
            select(Alumno)
            .where(
                (Alumno.claveT == claveT) | (Alumno.matricula == claveT)  # Busca en ambos campos
            )
        )
        
        if not alumno:
            return JSONResponse(
                content={"error": "Tarjeta/matrícula no reconocida"},
                status_code=404
            )

        # 2. Obtener materia actual del alumno
        ahora = datetime.now()
        dia_semana = ahora.strftime("%A")
        hora_actual = ahora.time()

        dias_map = {
            "Monday": "Lunes",
            "Tuesday": "Martes",
            "Wednesday": "Miércoles",
            "Thursday": "Jueves",
            "Friday": "Viernes"
        }
        dia_bd = dias_map.get(dia_semana, dia_semana)

        materia_horario = await db.scalar(
            select(Horario)
            .join(MateriaAlumno, and_(
                MateriaAlumno.matricula == alumno.matricula,  # Usamos matrícula (no claveT)
                MateriaAlumno.claveM == Horario.claveM
            ))
            .where(Horario.dia == dia_bd)
            .where(Horario.numGrup == alumno.numGrupo)
            .where(Horario.hora <= hora_actual)
            .order_by(Horario.hora.desc())
            .limit(1)
        )

        if not materia_horario:
            return JSONResponse(
                content={
                    "nombre": f"{alumno.nombre} {alumno.ape1}",
                    "error": "No hay clases en este horario"
                },
                status_code=200
            )

        materia = await db.scalar(
            select(Materia)
            .where(Materia.claveM == materia_horario.claveM)
        )

        return {
            "nombre": f"{alumno.nombre} {alumno.ape1}",
            "materia_actual": materia.nomMateria,
            "horario_actual": f"{materia_horario.dia} {materia_horario.hora}",
            "grupo": alumno.numGrupo,
            "matricula": alumno.matricula,  # Aseguramos que se devuelva la matrícula
            "claveM": materia_horario.claveM  # Necesario para el registro
        }

    except Exception as e:
        logging.error(f"Error en buscar-alumno: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al procesar la tarjeta"
        )

@router.post("/registrar-asistencia")
async def registrar_asistencia(
    registro: RegistroAsistencia,
    db: AsyncSession = Depends(get_db)
):
    try:
        logging.info(f"Datos recibidos para registro: {registro.dict()}")
        
        hoy = date.today()
        hora_actual = datetime.now().time()

        # Verificar si ya existe registro
        existe = await db.scalar(
            select(Asistencia)
            .where(Asistencia.matricula == registro.matricula)
            .where(Asistencia.claveM == registro.claveM)
            .where(Asistencia.fecha == hoy)
        )

        if existe:
            logging.warning(f"Asistencia ya registrada hoy para {registro.matricula}")
            return JSONResponse(
                content={"error": "La asistencia ya fue registrada hoy"},
                status_code=400
            )

        # Crear nuevo registro
        nueva_asistencia = Asistencia(
            matricula=registro.matricula,
            claveM=registro.claveM,
            numGrup=registro.numGrup,
            fecha=hoy,
            horaRegistro=hora_actual,
            presente=registro.presente,
            observaciones=registro.observaciones
        )

        db.add(nueva_asistencia)
        await db.commit()
        await db.refresh(nueva_asistencia)

        logging.info(f"Asistencia registrada exitosamente: {nueva_asistencia.idAsistencia}")
        
        return {
            "mensaje": "Asistencia registrada exitosamente",
            "id_asistencia": nueva_asistencia.idAsistencia
        }

    except Exception as e:
        await db.rollback()
        logging.error(f"Error al registrar asistencia: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al registrar asistencia: {str(e)}"
        )