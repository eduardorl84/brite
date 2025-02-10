import pytest
from httpx import AsyncClient
from app.models import Movie, User
from app.auth import get_password_hash
from sqlmodel import select

@pytest.mark.asyncio
async def test_listar_peliculas_vacio(client: AsyncClient, test_session):
    """Prueba listar películas cuando la base de datos está vacía."""
    response = await client.get("/api/v1/movies/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["skip"] == 0
    assert data["limit"] == 10

@pytest.mark.asyncio
async def test_listar_peliculas_con_paginacion(client: AsyncClient, test_session):
    """Prueba listar películas con paginación."""
    # Crear películas de prueba
    peliculas = [
        Movie(title=f"Película de Prueba {i}", year="2024", imdb_id=f"tt{i:07d}")
        for i in range(15)
    ]
    for pelicula in peliculas:
        test_session.add(pelicula)
    await test_session.commit()

    # Probar paginación por defecto (10 elementos)
    response = await client.get("/api/v1/movies/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["items"]) == 10

    # Probar paginación personalizada
    response = await client.get("/api/v1/movies/?skip=10&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["skip"] == 10
    assert data["limit"] == 5

@pytest.mark.asyncio
async def test_obtener_pelicula_por_id(client: AsyncClient, test_session):
    """Prueba obtener una película específica por ID."""
    pelicula = Movie(title="Película de Prueba", year="2024", imdb_id="tt0000001")
    test_session.add(pelicula)
    await test_session.commit()
    await test_session.refresh(pelicula)

    response = await client.get(f"/api/v1/movies/{pelicula.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Película de Prueba"
    assert data["imdb_id"] == "tt0000001"

@pytest.mark.asyncio
async def test_obtener_pelicula_no_existente(client: AsyncClient):
    """Prueba obtener una película que no existe."""
    response = await client.get("/api/v1/movies/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_crear_pelicula(client: AsyncClient, monkeypatch):
    """Prueba crear una nueva película."""
    # Simular respuesta del servicio OMDB
    async def mock_busqueda(*args, **kwargs):
        return {
            "Search": [{
                "Title": "Película de Prueba",
                "Year": "2024",
                "imdbID": "tt0000001",
                "Type": "movie"
            }],
            "Response": "True"
        }

    async def mock_detalles(*args, **kwargs):
        return {
            "Title": "Película de Prueba",
            "Year": "2024",
            "imdbID": "tt0000001",
            "Plot": "Trama de prueba",
            "Poster": "test.jpg",
            "Response": "True"
        }

    from app.services.omdb_service import OMDBService
    monkeypatch.setattr(OMDBService, "search_movies", mock_busqueda)
    monkeypatch.setattr(OMDBService, "get_movie_details", mock_detalles)

    response = await client.post(
        "/api/v1/movies/",
        json={"title": "Película de Prueba"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Película de Prueba"
    assert data["imdb_id"] == "tt0000001"

@pytest.mark.asyncio
async def test_eliminar_pelicula_sin_autorizacion(client: AsyncClient, test_session):
    """Prueba eliminar una película sin autenticación."""
    pelicula = Movie(title="Película de Prueba", year="2024", imdb_id="tt0000001")
    test_session.add(pelicula)
    await test_session.commit()
    await test_session.refresh(pelicula)

    response = await client.delete(f"/api/v1/movies/{pelicula.id}")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_eliminar_pelicula_autorizado(client: AsyncClient, test_session):
    """Prueba eliminar una película con autenticación correcta."""
    # Crear usuario de prueba
    usuario = User(
        username="usuario_prueba",
        hashed_password=get_password_hash("password_prueba")
    )
    test_session.add(usuario)
    await test_session.commit()

    # Obtener token de autenticación
    response = await client.post(
        "/api/v1/token",
        data={"username": "usuario_prueba", "password": "password_prueba"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Crear y eliminar película
    pelicula = Movie(title="Película de Prueba", year="2024", imdb_id="tt0000001")
    test_session.add(pelicula)
    await test_session.commit()
    await test_session.refresh(pelicula)

    response = await client.delete(
        f"/api/v1/movies/{pelicula.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    # Verificar que la película fue eliminada
    resultado = await test_session.execute(
        select(Movie).where(Movie.id == pelicula.id)
    )
    assert resultado.scalar_one_or_none() is None

@pytest.mark.asyncio
async def test_buscar_pelicula_por_titulo(client: AsyncClient, test_session):
    """Prueba buscar una película por título."""
    pelicula = Movie(title="El Padrino", year="1972", imdb_id="tt0068646")
    test_session.add(pelicula)
    await test_session.commit()
    
    response = await client.get("/api/v1/movies/title/Padrino")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "El Padrino"
    assert data["imdb_id"] == "tt0068646"

@pytest.mark.asyncio
async def test_buscar_pelicula_titulo_no_existente(client: AsyncClient):
    """Prueba buscar una película con un título que no existe."""
    response = await client.get("/api/v1/movies/title/PeliculaInexistente")
    assert response.status_code == 404