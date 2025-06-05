from pydantic import BaseModel

class LoginRequest(BaseModel):
    usuario: str
    password: str
    rol: int  # 1: Alumno, 2: Profesor, 3: Admin
