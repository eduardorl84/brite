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
    """Modelo para crear una nueva película solo con el título."""
    title: str

class MovieResponse(MovieBase):
    id: int

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True

class UserCreate(SQLModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int