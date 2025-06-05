from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.usuario import Alumno
from database import get_db
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Schema para validación (Pydantic)
class AlumnoSchema(BaseModel):
    matricula: str
    nombre: str
    ape1: str
    ape2: str | None = None
    password: str
    claveT: str  # Tarjeta RFID

    class Config:
        from_attributes = True  # Para compatibilidad con SQLAlchemy 2.0+



# Endpoint para listar alumnos (GET)
@router.get("/alumnos", response_model=List[AlumnoSchema])
async def listar_alumnos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alumno).where(Alumno.numGrupo == 3401))
    return result.scalars().all()

# Endpoint para crear alumno (POST)
@router.post("/alumnos", response_model=AlumnoSchema)
async def crear_alumno(alumno_data: AlumnoSchema, db: AsyncSession = Depends(get_db)):
    # Verificar si la matrícula ya existe
    existing = await db.execute(
        select(Alumno).where(Alumno.matricula == alumno_data.matricula)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Matrícula ya registrada")
    
    # Crear nuevo alumno
    nuevo_alumno = Alumno(
        matricula=alumno_data.matricula,
        nombre=alumno_data.nombre,
        ape1=alumno_data.ape1,
        ape2=alumno_data.ape2,
        password=alumno_data.password,
        claveT=alumno_data.claveT,
        numGrupo=3401  # Grupo fijo
    )
    
    db.add(nuevo_alumno)
    await db.commit()
    await db.refresh(nuevo_alumno)
    return nuevo_alumno


@router.delete("/alumnos/{matricula}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_alumno(matricula: str, db: AsyncSession = Depends(get_db)):
    # Verificar si el alumno existe
    result = await db.execute(
        select(Alumno).where(Alumno.matricula == matricula)
    )
    alumno = result.scalar_one_or_none()
    
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alumno con matrícula {matricula} no encontrado"
        )
    
    # Eliminar el alumno
    await db.execute(
        delete(Alumno).where(Alumno.matricula == matricula)
    )
    await db.commit()
    
    return None  # 204 No Content no devuelve cuerpo