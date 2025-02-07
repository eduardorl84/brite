import httpx
from ..config import settings

async def fetch_movie_details(imdb_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://www.omdbapi.com/",
            params={
                "apikey": settings.omdb_api_key,
                "i": imdb_id
            }
        )
        return response.json()