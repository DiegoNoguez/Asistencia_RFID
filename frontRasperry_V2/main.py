
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a base de datos
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='Default',
    cursorclass=pymysql.cursors.DictCursor
)

class Alumno(BaseModel):
    nombre: str
    materia: Optional[str] = "Base de Datos"
    horario: Optional[str] = "10:00 - 12:00"

@app.get("/buscar")
def buscar(claveT: str):
    try:
        with conn.cursor() as cursor:
            sql = "SELECT nombre FROM ALUMNO WHERE claveT = %s"
            cursor.execute(sql, (claveT,))
            result = cursor.fetchone()

            if result:
                return Alumno(nombre=result['nombre'])
            else:
                return None
    except Exception as e:
        return {"error": str(e)}
