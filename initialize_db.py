import asyncio
from app.models.database import engine, Base

async def init_db():
    async with engine.begin() as conn:
        print("Creando tablas...")
        await conn.run_sync(lambda x: print(Base.metadata.tables))
        await conn.run_sync(Base.metadata.create_all)
        print("Tablas creadas con éxito.")

if __name__ == "__main__":
    asyncio.run(init_db())
