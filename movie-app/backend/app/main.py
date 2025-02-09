from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router
from .database import create_db_and_tables, engine
from sqlalchemy.ext.asyncio import AsyncSession
from .services.omdb_service import get_omdb_service, omdb_service
from .api import router, tags_metadata
from loguru import logger
import sys

# Configurar el logger
logger.remove()  # Remover el handler por defecto
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/movie_app.log",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

app = FastAPI(
    title="Movie API",
    openapi_tags=tags_metadata
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    # Crear tablas
    await create_db_and_tables()
    
    # Cargar películas iniciales
    async with AsyncSession(engine) as session:
        await omdb_service.fetch_initial_movies(session)