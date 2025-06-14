from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import pandas as pd
from datetime import datetime
import os
from database import get_db

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)

async def generar_excel_desde_filas(rows, claveM, extra_nombre=""):
    registros = []
    for row in rows:
        nombre = row.nombre_completo or ""
        partes_nombre = nombre.split(' ')
        
        registros.append({
            "Matrícula": row.matricula,
            "Nombre": partes_nombre[0] if len(partes_nombre) > 0 else "",
            "Apellido Paterno": partes_nombre[1] if len(partes_nombre) > 1 else "",
            "Apellido Materno": partes_nombre[2] if len(partes_nombre) > 2 else "",
            "Asistencia": "Presente" if row.presente else "Ausente",
            "Fecha": row.fecha.strftime("%Y-%m-%d") if row.fecha else ""
        })

    df = pd.DataFrame(registros)
    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"asistencia_{claveM}{extra_nombre}_{fecha_hora}.xlsx"
    output_dir = "temp_excel"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    df.to_excel(file_path, index=False)

    return file_path, filename

# 🔷 ADMIN
@router.get("/excel_asistencias")
async def exportar_excel_asistencias(
    claveM: str = Query(...),
    numGrup: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = """
            SELECT 
                a.matricula,
                CONCAT(al.nombre, ' ', al.ape1, ' ', IFNULL(al.ape2, '')) AS nombre_completo,
                a.presente,
                a.fecha
            FROM ASISTENCIA a
            JOIN ALUMNO al ON a.matricula = al.matricula
            JOIN MATERIA m ON a.claveM = m.claveM
            JOIN GRUPO g ON a.numGrup = g.numGrup
            WHERE m.claveM = :claveM AND g.numGrup = :numGrup
            ORDER BY a.fecha DESC, al.ape1, al.ape2, al.nombre
        """
        result = await db.execute(text(query), {'claveM': claveM, 'numGrup': numGrup})
        rows = result.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No se encontraron registros")

        path, filename = await generar_excel_desde_filas(rows, claveM, f"_grupo{numGrup}")
        return FileResponse(path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=filename)

    except HTTPException:
        raise
    except Exception as e:
        print("❌ Error al generar Excel (ADMIN):", e)
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")


# 🔷 PROFESOR
@router.get("/excel_asistencias_profesor")
async def exportar_excel_profesor(
    claveP: str = Query(..., description="Clave del profesor"),
    claveM: str = Query(..., description="Clave de la materia"),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = """
            SELECT 
                a.matricula,
                CONCAT(al.nombre, ' ', al.ape1, ' ', IFNULL(al.ape2, '')) AS nombre_completo,
                a.presente,
                a.fecha
            FROM ASISTENCIA a
            JOIN ALUMNO al ON a.matricula = al.matricula
            JOIN MATERIA m ON a.claveM = m.claveM
            JOIN USUARIO_MATERIA um ON um.claveM = m.claveM
            WHERE m.claveM = :claveM AND um.claveP = :claveP
            ORDER BY a.fecha DESC, al.ape1, al.ape2, al.nombre
        """
        result = await db.execute(text(query), {'claveM': claveM, 'claveP': claveP})
        rows = result.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No se encontraron registros")

        path, filename = await generar_excel_desde_filas(rows, claveM, f"prof{claveP}")
        return FileResponse(
            path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        print("❌ Error al generar Excel (PROFESOR):", e)
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")