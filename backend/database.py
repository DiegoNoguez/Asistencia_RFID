from sqlalchemy import create_engine, MetaData

DATABASE_URL = "mysql+pymysql://root@localhost/default"  # Ajusta tus credenciales

engine = create_engine(DATABASE_URL)
metadata = MetaData()
