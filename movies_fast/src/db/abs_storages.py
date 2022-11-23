"""Модуль определяет абстрактные классы для работы с хранилищами."""

from abc import ABC, abstractmethod
from uuid import UUID


class BaseCacheStorage(ABC):
    @abstractmethod
    async def get_object(self, object_id: UUID) -> dict | None:
        """Возвращает словарь с данными объекта по id в кэше."""
        pass

    @abstractmethod
    async def save_object(self, object_id: UUID, body: dict) -> None:
        """Сохраняет объект в кэш."""
        pass

    @abstractmethod
    async def get_list_objects(self, key: str) -> list[dict] | None:
        """Возвращает список объектов (словарей) по ключу."""
        pass

    @abstractmethod
    async def save_list_objects(self, key: str, objs: list[dict]) -> None:
        """Сохраняет список объектов (словарей) по ключу в кэш."""
        pass


class BaseDbStorage(ABC):
    @abstractmethod
    async def get_genre(self, genre_id: UUID) -> dict | None:
        """Возвращает жанр по id."""
        pass

    @abstractmethod
    async def get_list_genre(
        self, offset: int = 0, limit: int = 10
    ) -> list[dict] | None:
        """Возвращает список жанров."""
        pass

    @abstractmethod
    async def get_person(self, genre_id: UUID) -> dict | None:
        """Возвращает персону по id."""
        pass

    @abstractmethod
    async def get_film(self, film_id: UUID) -> dict | None:
        """Получить фильм по id."""
        pass

    @abstractmethod
    async def get_person_details(self, person_id: UUID) -> dict | None:
        """Получить детали персоны (фильмы, роли) по id."""
        pass

    @abstractmethod
    async def search_person(
        self, query: str, offset: int = 0, limit: int = 10
    ) -> list[dict] | None:
        """Поиск. Возвращает список персон - нужное кол-во с нужной позиции."""
        pass

    @abstractmethod
    async def search_film(self,
                          query: str | None = None,
                          filter_genre: UUID | None = None,
                          offset: int = 0,
                          limit: int = 10,
                          sort: str = '-imdb_rating',
                          ) -> list[dict] | None:
        """Поиск фильмов с пагинацией и фильтрацией."""
        pass

    @abstractmethod
    async def get_pers_films(
        self,
        person_id: UUID,
        offset: int = 0,
        limit: int = 10,
    ) -> list[dict] | None:
        """Возвращает список фильмов заданной персоны."""
        pass
