from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.usuario import Alumno
from database import get_db
from pydantic import BaseModel, EmailStr
from typing import List, Optional

router = APIRouter()

class AlumnoSchema(BaseModel):
    matricula: str
    nombre: str
    ape1: str
    ape2: Optional[str] = None
    correo: Optional[EmailStr] = None
    password: str
    claveT: str

    class Config:
        from_attributes = True

class AlumnoResponseSchema(BaseModel):
    matricula: str
    nombre: str
    ape1: str
    ape2: Optional[str] = None
    correo: Optional[EmailStr] = None
    claveT: str

    class Config:
        from_attributes = True

@router.get("/alumnos", response_model=List[AlumnoResponseSchema])
async def listar_alumnos(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Alumno).where(Alumno.numGrupo == 3401))
        alumnos = result.scalars().all()
        return alumnos
    except Exception as e:
        print(f"Error al listar alumnos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al obtener alumnos")

@router.post("/alumnos", response_model=AlumnoResponseSchema)
async def crear_alumno(alumno_data: AlumnoSchema, db: AsyncSession = Depends(get_db)):
    try:
        existing = await db.execute(
            select(Alumno).where(Alumno.matricula == alumno_data.matricula)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Matrícula ya registrada")
        
        nuevo_alumno = Alumno(
            matricula=alumno_data.matricula,
            nombre=alumno_data.nombre,
            ape1=alumno_data.ape1,
            ape2=alumno_data.ape2,
            correo=alumno_data.correo,
            password=alumno_data.password,
            claveT=alumno_data.claveT,
            numGrupo=3401
        )
        
        db.add(nuevo_alumno)
        await db.commit()
        await db.refresh(nuevo_alumno)
        return nuevo_alumno
    except Exception as e:
        print(f"Error al crear alumno: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al crear alumno: {str(e)}")

@router.delete("/alumnos/{matricula}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_alumno(matricula: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Alumno).where(Alumno.matricula == matricula)
        )
        alumno = result.scalar_one_or_none()
        
        if not alumno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alumno con matrícula {matricula} no encontrado"
            )
        
        await db.execute(
            delete(Alumno).where(Alumno.matricula == matricula)
        )
        await db.commit()
        return None
    except Exception as e:
        print(f"Error al eliminar alumno: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al eliminar alumno: {str(e)}")