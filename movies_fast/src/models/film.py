from datetime import datetime

from models.genre import Genre
from models.mixins import DateMixin, UUIDMixin
from models.person import Person
from pydantic.types import FilePath


class Film(UUIDMixin, DateMixin):
    file_path: FilePath | None
    title: str
    description: str | None
    creation_date: datetime | None
    imdb_rating: float | None
    type: str
    genres: list[Genre] | None
    persons: list[Person] | None
