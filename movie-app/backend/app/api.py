from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .database import get_session
from .models import Movie, MovieResponse, PaginatedResponse, MovieCreate
from .services.omdb_service import OMDBService, get_omdb_service

router = APIRouter()

@router.get("/movies/", response_model=PaginatedResponse[MovieResponse])
async def list_movies(
    skip: int = Query(
        default=0,
        ge=0,
        description="Número de registros a saltar"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Número de registros a retornar por página (máximo 100)"
    ),
    session: AsyncSession = Depends(get_session)
):
    """
    Lista todas las películas de la base de datos con paginación.
    
    Los resultados están ordenados por título alfabéticamente.
    
    Parámetros:

        - skip: Número de registros a saltar (para paginación)
        - limit: Número de registros a retornar (tamaño de página)
    
    Ejemplo de uso:

        - Obtener primeras 10 películas: /movies/
        - Obtener siguientes 10 películas: /movies/?skip=10
        - Obtener 20 películas por página: /movies/?limit=20
    """
    # Consulta para obtener películas ordenadas por título
    query = select(Movie).order_by(Movie.title).offset(skip).limit(limit)
    result = await session.execute(query)
    movies = result.scalars().all()
    
    # Consulta eficiente para el conteo total
    count_query = select(func.count()).select_from(Movie)
    total = await session.scalar(count_query)
    
    return PaginatedResponse(
        items=movies,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/movies/{movie_id}", response_model=MovieResponse)
async def get_movie_by_id(
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

@router.get("/movies/title/{title}", response_model=MovieResponse)
async def get_movie_by_title(
    title: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Obtiene una película específica por su título.

    Args:

        - title (str): Título de la película a buscar
        - session (AsyncSession): Sesión de base de datos

    Returns:

        - MovieResponse: Datos de la película encontrada

    Raises:

        - HTTPException: Si la película no se encuentra (404)
    """
    # Usamos ilike para hacer la búsqueda case-insensitive
    query = select(Movie).where(Movie.title.ilike(f"%{title}%"))
    result = await session.execute(query)
    movies = result.scalars().all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found with that title")
    
    # Si hay múltiples coincidencias, devolvemos la primera
    if len(movies) > 1:
        return movies[0]
    
    return movies[0]

@router.post("/movies/", response_model=MovieResponse)
async def create_movie(
    movie: MovieCreate,
    session: AsyncSession = Depends(get_session),
    omdb_service: OMDBService = Depends(get_omdb_service)
):
    """
    Crea una nueva película en la base de datos.
    
    Args:

        - movie (MovieCreate): Datos de la película (título)
        - session (AsyncSession): Sesión de base de datos
        - omdb_service (OMDBService): Servicio de OMDB
    
    Returns:

        - MovieResponse: Película creada con sus datos completos
    
    Raises:

        - HTTPException: Si la película no se encuentra en OMDB (404) o si ya existe en la base de datos (400)
    """
    # Buscar película por título
    search_result = await omdb_service.search_movies(movie.title)
    
    if not search_result or search_result.get("Response") == "False":
        raise HTTPException(status_code=404, detail="Movie not found in OMDB")
    
    # Tomar el primer resultado
    first_movie = search_result["Search"][0]
    
    # Verificar si la película ya existe
    existing_movie = await session.execute(
        select(Movie).where(Movie.imdb_id == first_movie["imdbID"])
    )
    if existing_movie.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Movie already exists in database")
    
    # Obtener detalles completos
    movie_details = await omdb_service.get_movie_details(first_movie["imdbID"])
    if not movie_details:
        raise HTTPException(status_code=404, detail="Could not fetch movie details")
    
    # Crear película con datos completos
    db_movie = Movie(
        title=movie_details["Title"],
        year=movie_details["Year"],
        imdb_id=movie_details["imdbID"],
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