# backend/app/api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .database import get_session
from .models import Movie, MovieCreate, MovieResponse, PaginatedResponse

router = APIRouter()

@router.get("/movies/", response_model=PaginatedResponse[MovieResponse])
async def list_movies(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    """
    Lista todas las películas con paginación.

    Args:

        - skip (int): Número de registros a saltar (offset). Por defecto 0
        - limit (int): Límite de registros a devolver. Por defecto 10
        - session (AsyncSession): Sesión de base de datos

    Returns:

        - PaginatedResponse[MovieResponse]: Lista paginada de películas con total de registros
    """
    query = select(Movie).offset(skip).limit(limit)
    result = await session.execute(query)
    movies = result.scalars().all()
    
    count_query = select(Movie)
    count_result = await session.execute(count_query)
    total = len(count_result.scalars().all())
    
    return PaginatedResponse(
        items=movies,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/movies/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Obtiene una película específica por su ID.

    Args:

        - movie_id (int): ID de la película a buscar
        - session (AsyncSession): Sesión de base de datos

    Returns:

        - MovieResponse: Datos de la película encontrada

    Raises:

        - HTTPException: Si la película no se encuentra (404)
    """
    query = select(Movie).where(Movie.id == movie_id)
    result = await session.execute(query)
    movie = result.scalar_one_or_none()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
        
    return movie

@router.post("/movies/", response_model=MovieResponse)
async def create_movie(
    movie: MovieCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Crea una nueva película en la base de datos.

    Args:

        - movie (MovieCreate): Datos de la película a crear
        - session (AsyncSession): Sesión de base de datos

    Returns:

        - MovieResponse: Película creada con sus datos completos

    Raises:

        - HTTPException: Si la película no se encuentra en OMDB (404)
    """
    # Obtener detalles completos de OMDB
    movie_details = await omdb_service.get_movie_details(movie.imdb_id)
    if not movie_details:
        raise HTTPException(status_code=404, detail="Movie not found in OMDB")
        
    # Crear película con datos completos
    db_movie = Movie(
        title=movie_details.get("Title"),
        year=movie_details.get("Year"),
        imdb_id=movie_details.get("imdbID"),
        plot=movie_details.get("Plot"),
        poster=movie_details.get("Poster")
    )
    
    session.add(db_movie)
    await session.commit()
    await session.refresh(db_movie)
    return db_movie

@router.delete("/movies/{movie_id}")
async def delete_movie(
    movie_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Elimina una película de la base de datos por su ID.

    Args:

        - movie_id (int): ID de la película a eliminar
        - session (AsyncSession): Sesión de base de datos

    Returns:

        - dict: Mensaje de confirmación de eliminación

    Raises:
    
        - HTTPException: Si la película no se encuentra (404)
    """
    query = select(Movie).where(Movie.id == movie_id)
    result = await session.execute(query)
    movie = result.scalar_one_or_none()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    await session.delete(movie)
    await session.commit()
    return {"message": "Movie deleted successfully"}