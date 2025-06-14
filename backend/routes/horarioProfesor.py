from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, selectinload
from typing import List
from pydantic import BaseModel
from database import get_db  
from models.usuario import Usuario
from models.horario import Horario
from models.usuario_materia import UsuarioMateria
from models.materia import Materia
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import join

router = APIRouter(prefix="/profesores", tags=["Profesores"])

# --- Modelos Pydantic para Response ---
class MateriaResponse(BaseModel):
    claveM: str
    nomMateria: str

class HorarioResponse(BaseModel):
    dia: str
    hora_inicio: str
    hora_final: str
    materia: MateriaResponse

# --- Endpoint para Profesores (Rol 2) ---
@router.get("/{claveP}/horario", response_model=List[HorarioResponse])
async def obtener_horario_profesor(claveP: int, db: AsyncSession = Depends(get_db)):
    # 1. Verificar si el usuario es profesor (idRol = 2)
    profesor = await db.execute(
        select(Usuario).filter(
            Usuario.claveP == claveP,
            Usuario.idRol == 2
        )
    )
    profesor = profesor.scalars().first()
    
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado o no tiene rol válido")

    # 2. Obtener materias asignadas al profesor
    materias_profesor = await db.execute(
        select(UsuarioMateria.claveM).filter(
            UsuarioMateria.claveP == claveP
        )
    )
    materias_profesor = materias_profesor.scalars().all()

    if not materias_profesor:
        return []

    # 3. Crear JOIN entre Horario y Materia
    j = join(Horario, Materia, Horario.claveM == Materia.claveM)
    
    # 4. Obtener horarios con información de materia
    horarios = await db.execute(
        select(Horario, Materia.nomMateria)
        .select_from(j)
        .filter(Horario.claveM.in_(materias_profesor))
    )
    horarios = horarios.all()

    # 5. Formatear respuesta
    response = []
    for horario, nombre_materia in horarios:
        response.append(HorarioResponse(
            dia=horario.dia,
            hora_inicio=horario.hora,
            hora_final=horario.hora,
            materia=MateriaResponse(
                claveM=horario.claveM,
                nomMateria=nombre_materia
            )
        ))
    return response