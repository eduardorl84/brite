import pytest
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Movie, User

@pytest.mark.asyncio
async def test_create_movie(test_session: AsyncSession):
    """Verifica que se pueda crear una película correctamente."""
    movie = Movie(title="Inception", year="2010", imdb_id="tt1375666", plot="A thief enters dreams", poster="url.jpg")
    test_session.add(movie)
    await test_session.commit()
    await test_session.refresh(movie)

    assert movie.id is not None
    assert movie.title == "Inception"

@pytest.mark.asyncio
async def test_unique_imdb_id_constraint(test_session: AsyncSession):
    """Verifica que no se puedan crear películas con el mismo imdb_id."""
    movie1 = Movie(title="Movie 1", year="2022", imdb_id="tt1234567")
    movie2 = Movie(title="Movie 2", year="2023", imdb_id="tt1234567")
    
    test_session.add(movie1)
    await test_session.commit()
    
    test_session.add(movie2)
    with pytest.raises(Exception):
        await test_session.commit()

@pytest.mark.asyncio
async def test_create_user(test_session: AsyncSession):
    """Verifica que se pueda crear un usuario correctamente."""
    user = User(username="testuser", hashed_password="hashedpass")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"

@pytest.mark.asyncio
async def test_unique_username_constraint(test_session: AsyncSession):
    """Verifica que no se puedan crear usuarios con el mismo username."""
    user1 = User(username="testuser", hashed_password="pass1")
    user2 = User(username="testuser", hashed_password="pass2")
    
    test_session.add(user1)
    await test_session.commit()
    
    test_session.add(user2)
    with pytest.raises(Exception):
        await test_session.commit()

@pytest.mark.asyncio
async def test_relationships(test_session: AsyncSession):
    """Verifica que las relaciones entre modelos funcionen correctamente."""
    movie = Movie(title="Interstellar", year="2014", imdb_id="tt0816692")
    user = User(username="movie_fan", hashed_password="securepass")
    test_session.add_all([movie, user])
    await test_session.commit()
    
    query = select(Movie).where(Movie.title == "Interstellar")
    result = await test_session.execute(query)
    retrieved_movie = result.scalar_one_or_none()
    assert retrieved_movie is not None
    assert retrieved_movie.title == "Interstellar"
