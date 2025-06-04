from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from database import engine
from models.usuario import usuario, alumno
from schemas.login import LoginRequest
from models.materia_alumno import materia_alumno 

router = APIRouter(prefix="/login", tags=["Login"])

@router.post("/")
def login_user(data: LoginRequest):
    try:
        with engine.connect() as conn:
            print("Datos recibidos:", data)

            if data.rol == 1:  # Alumno
                query = select(alumno).where(alumno.c.matricula == data.usuario)
                result = conn.execute(query).fetchone()

                if not result:
                    raise HTTPException(status_code=404, detail="Alumno no encontrado")
                if result.password != data.password:
                    raise HTTPException(status_code=401, detail="Contraseña incorrecta")

                # Obtener materias inscritas
                materias_query = select(materia_alumno.c.clave_materia).where(
                    materia_alumno.c.matricula == data.usuario
                )
                materias_result = conn.execute(materias_query).fetchall()
                materias = [row.clave_materia for row in materias_result]

                return {
                    "message": "Login exitoso",
                    "matricula": result.matricula,
                    "nombre": result.nombre,
                    "ape1": result.ape1,
                    "ape2": result.ape2,
                    "rol": data.rol
                }

            elif data.rol in [2, 3]:  # Profesor o Admin
                query = select(usuario).where(
                    usuario.c.claveP == data.usuario,
                    usuario.c.idRol == data.rol
                )
                result = conn.execute(query).fetchone()

                if not result:
                    raise HTTPException(status_code=404, detail="Usuario no encontrado")
                if result.password != data.password:
                    raise HTTPException(status_code=401, detail="Contraseña incorrecta")

                return {
                    "message": "Login exitoso",
                    "claveP": str(data.usuario),
                    "nombre": result.nombre,
                    "rol": data.rol
                }
            else:
                raise HTTPException(status_code=400, detail="Rol inválido")

    except Exception as e:
        print("ERROR en login:", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")
