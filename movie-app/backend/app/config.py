from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    omdb_api_key: str
    google_cloud_project: str

    class Config:
        env_file = ".env"

settings = Settings()