from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .security.security_middleware import SecurityHeadersMiddleware
from .security.backup_manager import backup_manager
from .routes import auth
from .database import engine, Base
import logging
from pathlib import Path

# Configurar logging
logging_dir = Path("logs")
logging_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FactuPiCe",
    description="Sistema de Facturación para Autónomos y Empresas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Añadir middleware de seguridad
app.add_middleware(SecurityHeadersMiddleware)

# Incluir routers
app.include_router(auth.router, prefix="/api")

# Iniciar backup automático
@app.on_event("startup")
async def startup_event():
    backup_manager.schedule_backups()

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a FactuPiCe API",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 