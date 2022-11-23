import logging
from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from db.abs_storages import BaseCacheStorage, BaseDbStorage
from db.elastic import get_elastic, ElasticStorage
from db.redis import get_redis, RedisCacheStorage
from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService:
    def __init__(self, cache_stor: BaseCacheStorage, db_stor: BaseDbStorage):
        self.cache_stor = cache_stor
        self.db_stor = db_stor

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        """Возвращает объект жанра по id."""
        # Пытаемся получить данные из кеша
        genre = await self.cache_stor.get_object(genre_id)
        if genre:
            logging.debug("Genre cache hit - %s", genre["name"])
        if not genre:
            # нет в кеше - ищем в базе
            genre = await self.db_stor.get_genre(genre_id)
            if not genre:
                return None
            await self.cache_stor.save_object(genre_id, genre)
            logging.debug("Genre saved to cache - %s", genre["name"])
        return Genre(**genre)

    async def get_genre_list(
        self,
        page: int | None = 1,
        size: int | None = 10,
    ) -> list[Genre] | None:
        """Возвращает список жанров."""
        if page is None or page < 1:
            page = 1
        if size is None or size < 1:
            size = 10
        cache_key = self._get_cache_key(page, size)
        # ищем в кеше по ключу
        genres = await self.cache_stor.get_list_objects(cache_key)
        if genres:
            logging.debug("Genre list cache hit - %s", cache_key)
        if not genres:
            # ищем в базе
            genres = await self.db_stor.get_list_genre(size * (page - 1), size)
            if not genres:
                return None
            # сохраняем в кэш
            await self.cache_stor.save_list_objects(cache_key, genres)
            logging.debug("Genre list saved to cache - %s", cache_key)
        return [Genre(**genre) for genre in genres]

    @staticmethod
    def _get_cache_key(page: int, size: int) -> str:
        return f"genres_page:{page}_size:{size}"


# Ниже определяется тип хранилища и кэша, с которыми будет работать GenreService.
# Нужно подготовить и отдать переменные с объектами хранилищ в создаваемый класс.
# При желании можно написать классы для других хранилищ и передавать объекты этих
# классов в создаваемый объект класса GenreService


# объявляем один объект на модуль
redis_cache_genre: RedisCacheStorage | None = None
elastic_genre: ElasticStorage | None = None


async def get_redis_cache() -> RedisCacheStorage:
    global redis_cache_genre
    if redis_cache_genre is None:
        redis = await get_redis()
        redis_cache_genre = RedisCacheStorage(redis, GENRE_CACHE_EXPIRE_IN_SECONDS)
    return redis_cache_genre


async def get_elastic_stor() -> ElasticStorage:
    global elastic_genre
    if elastic_genre is None:
        elastic_conn = await get_elastic()
        elastic_genre = ElasticStorage(elastic_conn)
    return elastic_genre


@lru_cache()
def get_genre_service(
    cache_db: BaseCacheStorage = Depends(get_redis_cache),
    storage_db: BaseDbStorage = Depends(get_elastic_stor),
) -> GenreService:
    return GenreService(cache_db, storage_db)
