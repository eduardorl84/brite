from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router
from .database import create_db_and_tables

app = FastAPI(title="Movie API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()