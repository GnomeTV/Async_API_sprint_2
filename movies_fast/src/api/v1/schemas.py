from uuid import UUID

from pydantic import BaseModel, Field


class PageParams(BaseModel):
    """Модель для нумерации и размера страниц в запросах."""

    page_num: int | None
    page_size: int | None


class SquareBracketsParams(PageParams):
    """К модели с пагинацией добавляется фильтр."""

    filter_genre: str | None


class Genre(BaseModel):
    """Класс модели для отдачи информации о жанре в АПИ."""

    id: UUID
    name: str


class PersonInfo(BaseModel):
    """Класс модели для отдачи информации о персоне в API."""

    id: UUID
    full_name: str = Field(alias="name")
    role: list[str]
    film_ids: list[UUID]


class MovieShortInfo(BaseModel):
    """Класс для краткой информации по фильму для персоны."""

    id: UUID
    title: str
    imdb_rating: float | None


class Person(BaseModel):
    id: UUID
    name: str


class Film(BaseModel):
    id: UUID
    imdb_rating: float | None
    genre: list[Genre]
    title: str
    description: str | None
    director: list[str] | None
    actors_names: list[str] | None
    writers_names: list[str] | None
    actors: list[Person] | None
    writers: list[Person] | None
    directors: list[Person] | None
