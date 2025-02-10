import pytest
import os
from app.config import Settings
from pydantic import ValidationError

def test_load_env_variables(monkeypatch):
    """Verifica que las variables de entorno se cargan correctamente."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("OMDB_API_KEY", "test_api_key")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test_project")
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    
    settings = Settings()
    assert settings.database_url == "sqlite:///test.db"
    assert settings.omdb_api_key == "test_api_key"
    assert settings.google_cloud_project == "test_project"
    assert settings.secret_key == "test_secret"
    assert settings.access_token_expire_minutes == 60

def test_default_values():
    """Verifica que los valores por defecto se asignan correctamente."""
    settings = Settings()
    assert settings.secret_key == "your-secret-key-here"
    assert settings.access_token_expire_minutes == 30

def test_invalid_configuration(monkeypatch):
    """Verifica que la configuración inválida genera errores apropiados."""
    # Eliminar todas las variables de entorno requeridas
    env_vars = [
        "DATABASE_URL",
        "OMDB_API_KEY",
        "GOOGLE_CLOUD_PROJECT",
        "SECRET_KEY",
        "ACCESS_TOKEN_EXPIRE_MINUTES"
    ]
    
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
    
    # Establecer un entorno limpio sin variables
    monkeypatch.setattr(os, 'environ', {})
    
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,  # Deshabilitar la carga del archivo .env
            _env_file_encoding=None
        )