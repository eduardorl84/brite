import httpx
from typing import Optional, Dict, List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Movie
from loguru import logger
from functools import lru_cache

class OMDBService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"

    async def search_movies(self, search_term: str, page: int = 1) -> Optional[dict]:
        params = {
            "apikey": self.api_key,
            "s": search_term,
            "page": str(page)
        }
        logger.info(f"Requesting: {self.base_url}?apikey={self.api_key}&s={search_term}&page={page}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                if response.status_code == 200:
                    return response.json()
                logger.error(f"Error status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Search request failed: {str(e)}")
            return None

    async def get_movie_details(self, imdb_id: str) -> Optional[Dict]:
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
        """Cargar películas iniciales si la base de datos está vacía."""
        logger.info("Starting initial movie fetch...")

        # Verificar si ya hay películas en la base de datos
        result = await session.execute(select(Movie))
        movies = result.scalars().all()
        if movies:
            logger.info(f"Found {len(movies)} existing movies")
            return

        # Términos de búsqueda para obtener películas variadas
        search_terms = ["Matrix", "Star Wars", "Lord", "Harry", "Avengers"]
        collected_movies = []

        for term in search_terms:
            logger.info(f"Searching for term: {term}")
            page = 1
            while len(collected_movies) < 100 and page <= 5:
                try:
                    search_result = await self.search_movies(term, page)
                    if not search_result or "Search" not in search_result:
                        logger.warning(f"No results for {term} page {page}")
                        break

                    movies_found = search_result["Search"]
                    logger.info(f"Found {len(movies_found)} movies for {term} page {page}")

                    for movie_data in movies_found:
                        if len(collected_movies) >= 100:
                            break

                        details = await self.get_movie_details(movie_data["imdbID"])
                        if details:
                            movie = Movie(
                                title=details["Title"],
                                year=details["Year"],
                                imdb_id=details["imdbID"],
                                plot=details.get("Plot"),
                                poster=details.get("Poster")
                            )
                            session.add(movie)
                            await session.flush()
                            collected_movies.append(movie)
                            logger.info(f"Added movie: {details['Title']}")

                        # Commit cada 10 películas
                        if len(collected_movies) % 10 == 0:
                            await session.commit()
                            logger.info(f"Committed batch of {len(collected_movies)} movies")

                    page += 1

                except Exception as e:
                    logger.error(f"Error processing {term} page {page}: {str(e)}")
                    continue

        try:
            await session.commit()
            logger.success(f"Successfully loaded {len(collected_movies)} movies")
        except Exception as e:
            await session.rollback()
            logger.error(f"Final commit error: {str(e)}")
            raise

@lru_cache()
def get_omdb_service() -> OMDBService:
    from ..config import settings
    api_key = settings.omdb_api_key
    if not api_key:
        raise ValueError("OMDB_API_KEY not configured in settings")
    return OMDBService(api_key=api_key)

# Crear una instancia global del servicio
omdb_service = get_omdb_service()