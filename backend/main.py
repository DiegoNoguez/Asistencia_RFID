from fastapi import FastAPI
from routes.login import router as login_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

import os

app = FastAPI()

# Obtener la ruta absoluta a la carpeta "frontend"
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Montamos los archivos estáticos en /static
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(login_router)



