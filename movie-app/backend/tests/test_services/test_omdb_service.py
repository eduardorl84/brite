import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp
from app.services.omdb_service import OMDBService
from ..fixtures.mock_responses import (
    MOCK_SEARCH_RESPONSE,
    MOCK_MOVIE_DETAILS,
    MOCK_ERROR_RESPONSE
)

@pytest.fixture
def omdb_service():
    return OMDBService(api_key="test_key")

class MockResponse:
    def __init__(self, status, data):
        self.status = status
        self._data = data

    async def json(self):
        return self._data

class MockGet:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture
def mock_aiohttp_session(monkeypatch):
    class MockSession:
        def __init__(self, response):
            self.response = response
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
        def get(self, url, **kwargs):
            return MockGet(self.response)
    
    async def mock_session(*args, **kwargs):
        return MockSession(MockResponse(200, MOCK_SEARCH_RESPONSE))
    
    monkeypatch.setattr(aiohttp, "ClientSession", mock_session)

@pytest.mark.asyncio
async def test_search_movies_success(omdb_service, mock_aiohttp_session):
    result = await omdb_service.search_movies("Matrix")
    assert result == MOCK_SEARCH_RESPONSE
    assert result["Search"][0]["Title"] == "The Matrix"

@pytest.mark.asyncio
async def test_search_movies_error(omdb_service, monkeypatch):
    async def mock_session(*args, **kwargs):
        class MockSession:
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                pass
            def get(self, *args, **kwargs):
                return MockGet(MockResponse(404, None))
        return MockSession()
    
    monkeypatch.setattr(aiohttp, "ClientSession", mock_session)
    result = await omdb_service.search_movies("NonExistentMovie")
    assert result is None

@pytest.mark.asyncio
async def test_get_movie_details_success(omdb_service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_MOVIE_DETAILS

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    with patch('httpx.AsyncClient', return_value=mock_client):
        result = await omdb_service.get_movie_details("tt0133093")

    assert result == MOCK_MOVIE_DETAILS
    assert result["Title"] == "The Matrix"
    assert result["imdbID"] == "tt0133093"

@pytest.mark.asyncio
async def test_get_movie_details_not_found(omdb_service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_ERROR_RESPONSE

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    with patch('httpx.AsyncClient', return_value=mock_client):
        result = await omdb_service.get_movie_details("tt9999999")

    assert result is None

@pytest.mark.asyncio
async def test_fetch_initial_movies_empty_db(omdb_service, test_session, monkeypatch):
    # Mock para la sesión de aiohttp
    async def mock_search_session(*args, **kwargs):
        class MockSession:
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                pass
            def get(self, *args, **kwargs):
                return MockGet(MockResponse(200, MOCK_SEARCH_RESPONSE))
        return MockSession()
    
    # Mock para httpx
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_MOVIE_DETAILS

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    monkeypatch.setattr(aiohttp, "ClientSession", mock_search_session)
    with patch('httpx.AsyncClient', return_value=mock_client):
        await omdb_service.fetch_initial_movies(test_session)

    result = await test_session.execute("SELECT COUNT(*) FROM movie")
    count = result.scalar()
    assert count > 0

@pytest.mark.asyncio
async def test_fetch_initial_movies_db_not_empty(omdb_service, test_session):
    # Insertar una película para simular DB no vacía
    await test_session.execute(
        "INSERT INTO movie (title, year, imdb_id, plot, poster) VALUES "
        "('Test Movie', '2024', 'tt9999999', 'Test Plot', 'test.jpg')"
    )
    await test_session.commit()
    
    # No necesitamos configurar mocks porque no deberían ser llamados
    await omdb_service.fetch_initial_movies(test_session)

    result = await test_session.execute("SELECT COUNT(*) FROM movie")
    count = result.scalar()
    assert count == 1  # Solo debe existir la película que insertamos