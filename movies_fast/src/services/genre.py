import json
import logging
from functools import lru_cache
from uuid import UUID

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        """Возвращает объект жанра по id."""
        # Пытаемся получить данные из кеша
        genre = await self._genre_from_cache(genre_id)
        if genre:
            logging.debug("Genre cache hit - %s", genre.name)
        if not genre:
            # нет в кеше - ищем его в Elasticsearch
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                # отсутствует в Elasticsearch -> жанра вообще нет в базе
                return None
            # Сохраняем жанр в кеш
            await self._put_genre_to_cache(genre)
            logging.debug("Genre saved to cache - %s", genre.name)
        return genre

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
        redis_key = self._get_redis_key(page, size)
        # ищем в кеше по ключу
        genres = await self._genre_list_from_cache(redis_key)
        if genres:
            logging.debug("Genre list cache hit - %s", redis_key)
        if not genres:
            # в кеше не найдено - ищем в эластике
            genres = await self._get_genre_list_from_elastic(size * (page - 1), size)
            if not genres:
                return None
            # сохраняем в кэш
            await self._put_genre_list_to_cache(redis_key, genres)
            logging.debug("Genre list saved to cache - %s", redis_key)
        return genres

    @staticmethod
    def _get_redis_key(page: int, size: int) -> str:
        return f"genres_page:{page}_size:{size}"

    async def _get_genre_list_from_elastic(
        self,
        offset: int,
        limit: int,
    ) -> list[Genre] | None:
        """Возвращает из эластика список моделей с жанрами."""
        try:
            doc = await self.elastic.search(index="genres", from_=offset, size=limit)
        except NotFoundError:
            return None
        genres = []
        for item in doc.raw["hits"]["hits"]:
            genres.append(Genre(**item["_source"]))  # попутная валидация
        return genres

    async def _get_genre_from_elastic(self, genre_id: UUID) -> Genre | None:
        try:
            doc = await self.elastic.get(index="genres", id=str(genre_id))
        except NotFoundError:
            return None
        return Genre(**doc["_source"])

    async def _genre_from_cache(self, genre_id: UUID) -> Genre | None:
        data = await self.redis.get(str(genre_id))
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            str(genre.id),
            genre.json(),
            ex=GENRE_CACHE_EXPIRE_IN_SECONDS,
        )

    async def _genre_list_from_cache(self, redis_key: str) -> list[Genre] | None:
        data = await self.redis.get(redis_key)
        if not data:
            return None
        data = json.loads(data)
        return [Genre.parse_raw(genre) for genre in data]

    async def _put_genre_list_to_cache(self, redis_key: str, genres: list[Genre]):
        genres_json = [genre.json() for genre in genres]
        await self.redis.set(
            redis_key,
            json.dumps(genres_json),
            ex=GENRE_CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
