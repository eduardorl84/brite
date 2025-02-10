import pytest
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import AsyncClient
from typing import AsyncGenerator
from app.database import get_session
from app.main import app
from loguru import logger

# Configuración de la base de datos de prueba
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="function")
async def async_engine():
    """Crear un motor de base de datos de prueba."""
    logger.info("Creating test database engine")
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False}
    )

    try:
        logger.info("Creating database tables")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully")

        yield engine

    finally:
        logger.info("Cleaning up database")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

        logger.info("Disposing database engine")
        await engine.dispose()
        logger.info("Test database cleanup complete")

@pytest.fixture(scope="function")
async def test_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Crear una sesión de base de datos de prueba."""
    logger.info("Creating test database session")
    async_session = AsyncSession(async_engine, expire_on_commit=False)
    try:
        yield async_session
    finally:
        logger.info("Closing test database session")
        await async_session.close()

@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Crear un cliente de prueba para la aplicación FastAPI."""
    logger.info("Creating test client")
    async with AsyncClient(
        app=app,
        base_url="http://test",
        backend="httpx"
    ) as ac:
        yield ac
    logger.info("Test client closed")

@pytest.fixture(autouse=True)
async def override_dependencies(test_session: AsyncSession):
    """Sobreescribir dependencias con dependencias de prueba."""
    logger.info("Setting up dependency overrides")
    app.dependency_overrides[get_session] = lambda: test_session
    yield
    logger.info("Clearing dependency overrides")
    app.dependency_overrides.clear()