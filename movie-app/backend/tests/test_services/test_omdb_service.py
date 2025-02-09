import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiohttp import ClientSession, ClientResponse
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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockClientSession:
    def __init__(self, response):
        self.response = response
        self.get = AsyncMock(return_value=response)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.mark.asyncio
async def test_search_movies_success(omdb_service):
    # Crear una respuesta mock
    mock_response = MockResponse(200, MOCK_SEARCH_RESPONSE)
    mock_session = MockClientSession(mock_response)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        result = await omdb_service.search_movies("Matrix")

    assert result == MOCK_SEARCH_RESPONSE
    assert result["Search"][0]["Title"] == "The Matrix"
    assert mock_session.get.called

@pytest.mark.asyncio
async def test_search_movies_error(omdb_service):
    # Crear una respuesta mock con error
    mock_response = MockResponse(404, None)
    mock_session = MockClientSession(mock_response)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        result = await omdb_service.search_movies("NonExistentMovie")

    assert result is None
    assert mock_session.get.called

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
async def test_fetch_initial_movies_empty_db(omdb_service, test_session):
    # Configurar los mocks para las llamadas a la API
    with patch.object(omdb_service, 'search_movies', new_callable=AsyncMock) as mock_search, \
         patch.object(omdb_service, 'get_movie_details', new_callable=AsyncMock) as mock_details:
        
        mock_search.return_value = MOCK_SEARCH_RESPONSE
        mock_details.return_value = MOCK_MOVIE_DETAILS
        
        await omdb_service.fetch_initial_movies(test_session)

        # Verificar que se intentó guardar al menos una película
        result = await test_session.execute("SELECT COUNT(*) FROM movie")
        count = result.scalar()
        assert count > 0
        
        # Verificar que se llamaron los métodos
        assert mock_search.called
        assert mock_details.called

@pytest.mark.asyncio
async def test_fetch_initial_movies_db_not_empty(omdb_service, test_session):
    # Primero insertamos una película para simular una base de datos no vacía
    await test_session.execute(
        "INSERT INTO movie (title, year, imdb_id, plot, poster) VALUES "
        "('Test Movie', '2024', 'tt9999999', 'Test Plot', 'test.jpg')"
    )
    await test_session.commit()

    # Configurar los mocks
    with patch.object(omdb_service, 'search_movies', new_callable=AsyncMock) as mock_search, \
         patch.object(omdb_service, 'get_movie_details', new_callable=AsyncMock) as mock_details:
        
        await omdb_service.fetch_initial_movies(test_session)

        # Verificar que los mocks no fueron llamados
        mock_search.assert_not_called()
        mock_details.assert_not_called()