# Configuración del Proyecto de Películas

## Stack Tecnológico

### Backend
- **FastAPI**: Framework web de alto rendimiento
- **SQLModel**: ORM + modelos de datos (combina SQLAlchemy y Pydantic)
- **PostgreSQL**: Sistema de gestión de base de datos
- **Pydantic**: Incluido en SQLModel para validación de datos

### Frontend
- **Reflex**: Framework para la interfaz web en Python

## Estructura del Proyecto

```
.
├── backend
│   ├── app
│   │   ├── api.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── Dockerfile
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── __pycache__
│   │   │   ├── api.cpython-311.pyc
│   │   │   ├── auth.cpython-311.pyc
│   │   │   ├── config.cpython-311.pyc
│   │   │   ├── database.cpython-311.pyc
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── main.cpython-311.pyc
│   │   │   └── models.cpython-311.pyc
│   │   └── services
│   │       ├── __init__.py
│   │       ├── omdb_service.py
│   │       └── __pycache__
│   │           ├── __init__.cpython-311.pyc
│   │           ├── omdb.cpython-311.pyc
│   │           └── omdb_service.cpython-311.pyc
│   ├── logs
│   │   └── movie_app.log
│   ├── pytest.ini
│   ├── requirements.txt
│   └── tests
│       ├── conftest.py
│       ├── fixtures
│       │   ├── __init__.py
│       │   ├── mock_responses.py
│       │   └── movie_data.py
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_auth.py
│       ├── test_config.py
│       ├── test_database.py
│       ├── test_models.py
│       └── test_services
│           ├── __init__.py
│           └── test_omdb_service.py
├── docker-compose.yml
└── frontend
    ├── components
    ├── pages
    └── requirements.txt
```

## Configuración para Google Cloud Run

### Dockerfiles

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
```

#### Frontend Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["reflex", "run", "--env", "prod", "--port", "${PORT}"]
```

### Variables de Entorno Críticas

```bash
# Base de datos
DATABASE_URL=postgresql+asyncpg://<user>:<password>@/<db>?host=/cloudsql/<instance>

# Google Cloud
GOOGLE_CLOUD_PROJECT=<your-project>

# API Externa
OMDB_API_KEY=<your-key>
```

## Consideraciones de Despliegue en Google Cloud Run

1. **Servicios Múltiples**:
   - Servicio backend (FastAPI)
   - Servicio frontend (Reflex)
   - Cloud SQL para PostgreSQL

2. **Seguridad**:
   - Usar Cloud SQL Auth Proxy para conexiones seguras a la base de datos
   - Gestionar secretos con Secret Manager
   - Configurar CORS entre servicios

3. **Configuraciones Específicas**:
   - Cloud Run asigna puertos dinámicamente (usar variable PORT)
   - Configurar Cloud SQL para PostgreSQL
   - Establecer políticas de IAM apropiadas

## Requisitos del Proyecto

1. **Fetch de Datos**:
   - Obtener 100 películas de OMDB API
   - Almacenar en PostgreSQL
   - Ejecutar solo si la base de datos está vacía

2. **API Endpoints**:
   - Listar películas (con paginación)
   - Obtener película individual
   - Añadir nueva película
   - Eliminar película (requiere autenticación)

3. **Funcionalidades Frontend**:
   - Visualización de lista de películas
   - Detalles de película individual
   - Formulario de adición de películas
   - Interfaz de administración

## Próximos Pasos de Implementación

1. **Configuración Inicial**:
   - Crear estructura de proyecto
   - Configurar entorno virtual
   - Instalar dependencias base

2. **Backend**:
   - Implementar modelos SQLModel
   - Configurar FastAPI
   - Crear endpoints básicos
   - Integrar con OMDB API

3. **Frontend**:
   - Configurar Reflex
   - Crear componentes base
   - Implementar páginas principales

4. **Despliegue**:
   - Configurar Google Cloud Project
   - Preparar Cloud SQL
   - Configurar Cloud Run
   - Implementar CI/CD

## Ejemplo de Modelo SQLModel

```python
from typing import Optional
from sqlmodel import Field, SQLModel

class Movie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    year: str
    imdb_id: str = Field(unique=True)
    plot: Optional[str] = None
    poster: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "The Matrix",
                "year": "1999",
                "imdb_id": "tt0133093"
            }
        }
```
