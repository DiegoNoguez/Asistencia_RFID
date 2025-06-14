from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.usuario import Usuario
from models.materia import Materia
from models.usuario_materia import UsuarioMateria
from database import get_db

router = APIRouter(prefix="/api/profesor", tags=["profesor"])

@router.get("/{claveP}/materias")
async def get_materias_profesor(claveP: str, db: AsyncSession = Depends(get_db)):
    try:
        # Verificar que el usuario existe y es profesor (idRol=2)
        profesor = await db.execute(
            select(Usuario)
            .where(Usuario.claveP == claveP)
            .where(Usuario.idRol == 2)
        )
        profesor = profesor.scalar_one_or_none()
        
        if not profesor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profesor no encontrado"
            )

        # Obtener materias asignadas
        materias = await db.execute(
            select(Materia)
            .join(UsuarioMateria)
            .where(UsuarioMateria.claveP == claveP)
        )
        materias = materias.scalars().all()

        return JSONResponse(
            status_code=200,
            content={
                "nombre": profesor.nombre,
                "ape1": profesor.ape1 or "",
                "materias": [
                    {
                        "claveM": m.claveM,
                        "nomMateria": m.nomMateria
                    } for m in materias
                ]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener materias: {str(e)}"
        )