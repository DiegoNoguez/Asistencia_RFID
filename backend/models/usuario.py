from sqlalchemy import Table, Column, Integer, String, MetaData
from database import metadata

usuario = Table(
    "USUARIO",
    metadata,
    Column("claveP", Integer, primary_key=True),
    Column("claveT", String(10)),
    Column("nombre", String(20)),
    Column("ape1", String(15)),
    Column("ape2", String(15)),
    Column("idRol", Integer),
    Column("password", String(100)),  # Asegúrate que exista
)

alumno = Table(
    "ALUMNO",
    metadata,
    Column("matricula", String(10), primary_key=True),
    Column("claveT", String(10)),
    Column("nombre", String(20)),
    Column("ape1", String(15)),
    Column("ape2", String(15)),
    Column("numGrupo", Integer),
    Column("password", String(100)),  # Asegúrate que exista
)
