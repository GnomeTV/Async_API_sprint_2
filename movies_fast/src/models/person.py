from enum import Enum

from models.mixins import DateMixin, UUIDMixin


class RoleEnum(str, Enum):
    actor: str = 'actor'
    writer: str = 'writer'
    director: str = 'director'


class Person(UUIDMixin, DateMixin):
    full_name: str
    role: RoleEnum

    class Config:
        use_enum_values = True
