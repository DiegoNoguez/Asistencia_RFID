#manera sincrona 
#from sqlalchemy import create_engine, MetaData

#DATABASE_URL = "mysql+pymysql://root@localhost/default"  # Ajusta tus credenciales

#engine = create_engine(DATABASE_URL)
#metadata = MetaData()


#manero asíncrona
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# Conexión asíncrona con asyncmy (MySQL)
DATABASE_URL = "mysql+asyncmy://root:@localhost/default?charset=utf8mb4"

engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True para ver logs # Base para modelos SQLAlchemy
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()  # Base para modelos SQLAlchemy

# Dependency para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session