#from fastapi import FastAPI
#from routes.login import router as login_router
#from fastapi.middleware.cors import CORSMiddleware
#from fastapi.staticfiles import StaticFiles
#from fastapi.responses import FileResponse
#from pathlib import Path
#from routes.alumnos import router as alumnos_router
#
#
#app = FastAPI()
#
## Obtener la ruta absoluta a la carpeta "frontend"
#BASE_DIR = Path(__file__).resolve().parent
#FRONTEND_DIR = BASE_DIR.parent / "frontend"
#
## Montamos los archivos estáticos en /static
#app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
#
## Middleware CORS
#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"],  # Cambia esto en producción
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)
#
## Rutas
#app.include_router(login_router)
#app.include_router(alumnos_router, prefix="/api")
#
#


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes.alumnos import router as alumnos_router
from routes.login import router as login_router  # Importamos el router de login
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

# Obtener la ruta absoluta a la carpeta "frontend"
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Montamos los archivos estáticos en /static
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(alumnos_router, prefix="/api")
app.include_router(login_router)  # Agregamos el router de login

# Evento startup para crear tablas (opcional en desarrollo)
@app.on_event("startup")
async def startup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Sistema de Asistencia RFID"}