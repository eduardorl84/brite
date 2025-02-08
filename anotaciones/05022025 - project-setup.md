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
movie-app/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app
│   │   ├── models.py         # SQLModel models
│   │   ├── database.py       # DB configuration
│   │   ├── api.py            # API endpoints
│   │   └── config.py         # Settings
│   └── tests/
│
├── frontend/                  # Reflex app
│   ├── pages/
│   └── components/
│
└── docker-compose.yml
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
