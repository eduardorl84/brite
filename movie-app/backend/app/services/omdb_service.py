from typing import Optional, List, Dict
import httpx
import random
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Movie
from ..config import settings

class OMDBService:
    def __init__(self):
        self.api_key = settings.omdb_api_key
        self.base_url = "http://www.omdbapi.com/"

    async def search_movies(self, search_term: str, page: int) -> Optional[Dict]:
        """Busca películas usando el parámetro de búsqueda y paginación."""
        async with httpx.AsyncClient() as client:
            params = {
                "apikey": self.api_key,
                "s": search_term,
                "type": "movie",
                "page": page
            }
            response = await client.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True":
                    return data
            return None

    async def get_movie_details(self, imdb_id: str) -> Optional[Dict]:
        """Obtiene los detalles completos de una película por su ID de IMDB."""
        async with httpx.AsyncClient() as client:
            params = {
                "apikey": self.api_key,
                "i": imdb_id,
                "plot": "full"
            }
            response = await client.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True":
                    return data
            return None

    async def fetch_initial_movies(self, session: AsyncSession) -> None:
        """
        Carga inicial de 100 películas si la base de datos está vacía.
        Usa la búsqueda paginada para obtener películas que contengan 'e'.
        """
        # Verificar si la base de datos está vacía
        query = select(Movie)
        result = await session.execute(query)
        if len(result.scalars().all()) > 0:
            print("Database already populated, skipping initial load")
            return

        collected_movies = []
        page = 1
        # Necesitamos aproximadamente 10 páginas para obtener 100 películas
        max_pages = 15  # Un poco más por si algunas películas fallan

        while len(collected_movies) < 100 and page <= max_pages:
            search_result = await self.search_movies("e", page)
            if not search_result or "Search" not in search_result:
                break

            # Obtener detalles completos de cada película
            for movie_basic in search_result["Search"]:
                if len(collected_movies) >= 100:
                    break

                movie_details = await self.get_movie_details(movie_basic["imdbID"])
                if movie_details:
                    movie = Movie(
                        title=movie_details.get("Title"),
                        year=movie_details.get("Year"),
                        imdb_id=movie_details.get("imdbID"),
                        plot=movie_details.get("Plot"),
                        poster=movie_details.get("Poster")
                    )
                    collected_movies.append(movie)
                    print(f"Fetched movie: {movie.title}")

            page += 1

        # Mezclar aleatoriamente las películas y tomar 100
        random.shuffle(collected_movies)
        movies_to_add = collected_movies[:100]

        # Guardar en la base de datos
        for movie in movies_to_add:
            session.add(movie)

        await session.commit()
        print(f"Successfully loaded {len(movies_to_add)} movies into the database")

# Instancia global del servicio
omdb_service = OMDBService()