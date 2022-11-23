import json
import logging
from uuid import UUID
from aioredis import Redis

from db.abs_storages import BaseCacheStorage

logger = logging.getLogger(__name__)

redis: Redis | None = None


async def get_redis() -> Redis:
    return redis


class RedisCacheStorage(BaseCacheStorage):
    """Реализация кэша объектов приложения Фильмы на Redis."""

    redis: Redis
    expire_timeout: int

    def __init__(self, redis_conn: Redis, expire_timeout: int = 300):
        self.redis = redis_conn
        self.expire_timeout = expire_timeout

    async def get_object(self, object_id: UUID) -> dict | None:
        try:
            data = await self.redis.get(str(object_id))
        except ConnectionError as e:
            data = None
            logger.error(e)
        if not data:
            return None
        return json.loads(data)

    async def save_object(self, object_id: UUID, body: dict) -> None:
        try:
            await self.redis.set(str(object_id),
                                 json.dumps(body),
                                 ex=self.expire_timeout,
                                 )
        except ConnectionError as e:
            logger.error(e)

    async def get_list_objects(self, key: str) -> list[dict] | None:
        try:
            data = await self.redis.get(key)
        except ConnectionError as e:
            data = None
            logger.error(e)
        if not data:
            return None
        return list(json.loads(data))

    async def save_list_objects(self, key: str, objs: list[dict]) -> None:
        try:
            await self.redis.set(key, json.dumps(objs), ex=self.expire_timeout)
        except ConnectionError as e:
            logger.error(e)
