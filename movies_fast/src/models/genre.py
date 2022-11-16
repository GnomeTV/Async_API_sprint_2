from models.mixins import DateMixin, UUIDMixin


class Genre(UUIDMixin, DateMixin):
    name: str
    description: str | None
