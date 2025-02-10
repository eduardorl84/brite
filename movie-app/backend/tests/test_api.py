import pytest
from httpx import AsyncClient
from sqlmodel import select
from app.models import Movie, User
from app.auth import create_access_token, get_password_hash
from typing import AsyncGenerator
import json
from loguru import logger

@pytest.fixture
async def test_movie(test_session) -> Movie:
    """Fixture para crear una película de prueba."""
    movie = Movie(
        title="Test Movie",
        year="2024",
        imdb_id="tt9999999",
        plot="Test plot",
        poster="test.jpg"
    )
    test_session.add(movie)
    await test_session.commit()
    await test_session.refresh(movie)
    return movie

@pytest.fixture
async def test_user(test_session) -> User:
    """Fixture para crear un usuario de prueba."""
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass"),
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user

@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """Fixture para generar headers de autenticación."""
    access_token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.mark.asyncio
async def test_list_movies_empty(client: AsyncClient):
    """Test para listar películas cuando la base de datos está vacía."""
    response = await client.get("/api/v1/movies/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["skip"] == 0
    assert data["limit"] == 10

@pytest.mark.asyncio
async def test_list_movies_with_data(client: AsyncClient, test_movie: Movie):
    """Test para listar películas cuando hay datos."""
    response = await client.get("/api/v1/movies/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Test Movie"

@pytest.mark.asyncio
async def test_list_movies_pagination(client: AsyncClient, test_session):
    """Test para verificar la paginación de películas."""
    # Crear 15 películas de prueba
    for i in range(15):
        movie = Movie(
            title=f"Test Movie {i}",
            year="2024",
            imdb_id=f"tt{i:07d}",
            plot=f"Test plot {i}",
            poster=f"test{i}.jpg"
        )
        test_session.add(movie)
    await test_session.commit()

    # Probar primera página (por defecto 10 items)
    response = await client.get("/api/v1/movies/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 15

    # Probar segunda página
    response = await client.get("/api/v1/movies/?skip=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5

@pytest.mark.asyncio
async def test_get_movie_by_id(client: AsyncClient, test_movie: Movie):
    """Test para obtener una película por ID."""
    response = await client.get(f"/api/v1/movies/{test_movie.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == test_movie.title
    assert data["imdb_id"] == test_movie.imdb_id

@pytest.mark.asyncio
async def test_get_movie_by_id_not_found(client: AsyncClient):
    """Test para obtener una película que no existe."""
    response = await client.get("/api/v1/movies/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_movie_by_title(client: AsyncClient, test_movie: Movie):
    """Test para obtener una película por título."""
    response = await client.get(f"/api/v1/movies/title/{test_movie.title}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == test_movie.title
    assert data["imdb_id"] == test_movie.imdb_id

@pytest.mark.asyncio
async def test_create_movie(client: AsyncClient, test_session, monkeypatch):
    """Test para crear una nueva película."""
    # Mock de la respuesta de OMDB
    async def mock_search_movies(*args, **kwargs):
        return {
            "Search": [{
                "Title": "New Test Movie",
                "Year": "2024",
                "imdbID": "tt8888888",
                "Type": "movie",
                "Poster": "test.jpg"
            }],
            "totalResults": "1",
            "Response": "True"
        }

    async def mock_get_movie_details(*args, **kwargs):
        return {
            "Title": "New Test Movie",
            "Year": "2024",
            "imdbID": "tt8888888",
            "Plot": "Test plot",
            "Poster": "test.jpg",
            "Response": "True"
        }

    # Aplicar los mocks
    from app.services.omdb_service import OMDBService
    monkeypatch.setattr(OMDBService, "search_movies", mock_search_movies)
    monkeypatch.setattr(OMDBService, "get_movie_details", mock_get_movie_details)

    # Solo enviamos el título como lo haría un cliente real
    response = await client.post(
        "/api/v1/movies/",
        json={"title": "New Test Movie"}
    )
    
    if response.status_code != 200:
        print("Response error:", response.json())
        
    assert response.status_code == 200
    
    data = response.json()
    # Verificamos que la respuesta contenga todos los datos que debería haber obtenido de OMDB
    assert data["title"] == "New Test Movie"
    assert data["year"] == "2024"
    assert data["imdb_id"] == "tt8888888"
    assert data["plot"] == "Test plot"
    assert data["poster"] == "test.jpg"

@pytest.mark.asyncio
async def test_delete_movie_unauthorized(client: AsyncClient, test_movie: Movie):
    """Test para eliminar una película sin autenticación."""
    response = await client.delete(f"/api/v1/movies/{test_movie.id}")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_movie_authorized(
    client: AsyncClient,
    test_movie: Movie,
    auth_headers: dict
):
    """Test para eliminar una película con autenticación."""
    response = await client.delete(
        f"/api/v1/movies/{test_movie.id}",
        headers=auth_headers
    )
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_movie_not_found(
    client: AsyncClient,
    auth_headers: dict
):
    """Test para eliminar una película que no existe."""
    response = await client.delete(
        "/api/v1/movies/999",
        headers=auth_headers
    )
    assert response.status_code == 404