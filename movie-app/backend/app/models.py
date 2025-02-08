from sqlmodel import SQLModel, Field
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel

class MovieBase(SQLModel):
    title: str
    year: str
    imdb_id: str = Field(unique=True)
    plot: Optional[str] = None
    poster: Optional[str] = None

class Movie(MovieBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class MovieCreate(SQLModel):
    title: str = Field(..., description="Título de la película a buscar")

class MovieResponse(MovieBase):
    id: int

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int