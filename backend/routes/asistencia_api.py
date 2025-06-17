from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from datetime import date, datetime
from sqlalchemy import select, and_, or_, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from models.asistencia import Asistencia
from models.usuario import Usuario, Alumno
from models.materia import Materia
from models.usuario_materia import UsuarioMateria
from models.alumno_materia import MateriaAlumno
from models.grupo_materia import MateriaGrupo
from models.horario import Horario
from database import get_db
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/asistencias", tags=["asistencias"])

# Modelos (se mantienen igual)
class AsistenciaCreate(BaseModel):
    matricula: str
    claveM: str
    numGrup: int
    fecha: date
    horaRegistro: str
    presente: bool
    observaciones: Optional[str] = None

class AsistenciaResponse(BaseModel):
    idAsistencia: int
    matricula: str
    nombre_completo: str
    claveM: str
    nombre_materia: str
    numGrup: int
    fecha: date
    horaRegistro: str
    presente: bool
    observaciones: Optional[str]
    profesor: str

class AsistenciaFiltros(BaseModel):
    matricula: Optional[str] = None
    claveM: Optional[str] = None
    numGrup: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    presente: Optional[bool] = None

# Funciones auxiliares (se mantienen igual)
async def verificar_asistencia_duplicada(db: AsyncSession, matricula: str, claveM: str, fecha: date) -> bool:
    existing = await db.scalar(
        select(Asistencia)
        .where(Asistencia.matricula == matricula)
        .where(Asistencia.claveM == claveM)
        .where(Asistencia.fecha == fecha)
    )
    return existing is not None

# Endpoints principales
@router.post("/", response_model=AsistenciaResponse)
async def crear_asistencia(asistencia_data: AsistenciaCreate, db: AsyncSession = Depends(get_db)):
    # Verificación de duplicados (existente)
    if await verificar_asistencia_duplicada(db, asistencia_data.matricula, asistencia_data.claveM, asistencia_data.fecha):
        raise HTTPException(status_code=400, detail="Registro de asistencia duplicado")
    
    nueva_asistencia = Asistencia(**asistencia_data.dict())
    db.add(nueva_asistencia)
    await db.commit()
    await db.refresh(nueva_asistencia)
    
    # Obtención de datos adicionales (existente)
    alumno = await db.scalar(select(Alumno).where(Alumno.matricula == nueva_asistencia.matricula))
    materia = await db.scalar(select(Materia).where(Materia.claveM == nueva_asistencia.claveM))
    profesor = await db.scalar(select(Usuario).where(Usuario.claveP == materia.ClaveM))
    
    return {
        "idAsistencia": nueva_asistencia.idAsistencia,
        "matricula": nueva_asistencia.matricula,
        "nombre_completo": f"{alumno.nombre} {alumno.ape1} {alumno.ape2 or ''}",
        "claveM": nueva_asistencia.claveM,
        "nombre_materia": materia.nomMateria,
        "numGrup": nueva_asistencia.numGrup,
        "fecha": nueva_asistencia.fecha,
        "horaRegistro": str(nueva_asistencia.horaRegistro),
        "presente": nueva_asistencia.presente,
        "observaciones": nueva_asistencia.observaciones,
        "profesor": f"{profesor.nombre} {profesor.ape1} {profesor.ape2}" if profesor else "Profesor no asignado"
    }

@router.get("/", response_model=List[AsistenciaResponse])
async def obtener_asistencias(
    matricula: Optional[str] = None,
    claveM: Optional[str] = None,
    numGrup: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    presente: Optional[bool] = None,
    unique: bool = False,  # Nuevo parámetro opcional
    db: AsyncSession = Depends(get_db)
):
    # Construcción de consulta base (existente)
    query = (
        select(
            Asistencia,
            Alumno.nombre,
            Alumno.ape1,
            Alumno.ape2,
            Materia.nomMateria,
            Usuario.nombre.label("profesor_nombre"),
            Usuario.ape1.label("profesor_ape1"),
            Usuario.ape2.label("profesor_ape2")
        )
        .join(Alumno, Alumno.matricula == Asistencia.matricula)
        .join(Materia, Materia.claveM == Asistencia.claveM)
    )

    # Filtros (existente)
    if matricula:
        query = query.where(Asistencia.matricula == matricula)
    if claveM:
        query = query.where(Asistencia.claveM == claveM)
    if numGrup:
        query = query.where(Asistencia.numGrup == numGrup)
    if fecha_inicio:
        query = query.where(Asistencia.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.where(Asistencia.fecha <= fecha_fin)
    if presente is not None:
        query = query.where(Asistencia.presente == presente)

    query = query.order_by(Asistencia.fecha.desc())

    # Ejecución (existente)
    result = await db.execute(query)
    registros = result.all()

    # Nuevo: Filtrado de duplicados (solo si unique=True)
    if unique:
        seen = set()
        unique_registros = []
        for r in registros:
            key = (r[0].matricula, r[0].claveM, r[0].fecha)
            if key not in seen:
                seen.add(key)
                unique_registros.append(r)
        registros = unique_registros

    # Transformación de resultados (existente)
    return [
        {
            "idAsistencia": a.idAsistencia,
            "matricula": a.matricula,
            "nombre_completo": f"{nombre} {ape1} {ape2 or ''}",
            "claveM": a.claveM,
            "nombre_materia": nomMateria,
            "numGrup": a.numGrup,
            "fecha": a.fecha,
            "horaRegistro": str(a.horaRegistro),
            "presente": a.presente,
            "observaciones": a.observaciones,
            "profesor": f"{profesor_nombre} {profesor_ape1}"
        } for a, nombre, ape1, ape2, nomMateria, profesor_nombre, profesor_ape1 in registros
    ]

@router.get("/verificar-duplicado/")
async def verificar_asistencia_duplicada_endpoint(
    matricula: str,
    claveM: str,
    fecha: date,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint específico para verificar duplicados"""
    existe = await verificar_asistencia_duplicada(db, matricula, claveM, fecha)
    return {"existe_duplicado": existe}

@router.get("/resumen-alumno/{matricula}")
async def resumen_asistencia_alumno(
    matricula: str,
    db: AsyncSession = Depends(get_db)
):
    # Obtener todas las materias del alumno usando MateriaAlumno
    materias = await db.execute(
        select(MateriaAlumno.claveM)
        .where(MateriaAlumno.matricula == matricula)
    )
    materias = [m[0] for m in materias.all()]

    if not materias:
        raise HTTPException(404, detail="Alumno no encontrado o sin materias")

    # Obtener resumen de asistencias por materia
    resumen = []
    for claveM in materias:
        # Obtener nombre de la materia
        materia_nombre = await db.scalar(
            select(Materia.nomMateria)
            .where(Materia.claveM == claveM)
        )

        # Contar asistencias (usando distinct para evitar duplicados)
        total = await db.scalar(
            select(distinct(Asistencia.fecha))
            .where(Asistencia.matricula == matricula)
            .where(Asistencia.claveM == claveM)
            .count()
        )
        presentes = await db.scalar(
            select(Asistencia)
            .where(Asistencia.matricula == matricula)
            .where(Asistencia.claveM == claveM)
            .where(Asistencia.presente == True)
            .count()
        )

        resumen.append({
            "claveM": claveM,
            "materia": materia_nombre,
            "total_clases": total,
            "asistencias": presentes,
            "porcentaje": round((presentes / total) * 100, 2) if total > 0 else 0
        })

    # Obtener información del alumno
    alumno_data = await db.scalar(
        select(Alumno)
        .where(Alumno.matricula == matricula)
    )

    return {
        "alumno": {
            "matricula": alumno_data.matricula,
            "nombre_completo": f"{alumno_data.nombre} {alumno_data.ape1} {alumno_data.ape2 or ''}",
            "grupo": alumno_data.numGrupo
        },
        "resumen": resumen
    }

@router.get("/resumen-materia/{claveM}/{numGrup}")
async def resumen_asistencia_materia(
    claveM: str,
    numGrup: int,
    db: AsyncSession = Depends(get_db)
):
    # Verificar que la materia existe
    materia_data = await db.scalar(
        select(Materia)
        .where(Materia.claveM == claveM)
    )
    if not materia_data:
        raise HTTPException(404, detail="Materia no encontrada")

    # Obtener alumnos en la materia/grupo
    alumnos = await db.execute(
        select(Alumno)
        .join(MateriaAlumno)
        .where(MateriaAlumno.claveM == claveM)
        .where(Alumno.numGrupo == numGrup)
    )
    alumnos = alumnos.scalars().all()

    if not alumnos:
        raise HTTPException(404, detail="No hay alumnos en este grupo/materia")

    # Generar resumen para cada alumno
    resumen = []
    for alumno_data in alumnos:
        # Usamos distinct para contar días únicos de asistencia
        total = await db.scalar(
            select(distinct(Asistencia.fecha))
            .where(Asistencia.matricula == alumno_data.matricula)
            .where(Asistencia.claveM == claveM)
            .count()
        )
        presentes = await db.scalar(
            select(Asistencia)
            .where(Asistencia.matricula == alumno_data.matricula)
            .where(Asistencia.claveM == claveM)
            .where(Asistencia.presente == True)
            .count()
        )

        resumen.append({
            "matricula": alumno_data.matricula,
            "nombre_completo": f"{alumno_data.nombre} {alumno_data.ape1} {alumno_data.ape2 or ''}",
            "total_clases": total,
            "asistencias": presentes,
            "porcentaje": round((presentes / total) * 100, 2) if total > 0 else 0
        })

    return {
        "materia": {
            "claveM": materia_data.claveM,
            "nombre": materia_data.nomMateria,
            "grupo": numGrup
        },
        "resumen": resumen
    }

#nuevo endpoint para obtener el horario de un alumno con asistencia
@router.get("/horario-alumno/{matricula}", response_model=List[dict])
async def obtener_horario_alumno(
    matricula: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Verificar que el alumno existe
        alumno = await db.scalar(
            select(Alumno)
            .where(Alumno.matricula == matricula)
        )
        if not alumno:
            raise HTTPException(404, detail="Alumno no encontrado")

        # 2. Obtener las materias del alumno
        materias_alumno = await db.execute(
            select(MateriaAlumno.claveM)
            .where(MateriaAlumno.matricula == matricula)
        )
        claves_materias = [m[0] for m in materias_alumno.all()]
        
        if not claves_materias:
            return []

        # 3. Obtener el horario del alumno agrupado por materia y día
        horario_query = (
            select(
                Horario.claveM,
                Materia.nomMateria.label("materia"),
                Horario.dia,
                func.min(Horario.hora).label("hora"),
                Horario.numGrup,
                Usuario.nombre.label("profesor_nombre"),
                Usuario.ape1.label("profesor_apellido")
            )
            .join(Materia, Materia.claveM == Horario.claveM)
            .where(Horario.claveM.in_(claves_materias))
            .where(Horario.numGrup == alumno.numGrupo)
            .group_by(
                Horario.claveM,
                Materia.nomMateria,
                Horario.dia,
                Horario.numGrup,
                Usuario.nombre,
                Usuario.ape1
            )
            .order_by(
                Horario.dia,
                func.min(Horario.hora)
            )
        )
        
        horario_result = await db.execute(horario_query)
        horario_data = horario_result.all()

        # 4. Obtener todas las asistencias del alumno en las materias de su horario
        todas_asistencias = await db.execute(
            select(Asistencia)
            .where(Asistencia.matricula == matricula)
            .where(Asistencia.claveM.in_(claves_materias))
            .order_by(Asistencia.fecha.desc())
        )
        todas_asistencias = todas_asistencias.scalars().all()

        # 5. Combinar los datos
        resultado = []
        for clase in horario_data:
            # Buscar asistencia más reciente para esta materia en este día específico
            asistencia_clase = None
            dia_horario = clase.dia  # "Lunes", "Martes", etc.
            
            for asistencia in todas_asistencias:
                # Obtener el nombre del día de la semana de la fecha de asistencia
                dia_asistencia = asistencia.fecha.strftime("%A")
                
                # Ajustar nombres para coincidir con los de la BD (español vs inglés)
                dia_asistencia_espanol = {
                    "Monday": "Lunes",
                    "Tuesday": "Martes",
                    "Wednesday": "Miércoles",
                    "Thursday": "Jueves",
                    "Friday": "Viernes",
                    "Saturday": "Sábado",
                    "Sunday": "Domingo"
                }.get(dia_asistencia, dia_asistencia)
                
                # Verificar que sea la misma materia y el mismo día de la semana
                if (asistencia.claveM == clase.claveM and 
                    dia_asistencia_espanol == dia_horario):
                    asistencia_clase = asistencia
                    break
            
            resultado.append({
                "clave_materia": clase.claveM,
                "materia": clase.materia,
                "dia": clase.dia,
                "hora": clase.hora,
                "numGrup": clase.numGrup,
                "asistencia": asistencia_clase.presente if asistencia_clase else None,
                "ultima_actualizacion": asistencia_clase.fecha.isoformat() if asistencia_clase else None
            })

        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el horario: {str(e)}"
        )


# Añadir estos nuevos endpoints al archivo asistencia_api.py
@router.get("/pase-lista-grupo/{numGrup}")
async def obtener_pase_lista_grupo(
    numGrup: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Obtener todas las materias del grupo
        materias = await db.execute(
            select(MateriaGrupo.claveM)
            .where(MateriaGrupo.numGrup == numGrup)
        )
        claves_materias = [m[0] for m in materias.all()]

        if not claves_materias:
            return JSONResponse(
                content={"error": "No se encontraron materias para este grupo"},
                status_code=404
            )

        # 2. Obtener todos los alumnos de esas materias
        alumnos = await db.execute(
            select(Alumno)
            .join(MateriaAlumno, MateriaAlumno.matricula == Alumno.matricula)
            .where(MateriaAlumno.claveM.in_(claves_materias))
            .distinct()
        )
        alumnos = alumnos.scalars().all()

        if not alumnos:
            return JSONResponse(
                content={"error": "No hay alumnos en las materias de este grupo"},
                status_code=404
            )

        # 3. Obtener información de materias con profesor (parte modificada)
        materias_info = {}
        materias_result = await db.execute(
            select(
                Materia.claveM,
                Materia.nomMateria,
                Usuario.nombre.label("profesor_nombre"),
                Usuario.ape1.label("profesor_ape1"),
                Usuario.ape2.label("profesor_ape2")
            )
            .join(UsuarioMateria, UsuarioMateria.claveM == Materia.claveM)
            .join(Usuario, Usuario.claveP == UsuarioMateria.claveP)
            .where(Materia.claveM.in_(claves_materias))
        )
        
        for m in materias_result:
            materias_info[m.claveM] = {
                "nombre": m.nomMateria,
                "profesor": f"{m.profesor_nombre} {m.profesor_ape1} {m.profesor_ape2 or ''}".strip()
            }

        # 4. Procesar datos para la respuesta (resto del código igual)
        response_data = {
            "grupo": numGrup,
            "materias": materias_info,  # Cambiado a diccionario
            "alumnos": []
        }

        for alumno in alumnos:
            alumno_data = {
                "matricula": alumno.matricula,
                "nombre_completo": f"{alumno.nombre} {alumno.ape1} {alumno.ape2 or ''}",
                "correo": f"{alumno.correo}",
                "asistencias": {}
            }

            for claveM in claves_materias:
                # Calcular asistencias
                total = await db.scalar(
                    select(func.count(distinct(Asistencia.fecha)))
                    .where(Asistencia.matricula == alumno.matricula)
                    .where(Asistencia.claveM == claveM)
                ) or 0
                
                presentes = await db.scalar(
                    select(func.count(Asistencia.idAsistencia))
                    .where(Asistencia.matricula == alumno.matricula)
                    .where(Asistencia.claveM == claveM)
                    .where(Asistencia.presente == True)
                ) or 0

                alumno_data["asistencias"][claveM] = {
                    "presentes": presentes,
                    "total": total,
                    "porcentaje": round((presentes / total) * 100, 2) if total > 0 else 0
                }

            response_data["alumnos"].append(alumno_data)

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el pase de lista: {str(e)}"
        )