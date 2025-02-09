import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from app.services.omdb_service import OMDBService
from ..fixtures.mock_responses import (
    MOCK_SEARCH_RESPONSE,
    MOCK_MOVIE_DETAILS,
    MOCK_ERROR_RESPONSE
)
from sqlmodel import select
from app.models import Movie
from loguru import logger

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

@pytest.mark.asyncio
async def test_search_movies_error(omdb_service):
    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    with patch('httpx.AsyncClient', return_value=mock_client):
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
    # Simplificar el mock de search_movies para devolver solo una película
    mock_search_result = {
        "Search": [
            {
                "Title": "Test Movie",
                "Year": "2024",
                "imdbID": "tt9999999",
                "Type": "movie",
                "Poster": "test.jpg"
            }
        ],
        "totalResults": "1",
        "Response": "True"
    }

    # Mock simplificado de las funciones de búsqueda
    async def mock_search(*args, **kwargs):
        return mock_search_result

    async def mock_details(*args, **kwargs):
        return {
            "Title": "Test Movie",
            "Year": "2024",
            "imdbID": "tt9999999",
            "Plot": "Test plot",
            "Poster": "test.jpg",
            "Response": "True"
        }

    # Aplicar los mocks
    with patch.object(omdb_service, 'search_movies', side_effect=mock_search), \
         patch.object(omdb_service, 'get_movie_details', side_effect=mock_details):
        
        try:
            # Agregar timeout para evitar que se quede colgado
            await asyncio.wait_for(omdb_service.fetch_initial_movies(test_session), timeout=5.0)
            
            # Verificar el resultado
            result = await test_session.execute(select(Movie))
            movies = result.scalars().all()
            assert len(movies) > 0
            assert movies[0].title == "Test Movie"
            
        except asyncio.TimeoutError:
            pytest.fail("fetch_initial_movies timed out after 5 seconds")

@pytest.mark.asyncio
async def test_fetch_initial_movies_db_not_empty(omdb_service, test_session):
    # Crear una película inicial
    movie = Movie(
        title="Test Movie",
        year="2024",
        imdb_id="tt9999999",
        plot="Test Plot",
        poster="test.jpg"
    )
    test_session.add(movie)
    await test_session.commit()
    
    # Mock simplificado que no debería ser llamado
    mock_search = AsyncMock()
    mock_details = AsyncMock()
    
    with patch.object(omdb_service, 'search_movies', new=mock_search), \
         patch.object(omdb_service, 'get_movie_details', new=mock_details):
        
        try:
            # Agregar timeout para evitar que se quede colgado
            await asyncio.wait_for(omdb_service.fetch_initial_movies(test_session), timeout=5.0)
            
            # Verificar que los mocks no fueron llamados
            mock_search.assert_not_called()
            mock_details.assert_not_called()
            
            # Verificar que solo existe una película
            result = await test_session.execute(select(Movie))
            movies = result.scalars().all()
            assert len(movies) == 1
            
        except asyncio.TimeoutError:
            pytest.fail("fetch_initial_movies timed out after 5 seconds")