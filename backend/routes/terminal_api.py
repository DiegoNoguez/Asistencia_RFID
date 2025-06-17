from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, cast, String
from datetime import datetime, date, time, timedelta
from database import get_db
from models.asistencia import Asistencia
from models.usuario import Alumno
from models.materia import Materia
from models.horario import Horario
from models.alumno_materia import MateriaAlumno
from models.usuario_materia import UsuarioMateria
from models.usuario import Usuario
from models.asistencia_profesor import AsistenciaProfesor
from schemas.asistencia_profesor import RegistroAsistenciaProfesor
from models.asistencia_profesor import AsistenciaProfesor
from pydantic import BaseModel
from typing import Optional
import logging

router = APIRouter(prefix="/terminal", tags=["Terminal de Asistencia"])

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos Pydantic
class AlumnoResponse(BaseModel):
    nombre: str
    materia_actual: str
    horario_actual: str
    grupo: int
    matricula: str
    claveM: str

class ProfesorResponse(BaseModel):
    nombre: str
    materia_actual: str
    horario_actual: str
    claveP: int
    claveM: str
    rango_horas: str

class RegistroAsistencia(BaseModel):
    matricula: str
    claveM: str
    numGrup: int
    presente: bool = True
    observaciones: Optional[str] = None

class RegistroAsistenciaProfesor(BaseModel):
    claveP: int
    claveM: str
    presente: bool = True

@router.get("/buscar-alumno", response_model=AlumnoResponse)
async def buscar_alumno_por_tarjeta(
    claveT: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca un alumno por su clave de tarjeta (claveT) en la tabla ALUMNO
    """
    try:
        # 1. Validar y limpiar entrada
        claveT = claveT.strip()
        if not claveT:
            logger.warning("ClaveT vacía recibida")
            return JSONResponse(
                content={"error": "Tarjeta no proporcionada"},
                status_code=400
            )

        logger.info(f"Buscando alumno con claveT: '{claveT}'")
        
        # 2. Buscar alumno por claveT (case sensitive)
        stmt = select(Alumno).where(Alumno.claveT == claveT)
        result = await db.execute(stmt)
        alumno = result.scalar_one_or_none()
        
        if not alumno:
            logger.warning(f"No se encontró alumno con claveT: '{claveT}'")
            # Verificar si existe pero con diferente formato
            stmt_case_insensitive = select(Alumno).where(
                func.upper(Alumno.claveT) == func.upper(claveT)
            )
            result_case = await db.execute(stmt_case_insensitive)
            if result_case.scalar_one_or_none():
                logger.warning("¡Alumno existe pero con diferente formato de claveT!")
            return JSONResponse(
                content={"error": "Tarjeta no reconocida"},
                status_code=404
            )

        logger.info(f"Alumno encontrado: {alumno.matricula} - {alumno.nombre}")

        # 3. Verificar grupo asignado
        if alumno.numGrupo is None:
            logger.warning(f"Alumno {alumno.matricula} no tiene grupo asignado")
            return {
                "nombre": f"{alumno.nombre} {alumno.ape1}",
                "materia_actual": "No disponible",
                "horario_actual": "No disponible",
                "grupo": 0,
                "matricula": alumno.matricula,
                "claveM": "ND"
            }

        # 4. Obtener día y hora actual
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

        # 5. Buscar materia actual del alumno
        materia_horario = await db.scalar(
            select(Horario)
            .join(MateriaAlumno, and_(
                MateriaAlumno.matricula == alumno.matricula,
                MateriaAlumno.claveM == Horario.claveM
            ))
            .where(Horario.dia == dia_bd)
            .where(Horario.numGrup == alumno.numGrupo)
            .where(Horario.hora <= hora_actual)
            .order_by(Horario.hora.desc())
            .limit(1)
        )

        if not materia_horario:
            logger.info(f"No se encontró horario para {alumno.matricula}")
            return {
                "nombre": f"{alumno.nombre} {alumno.ape1}",
                "materia_actual": "No hay clase en este horario",
                "horario_actual": "No disponible",
                "grupo": alumno.numGrupo,
                "matricula": alumno.matricula,
                "claveM": "ND"
            }

        # 6. Obtener nombre de la materia
        materia = await db.scalar(
            select(Materia)
            .where(Materia.claveM == materia_horario.claveM)
        )
        
        if not materia:
            logger.error(f"Materia {materia_horario.claveM} no encontrada")
            return {
                "nombre": f"{alumno.nombre} {alumno.ape1}",
                "materia_actual": "Materia no registrada",
                "horario_actual": "No disponible",
                "grupo": alumno.numGrupo,
                "matricula": alumno.matricula,
                "claveM": materia_horario.claveM
            }

        # 7. Formatear horario - AQUÍ ESTÁ EL CAMBIO PRINCIPAL
        hora_inicio = materia_horario.hora
        # Asegurarnos que hora_inicio es un objeto time
        if isinstance(hora_inicio, str):
            try:
                # Si viene en formato "HH:MM-HH:MM", tomamos la primera parte
                if '-' in hora_inicio:
                    hora_inicio = hora_inicio.split('-')[0].strip()
                hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
            except ValueError as e:
                logger.error(f"Error al parsear hora: {hora_inicio} - {str(e)}")
                hora_inicio = time(0, 0)  # Hora por defecto si hay error
        
        hora_fin = (datetime.combine(date.today(), hora_inicio) + timedelta(hours=2)).time()
        rango_horas = f"{hora_inicio.strftime('%H:%M')}-{hora_fin.strftime('%H:%M')}"

        return {
            "nombre": f"{alumno.nombre} {alumno.ape1}",
            "materia_actual": materia.nomMateria,
            "horario_actual": f"{dia_bd} {rango_horas}",
            "grupo": alumno.numGrupo,
            "matricula": alumno.matricula,
            "claveM": materia_horario.claveM
        }

    except Exception as e:
        logger.error(f"Error en buscar-alumno: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar la tarjeta: {str(e)}"
        )

@router.post("/registrar-asistencia")
async def registrar_asistencia(
    registro: RegistroAsistencia,
    db: AsyncSession = Depends(get_db)
):
    """
    Registra la asistencia de un alumno a una materia en un grupo específico.
    """
    try:
        logger.info(f"Registrando asistencia para matrícula: {registro.matricula}")
        
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
            logger.warning(f"Asistencia ya registrada hoy para {registro.matricula}")
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

        logger.info(f"Asistencia registrada exitosamente: {nueva_asistencia.idAsistencia}")
        
        return {
            "mensaje": "Asistencia registrada exitosamente",
            "id_asistencia": nueva_asistencia.idAsistencia
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Error al registrar asistencia: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al registrar asistencia: {str(e)}"
        )

@router.get("/buscar-profesor", response_model=ProfesorResponse)
async def buscar_profesor_por_tarjeta(
    claveT: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca un profesor por su clave de tarjeta (claveT) y devuelve sus datos actuales,
    incluyendo la materia y horario que debería estar impartiendo en este momento.
    """
    try:
        logger.info(f"Buscando profesor con claveT: {claveT}")
        
        # 1. Buscar profesor por claveT
        profesor = await db.scalar(
            select(Usuario)
            .where(Usuario.claveT == claveT)
            .where(Usuario.idRol == 2)  # 2 = profesor
        )
        
        if not profesor:
            logger.warning(f"No se encontró profesor con claveT: {claveT}")
            return JSONResponse(
                content={"success": False, "error": "Tarjeta no reconocida o no es profesor"},
                status_code=404
            )

        # 2. Obtener materias del profesor
        materias_profesor = await db.scalars(
            select(UsuarioMateria.claveM)
            .where(UsuarioMateria.claveP == profesor.claveP)
        )
        claves_materias = materias_profesor.all()

        if not claves_materias:
            logger.info(f"Profesor {profesor.claveP} no tiene materias asignadas")
            return JSONResponse(
                content={
                    "success": False,
                    "error": "No tiene materias asignadas",
                    "nombre": f"{profesor.nombre} {profesor.ape1}"
                },
                status_code=200
            )

        # 3. Obtener horario actual
        ahora = datetime.now()
        dia_semana = ahora.strftime("%A")
        dias_map = {
            "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
            "Thursday": "Jueves", "Friday": "Viernes"
        }
        dia_bd = dias_map.get(dia_semana, dia_semana)

        materia_horario = await db.scalar(
            select(Horario)
            .where(Horario.claveM.in_(claves_materias))
            .where(Horario.dia == dia_bd)
            .order_by(Horario.hora)
        )
        
        if not materia_horario:
            logger.info(f"Profesor {profesor.claveP} no tiene clase hoy")
            return JSONResponse(
                content={
                    "success": False,
                    "error": "No tiene clase en este horario",
                    "nombre": f"{profesor.nombre} {profesor.ape1}"
                },
                status_code=200
            )

        # 4. Obtener información de la materia
        materia = await db.scalar(
            select(Materia)
            .where(Materia.claveM == materia_horario.claveM)
        )
        
        if not materia:
            logger.error(f"Materia no encontrada: {materia_horario.claveM}")
            raise HTTPException(
                status_code=500,
                detail="Datos de materia incompletos"
            )

        # 5. Formatear horario
        hora_inicio = materia_horario.hora
        if isinstance(hora_inicio, str):
            try:
                hora_inicio = datetime.strptime(hora_inicio.split('-')[0].strip(), "%H:%M").time()
            except ValueError:
                hora_inicio = time(0, 0)
        
        hora_fin = (datetime.combine(date.today(), hora_inicio) + timedelta(hours=2)).time()
        rango_horas = f"{hora_inicio.strftime('%H:%M')}-{hora_fin.strftime('%H:%M')}"

        logger.info(f"Profesor encontrado: {profesor.claveP} - Materia: {materia.nomMateria}")

        return {
            "success": True,
            "nombre": f"{profesor.nombre} {profesor.ape1}",
            "materia_actual": materia.nomMateria,
            "horario_actual": f"{dia_bd} {rango_horas}",
            "claveP": profesor.claveP,
            "claveM": materia_horario.claveM,
            "rango_horas": rango_horas
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en buscar-profesor: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar la tarjeta: {str(e)}"
        )

@router.post("/registrar-asistencia-profesor")
async def registrar_asistencia_profesor(
    registro: RegistroAsistenciaProfesor,
    db: AsyncSession = Depends(get_db)
):
    """
    Registra la asistencia de un profesor a una materia.
    """
    try:
        logger.info(f"Registrando asistencia para profesor: {registro.claveP}")
        
        ahora = datetime.now()
        hoy = ahora.date()
        hora_actual = ahora.time()
        
        # 1. Verificar que el profesor tiene esta materia asignada
        tiene_materia = await db.scalar(
            select(UsuarioMateria)
            .where(UsuarioMateria.claveP == registro.claveP)
            .where(UsuarioMateria.claveM == registro.claveM)
        )
        
        if not tiene_materia:
            logger.warning(f"Profesor {registro.claveP} no tiene asignada la materia {registro.claveM}")
            raise HTTPException(
                status_code=400,
                detail="No tiene asignada esta materia"
            )
        
        # 2. Verificar duplicados
        existe = await db.scalar(
            select(AsistenciaProfesor)
            .where(AsistenciaProfesor.claveP == registro.claveP)
            .where(AsistenciaProfesor.claveM == registro.claveM)
            .where(AsistenciaProfesor.fecha == hoy)
        )
        
        if existe:
            logger.warning(f"Asistencia ya registrada hoy: {registro.claveP}")
            raise HTTPException(
                status_code=400,
                detail="Ya registró asistencia hoy para esta materia"
            )

        # 3. Crear registro
        nueva_asistencia = AsistenciaProfesor(
            claveP=registro.claveP,
            claveM=registro.claveM,
            fecha=hoy,
            hora_registro=hora_actual,
            asistio=1 if registro.presente else 0
        )

        db.add(nueva_asistencia)
        await db.commit()

        logger.info(f"Asistencia de profesor registrada exitosamente")
        
        return {
            "mensaje": "Asistencia registrada exitosamente",
            "detalles": {
                "profesor": registro.claveP,
                "materia": registro.claveM,
                "hora_registro": hora_actual.strftime("%H:%M"),
                "fecha": hoy.strftime("%Y-%m-%d")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error al registrar asistencia profesor: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al registrar asistencia: {str(e)}"
        )