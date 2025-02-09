import pytest
from aiohttp import ClientSession
from unittest.mock import AsyncMock, patch
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
async def test_search_movies_success(omdb_service, mock_aiohttp_session):
    # Configurar el mock de la respuesta
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = MOCK_SEARCH_RESPONSE
    mock_aiohttp_session.get.return_value.__aenter__.return_value = mock_response

    with patch('aiohttp.ClientSession', return_value=mock_aiohttp_session):
        result = await omdb_service.search_movies("Matrix")

    assert result == MOCK_SEARCH_RESPONSE
    assert result["Search"][0]["Title"] == "The Matrix"
    mock_aiohttp_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_search_movies_error(omdb_service, mock_aiohttp_session):
    # Configurar el mock para simular un error
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_aiohttp_session.get.return_value.__aenter__.return_value = mock_response

    with patch('aiohttp.ClientSession', return_value=mock_aiohttp_session):
        result = await omdb_service.search_movies("NonExistentMovie")

    assert result is None
    mock_aiohttp_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_get_movie_details_success(omdb_service):
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value.json.return_value = MOCK_MOVIE_DETAILS

        result = await omdb_service.get_movie_details("tt0133093")

        assert result == MOCK_MOVIE_DETAILS
        assert result["Title"] == "The Matrix"
        assert result["imdbID"] == "tt0133093"

@pytest.mark.asyncio
async def test_get_movie_details_not_found(omdb_service):
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value.json.return_value = MOCK_ERROR_RESPONSE

        result = await omdb_service.get_movie_details("tt9999999")

        assert result is None

@pytest.mark.asyncio
async def test_fetch_initial_movies_empty_db(omdb_service, test_session, mock_aiohttp_session):
    # Configurar mocks para search_movies y get_movie_details
    omdb_service.search_movies = AsyncMock(return_value=MOCK_SEARCH_RESPONSE)
    omdb_service.get_movie_details = AsyncMock(return_value=MOCK_MOVIE_DETAILS)

    await omdb_service.fetch_initial_movies(test_session)

    # Verificar que se intentó guardar al menos una película
    result = await test_session.execute("SELECT COUNT(*) FROM movie")
    count = result.scalar()
    assert count > 0

@pytest.mark.asyncio
async def test_fetch_initial_movies_db_not_empty(omdb_service, test_session):
    # Primero insertamos una película para simular una base de datos no vacía
    await test_session.execute(
        "INSERT INTO movie (title, year, imdb_id, plot, poster) VALUES "
        "('Test Movie', '2024', 'tt9999999', 'Test Plot', 'test.jpg')"
    )
    await test_session.commit()

    # El mock no debería ser llamado porque la base de datos ya tiene datos
    omdb_service.search_movies = AsyncMock()
    omdb_service.get_movie_details = AsyncMock()

    await omdb_service.fetch_initial_movies(test_session)

    # Verificar que los mocks no fueron llamados
    omdb_service.search_movies.assert_not_called()
    omdb_service.get_movie_details.assert_not_called()

@pytest.mark.asyncio
async def test_fetch_initial_movies_api_error(omdb_service, test_session):
    # Configurar el mock para simular un error en la API
    omdb_service.search_movies = AsyncMock(return_value=None)

    await omdb_service.fetch_initial_movies(test_session)

    # Verificar que no se guardaron películas debido al error
    result = await test_session.execute("SELECT COUNT(*) FROM movie")
    count = result.scalar()
    assert count == 0