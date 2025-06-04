from sqlalchemy import Table, Column, String, MetaData, ForeignKey, PrimaryKeyConstraint

metadata = MetaData()

materia_alumno = Table(
    "MATERIA_ALUMNO",
    metadata,
    Column("claveM", String(10), nullable=False),  # No puede ser nulo (como indica la imagen)
    Column("matricula", String(10), ForeignKey("ALUMNO.matricula"), nullable=False),  # Clave foránea + no nulo
    PrimaryKeyConstraint("claveM", "matricula")  # Clave primaria compuesta
)