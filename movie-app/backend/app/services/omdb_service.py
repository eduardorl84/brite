import httpx
from typing import Optional, Dict, List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Movie
from loguru import logger

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

        search_terms = ["Matrix"]  # Simplificado para pruebas
        collected_movies = []

        for term in search_terms:
            logger.info(f"Searching for term: {term}")
            search_result = await self.search_movies(term, page=1)
            
            if not search_result or "Search" not in search_result:
                logger.warning(f"No results for {term}")
                continue

            movies_found = search_result["Search"]
            for movie_data in movies_found[:1]:  # Solo procesar la primera película
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
                    await session.commit()
                    collected_movies.append(movie)
                    break  # Salir después de la primera película

        logger.info(f"Successfully loaded {len(collected_movies)} movies")

def get_omdb_service() -> OMDBService:
    from ..config import settings
    api_key = settings.omdb_api_key
    if not api_key:
        raise ValueError("OMDB_API_KEY not configured in settings")
    return OMDBService(api_key=api_key)

# Crear una instancia global del servicio
omdb_service = get_omdb_service()