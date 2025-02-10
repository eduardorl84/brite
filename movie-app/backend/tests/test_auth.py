import pytest
from httpx import AsyncClient
from sqlmodel import select
from app.models import User, Movie
from app.auth import create_access_token, get_password_hash

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
async def auth_headers(test_user: User) -> dict:
    """Fixture para generar headers de autenticación."""
    access_token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, test_session):
    """Test para crear un nuevo usuario."""
    user_data = {
        "username": "newuser",
        "password": "testpass123"
    }
    
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "User created successfully"
    
    # Verificar que el usuario fue creado en la base de datos
    result = await test_session.execute(
        select(User).where(User.username == user_data["username"])
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.username == user_data["username"]

@pytest.mark.asyncio
async def test_create_duplicate_user(client: AsyncClient, test_user):
    """Test para verificar que no se pueden crear usuarios duplicados."""
    user_data = {
        "username": test_user.username,
        "password": "testpass123"
    }
    
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_valid_user(client: AsyncClient, test_user):
    """Test para verificar el login exitoso."""
    form_data = {
        "username": "testuser",
        "password": "testpass"
    }
    
    response = await client.post("/api/v1/token", data=form_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    """Test para verificar el rechazo de contraseña incorrecta."""
    form_data = {
        "username": test_user.username,
        "password": "wrongpass"
    }
    
    response = await client.post("/api/v1/token", data=form_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_invalid_username(client: AsyncClient):
    """Test para verificar el rechazo de usuario inexistente."""
    form_data = {
        "username": "nonexistentuser",
        "password": "testpass"
    }
    
    response = await client.post("/api/v1/token", data=form_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_protected_route_with_token(
    client: AsyncClient,
    test_movie,
    auth_headers
):
    """Test para verificar acceso a ruta protegida con token válido."""
    response = await client.delete(
        f"/api/v1/movies/{test_movie.id}",
        headers=auth_headers
    )
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_protected_route_no_token(client: AsyncClient, test_movie):
    """Test para verificar rechazo a ruta protegida sin token."""
    response = await client.delete(f"/api/v1/movies/{test_movie.id}")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

@pytest.mark.asyncio
async def test_protected_route_invalid_token(client: AsyncClient, test_movie):
    """Test para verificar rechazo a ruta protegida con token inválido."""
    headers = {"Authorization": "Bearer invalidtoken123"}
    response = await client.delete(
        f"/api/v1/movies/{test_movie.id}",
        headers=headers
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]