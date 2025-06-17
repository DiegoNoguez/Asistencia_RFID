from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List

from database import Base, engine
from schemas.asistencia_profesor import AsistenciaProfesorConsulta
from database import get_db

router = APIRouter(
    prefix="/asistencia-profesores",
    tags=["asistencia_profesores"],
)

@router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@router.get("/", response_model=List[AsistenciaProfesorConsulta])
async def obtener_asistencia_profesores(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT 
                u.claveP,
                CONCAT(u.nombre, ' ', u.ape1, ' ', COALESCE(u.ape2, '')) as nombre,
                m.nomMateria as materia,
                m.claveM,
                COUNT(CASE WHEN ap.asistio = 1 THEN 1 END) as asistencias,
                COUNT(ap.id_asistencia) as total_clases,
                CASE 
                    WHEN COUNT(ap.id_asistencia) = 0 THEN 100.0
                    ELSE ROUND(COUNT(CASE WHEN ap.asistio = 1 THEN 1 END) * 100.0 / 
                         COUNT(ap.id_asistencia), 2)
                END as porcentaje
            FROM 
                USUARIO u
            JOIN 
                USUARIO_MATERIA um ON u.claveP = um.claveP
            JOIN 
                MATERIA m ON um.claveM = m.claveM
            LEFT JOIN 
                ASISTENCIA_PROFESOR ap ON u.claveP = ap.claveP AND m.claveM = ap.claveM
            WHERE 
                u.idRol = 2
            GROUP BY 
                u.claveP, u.nombre, u.ape1, u.ape2, m.nomMateria, m.claveM
            ORDER BY 
                u.nombre, u.ape1, u.ape2
        """)
        
        result = await db.execute(query)
        profesores = []
        
        for row in result.mappings():
            profesores.append({
                "claveP": row["claveP"],
                "nombre": row["nombre"],
                "materia": row["materia"],
                "claveM": row["claveM"],
                "asistencias": row["asistencias"],
                "total_clases": row["total_clases"],
                "porcentaje": row["porcentaje"]
            })
        
        return profesores
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos: {str(e)}"
        )