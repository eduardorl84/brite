from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    omdb_api_key: str
    google_cloud_project: str
    secret_key: str = "your-secret-key-here"  # En producción, usar una clave secreta segura
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()