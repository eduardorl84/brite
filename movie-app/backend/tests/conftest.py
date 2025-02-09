import pytest
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import AsyncClient
from typing import AsyncGenerator, Generator
import asyncio
from fastapi import FastAPI
import aiohttp
from unittest.mock import Mock, AsyncMock

from app.database import get_session
from app.main import app
from app.config import settings
from app.services.omdb_service import OMDBService, get_omdb_service

# Configuración de la base de datos de prueba
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Removed event_loop fixture to use pytest-asyncio's default implementation

@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with AsyncSession(test_engine) as session:
        yield session

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_omdb_service() -> OMDBService:
    """Create a mock OMDB service."""
    service = Mock(spec=OMDBService)
    service.search_movies = AsyncMock()
    service.get_movie_details = AsyncMock()
    service.fetch_initial_movies = AsyncMock()
    return service

@pytest.fixture
def mock_aiohttp_session():
    """Create a mock aiohttp client session."""
    session = Mock(spec=aiohttp.ClientSession)
    session.get = AsyncMock()
    return session

# Override service dependencies for testing
@pytest.fixture(autouse=True)
async def override_dependencies(mock_omdb_service):
    """Override service dependencies with mocks."""
    app.dependency_overrides[get_omdb_service] = lambda: mock_omdb_service
    app.dependency_overrides[get_session] = lambda: test_session
    yield
    app.dependency_overrides = {}