from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router
from .database import create_db_and_tables, engine
from sqlalchemy.ext.asyncio import AsyncSession
from .services.omdb_service import omdb_service

app = FastAPI(title="Movie API")

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