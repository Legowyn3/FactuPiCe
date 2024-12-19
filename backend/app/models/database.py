from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Configuración del motor de base de datos
engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Declaración base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión
async def get_db():
    async with async_session() as session:
        yield session
