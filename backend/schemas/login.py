from pydantic import BaseModel

class LoginRequest(BaseModel):
    rol: int
    usuario: str
    password: str
