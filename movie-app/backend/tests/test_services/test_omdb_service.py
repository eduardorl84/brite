import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from app.services.omdb_service import OMDBService
from ..fixtures.mock_responses import (
    MOCK_SEARCH_RESPONSE,
    MOCK_MOVIE_DETAILS,
    MOCK_ERROR_RESPONSE
)

@pytest.fixture
def omdb_service():
    return OMDBService(api_key="test_key")

@pytest.mark.asyncio
async def test_search_movies_success(omdb_service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_SEARCH_RESPONSE

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    with patch('httpx.AsyncClient', return_value=mock_client):
        result = await omdb_service.search_movies("Matrix")

    assert result == MOCK_SEARCH_RESPONSE
    assert result["Search"][0]["Title"] == "The Matrix"
    mock_client.__aenter__.return_value.get.assert_called_once()

@pytest.mark.asyncio
async def test_search_movies_error(omdb_service):
    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    with patch('httpx.AsyncClient', return_value=mock_client):
        result = await omdb_service.search_movies("NonExistentMovie")

    assert result is None
    mock_client.__aenter__.return_value.get.assert_called_once()

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
    # Mock para search_movies
    async def mock_search_movies(*args, **kwargs):
        return MOCK_SEARCH_RESPONSE
    
    # Mock para get_movie_details
    async def mock_get_movie_details(*args, **kwargs):
        return MOCK_MOVIE_DETAILS
    
    # Aplicar los mocks
    with patch.object(omdb_service, 'search_movies', mock_search_movies), \
         patch.object(omdb_service, 'get_movie_details', mock_get_movie_details):
        
        await omdb_service.fetch_initial_movies(test_session)
        
        # Verificar que se guardó al menos una película
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
    
    # Verificar que no se añadieron más películas
    result = await test_session.execute("SELECT COUNT(*) FROM movie")
    count = result.scalar()
    assert count == 1  # Solo debe existir la película que insertamos