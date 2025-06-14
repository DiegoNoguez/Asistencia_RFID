from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.usuario import Usuario, Alumno  # Importamos las clases
from database import get_db
from schemas.login import LoginRequest

router = APIRouter(prefix="/login", tags=["Login"])

@router.post("/")
async def login_user(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        if data.rol == 1:  # Alumno
            result = await db.execute(
                select(Alumno).where(Alumno.matricula == data.usuario)
            )
            alumno_data = result.scalar_one_or_none()
            
            if not alumno_data:
                raise HTTPException(status_code=404, detail="Alumno no encontrado")
            if alumno_data.password != data.password:
                raise HTTPException(status_code=401, detail="Contraseña incorrecta")

            return {
                "message": "Login exitoso",
                "matricula": alumno_data.matricula,
                "nombre": alumno_data.nombre,
                "ape1": alumno_data.ape1,
                "ape2": alumno_data.ape2,
                "correo": alumno_data.correo,
                "rol": data.rol
            }

        elif data.rol in [2, 3]:  # Profesor o Admin
            result = await db.execute(
                select(Usuario).where(
                    Usuario.claveP == data.usuario,
                    Usuario.idRol == data.rol
                )
            )
            usuario_data = result.scalar_one_or_none()
            
            if not usuario_data:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            if usuario_data.password != data.password:
                raise HTTPException(status_code=401, detail="Contraseña incorrecta")

            return {
                "message": "Login exitoso",
                "claveP": str(data.usuario),
                "nombre": usuario_data.nombre,
                "rol": data.rol
            }

        else:
            raise HTTPException(status_code=400, detail="Rol inválido")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))