import pytest
from sqlmodel import SQLModel, select
from app.database import create_db_and_tables, get_session
from app.models import Movie, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, text
from loguru import logger

@pytest.mark.asyncio
async def test_create_db_and_tables(async_engine):
    """Verifica que las tablas se crean correctamente en la base de datos."""
    await create_db_and_tables()
    
    async with async_engine.connect() as conn:
        def get_tables(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()
        
        tables = await conn.run_sync(get_tables)
        
        assert "movie" in tables, "Tabla 'movie' no fue creada"
        assert "user" in tables, "Tabla 'user' no fue creada"
        await conn.commit()

@pytest.mark.asyncio
async def test_get_session(test_session: AsyncSession):
    """Verifica que get_session proporciona una sesión funcional."""
    # Crear una película de prueba
    test_movie = Movie(
        title="Test Movie",
        year="2024",
        imdb_id="tt9999999",
        plot="Test plot",
        poster="test.jpg"
    )
    
    # Probar crear
    test_session.add(test_movie)
    await test_session.commit()
    
    # Obtener el ID después del commit
    movie_id = test_movie.id
    assert movie_id is not None, "El ID no fue asignado"
    
    # Probar leer
    stmt = select(Movie).where(Movie.id == movie_id)
    result = await test_session.execute(stmt)
    movie = result.scalar_one()
    assert movie.title == "Test Movie"
    
    # Probar actualizar
    movie.year = "2025"
    await test_session.commit()
    
    # Recargar la película desde la base de datos
    stmt = select(Movie).where(Movie.id == movie_id)
    result = await test_session.execute(stmt)
    updated_movie = result.scalar_one()
    assert updated_movie.year == "2025"
    
    # Probar eliminar
    await test_session.delete(movie)
    await test_session.commit()
    
    # Verificar eliminación
    stmt = select(Movie).where(Movie.id == movie_id)
    result = await test_session.execute(stmt)
    assert result.first() is None

@pytest.mark.asyncio
async def test_session_rollback(test_session: AsyncSession):
    """Verifica el comportamiento del rollback de la sesión."""
    # Crear primera película
    movie1 = Movie(
        title="First Movie",
        year="2024",
        imdb_id="tt9999999",
        plot="Test plot",
        poster="test.jpg"
    )
    test_session.add(movie1)
    await test_session.commit()
    
    try:
        # Intentar crear segunda película con mismo imdb_id
        movie2 = Movie(
            title="Second Movie",
            year="2024",
            imdb_id="tt9999999",  # ID duplicado
            plot="Another plot",
            poster="another.jpg"
        )
        test_session.add(movie2)
        await test_session.commit()
        pytest.fail("Debería haber fallado por ID duplicado")
    except:
        await test_session.rollback()
    
    # Verificar que solo existe la primera película
    result = await test_session.execute(
        select(Movie).where(Movie.imdb_id == "tt9999999")
    )
    movies = list(result.scalars().all())
    assert len(movies) == 1
    assert movies[0].title == "First Movie"

@pytest.mark.asyncio
async def test_concurrent_sessions(async_engine):
    """Verifica operaciones con múltiples sesiones."""
    async with AsyncSession(async_engine) as session1, \
               AsyncSession(async_engine) as session2:
        # Crear película en primera sesión
        movie1 = Movie(
            title="Movie 1",
            year="2024",
            imdb_id="tt0000001",
            plot="Plot 1",
            poster="poster1.jpg"
        )
        session1.add(movie1)
        await session1.commit()
        
        # Crear película en segunda sesión
        movie2 = Movie(
            title="Movie 2",
            year="2024",
            imdb_id="tt0000002",
            plot="Plot 2",
            poster="poster2.jpg"
        )
        session2.add(movie2)
        await session2.commit()
        
        # Verificar que ambas sesiones pueden ver todas las películas
        for session in [session1, session2]:
            result = await session.execute(
                select(Movie).order_by(Movie.title)
            )
            movies = list(result.scalars().all())
            assert len(movies) == 2
            assert {m.title for m in movies} == {"Movie 1", "Movie 2"}