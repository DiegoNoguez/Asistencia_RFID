from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.usuario import Alumno
from models.alumno_materia import MateriaAlumno
from models.asistencia import Asistencia
from models.materia import Materia
from models.horario import Horario
from models.grupo import Grupo  # Añade esta línea al inicio
from database import get_db
from pydantic import BaseModel, EmailStr
from typing import List, Optional

router = APIRouter()

# Lista de materias predefinidas para asignar a nuevos alumnos
MATERIAS_POR_DEFECTO = ["ACA-0907", "ACF-0905", "AEF-1031", "SCA-1026", "SCC-1017", "SCD-1003", "SCD-1027", "ING-001"]

# Horario predefinido (basado en lo que proporcionaste)
HORARIO_POR_DEFECTO = [
    # Lunes
    {"claveM": "SCA-1026", "dia": "Lunes", "hora": "07:00-09:00"},
    {"claveM": "ING-001", "dia": "Lunes", "hora": "09:00-11:00"},
    {"claveM": "AEF-1031", "dia": "Lunes", "hora": "11:00-13:00"},
    {"claveM": "ACF-0905", "dia": "Lunes", "hora": "13:00-15:00"},
    
    # Martes
    {"claveM": "AEF-1031", "dia": "Martes", "hora": "08:00-10:00"},
    {"claveM": "ACA-0907", "dia": "Martes", "hora": "10:00-12:00"},
    {"claveM": "SCD-1027", "dia": "Martes", "hora": "12:00-15:00"},
    {"claveM": "ING-001", "dia": "Martes", "hora": "15:00-16:00"},
    
    # Miércoles
    {"claveM": "AEF-1031", "dia": "Miércoles", "hora": "08:00-11:00"},
    {"claveM": "SCC-1017", "dia": "Miércoles", "hora": "11:00-13:00"},
    {"claveM": "SCD-1003", "dia": "Miércoles", "hora": "13:00-15:00"},
    
    # Jueves
    {"claveM": "SCA-1026", "dia": "Jueves", "hora": "07:00-09:00"},
    {"claveM": "SCD-1027", "dia": "Jueves", "hora": "09:00-11:00"},
    {"claveM": "SCC-1017", "dia": "Jueves", "hora": "11:00-13:00"},
    {"claveM": "ACA-0907", "dia": "Jueves", "hora": "13:00-15:00"},
    
    # Viernes
    {"claveM": "ING-001", "dia": "Viernes", "hora": "07:00-09:00"},
    {"claveM": "SCD-1003", "dia": "Viernes", "hora": "09:00-12:00"},
    {"claveM": "ACF-0905", "dia": "Viernes", "hora": "12:00-15:00"}
]

# Esquemas Pydantic para validación y documentación
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

# Endpoint para crear un nuevo alumno
# Endpoint para crear un nuevo alumno
@router.post("/alumnos", response_model=AlumnoResponseSchema)
async def crear_alumno(alumno_data: AlumnoSchema, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Verificar si el grupo 3401 existe (como integer)
        grupo_existente = await db.execute(
            select(Grupo).where(Grupo.numGrup == 3401)  # Sin comillas, es integer
        )
        if not grupo_existente.scalar_one_or_none():
            # Crear el grupo si no existe
            nuevo_grupo = Grupo(numGrup=3401)  # Sin comillas
            db.add(nuevo_grupo)
            await db.flush()
            print("Grupo 3401 creado automáticamente")

        # 2. Verificar si la matrícula ya existe
        existing = await db.execute(
            select(Alumno).where(
                 (Alumno.matricula == alumno_data.matricula) |
            (Alumno.claveT == alumno_data.claveT)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Matrícula ya registrada")
            raise HTTPException(status_code=400, detail="Clave de tarjeta ya resgistrada")
        
        # 3. Crear el nuevo alumno
        nuevo_alumno = Alumno(
            matricula=alumno_data.matricula,
            nombre=alumno_data.nombre,
            ape1=alumno_data.ape1,
            ape2=alumno_data.ape2,
            correo=alumno_data.correo,
            password=alumno_data.password,
            claveT=alumno_data.claveT,
            numGrupo=3401  # Como integer
        )
        
        db.add(nuevo_alumno)
        await db.flush()
        
        # 4. Asignar materias y horarios predefinidos
        for clave_materia in MATERIAS_POR_DEFECTO:
            # Verificar que la materia existe
            result = await db.execute(
                select(Materia).where(Materia.claveM == clave_materia)
            )
            materia = result.scalar_one_or_none()
            
            if materia:
                # Crear relación alumno-materia
                nueva_relacion = MateriaAlumno(
                    claveM=clave_materia,
                    matricula=nuevo_alumno.matricula
                )
                db.add(nueva_relacion)
                
                # Asignar horarios para esta materia
                horarios_materia = [h for h in HORARIO_POR_DEFECTO if h["claveM"] == clave_materia]
                for horario in horarios_materia:
                    nuevo_horario = Horario(
                        matricula=nuevo_alumno.matricula,
                        claveM=clave_materia,
                        numGrup=3401,  # Como integer
                        dia=horario["dia"],
                        hora=horario["hora"]
                    )
                    db.add(nuevo_horario)
            else:
                print(f"Advertencia: Materia {clave_materia} no encontrada")
        
        await db.commit()
        await db.refresh(nuevo_alumno)
        return nuevo_alumno
    except Exception as e:
        print(f"Error al crear alumno: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al crear alumno: {str(e)}")

# Endpoint para listar alumnos (actualizado para integer)
@router.get("/alumnos", response_model=List[AlumnoResponseSchema])
async def listar_alumnos(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Alumno).where(Alumno.numGrupo == 3401))  # Como integer
        alumnos = result.scalars().all()
        return alumnos
    except Exception as e:
        print(f"Error al listar alumnos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al obtener alumnos")

# Endpoint para eliminar un alumno
@router.delete("/alumnos/{matricula}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_alumno(matricula: str, db: AsyncSession = Depends(get_db)):
    try:
        # Verificar si existe el alumno
        alumno = await db.get(Alumno, matricula)
        if not alumno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alumno con matrícula {matricula} no encontrado"
            )
        
        # Eliminar registros relacionados (materias, asistencias y horarios)
        await db.execute(
            delete(MateriaAlumno).where(MateriaAlumno.matricula == matricula)
        )
        await db.execute(
            delete(Asistencia).where(Asistencia.matricula == matricula)
        )
        await db.execute(
            delete(Horario).where(Horario.matricula == matricula)
        )
        
        # Eliminar el alumno
        await db.delete(alumno)
        await db.commit()
        return None
    except Exception as e:
        print(f"Error al eliminar alumno: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al eliminar alumno: {str(e)}")